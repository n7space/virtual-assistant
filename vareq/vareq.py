import logging
from .vallminterface import LlmConfig
from .vaengine import Engine, EngineConfig
from .varequirementreader import Mappings


def main():
    """
    The main entry point of Virtual Assistant.
    """
    logging.basicConfig(level=logging.DEBUG)
    # TODO - this is a temporary CLI, used only for testing
    llm_config = LlmConfig()
    llm_config.chat_model_name = "qwen2.5"
    llm_config.embeddings_model_name = "nomic-embed-text"
    # TODO - temporary setup, a more powerful LLM is executed on a remote computer
    llm_config.url = "192.168.1.110:11434"
    llm_config.temperature = 0.2

    cfg = EngineConfig()
    cfg.llm_config = llm_config
    cfg.document_directories = ["./"]
    cfg.requirements_file_path = "requirements.xlsx"
    # Temporary, to make it compatible with the custom test sheet
    cfg.lib_config.requirement_document_mappings = Mappings().update_from_dict(
        {
            "worksheet_name": "Requirements",
            "first_row_number": 2,
            "id": "D",
            "type": "",
            "validation_type": "I",
            "description": "E",
            "note": "F",
            "justification": "G",
            "traces": "H",
            "trace_separator": ",",
        }
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
        for index, reference in enumerate(reply.references):
            print(f"-- Reference {index}(length {len(reference)}):\n{reference}\n")
        print(f"-- Total references: {len(reply.references)}")
        print(f"-- Reference names: {','.join(reply.reference_names)}")
        print(f"-- User query: {reply.query}")
        print(f"-- System response: {reply.answer}")


if __name__ == "__main__":
    main()
