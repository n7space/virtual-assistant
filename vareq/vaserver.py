from flask import Flask, jsonify, views
import os
import logging
import warnings
import sys

class QueryView(views.View):
    def __init__(self):
        pass

    def dispatch_request(self, query_id : str, requirement_id : str):
        result = {"query_id": query_id, "requirement_id" : requirement_id}
            
        return jsonify(result)
    
class ServerConfig:
    host : str
    port : int
    debug : bool

    def __init__(self, host : str = "127.0.0.1", port : int = 8080, debug : bool = False):
        self.debug = debug
        self.host = host
        self.port = port

class VaServer:
    app : Flask
    config : ServerConfig


    def __init__(self, config : ServerConfig):
        self.app = None
        self.config = config
        
    
    def run(self):
        if not self.config.debug:
            # Disable Flask warnings related to the development usage.
            # Flask insists on being wrapped by a WSGI server
            # for higher scalability and security.
            # However, there is no scalability, and the app is meant to
            # be used by a single user at a time.
            warnings.filterwarnings('ignore', category=UserWarning, module='werkzeug')
            logging.getLogger('werkzeug').setLevel(logging.ERROR)

        self.app = Flask(__name__)
        self.app.add_url_rule('/query/<string:query_id>/', defaults={'requirement_id': None}, view_func=QueryView.as_view('nary-query'))
        self.app.add_url_rule('/query/<string:query_id>/<string:requirement_id>', view_func=QueryView.as_view('unary-query'))
        self.app.run(host=self.config.host, port=self.config.port, debug=self.config.debug, use_reloader=False)
