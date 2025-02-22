import os
import git
from pathlib import Path
import subprocess

# Files/extensions to skip (non-code files)
NON_CODE_PATTERNS = {
    "package-lock.json", "poetry.lock", "uv.lock", "Pipfile.lock", "yarn.lock",
    ".gitignore", ".gitattributes", ".editorconfig", ".prettierrc", ".eslintrc",
    "LICENSE", "CHANGELOG", "CONTRIBUTING",
    ".json", ".yaml", ".yml", ".toml", ".txt", ".log", ".lock"
}

def print_filtered_tree(files, output_lines=None):
    """Builds a tree structure from a list of file paths"""
    if output_lines is None:
        output_lines = []
    tree = {}
    for file_path in files:
        parts = file_path.split('/')
        current = tree
        for part in parts[:-1]:
            current = current.setdefault(part, {})
        current[parts[-1]] = None

    def render_tree(node, prefix=""):
        if not isinstance(node, dict):
            return
        items = sorted(node.keys())
        for i, item in enumerate(items):
            is_last = i == len(items) - 1
            output_lines.append(f"{prefix}{'└── ' if is_last else '├── '}{item}")
            if isinstance(node[item], dict):
                render_tree(node[item], prefix + ("    " if is_last else "│   "))

    render_tree(tree)
    return output_lines

def get_git_files(include_md=False):
    """Get all tracked code files from git repo, optionally including .md files"""
    try:
        repo = git.Repo(os.getcwd(), search_parent_directories=True)
        files = [item.path for item in repo.tree().traverse()
                if not repo.ignored(item.path) and item.type == 'blob']
        filtered_files = [
            f for f in files
            if not (
                f in NON_CODE_PATTERNS or
                any(f.endswith(ext) for ext in NON_CODE_PATTERNS) or
                (not include_md and (f.endswith('.md') or 'README' in f))
            )
        ]
        return [], sorted(filtered_files)
    except git.InvalidGitRepositoryError:
        return ["Error: Not in a git repository"], []
    except Exception as e:
        return [f"Error accessing git repository: {e}"], []

def copy_to_clipboard(text):
    """Copy text to system clipboard using xclip"""
    try:
        process = subprocess.run(
            ['xclip', '-selection', 'clipboard'],
            input=text.encode('utf-8'),
            check=True
        )
        return True
    except subprocess.CalledProcessError:
        print("Warning: Failed to copy to clipboard (xclip error)")
        return False
    except FileNotFoundError:
        print("Warning: xclip not installed. Install it with 'sudo apt install xclip'")
        return False

def estimate_tokens(text):
    """Estimate token count using 1 token ≈ 4 characters"""
    char_count = len(text)
    token_count = char_count // 4  # Integer division for approximate tokens
    return token_count

def print_git_contents(include_md=False):
    """Build output for clipboard, print tree and token count to stdout"""
    output_lines = []  # For clipboard
    tree_lines = []    # For stdout

    try:
        repo = git.Repo(os.getcwd(), search_parent_directories=True)
        repo_root = Path(repo.working_dir)
    except git.InvalidGitRepositoryError:
        tree_lines.append("Error: Not in a git repository")
        print("\n".join(tree_lines))
        return "\n".join(tree_lines)

    # Get filtered files
    errors, files = get_git_files(include_md=include_md)
    if errors:
        tree_lines.extend(errors)
        print("\n".join(tree_lines))
        return "\n".join(tree_lines)

    # Print tree to stdout
    tree_lines.append("\nFiles Included in Context:")
    print_filtered_tree(files, tree_lines)

    # Build full output for clipboard (tree + contents)
    output_lines.extend(tree_lines)
    output_lines.append("\n" + "-" * 50 + "\n")
    for file_path in files:
        full_path = repo_root / file_path
        if full_path.is_file():
            output_lines.append(f"{file_path}:")
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                output_lines.append(content)
            except Exception as e:
                output_lines.append(f"Error reading file: {e}")
            output_lines.append("")

    # Calculate and append token count
    full_output = "\n".join(output_lines)
    token_count = estimate_tokens(full_output)

    # Add token count to both stdout and clipboard output
    token_info = f"\nApproximate token count: {token_count} (based on 1 token ≈ 4 chars)"
    tree_lines.append(token_info)
    output_lines.append(token_info)

    # Print to stdout
    print("\n".join(tree_lines))

    return "\n".join(output_lines)
