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
            if isinstance(result, str):
                result = result.strip()
                if result.startswith('```json'):
                    result = result.split('\n', 1)[1]
                if result.endswith('```'):
                    result = result.rsplit('\n', 1)[0]
            
            parsed_result = json.loads(result)
            
            # Format the code changes for better readability
            if "files" in parsed_result:
                for filename, file_data in parsed_result["files"].items():
                    if "changes" in file_data:
                        for change in file_data["changes"]:
                            if "content" in change:
                                # Properly handle line breaks and indentation
                                content = change["content"]
                                # Replace literal \n with actual line breaks
                                content = content.replace('\\n', '\n')
                                # Handle indentation
                                lines = content.split('\n')
                                # Detect base indentation from first non-empty line
                                base_indent = len(lines[0]) - len(lines[0].lstrip()) if lines else 0
                                # Properly indent all lines
                                formatted_lines = []
                                for line in lines:
                                    if line.strip():  # If line is not empty
                                        current_indent = len(line) - len(line.lstrip())
                                        # Preserve relative indentation
                                        relative_indent = current_indent - base_indent
                                        formatted_lines.append(' ' * max(0, relative_indent) + line.lstrip())
                                    else:
                                        formatted_lines.append('')
                                change["content"] = '\n'.join(formatted_lines)
            
            return json.dumps(parsed_result, indent=2)
            
        except json.JSONDecodeError as e:
            error_response = {
                "explanation": {
                    "problem_analysis": f"Error: Invalid response format from LLM. Details: {str(e)}",
                    "solution_overview": "Failed to generate solution",
                    "considerations": [],
                    "risks": ["Response parsing failed"]
                },
                "files": {},
                "testing": {
                    "required_tests": [],
                    "validation_steps": []
                }
            }
            return json.dumps(error_response, indent=2)
        
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
        
