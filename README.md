# ctxify 🎉
**Turn Your Git Repo into a Clipboard-Ready Context Machine**

*Built mostly with the help of xAI's Grok model—AI-powered coding at its finest!*

![GitHub release (latest by date)](https://img.shields.io/github/v/release/MQ37/ctxify?color=brightgreen)
![Code Checks](https://github.com/mq37/ctxify/actions/workflows/code_checks.yml/badge.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**`ctxify`** is a sleek CLI tool that grabs all tracked files in your Git repository, builds a neat tree structure, and copies everything—code and all—to your clipboard with a single command. Perfect for sharing project context, debugging, or feeding your code straight into AI assistants. It even gives you an approximate token count for fun! 🚀

---

## Why ctxify?
Ever wanted to:
- Share your project structure and code in one go?
- Hand-pick files interactively with tab autocompletion?
- Skip the hassle of manually copying files?
- Get just the structure without the contents?
- Know how many tokens your project weighs in at?

`ctxify` does it all. It's lightweight, fast, and skips the fluff (like lock files or `.gitignore`). Built with Python 3.13 and Git magic. ✨

---

## Features
- 📂 **Git-Powered Tree View**: Prints a gorgeous file tree of tracked files.
- 📋 **Clipboard Ready**: Copies the tree *and* file contents instantly.
- 🚫 **Smart Filtering**: Ignores non-code files (e.g., `uv.lock`, `.txt`) by default.
- 📝 **Markdown Support**: Optionally include `.md` files with a flag.
- 🎮 **Interactive Mode**: Pick files with fuzzy tab autocompletion.
- 🌳 **Structure-Only Mode**: Output just the tree, no contents.
- 📏 **Token Count**: Estimates tokens (1 token ≈ 4 chars) for the full output.

---

## Installation

Install `ctxify` from PyPI:

- **With `pipx`** (recommended for isolated CLI tools):
  ```bash
  pipx install ctxify
  ```

- **With `uv`** (fast and modern Python tool management):
  ```bash
  uv tool install ctxify
  ```

### Optional (for clipboard support)
On Linux, install `xclip`:
```bash
sudo apt install xclip
```

On macOS, clipboard support is built-in (uses `pbcopy`), so no additional installation is needed.

---

## Usage
Run it from your Git repo's root:

```bash
ctxify
```

### Options
- `--md` / `-md`: Include `.md` files (e.g., `README.md`).
   ```bash
   ctxify --md
   ```
- `-i` / `--interactive`: Select files interactively with tab autocompletion.
   ```bash
   ctxify -i
   ```
- `-s` / `--structure`: Output only the project structure, no contents.
   ```bash
   ctxify -s
   ```

### Example Output
```
Files Included in Context (from .):
├── .python-version
└── src
    └── ctxify
        ├── __init__.py
        ├── cli.py
        └── main.py

Approximate token count: 512 (based on 1 token ≈ 4 chars)
```

The clipboard gets the tree *plus* file contents (unless using `-s`)—ready to paste anywhere!

---

## Contributing
Love `ctxify`? Want to make it better?
- Fork it.
- Submit a PR.
- Open an issue with ideas or bugs.
