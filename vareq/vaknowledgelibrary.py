from typing import List, Set, Dict
from enum import Enum
import logging
import os.path
import docx
import pathlib
import pdfplumber
import chromadb
import langchain_text_splitters
from .vallminterface import Llm
from .varequirementreader import Requirement, RequirementReader, Mappings


class ItemKind(Enum):
    DOCUMENT = 1
    REQUIREMENT = 2


class KnowledgeLibraryConfig:
    chunk_size: int
    chunk_overlap: int
    persistent_storage_path: str
    requirement_document_mappings : Mappings

    def __init__(self):
        self.chunk_size = 8000
        self.chunk_overlap = 2000
        self.persistent_storage_path = "knowledge_library.db"
        self.requirement_document_mappings = Mappings()


class KnowledgeLibrary:
    persistent_db: chromadb.ClientAPI
    documents: chromadb.Collection
    llm: Llm
    config: KnowledgeLibraryConfig

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
        with open(file_path, mode="rt", encoding="utf-8") as file:
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

    def register_document(self, name: str, path: str, timestamp: float, text: str):
        logging.info(
            f"Registering document \"{name}\" from path \"{path}\" of timestamp {timestamp}"
        )
        chunks = self.split_text(text)
        for index, chunk in enumerate(chunks):
            embedding = self.llm.embedding(chunk)
            self.documents.add(
                ids=[f"{path}:{index}"],
                metadatas=[
                    {
                        "path": path,
                        "name": name,
                        "index": index,
                        "timestamp": timestamp,
                        "type": ItemKind.DOCUMENT.value,
                    }
                ],
                documents=[f"### Document {name} part {index}\n" + chunk],
                embeddings=embedding,
            )

    def is_document_up_to_date(self, path: str) -> bool:
        registered_timestamp = self.get_document_timestamp(path)
        if registered_timestamp < 0:
            # Document is not registered, so not up to date
            return False
        actual_timestamp = os.path.getmtime(path)
        if actual_timestamp > registered_timestamp:
            logging.info(f"Document \"{path}\" timestamp changed from {registered_timestamp} to {actual_timestamp}")
            return False
        # Document is registered, and the timestamp is not in the past
        return True

    def add_document(self, path: str, override: bool = False) -> bool:
        if not override:
            if self.is_document_up_to_date(path):
                logging.info(f"Document {path} not added, as up-to-date")
                return False
        timestamp = os.path.getmtime(path)
        name = pathlib.Path(path).stem
        text = self.read_document(path)
        self.register_document(name, path, timestamp, text)
        return True
    
    def is_requirements_document_up_to_date(self, path : str) -> bool:
        registered_timestamp = self.get_requirements_timestamp()
        if registered_timestamp < 0:
            # Document is not registered, so not up to date
            return False
        actual_timestamp = os.path.getmtime(path)
        if actual_timestamp > registered_timestamp:
            return False
        # Document is registered, and the timestamp is not in the past
        return True
    
    def set_requirements_document(self, path : str, override: bool = False) -> bool:
        if not override:
            if self.is_requirements_document_up_to_date(path):
                logging.info(f"Requirements {path} not added, as up-to-date")
                return False
        self.delete_all_requirements()
        timestamp = os.path.getmtime(path)
        reader = RequirementReader(self.config.requirement_document_mappings)
        requirements = reader.read_requirements(path)
        self.add_requirements(requirements, timestamp)
        return True

    def add_directory(self, path: str, override: bool = False) -> int:
        root = pathlib.Path(path)
        extensions = [".txt", ".docx", ".pdf"]
        for file in root.rglob("*"):
            path = pathlib.Path(file)
            extension = path.suffix.lower()
            file_path = str(path)
            logging.debug(
                f"Adding directory \"{path}\": found file \"{file_path}\" with extension \"{extension}\""
            )
            if extension in extensions:
                logging.info(f"Adding file \"{file_path}\" from directory \"{path}\"")
                self.add_document(file_path, override)

    def delete_all_documents(self):
        logging.debug(f"Deleting all documents")
        self.documents.delete(where={"type": ItemKind.DOCUMENT.value})

    def delete_all_requirements(self):
        logging.debug(f"Deleting all requirements")
        self.documents.delete(where={"type": ItemKind.REQUIREMENT.value})

    def add_requirement(self, requirement: Requirement, timestamp : float = -1):
        logging.info(f"Adding requirement {requirement.id}: {requirement.description}")
        text = (
            f"### Requirement {requirement.id}\nDescription: {requirement.description}"
        )
        if requirement.note is not None and len(requirement.note) > 0:
            text = f"{text}\nNote: {requirement.note}\n"
        if requirement.justification is not None and len(requirement.justification) > 0:
            text = f"{text}\nJustification: {requirement.justification}\n"

        embedding = self.llm.embedding(text)
        self.documents.add(
            ids=[f"REQ:{requirement.id}"],
            metadatas=[
                {
                    "path": "",
                    "name": requirement.id,
                    "index": 0,
                    "timestamp": timestamp,
                    "type": ItemKind.REQUIREMENT.value,
                }
            ],
            documents=[text],
            embeddings=embedding,
        )

    def add_requirements(self, requirements: List[Requirement], timestamp : float = -1):
        for requirement in requirements:
            self.add_requirement(requirement, timestamp)

    def get_document_timestamp(self, path) -> float:
        results = self.documents.get(where={"path": path}, include=["metadatas"])
        metadatas = results["metadatas"]
        if len(metadatas) == 0:
            return -1
        timestamp = metadatas[0]["timestamp"]
        for meta in metadatas:
            timestamp = min(timestamp, meta["timestamp"])
        return timestamp

    def get_requirements_timestamp(self) -> float:
        results = self.documents.get(where={"type": ItemKind.REQUIREMENT.value}, include=["metadatas"])
        metadatas = results["metadatas"]
        if len(metadatas) == 0:
            return -1
        timestamp = metadatas[0]["timestamp"]
        for meta in metadatas:
            timestamp = min(timestamp, meta["timestamp"])
        return timestamp

    def get_relevant_documents(self, text: str, count: int) -> List[str]:
        embedding = self.llm.embedding(text)
        results = self.documents.query(query_embeddings=[embedding], n_results=count)
        docs = []
        for document in results["documents"][0]:
            docs.append(document)
        return docs

    def get_all_documents(self) -> List[str]:
        results = self.documents.get()
        docs = []
        for document in results["documents"]:
            docs.append(document)
        return docs
