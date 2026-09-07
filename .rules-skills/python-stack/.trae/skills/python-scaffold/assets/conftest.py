import pytest
import os


@pytest.fixture(autouse=True)
def setup_test_env():
    """Set up test environment variables."""
    os.environ["ENV"] = "testing"
    yield
    # Cleanup if needed
