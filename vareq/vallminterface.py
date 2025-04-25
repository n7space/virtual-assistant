from typing import List, Set, Dict
import requests
from langchain_ollama.llms import OllamaLLM
from langchain_ollama import OllamaEmbeddings


class Llm:
    chat_model_name: str
    embeddings_model_name: str
    chat_model: object
    embeddings_model: object
    url: str

    def __init__(
        self,
        chat_model_name: str = "qwen2.5:1.5b-instruct-q8_0",
        embeddings_model_name: str = "nomic-embed-text",
        url : str = "127.0.0.1:11434"
    ):
        self.url = url
        self.set_chat_model(chat_model_name)
        self.set_chat_model(embeddings_model_name)

    def set_url(self, url : str):
        self.url = url
        self.set_chat_model(self.chat_model_name)
        self.set_chat_model(self.embeddings_model_name)

    def set_chat_model(self, name: str):
        self.chat_model_name = name
        self.chat_model = OllamaLLM(model=name, base_url=self.url)

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