from typing import List, Set, Dict
import logging
import os.path
import docx
import pathlib
import pdfplumber
import chromadb
import langchain_text_splitters
from .vallminterface import Llm


class KnowledgeLibraryConfig:
    chunk_size: int
    chunk_overlap: int
    persistent_storage_path: str

    def __init__(self):
        self.chunk_size = 8000
        self.chunk_overlap = 2000
        self.persistent_storage_path = "knowledge_library.db"


class KnowledgeLibrary:
    persistent_db: chromadb.ClientAPI
    documents: chromadb.Collection
    llm: Llm
    config : KnowledgeLibraryConfig

    def __init__(self, llm: Llm, config: KnowledgeLibraryConfig):
        self.llm = llm
        self.config = config
        self.persistent_db = chromadb.PersistentClient(
            path=config.persistent_storage_path
        )
        self.documents = self.persistent_db.get_or_create_collection(name="documents")

    def read_docx(self, file_path: str) -> str:
        lines = []
        document = docx.Document(file_path)
        for paragraph in document.paragraphs:
            paragrapth_text = paragraph.text
            lines.append(paragrapth_text)
            logging.debug(f"Retrieved paragraph: {paragrapth_text}")
        return "\n".join(lines)

    def read_txt(self, file_path: str) -> str:
        with open(file_path) as file:
            content = file.read()
            logging.debug(f"Retrieved content: {content}")
            return content

    def read_pdf(self, file_path: str) -> str:
        lines = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text_simple()
                lines.append(page_text)
                logging.debug(f"Retrieved page: {page_text}")
        return "\n".join(lines)

    def read_document(self, file_path: str) -> str:
        extension = pathlib.Path(file_path).suffix.lower()
        if extension == ".docx":
            return self.read_docx(file_path)
        elif extension == ".pdf":
            return self.read_pdf(file_path)
        else:
            return self.read_txt(file_path)

    def split_text(self, text: str) -> List[str]:
        splitter = langchain_text_splitters.RecursiveCharacterTextSplitter(
            chunk_size=self.config.chunk_size, chunk_overlap=self.config.chunk_overlap
        )
        chunks = splitter.split_text(text)
        logging.debug(f"Text split into {len(chunks)} chunks")
        for chunk in chunks:
            logging.debug(f"Chunk: {chunk}")
        return chunks
    
    def register_document(self, name : str, path : str, timestamp : float, text : str):
        chunks = self.split_text(text)
        for index, chunk in enumerate(chunks):
            embedding = self.llm.embedding(chunk)
            self.documents.add(
                ids = [f"{path}:{index}"],
                metadatas=[{
                    "path" : path,
                    "name" : name,
                    "index" : index,
                    "timestamp" : timestamp,
                }],
                documents=[f"### Document {name} part {index}\n" + chunk],
                embeddings = embedding
            )

    def is_document_up_to_date(self, path : str) -> bool:
        registered_timestamp = self.get_document_timestamp(path)
        if registered_timestamp < 0:
            # Document is not registered, so not up to date
            return False
        actual_timestamp = os.path.getmtime(path)
        if actual_timestamp > registered_timestamp:
            return False
        # Document is registered, and the timestamp is not in the past
        return True

    def add_document(self, path : str, override : bool = False) -> bool:
        if not override:
            if self.is_document_up_to_date(path):
                return False
        timestamp = os.path.getmtime(path)
        name = pathlib.Path(path).stem
        text = self.read_document(path)
        self.register_document(name, path, timestamp, text)
        return True

    def get_document_timestamp(self, path) -> float:
        results = self.documents.get(where={"path" : path}, include=["metadatas"])
        metadatas = results["metadatas"]
        if len(metadatas) == 0:
            return -1
        timestamp = metadatas[0]["timestamp"]
        for meta in metadatas:
            timestamp = min(timestamp, meta["timestamp"])
        return timestamp
    
    def get_relevant_documents(self, text : str, count : int) -> List[str]:
        embedding = self.llm.embedding(text)
        results = self.documents.query(query_embeddings=[embedding], n_results=count)
        docs = []
        for document in results["documents"][0]:
            docs.append(document)
        return docs
