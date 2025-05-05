import logging
import os.path
from typing import List
from .vallminterface import Llm, Chat, LlmConfig, ChatConfig
from .vaknowledgelibrary import KnowledgeLibrary, KnowledgeLibraryConfig


class AugmentedChatConfig:
    max_knowledge_size: int
    max_knowledge_items: int

    def __init__(self):
        self.max_knowledge_items = 64
        self.max_knowledge_size = 16384


class AugmentedChatReply:
    query: str
    answer: str
    references: List[str]
    reference_names: List[str]


class AugmentedChat:
    llm_chat: Chat
    lib: KnowledgeLibrary
    config: AugmentedChatConfig

    def __init__(self, chat: Chat, lib: KnowledgeLibrary, config: AugmentedChatConfig):
        self.config = config
        self.llm_chat = chat
        self.lib = lib

    def get_relevant_documents(self, query: str) -> List[str]:
        documents = self.lib.get_relevant_documents(
            query, self.config.max_knowledge_items
        )
        if len(documents) == 0:
            logging.debug(f"Found no relevant documents")
            return []
        logging.debug(f"Found {len(documents)} relevant documents")
        total_size = 0
        total_count = 0
        for document in documents:
            size = len(document)
            total_size = total_size + size
            total_count = total_count + 1
            if (
                total_size >= self.config.max_knowledge_size
                or total_count >= self.config.max_knowledge_items
            ):
                break
        count = max(total_count, 1)  # return at least one document
        return documents[0:count]

    def extract_reference_name(self, reference: str) -> str:
        if reference is None:
            return ""
        lines = reference.splitlines()
        if len(lines) == 0:
            return ""
        return lines[0].strip()

    def chat(self, query: str) -> AugmentedChatReply:
        reply = AugmentedChatReply()
        reply.query = query
        documents = self.get_relevant_documents(query)
        documents_count = len(documents)
        reply.references = documents
        reply.reference_names = [self.extract_reference_name(x) for x in documents]
        documents.reverse()  # The least relevant in the beggining (LLM may forget that)
        context = "\n".join(documents) if documents_count > 0 else ""
        answer = self.llm_chat.chat(context, query)
        reply.answer = answer
        return reply


class EngineConfig:
    llm_config: LlmConfig
    chat_config: ChatConfig
    lib_config: KnowledgeLibraryConfig
    requirements_file_path: str
    document_directories: List[str]

    def __init__(self):
        self.document_directories = []
        self.requirements_file_path = None
        self.lib_config = KnowledgeLibraryConfig()
        self.llm_config = LlmConfig()
        self.chat_config = ChatConfig()


class Engine:
    chat: Chat
    llm: Llm
    lib: KnowledgeLibrary
    config: EngineConfig

    def __init__(self, config: EngineConfig):
        self.config = config
        self.llm = Llm(config.llm_config)
        self.chat = Chat(self.llm, config.chat_config)
        self.lib = KnowledgeLibrary(self.llm, self.config.lib_config)
        for directory in self.config.document_directories:
            self.lib.add_directory(directory)
        if self.config.requirements_file_path is not None and os.path.exists(
            self.config.requirements_file_path
        ):
            self.lib.set_requirements_document(self.config.requirements_file_path)

    def get_chat(self) -> AugmentedChat:
        cfg = AugmentedChatConfig()
        chat = AugmentedChat(self.chat, self.lib, cfg)
        return chat
