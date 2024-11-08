import pandas as pd
import os

@staticmethod
def analyze_repository(repo_path) -> pd.DataFrame:
    contents = []
    for root, dirs, files in os.walk(repo_path):
        # Add directory entries
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            contents.append({
                'Name': dir_name,
                'Path': dir_path,
                'Type': 'directory',
                'Content': None
            })
        
        # Add file entries
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                contents.append({
                    'Name': file,
                    'Path': file_path,
                    'Type': 'file',
                    'Content': content
                })
            except Exception as e:
                print(f"Error reading file {file}: {str(e)}")
                contents.append({
                    'Name': file,
                    'Path': file_path,
                    'Type': 'file',
                    'Content': "Error reading file"
                })
    
    df = pd.DataFrame(contents)
    df.to_csv('data/repo_content.csv', index=False)
    return df
