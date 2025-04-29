from typing import List, Set
import logging
from .vallminterface import Chat
from .vallminterface import Llm
from .vaknowledgelibrary import KnowledgeLibrary
from .vaknowledgelibrary import KnowledgeLibraryConfig


def main():
    """
    The main entry point of Virtual Assistant.
    """
    logging.basicConfig(level=logging.DEBUG)
    # TODO - this is a temporary CLI, used only for testing
    context = ""
    llm = Llm()
    chat = Chat(llm)
    lib_cfg = KnowledgeLibraryConfig()
    lib = KnowledgeLibrary(llm, lib_cfg)
    lib.add_directory("./")
    docs = lib.get_all_documents()
    for doc in docs:
        print("-----Document-----\n")
        print(doc)
        print("---End Document---\n")
    while True:
        query = input()
        if len(query) == 0:
            break
        context = lib.get_relevant_documents(query, 1)[0]
        answer = chat.chat(context, query)
        print(f"Retrieved context is\n---------------\n{context}\n---------------\n")
        print(f"Answer: {answer}\n")


if __name__ == "__main__":
    main()
