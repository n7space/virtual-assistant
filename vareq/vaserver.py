from typing import List
from flask import Flask, jsonify, views
import logging
import warnings
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


class AreYouAliveView(views.View):
    context: Context

    def __init__(self, context: Context):
        self.context = context

    def dispatch_request(self):
        logging.info(f"Server are you alive")
        result = {
            "status": "ok",
        }
        return jsonify(result)


class ReloadView(views.View):
    context: Context

    def __init__(self, context: Context):
        self.context = context

    def dispatch_request(self):
        logging.info(f"Server reload")
        try:
            self.context.reinit()
            logging.info(f"Server reload done")
            result = {"status": "ok"}
            return jsonify(result)
        except Exception as e:
            logging.error(f"Exception when handling server reload: {str(e)}")
            result = {
                "status": "failed",
                "error": str(e),
            }
            return jsonify(result)


class ChatView(views.View):
    context: Context

    def __init__(self, context: Context):
        self.context = context

    def dispatch_request(self, query: str):
        logging.info(f"Server chat: {query}")
        try:
            reply = self.context.chat.chat(query)
            logging.info(f"Server chat reply: {reply}")
            result = {
                "query": query,
                "reply": reply.answer,
                "references": reply.references,
                "reference_names": reply.reference_names,
                "status": "ok",
            }
            return jsonify(result)
        except Exception as e:
            logging.error(f"Exception when handling server chat: {str(e)}")
            result = {
                "query": query,
                "status": "failed",
                "error": str(e),
            }
            return jsonify(result)


class QueryView(views.View):
    context: Context

    def __init__(self, context: Context):
        self.context = context

    def handle_unary(self, query_id: str, requirement_id: str):
        requirement = None
        try:
            requirement = next(
                r for r in self.context.requirements if r.id == requirement_id
            )
        except StopIteration:
            pass
        if requirement is None:
            result = {
                "query_id": query_id,
                "requirement_id": requirement_id,
                "status": "failed",
                "reply": None,
                "error": "Requirement not found",
            }
            return jsonify(result)
        if not self.context.engine.query_exists(query_id):
            result = {
                "query_id": query_id,
                "requirement_id": requirement_id,
                "status": "failed",
                "reply": None,
                "error": "Query not found",
            }
            return jsonify(result)
        reply = self.context.engine.process_query(query_id, requirement)
        logging.info(f"Server query reply {reply}")
        status = "failed" if reply is None else "ok"
        error = "Processing failed" if reply is None else None
        result = {
            "query_id": query_id,
            "requirement_id": requirement_id,
            "status": status,
            "reply": reply,
            "error": error,
        }
        return jsonify(result)

    def handle_nary(self, query_id):
        if not self.context.engine.query_exists(query_id):
            result = {
                "query_id": query_id,
                "status": "failed",
                "reply": None,
                "error": "Query not found",
            }
            return jsonify(result)
        reply = self.context.engine.process_batch_query(
            query_id, self.context.requirements
        )
        logging.info(f"Server query reply {reply}")
        status = "failed" if reply is None else "ok"
        error = "Processing failed" if reply is None else None
        batch_data = [element.to_dict() for element in reply]
        result = {
            "query_id": query_id,
            "status": status,
            "reply": batch_data,
            "error": error,
        }
        return jsonify(result)

    def dispatch_request(self, query_id: str, requirement_id: str):
        logging.info(
            f"Server query: query_id : {query_id}, requirement_id : {requirement_id}"
        )
        try:
            if requirement_id:
                return self.handle_unary(query_id, requirement_id)
            else:
                return self.handle_nary(query_id)
        except Exception as e:
            logging.error(f"Exception when handling server query: {str(e)}")
            result = {
                "query_id": query_id,
                "reply": None,
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

    def prepare(self):
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
        self.app.add_url_rule(
            "/reload/",
            view_func=ReloadView.as_view("reload", self.context),
        )
        self.app.add_url_rule(
            "/chat/<string:query>/",
            view_func=ChatView.as_view("chat", self.context),
        )
        self.app.add_url_rule(
            "/areyoualive/",
            view_func=AreYouAliveView.as_view("areyoualive", self.context),
        )

    def run(self):
        self.prepare()
        self.app.run(
            host=self.config.host,
            port=self.config.port,
            debug=self.config.debug,
            use_reloader=False,
        )
