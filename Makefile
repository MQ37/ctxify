.PHONY: format lint bump test

CODE_DIRS := src/ tests/

# Format code with ruff
format:
	uv run ruff format $(CODE_DIRS)          # Apply formatting
	uv run ruff format $(CODE_DIRS) --check  # Check formatting first

# Lint code with ruff
lint:
	uv run ruff check $(CODE_DIRS) --fix     # Check and auto-fix where possible
	uv run ruff check $(CODE_DIRS)           # Final check after fixes

# Bump version (patch, minor, major)
bump:
	uv run python bump_version.py $(TYPE)

# Default to patch if no TYPE is specified
TYPE ?= patch

# Alias targets for -p, -m, -M
bump-patch: TYPE = patch
bump-patch: bump

bump-minor: TYPE = minor
bump-minor: bump

bump-major: TYPE = major
bump-major: bump

# Run tests with pytest
test:
	uv run pytest tests/ -v

# Combined check for CI
check: format lint test
