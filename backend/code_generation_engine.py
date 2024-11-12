import json
from models import LLMResponse

class CodeGenerationEngine:
    def __init__(self, llm_chain, df):
        self.llm_chain = llm_chain
        self.df = df

    def generate_code(self, query, reference_filepaths=None):
        result = self.llm_chain.invoke(
            query=query,
            reference_filepaths=reference_filepaths
        )
        try:
            print("Raw LLM result:", result)
            print("Result type:", type(result))
            result = json.loads(result)
            response = LLMResponse(
                explanation=result.get("explanation", ""),
                files=result.get("files", {})
            )
            return json.dumps(response.model_dump(), indent=2)
        except json.JSONDecodeError as e:
            print("JSON Decode Error:", str(e))
            print("Failed to parse result:", result)
            response = LLMResponse(
                explanation="Error: Invalid response format from LLM",
                files={"error.txt": result}
            )
            return json.dumps(response.model_dump(), indent=2)
