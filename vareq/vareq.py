from typing import List, Set
import os.path
import logging
from .vallminterface import Chat
from .vallminterface import Llm
from .vaknowledgelibrary import KnowledgeLibrary
from .vaknowledgelibrary import KnowledgeLibraryConfig
from .vaengine import Engine, EngineConfig
from .varequirementreader import Mappings

def main():
    """
    The main entry point of Virtual Assistant.
    """
    logging.basicConfig(level=logging.DEBUG)
    # TODO - this is a temporary CLI, used only for testing
    cfg = EngineConfig()
    cfg.document_directories = ["./"]
    cfg.requirements_file_path = os.path.join("tests","unit","resources","test_requirements.xlsx")
    # Temporary, to make it compatible with the custom test sheet
    cfg.requirement_reader_mappings = Mappings().update_from_dict(
        {"worksheet_name": "reqs"}
    )

    engine = Engine(cfg)
    chat = engine.get_chat()
    print(f"----------------------------")
    print(f"System ready, please enter your query")
    while True:
        query = input()
        if len(query) == 0:
            print("System: Exiting...")
            return 0
        reply = chat.chat(query)
        print(f"----------------------------")
        for reference in reply.references:
            print(f"Reference:\n{reference}\n")
        print(f"User query: {reply.query}")
        print(f"System response: {reply.answer}")

if __name__ == "__main__":
    main()
