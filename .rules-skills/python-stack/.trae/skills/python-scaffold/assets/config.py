import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings.
    """
    project_name: str = "{{ project_name }}"
    environment: str = os.getenv("ENV", "development")
    
    # Add your configuration fields here
    # Example:
    # api_key: str = "default_key"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
