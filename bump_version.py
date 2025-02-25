#!/usr/bin/env python3
import sys
from pathlib import Path

def bump_version(init_file="src/ctxify/__init__.py", toml_file="pyproject.toml", bump_type="patch"):
    """
    Bump the version in both __init__.py and pyproject.toml based on the bump type.
    Args:
        init_file (str): Path to the __init__.py file containing __version__.
        toml_file (str): Path to the pyproject.toml file.
        bump_type (str): One of 'patch', 'minor', 'major'.
    """
    # Validate bump_type
    valid_types = {"patch", "minor", "major"}
    if bump_type not in valid_types:
        print(f"Error: Invalid bump type '{bump_type}'. Use 'patch', 'minor', or 'major'.")
        sys.exit(1)

    # Read and bump version from __init__.py
    init_path = Path(init_file)
    if not init_path.exists():
        print(f"Error: Version file '{init_file}' not found.")
        sys.exit(1)

    with open(init_path, "r") as f:
        init_content = f.read()

    # Find the __version__ line
    version_line = None
    for line in init_content.splitlines():
        if line.strip().startswith("__version__ ="):
            version_line = line.strip()
            break

    if not version_line:
        print(f"Error: Could not find version in '{init_file}'.")
        sys.exit(1)

    # Extract current version and quote style
    if "'Version__" in version_line or '"Version__' in version_line:
        print(f"Error: Malformed version in '{init_file}'. Expected '__version__ = \"X.Y.Z\"' or '__version__ = 'X.Y.Z''.")
        sys.exit(1)
    quote = "'" if "'" in version_line else '"'
    current_version = version_line.split(quote)[1]  # Get the part between quotes
    try:
        major, minor, patch = map(int, current_version.split("."))
    except ValueError:
        print(f"Error: Invalid version format '{current_version}' in '{init_file}'. Expected 'X.Y.Z'.")
        sys.exit(1)

    # Bump the version based on type
    if bump_type == "patch":
        patch += 1
    elif bump_type == "minor":
        minor += 1
        patch = 0
    elif bump_type == "major":
        major += 1
        minor = 0
        patch = 0

    # Construct new version string
    new_version_str = f"{major}.{minor}.{patch}"
    new_init_version = f"__version__ = {quote}{new_version_str}{quote}"
    new_init_content = init_content.replace(version_line, new_init_version)

    # Write updated version to __init__.py
    with open(init_path, "w") as f:
        f.write(new_init_content)

    # Read and update pyproject.toml
    toml_path = Path(toml_file)
    if not toml_path.exists():
        print(f"Warning: '{toml_file}' not found. Only updated '{init_file}'.")
    else:
        with open(toml_path, "r") as f:
            toml_content = f.read()

        # Find the version line in pyproject.toml
        toml_version_line = None
        for line in toml_content.splitlines():
            if line.strip().startswith("version ="):
                toml_version_line = line.strip()
                break

        if not toml_version_line:
            print(f"Warning: Could not find version in '{toml_file}'. Only updated '{init_file}'.")
        else:
            new_toml_version = f'version = "{new_version_str}"'
            new_toml_content = toml_content.replace(toml_version_line, new_toml_version)
            with open(toml_path, "w") as f:
                f.write(new_toml_content)

    print(f"Version bumped to {new_version_str}")

if __name__ == "__main__":
    # Default to patch if no argument provided
    bump_type = sys.argv[1] if len(sys.argv) > 1 else "patch"
    bump_version(bump_type=bump_type)
