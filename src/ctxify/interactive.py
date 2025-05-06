from pathlib import Path
from typing import List

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import FuzzyWordCompleter

from ctxify.utils import (
    check_git_repo,
    estimate_tokens,
    get_files_from_directory,
    get_git_files,
    print_filtered_tree,
)


def interactive_file_selection(
    root_dir: str = '.', include_md: bool = False, use_git: bool = False
) -> str:
    """Interactively select files or directories to include with fuzzy tab autocompletion."""
    output_lines: List[str] = []
    tree_lines: List[str] = []

    # Determine whether to use Git or filesystem
    if use_git:
        if not check_git_repo(root_dir):
            print(
                f'Warning: {root_dir} is not within a git repository. Falling back to filesystem scan.'
            )
            errors, all_files, code_files = get_files_from_directory(
                root_dir, include_md=include_md
            )
        else:
            errors, all_files, code_files = get_git_files(
                root_dir, include_md=include_md
            )
    else:
        errors, all_files, code_files = get_files_from_directory(
            root_dir, include_md=include_md
        )

    if errors:
        tree_lines.extend(errors)
        print('\n'.join(tree_lines))
        return '\n'.join(tree_lines)

    all_dirs = {
        str(parent)
        for f in all_files
        for parent in Path(f).parents
        if str(parent) != '.'
    }
    completion_options = sorted(all_files + list(all_dirs))

    completer = FuzzyWordCompleter(completion_options)
    session = PromptSession(completer=completer, complete_while_typing=True)

    tree_lines.append(
        f'\nFiles and Directories Available in Context (from {root_dir}):'
    )
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
            output_lines.append(f'{item_path}:')
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                output_lines.append(content)
            except Exception as e:
                output_lines.append(f'Error reading file: {e}')
            output_lines.append('')
        elif full_path.is_dir():
            dir_files = [
                f for f in all_files if f.startswith(item_path + '/') or f == item_path
            ]
            if not dir_files:
                output_lines.append(f'No tracked files found in {item_path}')
                continue
            for file_path in dir_files:
                full_file_path = target_dir / file_path
                if full_file_path.is_file():
                    output_lines.append(f'{file_path}:')
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


def interactive_file_exclusion(
    root_dir: str = '.', include_md: bool = False, use_git: bool = False
) -> str:
    """Interactively select files or directories to exclude with fuzzy tab autocompletion."""
    tree_lines: List[str] = []

    # Determine whether to use Git or filesystem
    if use_git:
        if not check_git_repo(root_dir):
            print(
                f'Warning: {root_dir} is not within a git repository. Falling back to filesystem scan.'
            )
            errors, all_files, code_files = get_files_from_directory(
                root_dir, include_md=include_md
            )
        else:
            errors, all_files, code_files = get_git_files(
                root_dir, include_md=include_md
            )
    else:
        errors, all_files, code_files = get_files_from_directory(
            root_dir, include_md=include_md
        )

    if errors:
        tree_lines.extend(errors)
        print('\n'.join(tree_lines))
        return '\n'.join(tree_lines)

    all_dirs = {
        str(parent)
        for f in all_files
        for parent in Path(f).parents
        if str(parent) != '.'
    }
    completion_options = sorted(all_files + list(all_dirs))

    completer = FuzzyWordCompleter(completion_options)
    session = PromptSession(completer=completer, complete_while_typing=True)

    tree_lines.append(
        f'\nFiles and Directories Available in Context (from {root_dir}):'
    )
    print_filtered_tree(all_files, tree_lines)
    print('\n'.join(tree_lines))
    print('\nEnter file or directory paths to exclude (press Enter twice to finish):')

    excluded_items: List[str] = []
    while True:
        try:
            input_path = session.prompt('> ')
            if not input_path:
                if not excluded_items:
                    continue
                break
            if input_path in completion_options:
                if input_path not in excluded_items:
                    excluded_items.append(input_path)
                    print(f'Excluded: {input_path}')
                else:
                    print(f'Already excluded: {input_path}')
            else:
                print(f'Path not found: {input_path}')
        except KeyboardInterrupt:
            break

    from .content import print_git_contents

    output = print_git_contents(
        root_dir=root_dir,
        include_md=include_md,
        structure_only=False,
        excluded_items=excluded_items,
        use_git=use_git,
    )
    return output
