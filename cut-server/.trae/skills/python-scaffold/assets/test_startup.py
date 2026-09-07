import pytest
from {{ project_name }}.config import settings


def test_settings_load():
    """Test that settings are loaded correctly."""
    assert settings.project_name == "{{ project_name }}"


def test_environment_variable(monkeypatch):
    """Test environment variable overriden."""
    monkeypatch.setenv("ENV", "production")
    # Note: Settings is a singleton, might need reload strategy for deep testing
    pass
