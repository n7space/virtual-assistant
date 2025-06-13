import logging

from vareq import helpers
from vareq import vaconfig

from .vaqueries import QueryArity
from .vallminterface import LlmConfig
from .vaengine import Engine, EngineConfig
from .varequirementreader import Mappings, RequirementReader
from .vaqueries import PredefinedQueryReader
from .vaserver import VaServer, ServerConfig
import sys
import json
import argparse


def parse_arguments() -> object:
    parser = argparse.ArgumentParser(
        description='Virtual Assistant\n Created as a part of "Model-Based Execution Platform for Space Applications" project (contract 4000146882/24/NL/KK) financed by the European Space Agency'
    )
    parser.add_argument(
        "--mode",
        choices=["chat", "query", "serve", "reset-db", "dump-config"],
        default="chat",
        help="Operating mode",
    )
    parser.add_argument(
        "--requirements", help="Path to the requirements file (overrides config)"
    )
    parser.add_argument(
        "--document-directories",
        help="Comma separated list of directories (overrides config)",
    )
    parser.add_argument("--model", help="LLM model name to use (overrides config)")
    parser.add_argument(
        "--query-definitions-base-directory",
        help="Base directory to resolve references within query definitions",
        default="./",
    )
    parser.add_argument("--query-definitions-path", help="Path to query definitions")
    parser.add_argument("--config-path", help="Path to config file")
    parser.add_argument("--config-json", help="Config JSON string")
    parser.add_argument("--server-config-json", help="Server config JSON string")
    parser.add_argument("--query-id", help="Query ID for query mode")
    parser.add_argument("--requirement-id", help="Requirement ID for query mode")
    parser.add_argument(
        "--setup-instructions",
        help="Print installation instructions",
        action="store_true",
    )
    parser.add_argument(
        "--verbosity",
        choices=["info", "debug", "warning", "error"],
        default="warning",
        help="Logging verbosity",
    )

    return parser.parse_args()


def get_log_level(level_str: str) -> int:
    log_levels = {
        "info": logging.INFO,
        "debug": logging.DEBUG,
        "warning": logging.WARNING,
        "error": logging.ERROR,
    }

    return log_levels.get(level_str.lower(), logging.WARNING)


def handle_setup_instructions() -> int:
    print(
        """ ---Setup instructions---
This software requires an Ollama installation to run properly.
For instructions on installing Ollama, refer to:
https://ollama.com/
Once Ollama is installed, please download the models intended for use.
Before downloading a model, please check:
- model licensing
- model disk space and memory requirements
In order to achieve the best reasoning performance, please make sure that
the context window size is increased to match the size supported by both
the model and the available memory.
Models can be downloaded by invoking in the command line:
        ollama pull MODEL_NAME
where MODEL_NAME should be replaced with the name of the model to be used,
such as:
- tinyllama:latest
- qwen3:1.7b
- qwen3:0.6b
- mistral:7b
- nomic-embed-text:latest
Please make sure that both generative and embeddings models are available.
Generative model availability can be checked by running in the command line:
        ollama run MODEL_NAME
In order to use a remote Ollama server, Ollama should be installed and
OLLAMA_HOST environment variable shall be set on both machines:
        OLLAMA_HOST=0.0.0.0:PORT_NUMBER on the remote machine
        OLLAMA_HOST=REMOTE_IP:PORT_NUMBER on the local machine

 ---Note---
Please be aware that LLMs are inherently untrustworhy and thus
should not be fully relied on. Human review should be always applied.
"""
    )
    return 0


def handle_chat(engine: Engine) -> int:
    chat = engine.get_chat()
    logging.info(f"System ready, please enter your query")
    while True:
        query = input()
        if len(query) == 0:
            logging.info("System: Exiting...")
            return 0
        reply = chat.chat(query)
        for index, reference in enumerate(reply.references):
            logging.info(
                f"-- Reference {index}(length {len(reference)}):\n{reference}\n"
            )
        logging.info(f"-- Total references: {len(reply.references)}")
        logging.info(f"-- Reference names: {','.join(reply.reference_names)}")
        logging.debug(f"-- User query: {reply.query}")
        logging.info(f"-- System response:")
        print(reply.answer)


def handle_reset_db(engine: Engine) -> int:
    logging.info(f"Deleting all documents")
    engine.lib.delete_all_documents()
    logging.info(f"Deleting all requirements")
    engine.lib.delete_all_requirements()
    logging.info(f"Deletion done")
    return 0


def handle_unary_query(engine: Engine, args: object) -> int:
    logging.info("Query mode - single requirement")
    config = engine.config
    if not config.requirements_file_path:
        print(f"Requirements path not provided")
        return -1
    mappings = config.lib_config.requirement_document_mappings
    requirements = RequirementReader(mappings).read_requirements(
        config.requirements_file_path
    )
    query_id = args.query_id
    requirement_id = args.requirement_id
    if not requirement_id:
        print(f"Requirement ID was not provided")
        return -1
    requirement = next(r for r in requirements if r.id == requirement_id)
    if not requirement:
        print(f"Requirement {requirement_id} was not found")
        return -1
    reply = engine.process_query(query_id, requirement)
    logging.info("Query result:")
    print(reply)
    return 0


