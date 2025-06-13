from typing import List
from flask import Flask, jsonify, views
import os
import logging
import warnings
import sys
from .vaengine import Engine, EngineConfig, AugmentedChat
from .varequirementreader import Requirement, RequirementReader


class Context:
    engine: Engine
    config: EngineConfig
    requirements: List[Requirement]
    chat: AugmentedChat

    def __init__(self, config: EngineConfig):
        self.config = config
        self.reinit()

    def reinit(self):
        self.engine = Engine(self.config)
        self.chat = self.engine.get_chat()
        self.requirements = []
        if self.config.requirements_file_path:
            mappings = self.config.lib_config.requirement_document_mappings
            reader = RequirementReader(mappings)
            self.requirements = reader.read_requirements(
                self.config.requirements_file_path
            )


class QueryView(views.View):
    context: Context

    def __init__(self, context: Context):
        self.context = context
        pass

    def handle_unary(self, query_id: str, requirement_id: str):
        requirement = next(
            r for r in self.context.requirements if r.id == requirement_id
        )
        reply = self.context.engine.process_query(query_id, requirement)
        result = {
            "query_id": query_id,
            "requirement_id": requirement_id,
            "status": "ok",
            "reply": reply,
        }
        return jsonify(result)

    def handle_nary(self, query_id):
        reply = self.context.engine.process_batch_query(
            query_id, self.context.requirements
        )
        result = {"query_id": query_id, "status": "ok", "reply": reply}
        return jsonify(result)

    def dispatch_request(self, query_id: str, requirement_id: str):
        logging.info(f"Query: query_id : {query_id}, requirement_id : {requirement_id}")
        try:
            if requirement_id:
                return self.handle_unary(query_id, requirement_id)
            else:
                return self.handle_nary(query_id)
        except Exception as e:
            result = {
                "query_id": query_id,
                "requirement_id": requirement_id,
                "status": "failed",
                "error": str(e),
            }
            return jsonify(result)


class ServerConfig:
    host: str
    port: int
    debug: bool

    def __init__(self, host: str = "127.0.0.1", port: int = 8080, debug: bool = False):
        self.debug = debug
        self.host = host
        self.port = port


class VaServer:
    app: Flask
    config: ServerConfig
    engine: Engine
    context: Context

    def __init__(self, server_config: ServerConfig, engine_config: EngineConfig):
        self.app = None
        self.config = server_config
        self.context = Context(engine_config)

    def run(self):
        if not self.config.debug:
            # Disable Flask warnings related to the development usage.
            # Flask insists on being wrapped by a WSGI server
            # for higher scalability and security.
            # However, there is no scalability, and the app is meant to
            # be used by a single user at a time.
            warnings.filterwarnings("ignore", category=UserWarning, module="werkzeug")
            logging.getLogger("werkzeug").setLevel(logging.ERROR)

        self.app = Flask(__name__)
        self.app.add_url_rule(
            "/query/<string:query_id>/",
            defaults={"requirement_id": None},
            view_func=QueryView.as_view("nary-query", self.context),
        )
        self.app.add_url_rule(
            "/query/<string:query_id>/<string:requirement_id>",
            view_func=QueryView.as_view("unary-query", self.context),
        )
        self.app.run(
            host=self.config.host,
            port=self.config.port,
            debug=self.config.debug,
            use_reloader=False,
        )
