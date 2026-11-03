import subprocess
import time
import os
import sys


def run_smoke_test():
    """Perform a smoke test by running the app and checking for successful output."""
    print("Running smoke startup test...")

    # Run the main script
    try:
        # We use a timeout to ensure it doesn't hang if the script expects input or runs forever
        result = subprocess.run(
            [sys.executable, "-m", "{{ project_name }}.main"],
            capture_output=True,
            text=True,
            timeout=10,
            env={**os.environ, "ENV": "testing"}
        )

        if result.returncode == 0 and "Starting" in result.stdout:
            print("Smoke test: Success")
            return True
        else:
            print(f"Smoke test: Failed (Exit code: {result.returncode})")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            return False

    except Exception as e:
        print(f"Smoke test encountered exception: {e}")
        return False


if __name__ == "__main__":
    if not run_smoke_test():
        sys.exit(1)
