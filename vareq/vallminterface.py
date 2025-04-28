from typing import List, Set, Dict
import requests
import logging
from langchain_ollama.llms import OllamaLLM
from langchain_ollama import OllamaEmbeddings


class Llm:
    chat_model_name: str
    embeddings_model_name: str
    chat_model: object
    embeddings_model: object
    url: str
    temperature: float

    def __init__(
        self,
        chat_model_name: str = "qwen2.5:1.5b-instruct-q8_0",
        embeddings_model_name: str = "nomic-embed-text",
        url: str = "127.0.0.1:11434",
        temperature: float = 0.8,
    ):
        self.url = url
        self.temperature = temperature
        self.set_chat_model(chat_model_name)
        self.set_embedding_model(embeddings_model_name)

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


class Chat:
    llm: Llm
    history: str
    history_summarization_template: str

    def __init__(self, llm: Llm):
        self.llm = llm
        self.history = ""
        self.history_summarization_template = """### Previous history
{0}
### New user query
{1}
### New system reply
{2}
### Instruction
Summarize the conversation history to include both the previous history, and the new query and reply. Be as concise as possible, do not include any formatting directives."""

    def set_history_summarization_template(self, template: str):
        self.history_summarization_template = template

    def chat(self, template: str, context_data: str, question: str) -> str:
        query = template.format(self.history, context_data, question)
        logging.debug(f"Query:\n---\n{query}\n---")
        answer = self.llm.query(query)
        logging.debug(f"Asnwer:\n---\n{answer}\n---")
        history_query = self.history_summarization_template.format(
            self.history, question, answer
        )
        logging.debug(f"History query:\n---\n{history_query}\n---")
        new_history = self.llm.query(history_query)
        logging.debug(f"History:\n---\n{new_history}\n---")
        self.history = new_history
        return answer
