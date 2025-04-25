from vareq import vallminterface
import logging
import pytest
import os

logging.basicConfig(level=logging.DEBUG)


def test_chat_query():
    llm = vallminterface.Llm()
    if not llm.is_available():
        pytest.skip("Ollama not available")
    model_name = "qwen2.5:1.5b-instruct-q8_0"
    llm.set_chat_model(model_name)

    result = llm.query("What are you")

    # Result is in practice non-deterministic, so check the expected properties
    assert result is not None
    assert isinstance(result, str)
    assert 10 < len(result)


def test_embedding():
    llm = vallminterface.Llm()
    if not llm.is_available():
        pytest.skip("Ollama not available")
    model_name = "nomic-embed-text"
    llm.set_embedding_model(model_name)

    result = llm.embedding("This is some text")

    # Result is in practice non-deterministic, so check the expected properties
    assert result is not None
    assert 10 < len(result)
    assert isinstance(result[0], float)
