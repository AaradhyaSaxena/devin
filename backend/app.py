from flask import Flask, request, jsonify
import random
import json
class APP:
    def __init__(self, df, code_generation_engine):
        self.app = Flask(__name__)
        self.df = df
        self.code_generation_engine = code_generation_engine
        self.config = self.load_config()
        self.port = self.config.get('PORT', 5001)
        self.setup_routes()

    def load_config(self):
        with open('./config/config.json') as config_file:
            return json.load(config_file)

    def setup_routes(self):
        @self.app.route('/status', methods=['GET'])
        def a_live():
            return "Alive!"

        @self.app.route('/predict', methods=['GET'])
        def predict():
            demo = random.randint(2000, 5000)    
            return str(demo)

        @self.app.route('/generate_code', methods=['POST'])
        def generate_code():
            data = request.json
            query = data.get('query')
            if not query:
                return jsonify({"error": "Missing query"}), 400
            result = self.code_generation_engine.generate_code(query)
            return jsonify({"code": result})

    def run(self):
        self.app.run(port=self.port)