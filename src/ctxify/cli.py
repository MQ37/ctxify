import click
from ctxify.main import print_git_contents

@click.command()
def main():
    """A tool to print all tracked files in a git repository with tree structure."""
    print_git_contents()

if __name__ == "__main__":
    main()
