import json
from langchain_google_vertexai import ChatVertexAI
from langchain.prompts import ChatPromptTemplate 

class LLMChain:
    def __init__(self, df, vector_store):
        self.df = df
        self.vector_store = vector_store
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

    def get_context(self, inputs):
        query = f"{inputs['question']}"
        docs = self.vector_store.get_relevant_documents(query)
        print("RAG context code", docs)
        if docs and isinstance(docs[0], str):
            return "\n".join(docs)
        else:
            return "\n".join(doc.page_content for doc in docs if hasattr(doc, 'page_content'))

    def setup_chain(self):
        return (
            {
                "system_prompt_intro": lambda x: self.prompt_components["system_prompt_intro"],
                "system_prompt": lambda x: self.system_prompt,
                "question_intro": lambda x: self.prompt_components["question_intro"],
                "question": lambda x: x["question"],
                "context_intro": lambda x: self.prompt_components["context_intro"],
                "context": lambda x: self.get_context(x),
                "output_instructions": lambda x: self.prompt_components["output_instructions"],
                "format_instructions": lambda x: self.prompt_components["format_instructions"]
            }
            | self.prompt_template
            | self.llm
        )

    def invoke(self, query):
        return self.chain.invoke({"question": query})
