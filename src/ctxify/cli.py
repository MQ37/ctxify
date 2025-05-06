import sys

import click

from ctxify.content import print_git_contents
from ctxify.interactive import interactive_file_exclusion, interactive_file_selection
from ctxify.utils import GitRepositoryError, copy_to_clipboard

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument('directory', default='.', type=click.Path(exists=True, file_okay=False))
@click.option(
    '--md', '-md', is_flag=True, help='Include README and other .md files in output'
)
@click.option(
    '-i',
    '--interactive',
    is_flag=True,
    help='Interactively select files to include with tab autocompletion',
)
@click.option(
    '-e',
    '--exclude',
    is_flag=True,
    help='Interactively select files to exclude with tab autocompletion',
)
@click.option(
    '-s',
    '--structure',
    is_flag=True,
    help='Output only the project structure without file contents',
)
@click.option(
    '-g',
    '--git',
    is_flag=True,
    help='Use Git tracked files only (default is to use all files in directory)',
)
def main(
    directory: str,
    md: bool,
    interactive: bool,
    exclude: bool,
    structure: bool,
    git: bool,
) -> None:
    """A tool to print files in a directory with tree structure and copy to clipboard.
    By default, it will include all files in the directory. Use --git flag to only include Git tracked files.
    """
    try:
        output: str
        if interactive:
            output = interactive_file_selection(directory, include_md=md, use_git=git)
        elif exclude:
            output = interactive_file_exclusion(directory, include_md=md, use_git=git)
        else:
            output = print_git_contents(
                root_dir=directory, include_md=md, structure_only=structure, use_git=git
            )
        if copy_to_clipboard(output):
            click.echo('Project context copied to clipboard!')
    except GitRepositoryError:
        if git:
            sys.exit(1)
        else:
            # If not using Git mode, we should never get here
            click.echo('Unexpected error occurred.')
            sys.exit(1)


if __name__ == '__main__':
    main()
