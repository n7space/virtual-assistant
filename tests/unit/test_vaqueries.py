from typing import List
from vareq import helpers
from vareq.vaqueries import PredefinedQueryReader, QueryKind, QueryArity
import logging
import pytest
import os
from vareq.vaqueries import PredefinedQueries, PredefinedQuery, QueryArity, QueryKind
from vareq.varequirementreader import Requirement

TEST_DIR: str = os.path.dirname(os.path.realpath(__file__))
RESOURCE_DIR: str = os.path.join(TEST_DIR, "resources")
logging.basicConfig(level=logging.DEBUG)


class LlmMock:
    _embedding_return: List[float]
    _query_return: str

    def __init__(self, embedding_return=None, query_return=None):
        self._embedding_return = embedding_return or [1.0, 0.0, 0.0]
        self._query_return = query_return or "42"

    def embedding(self, text):
        return self._embedding_return

    def query(self, question):
        return self._query_return


def create_requirement(id: str, description: str):
    requirement = Requirement()
    requirement.id = id
    requirement.description = description
    requirement.note = "note"
    requirement.justification = "justification"
    requirement.type = "functional"
    requirement.validation_type = "T"
    requirement.traces = ["REQ-10", "REQ-20"]
    return requirement


def test_predefined_queries_are_read():
    reader = PredefinedQueryReader(RESOURCE_DIR)

    queries = reader.load_from_file(
        os.path.join(RESOURCE_DIR, "predefined_queries.json")
    )

    assert not queries is None
    assert 4 == len(queries)
    assert "review" == queries[0].id
    assert QueryArity.UNARY == queries[0].arity
    assert QueryKind.FREETEXT == queries[0].kind
    assert "assign-type" == queries[1].id
    assert QueryArity.UNARY == queries[1].arity
    assert QueryKind.FREETEXT == queries[1].kind
    assert "multi" == queries[2].id
    assert QueryArity.NARY == queries[2].arity
    assert QueryKind.BINARY == queries[2].kind
    assert 50 == queries[2].threshold
    assert "check" == queries[3].id
    assert QueryArity.UNARY == queries[3].arity
    assert QueryKind.BINARY == queries[3].kind
    assert 75 == queries[3].threshold


def test_predefined_query_template_is_rendered():
    reader = PredefinedQueryReader(RESOURCE_DIR)

    queries = reader.load_from_file(
        os.path.join(RESOURCE_DIR, "predefined_queries.json")
    )
    template = queries[0].template

    # Check the included file
    assert '1. Each requirement shall use "shall".' in template
    # Check the insertion points for the python format
    assert "Description: {1}" in template


def test_initialize_batch_response_succeeds():
    llm = LlmMock([1, 0, 0])
    queries = PredefinedQueries(llm)
    requirements = [
        create_requirement(f"REQ-FUN-{i}0", f"Description {i}") for i in range(3)
    ]
    batch = queries.initialize_batch_response(requirements)
    assert len(batch) == 3
    for element, requirement in zip(batch, requirements):
        assert requirement == element.requirement
        assert [1, 0, 0] == element.embedding
        assert isinstance(element.applied_requirements, list)
        assert hasattr(element, "context_requirements")


def test_process_batch_response_handles_freetext_query():
    llm = LlmMock(query_return="Some reply")
    queries = PredefinedQueries(llm)
    query = PredefinedQuery(QueryKind.FREETEXT, QueryArity.NARY, "id", "{0} {1}")
    requirements = [
        create_requirement("REQ-10", "Description A"),
        create_requirement("REQ-20", "Description B"),
    ]
    batch = queries.initialize_batch_response(requirements)
    result = queries.process_batch_response(query, batch)
    for element in result:
        assert 1 == len(element.applied_requirements)
        assert "Some reply" == element.message


def test_process_handles_binary_query_over_threshold():
    llm = LlmMock(query_return="80")
    queries = PredefinedQueries(llm)
    query = PredefinedQuery(QueryKind.BINARY, QueryArity.UNARY, "id", "{0} {1}")
    query.threshold = 50
    queries.register(query)
    requirement = create_requirement("REQ-10", "Description A")
    result = queries.process("id", requirement)
    assert "true" == result.lower()


def test_process_handles_binary_query_under_threshold():
    llm = LlmMock(query_return="80")
    queries = PredefinedQueries(llm)
    query = PredefinedQuery(QueryKind.BINARY, QueryArity.UNARY, "id", "{0} {1}")
    query.threshold = 90
    queries.register(query)
    requirement = create_requirement("REQ-10", "Description A")
    result = queries.process("id", requirement)
    assert "false" == result.lower()


def test_process_batch_response_handles_binary_query_over_threshold():
    llm = LlmMock(query_return="80")
    queries = PredefinedQueries(llm)
    query = PredefinedQuery(QueryKind.BINARY, QueryArity.NARY, "id", "{0} {1}")
    query.threshold = 50
    requirements = [
        create_requirement("REQ-10", "Description A"),
        create_requirement("REQ-20", "Description B"),
    ]
    batch = queries.initialize_batch_response(requirements)
    result = queries.process_batch_response(query, batch)
    for element in result:
        assert 1 == len(element.applied_requirements)
        assert "80" == element.message


def test_process_batch_response_handles_binary_query_under_threshold():
    llm = LlmMock(query_return="30")
    queries = PredefinedQueries(llm)
    query = PredefinedQuery(QueryKind.BINARY, QueryArity.NARY, "id", "{0} {1}")
    query.threshold = 50
    requirements = [
        create_requirement("REQ-10", "Description A"),
        create_requirement("REQ-20", "Description B"),
    ]
    batch = queries.initialize_batch_response(requirements)
    result = queries.process_batch_response(query, batch)
    for element in result:
        assert 0 == len(element.applied_requirements)
        assert element.message is None


def test_process_batch_handles_wrong_id():
    llm = LlmMock()
    queries = PredefinedQueries(llm)
    requirements = [create_requirement("REQ-10", "Description")]
    result = queries.process_batch("not-found", requirements)
    assert result is None


def test_process_batch_handles_wrong_arity():
    llm = LlmMock()
    queries = PredefinedQueries(llm)
    query = PredefinedQuery(QueryKind.BINARY, QueryArity.UNARY, "do-stuff", "{0}")
    queries.register(query)
    requirements = [create_requirement("REQ-10", "Description")]
    result = queries.process_batch("do-stuff", requirements)
    assert result is None


def test_process_batch_succeeds():
    llm = LlmMock(query_return="70", embedding_return=[1.0])
    queries = PredefinedQueries(llm)
    query = PredefinedQuery(QueryKind.BINARY, QueryArity.NARY, "do-stuff", "{0}")
    query.threshold = 50
    queries.register(query)
    requirements = [
        create_requirement("REQ-10", "Description A"),
        create_requirement("REQ-20", "Description B"),
    ]
    result = queries.process_batch("do-stuff", requirements)
    assert result is not None
    assert 2 == len(result)
    assert "REQ-10" == result[0].requirement.id
    assert 1 == len(result[0].applied_requirements)
    assert "70" == result[0].message
    assert "REQ-20" == result[1].requirement.id
    assert 1 == len(result[1].applied_requirements)
    assert "70" == result[1].message
