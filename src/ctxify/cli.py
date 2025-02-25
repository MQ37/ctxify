import click

from ctxify.main import copy_to_clipboard, print_git_contents, interactive_file_selection


@click.command()
@click.argument('directory', default='.', type=click.Path(exists=True, file_okay=False))
@click.option(
    '--md', '-md', is_flag=True, help='Include README and other .md files in output'
)
@click.option(
    '-i', '--interactive', is_flag=True, help='Interactively select files to include with tab autocompletion'
)
def main(directory, md, interactive):
    """A tool to print all tracked files in a git repository directory with tree structure and copy to clipboard."""
    if interactive:
        output = interactive_file_selection(directory, include_md=md)
    else:
        output = print_git_contents(root_dir=directory, include_md=md)
    if copy_to_clipboard(output):
        click.echo('Project context copied to clipboard!')


if __name__ == '__main__':
    main()
