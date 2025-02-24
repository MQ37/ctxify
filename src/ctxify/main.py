import os
import subprocess
from pathlib import Path

# Files/extensions to skip (non-code files) for content inclusion
NON_CODE_PATTERNS = {
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
    '.json',
    '.yaml',
    '.yml',
    '.toml',
    '.txt',
    '.log',
    '.lock',
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

    def render_tree(node, prefix=''):
        if not isinstance(node, dict):
            return
        items = sorted(node.keys())
        for i, item in enumerate(items):
            is_last = i == len(items) - 1
            output_lines.append(f'{prefix}{"└── " if is_last else "├── "}{item}')
            if isinstance(node[item], dict):
                render_tree(node[item], prefix + ('    ' if is_last else '│   '))

    render_tree(tree)
    return output_lines


def get_git_files(root_dir, include_md=False):
    """Get all tracked files from a specific directory within a git repo using git ls-files"""
    try:
        # Resolve the repo root and target directory
        repo_root = Path(subprocess.check_output(
            ['git', 'rev-parse', '--show-toplevel'],
            text=True
        ).strip())
        target_dir = Path(root_dir).resolve()

        # Ensure the target directory is within the repo
        if not str(target_dir).startswith(str(repo_root)):
            return [f'Error: Directory {root_dir} is outside the git repository'], [], []

        # Get all tracked files using git ls-files
        all_files = subprocess.check_output(
            ['git', 'ls-files'],
            cwd=repo_root,
            text=True
        ).splitlines()

        # Filter files to those under the target directory
        rel_path = target_dir.relative_to(repo_root) if target_dir != repo_root else Path('.')
        rel_str = str(rel_path)
        dir_files = []
        for f in all_files:
            if rel_str == '.' or f.startswith(rel_str + '/') or f == rel_str:
                # Adjust path to be relative to target_dir
                if rel_str != '.' and f.startswith(rel_str + '/'):
                    dir_files.append(f[len(rel_str) + 1:])
                else:
                    dir_files.append(f)

        # Filter code files (exclude non-code and optionally .md files)
        code_files = [
            f
            for f in dir_files
            if not (
                f in NON_CODE_PATTERNS
                or any(f.endswith(ext) for ext in NON_CODE_PATTERNS)
                or (not include_md and (f.endswith('.md') or 'README' in f))
            )
        ]
        return [], sorted(dir_files), sorted(code_files)
    except subprocess.CalledProcessError as e:
        return [f'Error accessing git repository: {e}'], [], []
    except Exception as e:
        return [f'Error processing directory: {e}'], [], []


def copy_to_clipboard(text):
    """Copy text to system clipboard using xclip"""
    try:
        subprocess.run(
            ['xclip', '-selection', 'clipboard'], input=text.encode('utf-8'), check=True
        )
        return True
    except subprocess.CalledProcessError:
        print('Warning: Failed to copy to clipboard (xclip error)')
        return False
    except FileNotFoundError:
        print("Warning: xclip not installed. Install it with 'sudo apt install xclip'")
        return False


def estimate_tokens(text):
    """Estimate token count using 1 token ≈ 4 characters"""
    char_count = len(text)
    token_count = char_count // 4  # Integer division for approximate tokens
    return token_count


def print_git_contents(root_dir='.', include_md=False):
    """Build output for clipboard, print tree with all files and token count to stdout"""
    output_lines = []  # For clipboard
    tree_lines = []  # For stdout

    # Resolve paths
    repo_root = Path(subprocess.check_output(
        ['git', 'rev-parse', '--show-toplevel'],
        text=True
    ).strip())
    target_dir = Path(root_dir).resolve()
    if not str(target_dir).startswith(str(repo_root)):
        tree_lines.append(f'Error: Directory {root_dir} is outside the git repository')
        print('\n'.join(tree_lines))
        return '\n'.join(tree_lines)

    # Get all files and code files
    errors, all_files, code_files = get_git_files(root_dir, include_md=include_md)
    if errors:
        tree_lines.extend(errors)
        print('\n'.join(tree_lines))
        return '\n'.join(tree_lines)

    # Print tree with all files to stdout and clipboard
    tree_lines.append(f'\nFiles Included in Context (from {root_dir}):')
    print_filtered_tree(all_files, tree_lines)
    output_lines.extend(tree_lines)

    # Add separator and contents of code files only
    output_lines.append('\n' + '-' * 50 + '\n')
    for file_path in code_files:
        full_path = target_dir / file_path
        if full_path.is_file():
            output_lines.append(f'{file_path}:')
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                output_lines.append(content)
            except Exception as e:
                output_lines.append(f'Error reading file: {e}')
            output_lines.append('')

    # Calculate token count and append only to stdout
    full_output = '\n'.join(output_lines)
    token_count = estimate_tokens(full_output)
    token_info = f'\nApproximate token count: {token_count} (based on 1 token ≈ 4 chars)'
    tree_lines.append(token_info)

    # Print to stdout
    print('\n'.join(tree_lines))

    return '\n'.join(output_lines)
