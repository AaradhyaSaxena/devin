import json
from langchain_google_vertexai import ChatVertexAI
from langchain.prompts import ChatPromptTemplate 

class LLMChain:
    def __init__(self, df):
        self.df = df
        self.llm = ChatVertexAI(model="gemini-1.5-pro")
        self.load_prompts()
        self.chain = self.setup_chain()

    def load_prompts(self):
        try:
            with open('config/prompts_config.json', 'r') as f:
                prompts = json.load(f)
            self.system_prompt = prompts['system_prompt']
            self.prompt_components = prompts['prompt_components']
            self.prompt_template = self.create_prompt_template(prompts['prompt_template'])
        except FileNotFoundError:
            print("prompts_config.json not found. Using default prompts.")
        except json.JSONDecodeError:
            print("Error parsing prompts_config.json. Using default prompts.")

    def create_prompt_template(self, template_string):
        return ChatPromptTemplate.from_template(template_string)

    def get_reference_code(self, filepaths):
        if not filepaths:
            return ""
        
        reference_codes = []
        for filepath in filepaths:
            try:
                file_data = self.df[self.df['Path'] == filepath]
                if not file_data.empty:
                    if file_data.iloc[0]['Type'] == 'directory':
                        # Get all files under this directory
                        dir_files = self.df[
                            (self.df['Type'] == 'file') & 
                            (self.df['Path'].str.startswith(filepath))
                        ]
                        for _, file_row in dir_files.iterrows():
                            reference_codes.append(
                                f"{file_row['Path']}: {file_row['Content']}"
                            )
                    else:
                        # Handle single file
                        content = file_data.iloc[0]['Content']
                        reference_codes.append(f"{filepath}: {content}")
            except Exception as e:
                print(f"Error getting reference code for {filepath}: {str(e)}")
        
        return "\n" + "\n".join(reference_codes) if reference_codes else ""

    def setup_chain(self):
        return (
            {
                "system_prompt_intro": lambda x: self.prompt_components["system_prompt_intro"],
                "system_prompt": lambda x: self.system_prompt,
                "repo_context": lambda x: self.prompt_components["repo_context"],
                "question_intro": lambda x: self.prompt_components["question_intro"],
                "question": lambda x: x["question"],
                "context_intro": lambda x: self.prompt_components["context_intro"],
                "context": lambda x: self.get_reference_code(x["reference_filepaths"]),
                "output_instructions": lambda x: self.prompt_components["output_instructions"],
                "format_instructions": lambda x: self.prompt_components["format_instructions"]
            }
            | self.prompt_template
            | self.llm
        )

    def invoke(self, query, reference_filepaths=None):
        input_data = {
            "question": query,
            "reference_filepaths": reference_filepaths if reference_filepaths else []
        }
        
        return self.chain.invoke(input_data).content
