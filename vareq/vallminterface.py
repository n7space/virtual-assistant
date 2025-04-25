from typing import List, Set, Dict
from langchain_ollama.llms import OllamaLLM
from langchain_ollama import OllamaEmbeddings

class Llm:
    chat_model_name : str
    embeddings_model_name : str
    chat_model : object
    embeddings_model : object
    ollama_url : str

    def __init__(self, chat_model_name : str = "qwen2.5:1.5b-instruct-q8_0", embeddings_model_name : str ="nomic-embed-text"):
        self.chat_model_name = chat_model_name
        self.embeddings_model_name = embeddings_model_name
        self.chat_model = OllamaLLM(model=self.chat_model_name)
        self.embeddings_model = OllamaEmbeddings(model=self.embeddings_model_name)

    def set_chat_model(self, name : str):
        self.chat_model_name = name
        self.chat_model = OllamaLLM(model=name)

    def set_embedding_model(self, name : str):
        self.embeddings_model_name = name
        self.embeddings_model = OllamaEmbeddings(model=name)

    def query(self, question : str) -> str:
        result = self.chat_model.invoke(question)
        return str(result)
    
    def embedding(self, text : str) -> List[float]:
        result = self.embeddings_model.embed_query(text)
        return result
    