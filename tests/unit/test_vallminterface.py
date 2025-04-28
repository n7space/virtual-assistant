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


def test_chat_has_memory():
    llm = vallminterface.Llm()
    if not llm.is_available():
        pytest.skip("Ollama not available")
    template = "### History\n{0}### Context information\n{1}\n### Instruction\n{2}"
    context = ""
    chat = vallminterface.Chat(llm)

    chat.chat(template, context, "The topic of the discussion is Medieval Trains")
    answer = chat.chat(template, context, "What is the topic of the discussion?")

    assert answer is not None
    assert 10 < len(answer)
    assert "medieval trains" in answer.lower()


def test_chat_understands_context():
    llm = vallminterface.Llm()
    if not llm.is_available():
        pytest.skip("Ollama not available")
    template = "### History\n{0}### Context information\n{1}\n### Instruction\n{2}"
    context = "The system has OBC with CPU, Mass Memory with 128 GB of flash and Power Supply providing 12V"
    chat = vallminterface.Chat(llm)

    answer = chat.chat(template, context, "What are the elements of the system?")

    assert answer is not None
    assert 10 < len(answer)
    assert "cpu" in answer.lower()
    assert "mass memory" in answer.lower()
    assert "power supply" in answer.lower()
