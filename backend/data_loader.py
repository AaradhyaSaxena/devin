import pandas as pd
import os

class DataLoader:
    @staticmethod
    def analyze_repository(repo_path) -> pd.DataFrame:
        file_contents = {}
        for root, _, files in os.walk(repo_path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    file_contents[file] = content
                except Exception as e:
                    print(f"Error reading file {file}: {str(e)}")
                    file_contents[file] = "Error reading file"
        
        df = pd.DataFrame(list(file_contents.items()), columns=['File Name', 'Content'])
        return df
