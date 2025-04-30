from vareq import vallminterface
import logging
import pytest
import os

logging.basicConfig(level=logging.DEBUG)

def test_chat_removes_thinking():
    # LLM is not used
    chat_config = vallminterface.ChatConfig()
    chat = vallminterface.Chat(None, chat_config)
    reply_in = "<think>If a > b, then c is red</think>Apples are green!"
    
    reply_out = chat.cleanup_reply(reply_in)

    assert "Apples are green!" == reply_out

def test_chat_thinking_removal_handles_newlines():
    # LLM is not used
    chat_config = vallminterface.ChatConfig()
    chat = vallminterface.Chat(None, chat_config)
    reply_in = """<think>
If a > b, then c is red
</think>
Apples are green!"""
    
    reply_out = chat.cleanup_reply(reply_in)

    assert "Apples are green!" == reply_out

def test_chat_does_not_alter_thoughtless_replies():
    # LLM is not used
    chat_config = vallminterface.ChatConfig()
    chat = vallminterface.Chat(None, chat_config)
    reply_in = "This (2+1!=x^2) is some serious math!"
    
    reply_out = chat.cleanup_reply(reply_in)

    assert "This (2+1!=x^2) is some serious math!" == reply_out

def test_chat_query():
    config = vallminterface.LlmConfig()
    llm = vallminterface.Llm(config)
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
    config = vallminterface.LlmConfig()
    llm = vallminterface.Llm(config)
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
    llm_config = vallminterface.LlmConfig()
    llm = vallminterface.Llm(llm_config)
    if not llm.is_available():
        pytest.skip("Ollama not available")
    llm.set_temperature(0.0)  # Be as deterministic as possible
    context = ""
    chat_config = vallminterface.ChatConfig()
    chat = vallminterface.Chat(llm, chat_config)

    chat.chat(context, "The topic of the discussion is Medieval Trains")
    answer = chat.chat(context, "What is the topic of the discussion?")

    assert answer is not None
    assert 10 < len(answer)
    assert "medieval trains" in answer.lower()


def test_chat_understands_context():
    llm_config = vallminterface.LlmConfig()
    llm = vallminterface.Llm(llm_config)
    if not llm.is_available():
        pytest.skip("Ollama not available")
    llm.set_temperature(0.0)  # Be as deterministic as possible
    context = "The system has OBC with CPU, Mass Memory with 128 GB of flash and Power Supply providing 12V"
    chat_config = vallminterface.ChatConfig()
    chat = vallminterface.Chat(llm, chat_config)

    answer = chat.chat(context, "What are the elements of the system?")

    assert answer is not None
    assert 10 < len(answer)
    assert "obc" in answer.lower()
    assert "mass memory" in answer.lower()
    assert "power supply" in answer.lower()
