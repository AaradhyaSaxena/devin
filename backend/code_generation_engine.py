import json

class CodeGenerationEngine:
    def __init__(self, llm_chain, df):
        self.llm_chain = llm_chain
        self.df = df

    def generate_code(self, query):
        result = self.llm_chain.invoke(query)
        response_dict = result.dict()
        json_response = json.dumps(response_dict, indent=2)
        return json.loads(json_response)

