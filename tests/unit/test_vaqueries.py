from vareq.vaqueries import PredefinedQueryReader
import logging
import pytest
import os

TEST_DIR: str = os.path.dirname(os.path.realpath(__file__))
RESOURCE_DIR: str = os.path.join(TEST_DIR, "resources")
logging.basicConfig(level=logging.DEBUG)

def test_predefined_queries_are_read():
    reader = PredefinedQueryReader(RESOURCE_DIR)
    
    queries = reader.load_from_file(os.path.join(RESOURCE_DIR, "predefined_queries.json"))

    assert not queries is None
    assert 2 == len(queries)
    assert "review" == queries[0].id
    assert "assign-type" == queries[1].id

def test_predefined_query_template_is_rendered():
    reader = PredefinedQueryReader(RESOURCE_DIR)
    
    queries = reader.load_from_file(os.path.join(RESOURCE_DIR, "predefined_queries.json"))
    template = queries[0].template

    assert "1. Each requirement shall use \"shall\"." in template
