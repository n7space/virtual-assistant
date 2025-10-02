import logging
import pytest
import os
import json
from unittest.mock import Mock, patch
import tempfile

from vareq.vaserver import VaServer, ServerConfig
from vareq.vaengine import Engine, EngineConfig
from vareq.vallminterface import LlmConfig
from vareq.varequirementreader import Mappings, Requirement

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
    # Use temporary database
    db_path = os.path.join(tempfile.mkdtemp(), "db")
    cfg.lib_config.persistent_storage_path = db_path
    yield cfg


@pytest.fixture
def server_config() -> ServerConfig:
    config = ServerConfig()
    config.host = "127.0.0.1"
    config.port = 8000
    yield config


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


def test_areyoualive_works(va_client):
    response = va_client.get("/areyoualive/")
    assert response.status_code == 200
    data = response.json
    assert len(data) == 1
    assert data["status"] == "ok"
