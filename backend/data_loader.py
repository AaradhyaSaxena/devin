import pandas as pd
import os
from typing import Set, List, Dict, Optional

class RepositoryAnalyzer:
    # Default extensions to include
    DEFAULT_INCLUDE_EXTENSIONS: Set[str] = {
        # Python
        '.py', '.pyx', '.pyi',
        # Java
        '.java', '.kt', '.scala',
        # Web
        '.js', '.jsx', '.ts', '.tsx',
        # Other common languages
        '.cpp', '.hpp', '.c', '.h', '.cs', '.go', '.rs',
        # Config & Data
        '.json', '.yaml', '.yml', '.toml',
        # Documentation
        '.md', '.rst',
        # Markdown
        '.md',
        # data
        '.csv', '.jsonl', '.sql'
    }

    # Default extensions to exclude
    DEFAULT_EXCLUDE_EXTENSIONS: Set[str] = {
        # Python
        '.pyc', '.pyo', '.pyd', '.egg', '.whl',
        # Java
        '.class', '.jar', '.war',
        # Build artifacts
        '.o', '.obj', '.dll', '.so', '.dylib',
        # IDE files
        '.idea', '.vscode',
        # Other
        '.log', '.cache', '.tmp', '.temp',
        '.git', '.svn', '.hg',
        '.env', '.venv',
        '.DS_Store'
    }

    def __init__(self, 
                 include_extensions: Optional[Set[str]] = None,
                 exclude_extensions: Optional[Set[str]] = None):
        self.include_extensions = include_extensions or self.DEFAULT_INCLUDE_EXTENSIONS
        self.exclude_extensions = exclude_extensions or self.DEFAULT_EXCLUDE_EXTENSIONS

    def _should_include_file(self, filename: str) -> bool:
        """Determine if a file should be included based on its extension."""
        file_ext = os.path.splitext(filename)[1].lower()
        return (file_ext not in self.exclude_extensions and 
                file_ext in self.include_extensions)

    def _filter_directories(self, dirs: List[str]) -> List[str]:
        """Filter out directories that match excluded extensions."""
        return [d for d in dirs if not any(d.endswith(ext) for ext in self.exclude_extensions)]

    def _read_file_content(self, file_path: str) -> Dict:
        """Read and return file content with error handling."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return {
                'Name': os.path.basename(file_path),
                'Path': file_path,
                'Type': 'file',
                'Content': content
            }
        except Exception as e:
            print(f"Error reading file {file_path}: {str(e)}")
            return {
                'Name': os.path.basename(file_path),
                'Path': file_path,
                'Type': 'file',
                'Content': "Error reading file"
            }

    def _create_directory_entry(self, dir_path: str) -> Dict:
        """Create a directory entry for the DataFrame."""
        return {
            'Name': os.path.basename(dir_path),
            'Path': dir_path,
            'Type': 'directory',
            'Content': None
        }

    def _save_to_csv(self, df: pd.DataFrame, output_path: str = 'data/repo_content.csv'):
        """Save DataFrame to CSV if not empty."""
        if not df.empty:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            df.to_csv(output_path, index=False)

    def analyze_repository(self, repo_path: str, save_csv: bool = True) -> pd.DataFrame:
        """
        Analyze repository contents with configured file extension filters.
        
        Args:
            repo_path: Path to the repository
            save_csv: Whether to save results to CSV
        """
        contents = []
        
        for root, dirs, files in os.walk(repo_path):
            print("root:", root, "dirs:", dirs, "files:", files, "\n")
            dirs[:] = self._filter_directories(dirs)
            
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                contents.append(self._create_directory_entry(dir_path))
            
            # Process files
            for file in files:
                if self._should_include_file(file):
                    file_path = os.path.join(root, file)
                    contents.append(self._read_file_content(file_path))
        
        df = pd.DataFrame(contents)
        
        if save_csv:
            self._save_to_csv(df)
            
        return df
