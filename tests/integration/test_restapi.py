import logging
import pytest
import os
import json
from unittest.mock import Mock, patch
import tempfile

from vareq.vaserver import VaServer, ServerConfig
from vareq.vaengine import EngineConfig
from vareq.vallminterface import LlmConfig, Llm
from vareq.varequirementreader import Mappings
from vareq.vaqueries import PredefinedQueryReader

TEST_DIR: str = os.path.dirname(os.path.realpath(__file__))
RESOURCE_DIR: str = os.path.join(TEST_DIR, "resources")
logging.basicConfig(level=logging.DEBUG)


def check_ollama_and_skip():
    config = LlmConfig()
    llm = Llm(config)
    if not llm.is_available():
        pytest.skip("Ollama not available")


@pytest.fixture
def engine_config() -> EngineConfig:
    cfg = EngineConfig()
    # Make the LLM as deterministic as possible
    cfg.llm_config.temperature = 0
    # For compatibility with the test requirements
    cfg.lib_config.requirement_document_mappings = Mappings().update_from_dict(
        {"worksheet_name": "reqs"}
    )
    cfg.requirements_file_path = os.path.join(RESOURCE_DIR, "test_requirements.xlsx")
    # Test queries
    reader = PredefinedQueryReader(RESOURCE_DIR)
    cfg.predefined_queries = reader.load_from_file(
        os.path.join(RESOURCE_DIR, "predefined_queries.json")
    )
    # Use temporary database
    db_path = os.path.join(tempfile.mkdtemp(), "db")
    cfg.lib_config.persistent_storage_path = db_path
    return cfg


@pytest.fixture
def server_config() -> ServerConfig:
    config = ServerConfig()
    config.host = "127.0.0.1"
    config.port = 8000
    return config


@pytest.fixture
def va_server(server_config, engine_config):
    server = VaServer(server_config=server_config, engine_config=engine_config)
    server.prepare()
    yield server


@pytest.fixture
def va_client(va_server):
    va_server.app.config["TESTING"] = True
    with va_server.app.test_client() as client:
        yield client


def test_areyoualive_responds(va_client):
    response = va_client.get("/areyoualive/")
    assert response.status_code == 200
    data = response.json
    assert len(data) == 1
    assert data["status"] == "ok"


def test_query_fails_for_uknown_unary_query(va_client):
    response = va_client.get("/query/unknown/REQ-10")
    assert response.status_code == 200
    data = response.json
    assert len(data) == 5
    assert data["query_id"] == "unknown"
    assert data["requirement_id"] == "REQ-10"
    assert data["status"] == "failed"
    assert data["error"] == "Query not found"
    assert data["reply"] is None


def test_query_fails_for_uknown_nary_query(va_client):
    response = va_client.get("/query/unknown/")
    assert response.status_code == 200
    data = response.json
    assert len(data) == 4
    assert data["query_id"] == "unknown"
    assert data["status"] == "failed"
    assert data["error"] == "Query not found"
    assert data["reply"] is None


def test_query_fails_for_unknown_requirement(va_client):
    response = va_client.get("/query/review/REF-MISSING-10")
    assert response.status_code == 200
    data = response.json
    assert len(data) == 5
    assert data["query_id"] == "review"
    assert data["requirement_id"] == "REF-MISSING-10"
    assert data["status"] == "failed"
    assert data["error"] == "Requirement not found"
    assert data["reply"] is None


def test_query_responds_for_unary(va_client):
    check_ollama_and_skip()
    response = va_client.get("/query/review/REQ-10")
    assert response.status_code == 200
    data = response.json
    assert len(data) == 5
    assert data["query_id"] == "review"
    assert data["requirement_id"] == "REQ-10"
    assert data["status"] == "ok"
    assert data["error"] is None
    assert len(data["reply"]) > 0


def test_query_responds_for_nary(va_client):
    check_ollama_and_skip()
    response = va_client.get("/query/detect-duplicate/")
    assert response.status_code == 200
    data = response.json
    assert len(data) == 4
    assert data["query_id"] == "detect-duplicate"
    assert data["status"] == "ok"
    assert data["error"] is None
    assert len(data["reply"]) > 0
    assert len(data["reply"][0]["requirement"]) > 0
    assert len(data["reply"][0]["embedding"]) > 0
    assert len(data["reply"][0]["applied_requirements"]) > 0
    assert data["reply"][0]["message"] is not None
    assert len(data["reply"][0]["context_requirements"]) > 0


def test_reload_responds(va_client):
    response = va_client.get("/reload/")
    assert response.status_code == 200
    data = response.json
    assert len(data) == 1
    assert data["status"] == "ok"


def test_chat_responds(va_client):
    check_ollama_and_skip()
    response = va_client.get("/chat/please%20respond/")
    assert response.status_code == 200
    data = response.json
    assert len(data) == 5
    assert data["status"] == "ok"
    assert data["query"] == "please respond"
    assert len(data["reply"]) > 0
    assert isinstance(data["references"], list)
    assert isinstance(data["reference_names"], list)
