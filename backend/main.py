import os
from config import load_config
from data_loader import DataLoader
from vector_store import VectorStore
from llm_chain import LLMChain
from code_generation_engine import CodeGenerationEngine
from app import APP

def main():
    load_config()
    
    df = DataLoader().analyze_repository('./codebase/')
    print(df.head())
    
    vector_store = VectorStore(df)
    if not os.path.exists(vector_store.persist_directory) or not os.listdir(vector_store.persist_directory):
        print("Persisted data not found. Creating and adding to stores...")
        vector_store.add_to_stores()
    else:
        print("Persisted data found. Loading existing stores...")
    
    llm_chain = LLMChain(df, vector_store)
    codeGenerationEngine = CodeGenerationEngine(llm_chain, df)
    
    app = APP(df, codeGenerationEngine)
    
    app.run()

if __name__ == '__main__':
    main()