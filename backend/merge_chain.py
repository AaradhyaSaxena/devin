import json
from langchain_google_vertexai import ChatVertexAI
from langchain.prompts import ChatPromptTemplate 

class MergeChain:
    def __init__(self, df):
        self.df = df
        self.llm = ChatVertexAI(model="gemini-1.5-pro")
        self.load_prompts()
        self.chain = self.setup_chain()

    def load_prompts(self):
        try:
            with open('config/code_merge_prompts_config.json', 'r') as f:
                prompts = json.load(f)
            self.system_prompt = prompts['system_prompt']
            self.prompt_components = prompts['prompt_components']
            self.prompt_template = self.create_prompt_template(prompts['prompt_template'])
        except FileNotFoundError:
            print("code_merge_prompts_config.json not found. Using default prompts.")
        except json.JSONDecodeError:
            print("Error parsing code_merge_prompts_config.json. Using default prompts.")

    def create_prompt_template(self, template_string):
        return ChatPromptTemplate.from_template(template_string)

 
    def setup_chain(self):
        return (
            {
                "system_prompt_intro": lambda x: self.prompt_components["system_prompt_intro"],
                "system_prompt": lambda x: self.system_prompt,
                "original_code_intro": lambda x: self.prompt_components["original_code_intro"],
                "original_code": lambda x: x["original_code"],
                "suggested_changes_intro": lambda x: self.prompt_components["suggested_changes_intro"],
                "suggested_changes": lambda x: x["suggested_changes"],
                "explanation_intro": lambda x: self.prompt_components["explanation_intro"],
                "explanation": lambda x: x["explanation"],
                "repo_context": lambda x: self.prompt_components["repo_context"],
                "output_instructions": lambda x: self.prompt_components["output_instructions"],
                "output_format": lambda x: self.prompt_components["output_format"],
                "format_instructions": lambda x: self.prompt_components["format_instructions"]
            }
            | self.prompt_template
            | self.llm
        )

    def invoke(self, original_code, suggested_changes, explanation):
        input_data = {
            "original_code": original_code,
            "suggested_changes": suggested_changes,
            "explanation": explanation
        }
        
        return self.chain.invoke(input_data).content
