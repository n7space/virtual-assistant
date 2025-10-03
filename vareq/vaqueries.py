from enum import Enum
from typing import List, Dict, Optional
from .varequirementreader import Requirement
from .vallminterface import Llm, Chat, LlmConfig, ChatConfig
from . import helpers
from mako.template import Template
from mako.lookup import TemplateLookup

import logging
import json
import os


class QueryArity(Enum):
    UNARY = 1
    BINARY = 2
    NARY = 3


class QueryKind(Enum):
    FREETEXT = 1
    BINARY = 2


class PredefinedQuery:
    id: str
    template: str
    arity: QueryArity
    kind: QueryKind
    threshold: float

    def __init__(self, kind: QueryKind, arity: QueryArity, id: str, template: str):
        self.id = id
        self.template = template
        self.kind = kind
        self.arity = arity
        self.threshold = 0 if self.kind == QueryKind.BINARY else None


class BatchResponseElement:
    requirement: Requirement
    embedding: List[float]
    applied_requirements: List[Requirement]
    message: str
    context_requirements: List[Requirement]

    def __init__(self):
        self.requirement = None
        self.message = None
        self.embedding = []
        self.context_requirements = []
        self.applied_requirements = []

    def to_dict(self) -> Dict:
        return {
            "requirement": self.requirement.to_dict() if self.requirement else None,
            "embedding": self.embedding,
            "applied_requirements": [
                req.to_dict() for req in self.applied_requirements
            ],
            "message": self.message,
            "context_requirements": [
                req.to_dict() for req in self.context_requirements
            ],
        }


