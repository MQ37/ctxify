.PHONY: format lint bump

# Format code with ruff
format:
	ruff format src/          # Apply formatting
	ruff format src/ --check  # Check formatting first

# Lint code with ruff
lint:
	ruff check src/ --fix     # Check and auto-fix where possible
	ruff check src/           # Final check after fixes

# Bump version (patch, minor, major)
bump:
	@python bump_version.py $(TYPE)

# Default to patch if no TYPE is specified
TYPE ?= patch

# Alias targets for -p, -m, -M
bump-patch: TYPE = patch
bump-patch: bump

bump-minor: TYPE = minor
bump-minor: bump

bump-major: TYPE = major
bump-major: bump
