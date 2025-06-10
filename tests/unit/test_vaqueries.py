from vareq.vaqueries import PredefinedQueryReader, QueryKind, QueryArity
import logging
import pytest
import os

TEST_DIR: str = os.path.dirname(os.path.realpath(__file__))
RESOURCE_DIR: str = os.path.join(TEST_DIR, "resources")
logging.basicConfig(level=logging.DEBUG)


def test_predefined_queries_are_read():
    reader = PredefinedQueryReader(RESOURCE_DIR)

    queries = reader.load_from_file(
        os.path.join(RESOURCE_DIR, "predefined_queries.json")
    )

    assert not queries is None
    assert 3 == len(queries)
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