def handle_nary_query(engine: Engine, args: object) -> int:
    logging.info("Query mode - batch")
    config = engine.config
    if not config.requirements_file_path:
        print(f"Requirements path not provided")
        return -1
    mappings = config.lib_config.requirement_document_mappings
    requirements = RequirementReader(mappings).read_requirements(
        config.requirements_file_path
    )
    query_id = args.query_id
    reply = engine.process_batch_query(query_id, requirements)
    clean_reply = helpers.extract_unique_detections(reply)
    logging.info(f"Query result:")
    for element in clean_reply:
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
    return 0


def handle_query(engine: Engine, args: object) -> int:
    id = args.query_id
    arity = engine.get_query_arity(id)
    if not arity:
        print(f"Query {id} not found")
        return -1
    if arity == QueryArity.NARY:
        return handle_nary_query(engine, args)
    elif arity == QueryArity.UNARY:
        return handle_unary_query(engine, args)
    else:
        logging.error("Unsupported query arity")
        return -1


def handle_serve(engine: Engine, config : ServerConfig) -> int:
    logging.info("Serve mode")
    logging.info(f"Using server configuration: {object_to_json_string(config)}")
    server = VaServer(config)
    server.run()
    return 0


def object_to_json_string(obj: object) -> str:
    # JSONization needs the object provided as lists or dictionaries
    # So, for each element, either use:
    # the built-in __dict__ dictionary
    # object converted to list, if it is iterable,
    #   but not a dictionary itself (previous case)
    #   or a string (conversion not needed)

    obj_json = json.dumps(
        obj,
        default=lambda o: o.__dict__
        if hasattr(o, "__dict__")
        else (
            list(o) if hasattr(o, "__iter__") and not isinstance(o, (str, dict)) else o
        ),
        sort_keys=True,
        indent=4,
    )
    return obj_json


def handle_dump_config(config: EngineConfig) -> int:
    config_json = object_to_json_string(config)
    print(config_json)


def main():
    args = parse_arguments()
    logging_level = get_log_level(args.verbosity)
    logging.basicConfig(level=logging_level)
    cfg = EngineConfig()
    server_config = ServerConfig()
    # Handle configuration overrides from the command line arguments
    if args.requirements:
        logging.info(f"Setting requirements path to {args.requirements}")
        cfg.requirements_file_path = args.requirements
    if args.document_directories:
        logging.info(f"Setting document directories to {args.document_directories}")
        cfg.document_directories = args.document_directories.split(",")
    if args.model:
        logging.info(f"Setting model to {args.model}")
        cfg.llm_config.model_name = args.model
    if args.query_definitions_path:
        logging.info(
            f"Reading predefined queries from {args.query_definitions_path}, with base path {args.query_definitions_path}"
        )
        cfg.predefined_queries = PredefinedQueryReader(
            args.query_definitions_path
        ).load_from_file(args.query_definitions_path)
    if args.config_path:
        logging.info(f"Reading config from {args.config_path}")
        with open(args.config_path, "r") as f:
            config_json = json.load(f)
            cfg = vaconfig.update_engine_configuration_from_json(cfg, config_json)
    # Config JSON is after path to enable config overwrite from command line
    if args.config_json:
        logging.info(f"Reading config from JSON {args.config_json}")
        config_json = json.loads(args.config_json)
        cfg = vaconfig.update_engine_configuration_from_json(cfg, config_json)
    if args.server_config_json:
        logging.info(f"Reading server config from JSON {args.server_config_json}")
        server_config_json = json.loads(args.server_config_json)
        server_config = vaconfig.update_server_configuration_from_json(server_config, server_config_json)

    logging.info(f"Using configuration: {object_to_json_string(cfg)}")
    engine = Engine(cfg)

    # Handle different modes
    if args.setup_instructions:
        logging.info("Printing setup instructions")
        return handle_setup_instructions()
    if args.mode == "chat":
        logging.info("Starting chat mode")
        return handle_chat(engine)
    elif args.mode == "query":
        logging.info("Executing query")
        return handle_query(engine, args)
    elif args.mode == "serve":
        logging.info("Starting serve mode")
        return handle_serve(engine, server_config)
    elif args.mode == "reset-db":
        logging.info("Resetting database")
        return handle_reset_db(engine)
    elif args.mode == "dump-config":
        logging.info("Dumping configuration")
        return handle_dump_config(cfg)
    else:
        print(f"Unknown mode")
        return -1


if __name__ == "__main__":
    main()
