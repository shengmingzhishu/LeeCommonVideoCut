import os
import sys


def check_structure():
    """Verify the project structure exists as expected."""
    required_paths = [
        "{{ project_name }}",
        "{{ project_name }}/__init__.py",
        "{{ project_name }}/main.py",
        "tests",
        "pyproject.toml",
        "requirements.txt",
    ]

    missing = []
    for path in required_paths:
        if not os.path.exists(path):
            missing.append(path)

    if missing:
        print(f"Structure check failed. Missing: {', '.join(missing)}")
        return False

    print("Structure check passed.")
    return True


if __name__ == "__main__":
    if not check_structure():
        sys.exit(1)
