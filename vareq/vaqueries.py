from typing import List, Dict
from .varequirementreader import Requirement
from .vallminterface import Llm, Chat, LlmConfig, ChatConfig
from mako.template import Template
from mako.lookup import TemplateLookup

import logging
import json
import os

class PredefinedQuery:
    id : str
    template : str

    def __init__(self, id : str, template : str):
        self.id = id
        self.template = template
    
class PredefinedQueries:
    llm : Llm
    queries : Dict[str, PredefinedQuery]

    def __init__(self, llm : Llm):
        self.queries = dict()
        self.llm = llm

    def register(self, query : PredefinedQuery):
        logging.debug(f"Registering query for ID {query.id}")
        self.queries[query.id] = query

    def process(self, id : str, requirement : Requirement) -> str:
        if not id in self.queries.keys():
            logging.error(f"Query for ID {id} not found")
            return None
        logging.debug(f"Found query for ID {id}")
        query = self.queries[id]
        question = query.template.format(requirement.id,
                                      requirement.description,
                                      requirement.note,
                                      requirement.justification,
                                      requirement.type,
                                      requirement.validation_type,
                                      ",".join(requirement.traces))
        logging.debug(f"Query got resolved to: {question}")
        reply = self.llm.query(question)
        logging.debug(f"Query result is: {reply}")
        return reply

class PredefinedQueryReader:

    base_directory : str

    def __init__(self, base_directory : str):
        self.base_directory = base_directory

    def load_from_file(self, path : str) -> List[PredefinedQuery]:
        if not os.path.exists(path):
            return dict()
        logging.debug(f"Reading predefined queries from {path}")
        with open(path, 'r') as file:
            data = json.load(file)
            queries = self.load_from_json(data)
            return queries

    def load_from_json(self, data : dict) -> List[PredefinedQuery]:
        queries = []
        lookup = TemplateLookup(directories=['.', self.base_directory]) 
        for query_data in data['queries']:
            id = query_data['id']
            query_template = query_data['query']
            logging.debug(f"Read query ID {id} with template {query_template}")
            template = Template(text=query_template, lookup=lookup)
            rendered_template = template.render()
            query = PredefinedQuery(id, rendered_template)
            queries.append(query)
        return queries




