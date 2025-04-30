from typing import List, Set, Dict
import requests
import logging
import re
from langchain_ollama.llms import OllamaLLM
from langchain_ollama import OllamaEmbeddings

class LlmConfig:
    chat_model_name: str
    embeddings_model_name: str
    chat_model: object
    embeddings_model: object
    url: str
    temperature: float

    def __init__(self):
        self.chat_model_name = "qwen2.5:1.5b-instruct-q8_0"
        self.embeddings_model_name = "nomic-embed-text"
        self.url = "127.0.0.1:11434"
        self.temperature = 0.8

class Llm:
    chat_model_name: str
    embeddings_model_name: str
    chat_model: object
    embeddings_model: object
    url: str
    temperature: float

    def __init__(
        self,
        config : LlmConfig
    ):
        self.url = config.url
        self.temperature = config.temperature
        self.set_chat_model(config.chat_model_name)
        self.set_embedding_model(config.embeddings_model_name)

    def set_url(self, url: str):
        self.url = url
        self.set_chat_model(self.chat_model_name)
        self.set_embedding_model(self.embeddings_model_name)

    def set_temperature(self, temperature: float):
        self.temperature = temperature
        # Temperature is relevant only to a chat
        self.set_chat_model(self.chat_model_name)

    def set_chat_model(self, name: str):
        self.chat_model_name = name
        self.chat_model = OllamaLLM(
            model=name, base_url=self.url, temperature=self.temperature
        )

    def set_embedding_model(self, name: str):
        self.embeddings_model_name = name
        self.embeddings_model = OllamaEmbeddings(model=name, base_url=self.url)

    def query(self, question: str) -> str:
        result = self.chat_model.invoke(question)
        return str(result)

    def embedding(self, text: str) -> List[float]:
        result = self.embeddings_model.embed_query(text)
        return result

    def is_available(self) -> bool:
        try:
            response = requests.get(f"http://{self.url}/api/tags")
            return response.status_code == 200
        except:
            return False


class ChatConfig:
    query_template: str
    history_summarization_template: str
    remove_thinking : bool

    def __init__(self):
        self.query_template = """### History
{0}
### Context information
You are an expert requirements engineer, working in the space industry. You have access to the following:
{1}
### Instruction
{2}"""
        self.remove_thinking = True
        self.history_summarization_template = """### Previous history
{0}
### New user query
{1}
### New system reply
{2}
### Instruction
Summarize the conversation history to include both the previous history, and the new query and reply. Be as concise as possible, do not include any formatting directives."""

class Chat:
    llm: Llm
    history: str
    config : ChatConfig

    def __init__(self, llm: Llm, config : ChatConfig):
        self.llm = llm
        self.config = config
        self.history = ""


    def set_history_summarization_template(self, template: str):
        self.config.history_summarization_template = template

    def set_query_template(self, template: str):
        self.config.query_template = str

    def cleanup_reply(self, reply : str) -> str:
        if self.config.remove_thinking and "<think>" in reply and "</think>" in reply:
            pattern = "<think>.*?</think>"
            return re.sub(pattern,"", reply, flags=re.DOTALL).strip()
        return reply

    def chat(self, context_data: str, question: str) -> str:
        query = self.config.query_template.format(self.history, context_data, question)
        logging.debug(f"Query:\n---\n{query}\n---")
        answer = self.llm.query(query)
        logging.debug(f"Asnwer:\n---\n{answer}\n---")
        clean_answer = self.cleanup_reply(answer)
        # thinking does not need to clutter the memory
        history_query = self.config.history_summarization_template.format(
            self.history, question, clean_answer
        )
        logging.debug(f"History query:\n---\n{history_query}\n---")
        new_history = self.llm.query(history_query)
        logging.debug(f"History:\n---\n{new_history}\n---")
        self.history = new_history
        return clean_answer
