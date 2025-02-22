import click

from ctxify.main import copy_to_clipboard, print_git_contents


@click.command()
@click.option(
    '--md', '-md', is_flag=True, help='Include README and other .md files in output'
)
def main(md):
    """A tool to print all tracked files in a git repository with tree structure and copy to clipboard."""
    output = print_git_contents(include_md=md)
    if copy_to_clipboard(output):
        click.echo('Project context copied to clipboard!')


if __name__ == '__main__':
    main()
