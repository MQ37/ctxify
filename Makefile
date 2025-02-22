.PHONY: format lint

# Format code with ruff
format:
	ruff format src/          # Apply formatting
	ruff format src/ --check  # Check formatting first

# Lint code with ruff
lint:
	ruff check src/ --fix     # Check and auto-fix where possible
	ruff check src/           # Final check after fixes
