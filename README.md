# ctxify

Copy your code to clipboard. That's it. ✨

![GitHub release (latest by date)](https://img.shields.io/github/v/release/MQ37/ctxify?color=brightgreen)
![Code Checks](https://github.com/mq37/ctxify/actions/workflows/code_checks.yml/badge.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

> 💫 100% vibe coded to perfection

## What it does

`ctxify` copies your project files to clipboard with a single command.

```bash
ctxify
```

That's it. Your code is now in your clipboard. Paste it into ChatGPT or whatever.

## Why?

Because copying files one by one is tedious, and I got tired of doing it.

## Install

```bash
pipx install ctxify  # if you're fancy
pip install ctxify   # works too
uv tool install ctxify  # if you're using uv
```

Linux needs `xclip`:
```bash
sudo apt install xclip
```

## Usage

Basic:
```bash
ctxify  # copies everything
```

Options that matter:
```bash
ctxify -i  # interactive mode, pick what you want
ctxify -e  # exclude stuff you don't want
ctxify -s  # structure only, no file contents
ctxify -g  # git tracked files only
ctxify --md  # include markdown files
```

## Example

```
Files Included in Context (from .):
├── .python-version
└── src
    └── ctxify
        ├── __init__.py
        ├── cli.py
        └── main.py

Approximate token count: 512
```

## Contributing

Fork it; Submit a PR; Create an issue with a bug or idea.
