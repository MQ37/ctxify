from pathlib import Path
from typing import List, Optional

from ctxify.utils import (
    check_git_repo,
    estimate_tokens,
    get_files_from_directory,
    get_git_files,
    print_filtered_tree,
)


def print_git_contents(
    root_dir: str = '.',
    include_md: bool = False,
    structure_only: bool = False,
    excluded_items: Optional[List[str]] = None,
    use_git: bool = False,
) -> str:
    """Build output for clipboard, print tree with all files and token count to stdout."""
    output_lines: List[str] = []
    tree_lines: List[str] = []

    target_dir = Path(root_dir).resolve()

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

    if excluded_items:
        excluded_files = set()
        for item in excluded_items:
            if item in all_files:
                excluded_files.add(item)
            else:
                excluded_files.update(f for f in all_files if f.startswith(item + '/'))
        all_files = [f for f in all_files if f not in excluded_files]
        code_files = [f for f in code_files if f not in excluded_files]

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
