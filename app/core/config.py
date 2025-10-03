"""Application configuration.

Centralizes environment variable parsing using pydantic-settings. Only the
`DATABASE_URL` is required for this exercise; extra env vars (e.g., POSTGRES_*)
are ignored to play nicely with docker-compose.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables."""

    DATABASE_URL: str = Field(
        default="postgresql+psycopg2://postgres:postgres@localhost:5432/appdb",
        description="SQLAlchemy URL for the primary database",
    )

    # Allow extra env vars so docker-compose's POSTGRES_* don't break settings load
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance.

    Returns:
        Settings: Parsed and validated configuration.
    """
    return Settings()
