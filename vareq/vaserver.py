from flask import Flask, jsonify, views

class QueryView(views.View):
    def __init__(self):
        pass

    def dispatch_request(self, query_id : str, requirement_id : str):
        result = {"query_id": query_id, "requirement_id" : requirement_id}
            
        return jsonify(result)

class VaServer:
    def __init__(self):
        self.app = None

    
    def run(self, host='0.0.0.0', port=8080, debug=False):
        self.app = Flask(__name__)
        self.app.add_url_rule('/query/<string:query_id>/', defaults={'requirement_id': None}, view_func=QueryView.as_view('nary-query'))
        self.app.add_url_rule('/query/<string:query_id>/<string:requirement_id>', view_func=QueryView.as_view('unary-query'))
        self.app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    server = VaServer()
    server.run(debug=True)