import click

from ctxify.main import (
    copy_to_clipboard,
    interactive_file_selection,
    print_git_contents,
)


@click.command()
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
    '-s',
    '--structure',
    is_flag=True,
    help='Output only the project structure without file contents',
)
def main(directory: str, md: bool, interactive: bool, structure: bool) -> None:
    """A tool to print all tracked files in a git repository directory with tree structure and copy to clipboard."""
    output: str
    if interactive:
        output = interactive_file_selection(directory, include_md=md)
    else:
        output = print_git_contents(
            root_dir=directory, include_md=md, structure_only=structure
        )
    if copy_to_clipboard(output):
        click.echo('Project context copied to clipboard!')


if __name__ == '__main__':
    main()
