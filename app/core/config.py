from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Only variable the app actually needs today
    DATABASE_URL: str = Field(
        default="postgresql+psycopg2://postgres:postgres@localhost:5432/appdb",
        description="SQLAlchemy URL for the primary database",
    )

    # Allow extra env vars so docker-compose's POSTGRES_* don't break settings load
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # <- important: ignore unknown env vars
        case_sensitive=True,  # keep env var names case-sensitive
    )


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance (safe to call anywhere)."""
    return Settings()
