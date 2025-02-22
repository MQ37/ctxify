# ctxify 🎉
**Turn Your Git Repo into a Clipboard-Ready Context Machine**

![GitHub release (latest by date)](https://img.shields.io/github/v/release/MQ37/ctxify?color=brightgreen)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**`ctxify`** is a sleek CLI tool that grabs all tracked files in your Git repository, builds a neat tree structure, and copies everything—code and all—to your clipboard with a single command. Perfect for sharing project context, debugging, or feeding your code straight into AI assistants. Oh, and it even throws in an approximate token count for good measure! 🚀

---

## Why ctxify?
Ever wanted to:
- Share your project structure and code in one go?
- Skip the hassle of manually copying files?
- Know how many tokens your project weighs in at (for AI fun)?

`ctxify` does it all. It’s lightweight, fast, and skips the fluff (like lock files or `.gitignore`). Plus, it’s built with Python 3.13 and Git magic. ✨

---

## Features
- 📂 **Git-Powered Tree View**: Prints a gorgeous file tree of tracked files.
- 📋 **Clipboard Ready**: Copies the tree *and* file contents instantly.
- 🚫 **Smart Filtering**: Ignores non-code files (e.g., `package-lock.json`, `.txt`) by default.
- 📝 **Markdown Support**: Optionally include `.md` files with a simple flag.
- 📏 **Token Count**: Estimates tokens (1 token ≈ 4 chars) for the full output.

---

## Installation

Install `ctxify` from PyPI using your favorite tool:

- **With `pipx`** (recommended for isolated CLI tools):
  ```bash
  pipx install ctxify
  ```

- **With `uv`** (fast and modern Python tool management):
  ```bash
  uv tool install ctxify
  ```

### Optional (for clipboard support)
On Linux, install `xclip` for clipboard functionality:
```bash
sudo apt install xclip
```

---

## Usage
Run it from your Git repo’s root:

```bash
ctxify
```

### Options
- `--md` / `-md`: Include `.md` files (like `README.md`) in the output.
   ```bash
   ctxify --md
   ```

### Example Output
```
Files Included in Context:
├── .python-version
└── src
    └── ctxify
        ├── __init__.py
        ├── cli.py
        └── main.py

Approximate token count: 512 (based on 1 token ≈ 4 chars)
```

The clipboard gets the tree *plus* all file contents—ready to paste anywhere!

---

## Contributing
Love `ctxify`? Want to make it even better?
- Fork it.
- Submit a PR.
- Open an issue with ideas or bugs.
