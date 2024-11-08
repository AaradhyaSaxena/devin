import json

class CodeGenerationEngine:
    def __init__(self, llm_chain, df):
        self.llm_chain = llm_chain
        self.df = df

    def generate_code(self, query, reference_filepaths=None, output_files=None):
        result = self.llm_chain.invoke(
            query=query,
            reference_filepaths=reference_filepaths,
            output_files=output_files
        )
        response_dict = result.dict()
        json_response = json.dumps(response_dict, indent=2)
        return json.loads(json_response)
