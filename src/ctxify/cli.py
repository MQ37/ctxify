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
def main(
    directory: str, md: bool, interactive: bool, exclude: bool, structure: bool
) -> None:
    """A tool to print all tracked files in a git repository directory with tree structure and copy to clipboard."""
    try:
        output: str
        if interactive:
            output = interactive_file_selection(directory, include_md=md)
        elif exclude:
            output = interactive_file_exclusion(directory, include_md=md)
        else:
            output = print_git_contents(
                root_dir=directory, include_md=md, structure_only=structure
            )
        if copy_to_clipboard(output):
            click.echo('Project context copied to clipboard!')
    except GitRepositoryError:
        sys.exit(1)


if __name__ == '__main__':
    main()
