import platform
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import FuzzyWordCompleter

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
    '.env',  # Added to explicitly ignore .env files
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


def print_filtered_tree(
    files: List[str], output_lines: Optional[List[str]] = None
) -> List[str]:
    """Builds a tree structure from a list of file paths"""
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


def get_git_files(
    root_dir: str, include_md: bool = False
) -> Tuple[List[str], List[str], List[str]]:
    """Get all tracked files from a specific directory within a git repo using git ls-files"""
    target_dir = Path(root_dir).resolve()
    try:
        # Resolve the repo root
        repo_root = Path(
            subprocess.check_output(
                ['git', 'rev-parse', '--show-toplevel'], text=True, cwd=target_dir
            ).strip()
        )

        # Ensure the target directory is within the repo
        if not str(target_dir).startswith(str(repo_root)):
            return (
                [f'Error: Directory {root_dir} is outside the git repository'],
                [],
                [],
            )

        # Get all tracked files using git ls-files
        all_files = subprocess.check_output(
            ['git', 'ls-files'], cwd=repo_root, text=True
        ).splitlines()

        # Filter files to those under the target directory
        rel_path = (
            target_dir.relative_to(repo_root) if target_dir != repo_root else Path('.')
        )
        rel_str = str(rel_path)
        dir_files = []
        for f in all_files:
            if rel_str == '.' or f.startswith(rel_str + '/') or f == rel_str:
                if rel_str != '.' and f.startswith(rel_str + '/'):
                    dir_files.append(f[len(rel_str) + 1 :])
                else:
                    dir_files.append(f)

        # Filter code files
        code_files = [
            f
            for f in dir_files
            if not (
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


def copy_to_clipboard(text: str) -> bool:
    """Copy text to system clipboard using pbcopy (macOS) or xclip (Linux)"""
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


def estimate_tokens(text: str) -> int:
    """Estimate token count using 1 token ≈ 4 characters"""
    char_count = len(text)
    return char_count // 4


def interactive_file_selection(root_dir: str = '.', include_md: bool = False) -> str:
    """Interactively select files or directories to include with fuzzy tab autocompletion"""
    if not check_git_repo(root_dir):
        print(
            f'Error: {root_dir} is not within a git repository. This tool requires a git repository.'
        )
        sys.exit(1)

    output_lines: List[str] = []
    tree_lines: List[str] = []

    errors, all_files, code_files = get_git_files(root_dir, include_md=include_md)
    if errors:
        tree_lines.extend(errors)
        print('\n'.join(tree_lines))
        return '\n'.join(tree_lines)

    # Add directories to completion options
    all_dirs = set()
    for f in all_files:
        path = Path(f)
        for parent in path.parents:
            if str(parent) != '.':
                all_dirs.add(str(parent))
    completion_options = sorted(all_files + list(all_dirs))

    completer = FuzzyWordCompleter(completion_options)
    session = PromptSession(completer=completer, complete_while_typing=True)

    tree_lines.append(f'\nFiles and Directories Available in Context (from {root_dir}):')
    print_filtered_tree(all_files, tree_lines)
    print('\n'.join(tree_lines))
    print('\nEnter file or directory paths to include (press Enter twice to finish):')

    selected_items: List[str] = []
    while True:
        try:
            input_path = session.prompt('> ')
            if not input_path:
                if not selected_items:
                    continue
                break
            if input_path in completion_options:
                if input_path not in selected_items:
                    selected_items.append(input_path)
                    print(f'Added: {input_path}')
                else:
                    print(f'Already added: {input_path}')
            else:
                print(f'Path not found: {input_path}')
        except KeyboardInterrupt:
            break

    output_lines.extend(tree_lines)
    output_lines.append('\n' + '-' * 50 + '\n')
    target_dir = Path(root_dir).resolve()

    for item_path in selected_items:
        full_path = target_dir / item_path
        if full_path.is_file():
            # Handle individual file
            output_lines.append(f'{item_path}:')
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                output_lines.append(content)
            except Exception as e:
                output_lines.append(f'Error reading file: {e}')
            output_lines.append('')
        elif full_path.is_dir():
            # Handle directory
            output_lines.append(f'\nDirectory {item_path} contents:')
            dir_files = [f for f in all_files if f.startswith(item_path + '/') or f == item_path]
            if not dir_files:
                output_lines.append(f'No tracked files found in {item_path}')
                continue
            # Print directory structure
            print_filtered_tree(dir_files, output_lines)
            output_lines.append('\nFile contents:')
            for file_path in dir_files:
                full_file_path = target_dir / file_path
                if full_file_path.is_file():
                    output_lines.append(f'\n{file_path}:')
                    try:
                        with open(full_file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        output_lines.append(content)
                    except Exception as e:
                        output_lines.append(f'Error reading file: {e}')
                    output_lines.append('')

    full_output = '\n'.join(output_lines)
    token_count = estimate_tokens(full_output)
    token_info = (
        f'\nApproximate token count: {token_count} (based on 1 token ≈ 4 chars)'
    )
    tree_lines.append(token_info)
    print('\n'.join(tree_lines[len(tree_lines) - 1 :]))

    return full_output

def print_git_contents(
    root_dir: str = '.', include_md: bool = False, structure_only: bool = False
) -> str:
    """Build output for clipboard, print tree with all files and token count to stdout"""
    if not check_git_repo(root_dir):
        print(
            f'Error: {root_dir} is not within a git repository. This tool requires a git repository.'
        )
        sys.exit(1)

    output_lines: List[str] = []
    tree_lines: List[str] = []

    target_dir = Path(root_dir).resolve()
    errors, all_files, code_files = get_git_files(root_dir, include_md=include_md)
    if errors:
        tree_lines.extend(errors)
        print('\n'.join(tree_lines))
        return '\n'.join(tree_lines)

    tree_lines.append(f'\nFiles Included in Context (from {root_dir}):')
    print_filtered_tree(all_files, tree_lines)
    output_lines.extend(tree_lines)

    if not structure_only:
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

    full_output = '\n'.join(output_lines)
    token_count = estimate_tokens(full_output)
    token_info = (
        f'\nApproximate token count: {token_count} (based on 1 token ≈ 4 chars)'
    )
    tree_lines.append(token_info)

    print('\n'.join(tree_lines))
    return full_output
