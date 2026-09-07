import sys
from {{ project_name }}.config import settings


def main():
    """Main entry point."""
    print(f"Starting {settings.project_name} in {settings.environment} mode...")
    # Your logic here


if __name__ == "__main__":
    main()
