from vareq.vallminterface import ChatConfig, LlmConfig, Llm
from vareq.varequirementreader import Mappings
from vareq.vaengine import Engine, EngineConfig
import logging
import pytest
import os
import tempfile

TEST_DIR: str = os.path.dirname(os.path.realpath(__file__))
RESOURCE_DIR: str = os.path.join(TEST_DIR, "resources")
logging.basicConfig(level=logging.DEBUG)


def check_ollama_and_skip():
    config = LlmConfig()
    llm = Llm(config)
    if not llm.is_available():
        pytest.skip("Ollama not available")


def prepare_engine_config() -> EngineConfig:
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
    return cfg


def test_engine_can_create_chat():
    check_ollama_and_skip()
    cfg = EngineConfig()
    engine = Engine(cfg)

    chat = engine.get_chat()

    assert chat is not None


def test_chat_knows_requirements():
    check_ollama_and_skip()
    cfg = prepare_engine_config()
    # Reuse the test requirements
    cfg.requirements_file_path = os.path.join(RESOURCE_DIR, "test_requirements.xlsx")
    engine = Engine(cfg)
    chat = engine.get_chat()

    answer = chat.chat("What is the topic of the requirements")

    assert "ASW" in answer.answer
    assert 0 < len(answer.reference_names)
    assert 0 < len(answer.references)


def test_chat_knows_documents():
    check_ollama_and_skip()
    cfg = prepare_engine_config()
    # Reuse the test documents
    cfg.document_directories = [RESOURCE_DIR]
    engine = Engine(cfg)
    chat = engine.get_chat()

    answer = chat.chat("What is the full name of a weaponized potato")

    assert "Universal Army Potato" in answer.answer
    assert 0 < len(answer.reference_names)
    assert 0 < len(answer.references)
