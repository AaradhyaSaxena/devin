import json
import os
import subprocess
from datetime import datetime


def create_branch_and_raise_pr(output_repo, description):
    # Generate a unique branch name using the current timestamp
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    branch_name = f"new-branch-{timestamp}"
    commit_message = "Updated files with new content"

    # Change to the repository directory
    os.chdir(output_repo)

    # Run git commands
    try:
        subprocess.run(["git", "checkout", "-b", branch_name], check=True)
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        subprocess.run(["git", "push", "-u", "origin", branch_name], check=True)

        # Raise a pull request using GitHub CLI (gh)
        result = subprocess.run(["gh", "pr", "create", "--title", "Automated PR", "--body", description], check=True,
                                capture_output=True, text=True)
        return result.stdout.strip()  # Assuming the PR link is in the stdout
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running git commands: {e}")


def handle_response(json_response):
    print("json_response before parsing:", json_response)
    if json_response.startswith('```json'):
        json_response = json_response[7:]
    if json_response.endswith('```'):
        json_response = json_response[:-3]
    print("json_response after parsing:", json_response)

    new_files = json.loads(json_response, strict=False)
    description = new_files.pop("explanation", None)  # Use None to avoid KeyError if "explanation" is not present
    output_repo = '/Users/as980m/repo/WORK-wayfair/pace/pace/output'
    update_files_in_directory(output_repo, new_files)
    # create_branch_and_raise_pr(output_repo, description)
    return description


def update_files_in_directory(output_repo, new_files):
    for file_path, new_content in new_files.items():
        full_path = os.path.join(output_repo, file_path)
        if os.path.exists(full_path):
            with open(full_path, 'w') as file:
                file.write(new_content)
            print(f"Updated file: {full_path}")
        else:
            with open(full_path, 'w') as file:
                file.write(new_content)
            print(f"File not found so Added new file: {full_path}")


