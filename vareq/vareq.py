import logging

from .vallminterface import LlmConfig
from .vaengine import Engine, EngineConfig
from .varequirementreader import Mappings, RequirementReader
from .vaqueries import PredefinedQueryReader
import sys


def main():
    """
    The main entry point of Virtual Assistant.
    """
    logging.basicConfig(level=logging.DEBUG)
    # TODO - this is a temporary CLI, used only for testing
    cfg = EngineConfig()
    cfg.llm_config.chat_model_name = "qwen3:4b"
    # cfg.llm_config.chat_model_name = "qwen2.5:0.5b"
    # cfg.llm_config.chat_model_name = "qwen2.5:1.5b-instruct-q8_0"
    cfg.llm_config.embeddings_model_name = "nomic-embed-text"
    # TODO - temporary setup, a more powerful LLM is executed on a remote computer
    # cfg.llm_config.url = "192.168.1.110:11434"
    cfg.llm_config.url = None
    cfg.llm_config.temperature = 0.2
    cfg.document_directories = ["./"]
    cfg.predefined_queries = PredefinedQueryReader("./").load_from_file(
        "predefined_queries.json"
    )
    # Temporary, to make it compatible with the custom test sheet
    cfg.requirements_file_path = "requirements.xlsx"
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
    # TODO - will be replaced later with a proper CLI
    if len(sys.argv) == 1:  # Chat mode
        print("Chat mode")
        chat = engine.get_chat()
        while True:
            print(f"----------------------------")
            print(f"System ready, please enter your query")
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
    elif len(sys.argv) == 2:  # Predefined batch query
        print("Query mode - batch")
        mappings = Mappings().update_from_dict({"worksheet_name": "reqs"})
        requirements = RequirementReader(mappings).read_requirements(
            "test_requirements.xlsx"
        )
        query_id = sys.argv[1]
        reply = engine.process_batch_query(query_id, requirements)
        print(f"Query result:")
        for element in reply:
            if (
                len(element.applied_requirements) > 0
                and element.message is not None
                and len(element.message) > 0
            ):
                requirement = element.requirement
                other = element.applied_requirements[0]
                print(
                    f"Detection: [{requirement.id}:{requirement.description}] and [{other.id}: {other.description}] - {element.message}"
                )

    elif len(sys.argv) == 3:  # Predefined queries
        print("Query mode - single requirement")
        mappings = Mappings().update_from_dict({"worksheet_name": "reqs"})
        requirements = RequirementReader(mappings).read_requirements(
            "test_requirements.xlsx"
        )
        query_id = sys.argv[1]
        requirement_id = sys.argv[2]
        requirement = next(r for r in requirements if r.id == requirement_id)
        reply = engine.process_query(query_id, requirement)
        print(f"Query result: {reply}")
    else:
        print(f"Wrong number of requirements, unknown mode")


if __name__ == "__main__":
    main()
