import os
from config import load_config
from data_loader import RepositoryAnalyzer
from llm_chain import LLMChain
from code_generation_engine import CodeGenerationEngine
from app import APP

def main():
    load_config()
    
    repo_analyzer = RepositoryAnalyzer()
    df = repo_analyzer.analyze_repository('./codebase/input/')
    print(df.head())
    
    llm_chain = LLMChain(df)
    codeGenerationEngine = CodeGenerationEngine(llm_chain, df)
    
    app = APP(df, codeGenerationEngine)
    
    app.run()

if __name__ == '__main__':
    main()