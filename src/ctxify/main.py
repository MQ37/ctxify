import os
import git
from pathlib import Path

def print_directory_tree(path, prefix=""):
    """Prints a simple directory tree structure"""
    entries = sorted([e for e in path.iterdir() if not e.name.startswith('.')
                     and e.name != '__pycache__'])
    for i, entry in enumerate(entries):
        is_last = i == len(entries) - 1
        print(f"{prefix}{'└── ' if is_last else '├── '}{entry.name}")
        if entry.is_dir():
            print_directory_tree(entry, prefix + ("    " if is_last else "│   "))

def get_git_files():
    """Get all tracked files from git repo respecting .gitignore"""
    try:
        repo = git.Repo(os.getcwd(), search_parent_directories=True)
        files = [item.path for item in repo.tree().traverse()
                if not repo.ignored(item.path) and item.type == 'blob']
        return sorted(files)
    except git.InvalidGitRepositoryError:
        print("Error: Not in a git repository")
        return []
    except Exception as e:
        print(f"Error accessing git repository: {e}")
        return []

def print_git_contents():
    """Print tree structure and file contents of git repo"""
    try:
        repo = git.Repo(os.getcwd(), search_parent_directories=True)
        repo_root = Path(repo.working_dir)
    except git.InvalidGitRepositoryError:
        print("Error: Not in a git repository")
        return

    # Print tree structure
    print("\nDirectory Structure:")
    print_directory_tree(repo_root)
    print("\n" + "-" * 50 + "\n")

    # Print file contents
    files = get_git_files()
    for file_path in files:
        full_path = repo_root / file_path
        if full_path.is_file():
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                print(f"{file_path}:")
                print(content)
                print()
            except Exception as e:
                print(f"{file_path}:")
                print(f"Error reading file: {e}\n")
