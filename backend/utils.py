import difflib
from typing import Dict, Tuple

def generate_diff(old_code: str, new_code: str) -> str:
    """
    Generate a unified diff between old and new code.
    Returns a string with diff markers (-, +) similar to GitHub.
    """
    diff = difflib.unified_diff(
        old_code.splitlines(keepends=True),
        new_code.splitlines(keepends=True),
        fromfile='old',
        tofile='new',
        lineterm=''
    )
    return ''.join(diff)

## TODO: there is a library which renders the diffs in color coding, handled on frontend
## both old and new files are provided, so we can compare them
def create_diff_response(old_files: Dict[str, str], new_files: Dict[str, str]) -> Dict[str, str]:
    """
    Create a diff response comparing old and new files.
    """
    diffs = {}
    # set(old_files.keys()) needed for deleted files
    for filename in set(old_files.keys()) | set(new_files.keys()):
        old_content = old_files.get(filename, '')
        new_content = new_files.get(filename, '')
        
        # Handle case where content might be a dict with 'original' and 'modified' keys
        if isinstance(old_content, dict) and 'original' in old_content:
            old_content = old_content['original']
        if isinstance(new_content, dict) and 'modified' in new_content:
            new_content = new_content['modified']
            
        if old_content != new_content:
            diffs[filename] = generate_diff(old_content, new_content)
    return diffs
