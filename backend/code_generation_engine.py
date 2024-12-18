import json
from models import LLMResponse
from utils import create_diff_response
from response_handler import handle_response

class CodeGenerationEngine:
    def __init__(self, llm_chain, df):
        self.llm_chain = llm_chain
        self.df = df

    def get_existing_file_content(self, filepath: str) -> str:
        """Get existing content of a file from the dataframe."""
        file_data = self.df[self.df['Path'] == filepath]
        if not file_data.empty:
            return file_data.iloc[0]['Content']
        return ''

    def generate_code(self, query, reference_filepaths=None):
        result = self.llm_chain.invoke(
            query=query,
            reference_filepaths=reference_filepaths
        )
        try:
            # print("Raw LLM result:", repr(result), "\n")
            # print("Result type:", type(result), "\n")
            # Strip any markdown code block indicators if present
            if isinstance(result, str):
                result = result.strip()
                if result.startswith('```json'):
                    result = result.split('\n', 1)[1]
                if result.endswith('```'):
                    result = result.rsplit('\n', 1)[0]
            
            print("result:", result)
            result = json.loads(result)
            return json.dumps(result, indent=2)
            # for filepath in result.get('files', {}).keys():
            #     print("filepath:", filepath, "\n")
            #     print("changes:", result.get('files', {}).get(filepath), "\n")
            # old_files = {
            #     filepath: self.get_existing_file_content(filepath)
            #     for filepath in result.get('files', {}).keys()
            # }
            # # Generate diffs
            # diffs = create_diff_response(old_files, result.get('files', {}))
            # # print("Result:", type(result))
            # # return result
            # response = LLMResponse(
            #     explanation=json.dumps(result.get("explanation", {})),
            #     files=result.get("files", {}),
            #     diffs=diffs
            # )
            # # print("Responsessssss:", response)
            # return json.dumps(response.model_dump_json(), indent=2)
        except json.JSONDecodeError as e:
            print("JSON Decode Error:", str(e))
            print("Failed to parse result:", repr(result))
            response = LLMResponse(
                explanation=f"Error: Invalid response format from LLM. Details: {str(e)}",
                files={"error.txt": str(result)}
            )
            return json.dumps(response.model_dump(), indent=2)
        
    def merge_code(self, filename, suggested_changes, explanation):
        original_code = self.get_existing_file_content(filename)

        result = self.merge_chain.invoke(
            original_code=original_code,
            suggested_changes=suggested_changes,
            explanation=explanation
        )   
        try:
            print("Raw LLM merge result:", result)
            result = json.loads(result)
            handle_response(result)
            return json.dumps(result, indent=2)
        except json.JSONDecodeError as e:
            print("JSON Decode Error:", str(e))
            print("Failed to parse result:", result)
            return json.dumps({"error.txt": result}, indent=2)
        
