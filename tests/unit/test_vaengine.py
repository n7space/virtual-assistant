from vareq.vallminterface import LlmConfig, Llm
from vareq.varequirementreader import Mappings, Requirement
from vareq.vaengine import Engine, EngineConfig, PredefinedQuery
from vareq.vaqueries import QueryArity, QueryKind
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


def test_engine_can_process_query():
    check_ollama_and_skip()
    cfg = EngineConfig()
    query = PredefinedQuery(
        QueryKind.FREETEXT,
        QueryArity.UNARY,
        "extract",
        "Extract the main subject of the requirement. Do not include the full sentence or any extre explanation, just return the subject. Requirement {0}: {1}\n",
    )
    cfg.predefined_queries.append(query)
    engine = Engine(cfg)

    requirement = Requirement("REQ-10", "The DPU shall be powerful")
    reply = engine.process_query("extract", requirement)

    assert "dpu" in reply.lower()


def test_engine_cannot_process_non_existing_query():
    cfg = EngineConfig()
    query = PredefinedQuery(
        QueryKind.FREETEXT,
        QueryArity.UNARY,
        "extract-id",
        "Extract the main subject of the requirement. Do not include the full sentence or any extre explanation, just return the subject. Requirement {0}: {1}\n",
    )
    cfg.predefined_queries.append(query)
    engine = Engine(cfg)

    requirement = Requirement("REQ-10", "The DPU shall be powerful")
    reply = engine.process_query("summarize", requirement)

    assert reply is None


def test_query_can_access_all_requirement_data():
    check_ollama_and_skip()
    cfg = EngineConfig()
    template = """
Return the requirement content without any alterations:
### REQUIREMENT
ID: {0}
Description: {1}
Note: {2}
Justification: {3}
Type: {4}
Validation: {5}
Traces: {6}
"""
    query = PredefinedQuery(QueryKind.FREETEXT, QueryArity.UNARY, "echo", template)
    cfg.predefined_queries.append(query)
    engine = Engine(cfg)

    requirement = Requirement("REQ-10", "CPU is fast")
    requirement.note = "Fast is at least 100 GHz"
    requirement.justification = "Lots of data to process"
    requirement.validation_type = "Test"
    requirement.type = "performance"
    requirement.traces = ["BR-10", "BR-20"]
    reply = engine.process_query("echo", requirement).lower()

    assert "cpu is fast" in reply
    assert "lots of data to process" in reply
    assert "performance" in reply
    assert "test" in reply
    assert "br-10" in reply
    assert "br-20" in reply
    assert "at least 100 ghz" in reply