class PredefinedQueries:
    llm: Llm
    queries: Dict[str, PredefinedQuery]
    batch_query_context_size: int

    def __init__(self, llm: Llm):
        self.queries = dict()
        self.llm = llm
        self.batch_query_context_size = 3

    def register(self, query: PredefinedQuery):
        logging.debug(f"Registering query for ID {query.id}")
        self.queries[query.id] = query

    def arity(self, id: str) -> QueryArity:
        if not id in self.queries.keys():
            return None
        query = self.queries[id]
        return query.arity

    def exists(self, id: str) -> bool:
        return id in self.queries.keys()

    def process(self, id: str, requirement: Requirement) -> str:
        if not id in self.queries.keys():
            logging.error(f"Query for ID {id} not found")
            return None
        logging.debug(f"Found query for ID {id}")
        query = self.queries[id]
        if query.arity != QueryArity.UNARY:
            logging.error(f"Query for ID {id} is not unary, but {query.arity}")
            return "Query not supported for a single requirement"
        question = query.template.format(
            requirement.id,
            requirement.description,
            requirement.note,
            requirement.justification,
            requirement.type,
            requirement.validation_type,
            ",".join(requirement.traces),
        )
        logging.debug(f"Query got resolved to: {question}")
        reply = self.llm.query(question)
        logging.debug(f"Query result is: {reply}")
        if query.kind == QueryKind.BINARY:
            # It is simpler to ask the LLM for estimate than change its sensititivy and try to get a yes/no answer directly
            # so an estimate is used; in order to extract properly, we need to ignore the thinking phase (if applicable)
            thoughtless_reply = helpers.remove_think_markers(reply)
            estimate = helpers.extract_number(thoughtless_reply)
            if estimate is None:
                return "False"
            if estimate >= query.threshold:
                return "True"
            return "False"
        return reply

    def initialize_batch_response(
        self, requirements: List[Requirement]
    ) -> List[BatchResponseElement]:
        response = []
        for requirement in requirements:
            element = BatchResponseElement()
            element.requirement = requirement
            logging.debug(f"Calculating embedding for {requirement.description}")
            element.embedding = self.llm.embedding(requirement.description)
            response.append(element)

        for element in response:
            similarities = []
            for other in response:
                # Do not consider itself
                if other is element:
                    continue
                similarity = helpers.cosine_similarity(
                    element.embedding, other.embedding
                )
                similarities.append((similarity, other.requirement))
            # Sort by similarity - first element of the tuple
            similarities.sort(reverse=True, key=lambda x: x[0])
            # Slicing does not raise an error is the list is too short, up to context_size will be returned
            element.context_requirements = [
                req for _, req in similarities[: self.batch_query_context_size]
            ]
        return response

    def find_existing_result(
        self,
        response: List[BatchResponseElement],
        requirement_1: Requirement,
        requirement_2: Requirement,
    ) -> Optional[str]:
        for element in response:
            if element.requirement == requirement_1:
                for applied_requirement in element.applied_requirements:
                    if applied_requirement == requirement_2:
                        return element.message
        return None

    def process_batch_response(
        self, query: PredefinedQuery, response: List[BatchResponseElement]
    ) -> List[BatchResponseElement]:
        total_requirement_count = len(response)
        pairs = {}
        for count, element in enumerate(response, 1):
            logging.debug(
                f"Processing requirement {count} of {total_requirement_count}"
            )
            requirement = element.requirement
            for other in element.context_requirements:
                logging.debug(
                    f"Processing pair: {requirement.description} and {other.description}"
                )
                if (requirement, other) in pairs:
                    # Query was already executed (for a different order)
                    logging.debug(
                        f"Skipping query for {requirement.id} and {other.id} [already done in reverse]"
                    )
                    existing_result = self.find_existing_result(
                        response, other, requirement
                    )
                    if existing_result:
                        logging.debug(
                            f"Reusing positive result for {requirement.id} and {other.id}"
                        )
                        element.applied_requirements.append(other)
                        element.message = existing_result
                    break
                # Do not query again
                pairs[(requirement, other)] = True
                pairs[(other, requirement)] = True
                question = query.template.format(
                    requirement.id,
                    requirement.description,
                    requirement.note,
                    requirement.justification,
                    requirement.type,
                    requirement.validation_type,
                    ",".join(requirement.traces),
                    other.id,
                    other.description,
                    other.note,
                    other.justification,
                    other.type,
                    other.validation_type,
                    ",".join(other.traces),
                )
                logging.debug(f"Query got resolved to: {question}")
                reply = self.llm.query(question)
                logging.debug(f"Query result is: {reply}")
                thoughtless_reply = helpers.remove_think_markers(reply)
                if query.kind == QueryKind.FREETEXT:
                    # Only a single comparison with the closes requirement
                    element.applied_requirements.append(other)
                    element.message = thoughtless_reply
                    break
                elif query.kind == QueryKind.BINARY:
                    # It is simpler to ask the LLM for estimate than change its sensititivy and try to get a yes/no answer directly
                    # so an estimate is used; in order to extract properly, we need to ignore the thinking phase (if applicable)
                    estimate = helpers.extract_number(thoughtless_reply)
                    if estimate is None:
                        continue
                    if estimate >= query.threshold:
                        logging.info(
                            f"Detection: {estimate}% for [{requirement.id}:{requirement.description}] and [{other.id}: {other.description}]"
                        )
                        element.applied_requirements.append(other)
                        element.message = thoughtless_reply
                        break
        return response

    def process_batch(
        self, id: str, requirements: List[Requirement]
    ) -> List[BatchResponseElement]:
        if id not in self.queries:
            logging.error(f"Query for ID {id} not found")
            return None
        query = self.queries[id]
        if query.arity != QueryArity.NARY:
            logging.error(f"Query for ID {id} is not nary, but {query.arity}")
            return None

        response = self.initialize_batch_response(requirements)
        response = self.process_batch_response(query, response)
        return response


class PredefinedQueryReader:

    base_directory: str

    def __init__(self, base_directory: str):
        self.base_directory = base_directory or "."

    def load_from_file(self, path: str) -> List[PredefinedQuery]:
        if not os.path.exists(path):
            return dict()
        logging.debug(f"Reading predefined queries from {path}")
        with open(path, "r") as file:
            data = json.load(file)
            queries = self.load_from_json(data)
            return queries

    def load_from_json(self, data: dict) -> List[PredefinedQuery]:
        queries = []
        lookup = TemplateLookup(directories=[".", self.base_directory])
        for query_data in data["queries"]:
            id = query_data["id"]
            arity = QueryArity[query_data["arity"].upper()]
            kind = QueryKind[query_data["kind"].upper()]
            if kind == QueryKind.BINARY:
                threshold = query_data["threshold"]
            else:
                threshold = None
            query_template = query_data["query"]
            logging.debug(f"Read query ID {id} with template {query_template}")
            template = Template(text=query_template, lookup=lookup)
            rendered_template = template.render()
            query = PredefinedQuery(kind, arity, id, rendered_template)
            query.threshold = threshold
            queries.append(query)
        return queries
