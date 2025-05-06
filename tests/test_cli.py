from unittest.mock import patch

from click.testing import CliRunner

from ctxify.cli import main


def test_cli_default():
    runner = CliRunner()
    with patch('ctxify.cli.copy_to_clipboard', return_value=True) as mock_copy:
        with patch('ctxify.cli.print_git_contents', return_value='mock output'):
            result = runner.invoke(main, ['.'])
            assert result.exit_code == 0
            assert 'Project context copied to clipboard!' in result.output
            mock_copy.assert_called_once_with('mock output')


def test_cli_with_md_flag():
    runner = CliRunner()
    with patch('ctxify.cli.copy_to_clipboard', return_value=True):
        with patch('ctxify.cli.print_git_contents') as mock_print:
            result = runner.invoke(main, ['.', '--md'])
            assert result.exit_code == 0
            mock_print.assert_called_once_with(
                root_dir='.', include_md=True, structure_only=False, use_git=False
            )


def test_cli_interactive():
    runner = CliRunner()
    with patch('ctxify.cli.copy_to_clipboard', return_value=True):
        with patch(
            'ctxify.cli.interactive_file_selection', return_value='interactive output'
        ) as mock_interactive:
            result = runner.invoke(main, ['.', '-i'])
            assert result.exit_code == 0
            mock_interactive.assert_called_once_with(
                '.', include_md=False, use_git=False
            )


def test_cli_structure_only():
    runner = CliRunner()
    with patch('ctxify.cli.copy_to_clipboard', return_value=True):
        with patch('ctxify.cli.print_git_contents') as mock_print:
            result = runner.invoke(main, ['.', '-s'])
            assert result.exit_code == 0
            mock_print.assert_called_once_with(
                root_dir='.', include_md=False, structure_only=True, use_git=False
            )


def test_cli_with_exclude_flag():
    runner = CliRunner()
    with patch('ctxify.cli.copy_to_clipboard', return_value=True):
        with patch('ctxify.cli.interactive_file_exclusion') as mock_exclude:
            result = runner.invoke(main, ['.', '-e'])
            assert result.exit_code == 0
            mock_exclude.assert_called_once_with('.', include_md=False, use_git=False)


def test_cli_with_git_flag():
    runner = CliRunner()
    with patch('ctxify.cli.copy_to_clipboard', return_value=True):
        with patch('ctxify.cli.print_git_contents') as mock_print:
            result = runner.invoke(main, ['.', '-g'])
            assert result.exit_code == 0
            mock_print.assert_called_once_with(
                root_dir='.', include_md=False, structure_only=False, use_git=True
            )


def test_cli_help_with_h():
    runner = CliRunner()
    result = runner.invoke(main, ['-h'])
    assert result.exit_code == 0
    assert 'A tool to print files in a directory' in result.output
