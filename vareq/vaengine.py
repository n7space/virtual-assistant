import logging
import os.path
from typing import List, Dict, Tuple
from .varequirementreader import Requirement
from .vallminterface import Llm, Chat, LlmConfig, ChatConfig
from .vaknowledgelibrary import KnowledgeLibrary, KnowledgeLibraryConfig, ItemKind
from .vaqueries import (
    PredefinedQueries,
    PredefinedQuery,
    BatchResponseElement,
    QueryArity,
)


class AugmentedChatConfig:
    max_knowledge_size: int
    max_knowledge_items: int
    use_requirements: bool
    use_documents: bool

    def __init__(self):
        self.max_knowledge_items = 64
        self.max_knowledge_size = 16384
        self.use_requirements = True
        self.use_documents = True


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

    def get_relevant_documents(self, query: str) -> List[Tuple[str, ItemKind, str]]:
        documents = self.lib.get_relevant_documents(
            query, self.config.max_knowledge_items
        )
        if len(documents) == 0:
            logging.debug(f"Found no relevant documents")
            return []
        logging.debug(f"Found {len(documents)} relevant documents")
        total_size = 0
        total_count = 0
        for (_, item_kind, document) in documents:
            if item_kind == ItemKind.DOCUMENT and not self.config.use_documents:
                continue
            if item_kind == ItemKind.REQUIREMENT and not self.config.use_requirements:
                continue
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
        reply.references = [document for (_, _, document) in documents]
        reply.reference_names = [name for (name, _, _) in documents]
        documents.reverse()  # The least relevant in the beggining (LLM may forget that)
        context = (
            "\n".join([document for (_, _, document) in documents])
            if documents_count > 0
            else ""
        )
        answer = self.llm_chat.chat(context, query)
        reply.answer = answer
        return reply


class EngineConfig:
    llm_config: LlmConfig
    chat_config: ChatConfig
    augmented_chat_config: AugmentedChatConfig
    lib_config: KnowledgeLibraryConfig
    batch_query_context_size: int
    requirements_file_path: str
    document_directories: List[str]
    predefined_queries: List[PredefinedQuery]

    def __init__(self):
        self.predefined_queries = []
        self.document_directories = []
        self.requirements_file_path = None
        self.lib_config = KnowledgeLibraryConfig()
        self.llm_config = LlmConfig()
        self.chat_config = ChatConfig()
        self.augmented_chat_config = AugmentedChatConfig()
        self.batch_query_context_size = 3


class Engine:
    chat: Chat
    llm: Llm
    lib: KnowledgeLibrary
    config: EngineConfig
    queries: PredefinedQueries

    def __init__(self, config: EngineConfig):
        self.config = config
        self.llm = Llm(config.llm_config)
        self.chat = Chat(self.llm, config.chat_config)
        self.lib = KnowledgeLibrary(self.llm, self.config.lib_config)
        self.queries = PredefinedQueries(self.llm)
        self.queries.batch_query_context_size = config.batch_query_context_size
        for query in self.config.predefined_queries:
            self.queries.register(query)
        for directory in self.config.document_directories:
            self.lib.add_directory(directory)
        if self.config.requirements_file_path is not None and os.path.exists(
            self.config.requirements_file_path
        ):
            self.lib.set_requirements_document(self.config.requirements_file_path)

    def get_chat(self) -> AugmentedChat:
        chat = AugmentedChat(self.chat, self.lib, self.config.augmented_chat_config)
        return chat

    def process_query(self, id: str, requirement: Requirement) -> str:
        return self.queries.process(id, requirement)

    def process_batch_query(
        self, id: str, requirements: List[Requirement]
    ) -> List[BatchResponseElement]:
        return self.queries.process_batch(id, requirements)

    def get_query_arity(self, id: str) -> QueryArity:
        return self.queries.arity(id)

    def get_config(self) -> EngineConfig:
        return self.config
