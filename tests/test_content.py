import subprocess
import sys
from unittest.mock import MagicMock, patch

from ctxify.content import print_git_contents
from ctxify.utils import (
    check_git_repo,
    copy_to_clipboard,
    estimate_tokens,
    get_files_from_directory,
    get_git_files,
    print_filtered_tree,
)


def test_check_git_repo_success(tmp_path):
    with patch('subprocess.check_output', return_value='/path/to/repo\n'):
        assert check_git_repo(str(tmp_path)) is True


def test_check_git_repo_failure(tmp_path):
    with patch(
        'subprocess.check_output', side_effect=subprocess.CalledProcessError(1, 'git')
    ):
        assert check_git_repo(str(tmp_path)) is False


def test_print_filtered_tree():
    files = ['src/main.py', 'src/utils/helper.py', 'README.md']
    output = print_filtered_tree(files)
    expected = [
        '├── README.md',
        '└── src',
        '    ├── main.py',
        '    └── utils',
        '        └── helper.py',
    ]
    assert output == expected


def test_get_git_files_success(tmp_path):
    with patch('subprocess.check_output') as mock_output:
        mock_output.side_effect = [
            f'{tmp_path}\n',  # git rev-parse --show-toplevel
            'file1.py\nfile2.txt\nREADME.md\n',  # git ls-files
        ]
        errors, all_files, code_files = get_git_files(str(tmp_path))
        assert errors == []
        assert all_files == ['README.md', 'file1.py', 'file2.txt']
        assert code_files == ['file1.py']


def test_get_git_files_not_in_repo(tmp_path):
    outside_path = tmp_path / 'outside'
    outside_path.mkdir()
    repo_root = '/some/other/repo'  # A path outside tmp_path
    with patch('subprocess.check_output', return_value=f'{repo_root}\n'):
        errors, all_files, code_files = get_git_files(str(outside_path))
        assert len(errors) == 1
        assert 'outside the git repository' in errors[0]
        assert all_files == []
        assert code_files == []


def test_get_files_from_directory(tmp_path):
    # Create test directory structure
    (tmp_path / 'file1.py').touch()
    (tmp_path / 'file2.txt').touch()
    (tmp_path / 'README.md').touch()

    # Create a directory to be ignored
    ignored_dir = tmp_path / '__pycache__'
    ignored_dir.mkdir()
    (ignored_dir / 'cache.pyc').touch()

    # Mock os.walk to return our test structure
    with patch('os.walk') as mock_walk:
        mock_walk.return_value = [
            (str(tmp_path), ['__pycache__'], ['file1.py', 'file2.txt', 'README.md']),
        ]

        errors, all_files, code_files = get_files_from_directory(str(tmp_path))
        assert errors == []
        # README.md is included in all_files but not in code_files
        assert sorted(all_files) == ['README.md', 'file1.py', 'file2.txt']
        assert code_files == ['file1.py']

        # Test with include_md=True
        errors, all_files, code_files = get_files_from_directory(
            str(tmp_path), include_md=True
        )
        assert errors == []
        assert sorted(all_files) == ['README.md', 'file1.py', 'file2.txt']
        assert sorted(code_files) == ['README.md', 'file1.py']


def test_copy_to_clipboard_success():
    with patch('subprocess.run', return_value=MagicMock(returncode=0)) as mock_run:
        assert copy_to_clipboard('test text') is True
        mock_run.assert_called_once()


def test_copy_to_clipboard_xclip_missing():
    with patch('subprocess.run', side_effect=FileNotFoundError):
        with patch('sys.stdout', new_callable=lambda: sys.stdout):  # Suppress print
            assert copy_to_clipboard('test text') is False


def test_estimate_tokens():
    assert estimate_tokens('Hello world') == 2  # 11 chars / 4 = 2 tokens
    assert estimate_tokens('') == 0


def test_print_git_contents_structure_only(tmp_path, mocker):
    mocker.patch('ctxify.content.check_git_repo', return_value=True)
    mocker.patch(
        'ctxify.content.get_git_files',
        return_value=([], ['file1.py'], ['file1.py']),
    )

    # Mock print_filtered_tree to return our test structure
    tree_lines = ['└── file1.py']
    mocker.patch(
        'ctxify.content.print_filtered_tree',
        side_effect=lambda files, lines=None: lines.extend(tree_lines)
        if lines is not None
        else tree_lines,
    )

    mocker.patch('sys.stdout', new_callable=lambda: sys.stdout)  # Suppress print

    output = print_git_contents(str(tmp_path), structure_only=True, use_git=True)
    assert '└── file1.py' in output


def test_print_git_contents_with_exclusions(tmp_path, mocker):
    mocker.patch('ctxify.content.check_git_repo', return_value=True)
    mocker.patch(
        'ctxify.content.get_git_files',
        return_value=([], ['file1.py', 'file2.txt'], ['file1.py']),
    )

    # Mock print_filtered_tree to return our test structure
    tree_lines = ['└── file2.txt']
    mocker.patch(
        'ctxify.content.print_filtered_tree',
        side_effect=lambda files, lines=None: lines.extend(tree_lines)
        if lines is not None
        else tree_lines,
    )

    mocker.patch('sys.stdout', new_callable=lambda: sys.stdout)  # Suppress print

    output = print_git_contents(
        str(tmp_path),
        include_md=False,
        structure_only=False,
        excluded_items=['file1.py'],
        use_git=True,
    )
    assert '└── file2.txt' in output


def test_print_git_contents_filesystem_mode(tmp_path, mocker):
    mocker.patch(
        'ctxify.content.get_files_from_directory',
        return_value=([], ['file1.py', 'file2.txt'], ['file1.py']),
    )

    # Mock print_filtered_tree to return our test structure
    tree_lines = ['├── file1.py', '└── file2.txt']
    mocker.patch(
        'ctxify.content.print_filtered_tree',
        side_effect=lambda files, lines=None: lines.extend(tree_lines)
        if lines is not None
        else tree_lines,
    )

    # Create a mock file for content reading
    (tmp_path / 'file1.py').write_text('print("Hello")')

    mocker.patch('sys.stdout', new_callable=lambda: sys.stdout)  # Suppress print

    output = print_git_contents(str(tmp_path), use_git=False)
    assert 'Files Included in Context' in output
    assert '├── file1.py' in output
