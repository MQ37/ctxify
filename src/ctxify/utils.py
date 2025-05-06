import os
import platform
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

# Files that should always be included regardless of extension
NEVER_IGNORE_FILES = {
    'package.json',
}

# Files/extensions to skip (non-code files) for content inclusion
IGNORE_FILES = {
    'package-lock.json',
    'poetry.lock',
    'uv.lock',
    'Pipfile.lock',
    'yarn.lock',
    '.gitignore',
    '.gitattributes',
    '.editorconfig',
    '.prettierrc',
    '.eslintrc',
    'LICENSE',
    'CHANGELOG',
    'CONTRIBUTING',
    '.env',
}

IGNORE_EXTENSIONS = {
    '.json',
    '.yaml',
    '.yml',
    '.toml',
    '.txt',
    '.log',
    '.lock',
}

# Directories to ignore when scanning files
IGNORE_DIRS = {
    '.git',
    '__pycache__',
    'node_modules',
    '.venv',
    'venv',
    'env',
    '.pytest_cache',
    '.ruff_cache',
    'dist',
    'build',
}


class GitRepositoryError(Exception):
    """Raised when a directory is not within a Git repository."""

    pass


def check_git_repo(root_dir: str) -> bool:
    """Check if the given directory is within a git repository."""
    try:
        subprocess.check_output(
            ['git', 'rev-parse', '--show-toplevel'],
            text=True,
            cwd=root_dir,
            stderr=subprocess.STDOUT,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def get_files_from_directory(
    root_dir: str, include_md: bool = False
) -> Tuple[List[str], List[str], List[str]]:
    """Get all files from a directory recursively, filtering out ignored files and directories."""
    target_dir = Path(root_dir).resolve()
    try:
        all_files = []

        # Walk through the directory recursively
        for dirpath, dirnames, filenames in os.walk(target_dir):
            # Filter out ignored directories in-place
            dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]

            # Process files in this directory
            for filename in filenames:
                full_path = Path(dirpath) / filename
                # Get path relative to target_dir
                rel_path = full_path.relative_to(target_dir)
                rel_path_str = str(rel_path)
                all_files.append(rel_path_str)

        # Filter code files
        code_files = [
            f
            for f in all_files
            if f in NEVER_IGNORE_FILES
            or not (
                f in IGNORE_FILES
                or any(f.endswith(ext) for ext in IGNORE_EXTENSIONS)
                or (not include_md and (f.endswith('.md') or 'README' in f))
            )
        ]

        return [], sorted(all_files), sorted(code_files)
    except Exception as e:
        return [f'Error processing directory: {e}'], [], []


def get_git_files(
    root_dir: str, include_md: bool = False
) -> Tuple[List[str], List[str], List[str]]:
    """Get all tracked files from a specific directory within a git repo using git ls-files."""
    target_dir = Path(root_dir).resolve()
    try:
        repo_root = Path(
            subprocess.check_output(
                ['git', 'rev-parse', '--show-toplevel'], text=True, cwd=target_dir
            ).strip()
        )
        if not str(target_dir).startswith(str(repo_root)):
            return (
                [f'Error: Directory {root_dir} is outside the git repository'],
                [],
                [],
            )
        all_files = subprocess.check_output(
            ['git', 'ls-files'], cwd=repo_root, text=True
        ).splitlines()
        rel_path = (
            target_dir.relative_to(repo_root) if target_dir != repo_root else Path('.')
        )
        rel_str = str(rel_path)
        dir_files = [
            f[len(rel_str) + 1 :]
            if rel_str != '.' and f.startswith(rel_str + '/')
            else f
            for f in all_files
            if rel_str == '.' or f.startswith(rel_str + '/') or f == rel_str
        ]
        code_files = [
            f
            for f in dir_files
            if f in NEVER_IGNORE_FILES
            or not (
                f in IGNORE_FILES
                or any(f.endswith(ext) for ext in IGNORE_EXTENSIONS)
                or (not include_md and (f.endswith('.md') or 'README' in f))
            )
        ]
        return [], sorted(dir_files), sorted(code_files)
    except subprocess.CalledProcessError as e:
        return [f'Error accessing git repository: {e}'], [], []
    except Exception as e:
        return [f'Error processing directory: {e}'], [], []


def print_filtered_tree(
    files: List[str], output_lines: Optional[List[str]] = None
) -> List[str]:
    """Builds a tree structure from a list of file paths."""
    if output_lines is None:
        output_lines = []
    tree: Dict[str, Union[None, Dict]] = {}
    for file_path in files:
        parts = file_path.split('/')
        current = tree
        for part in parts[:-1]:
            if current is not None:
                current = current.setdefault(part, {})
        if current is not None:
            current[parts[-1]] = None

    def render_tree(node: Dict[str, Union[None, Dict]], prefix: str = '') -> None:
        if not isinstance(node, dict):
            return
        items = sorted(node.keys())
        for i, item in enumerate(items):
            is_last = i == len(items) - 1
            output_lines.append(f'{prefix}{"└── " if is_last else "├── "}{item}')
            next_node = node[item]
            if isinstance(next_node, dict):
                render_tree(next_node, prefix + ('    ' if is_last else '│   '))

    render_tree(tree)
    return output_lines


def estimate_tokens(text: str) -> int:
    """Estimate token count using 1 token ≈ 4 characters."""
    char_count = len(text)
    return char_count // 4


def copy_to_clipboard(text: str) -> bool:
    """Copy text to system clipboard using pbcopy (macOS) or xclip (Linux)."""
    system = platform.system().lower()
    try:
        if system == 'darwin':  # macOS
            subprocess.run(['pbcopy'], input=text.encode('utf-8'), check=True)
        elif system == 'linux':  # Linux
            subprocess.run(
                ['xclip', '-selection', 'clipboard'],
                input=text.encode('utf-8'),
                check=True,
            )
        else:
            print(f'Warning: Clipboard operations not supported on {platform.system()}')
            return False
        return True
    except subprocess.CalledProcessError:
        cmd = 'pbcopy' if system == 'darwin' else 'xclip'
        print(f'Warning: Failed to copy to clipboard ({cmd} error)')
        return False
    except FileNotFoundError:
        if system == 'darwin':
            print(
                'Warning: pbcopy not found. This is unexpected as it should be built into macOS'
            )
        else:
            print(
                "Warning: xclip not installed. Install it with 'sudo apt install xclip'"
            )
        return False
