# tests/unit/test_core_components.py
"""
Unit tests for core components:
1) Settings loader (app.core.config): ensures env overrides are respected and
   extra env vars (e.g., docker-compose POSTGRES_*) are ignored.
2) Pydantic schema (app.schemas.item.ItemCreate): validates input correctly.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.core.config import get_settings
from app.schemas.item import ItemCreate


def test_settings_loads_from_env_and_ignores_extras(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    - Set DATABASE_URL in the environment and verify get_settings() reads it.
    - Add an unrelated POSTGRES_* var to prove extra env vars are ignored.
    - Clear the lru_cache before/after to ensure a clean read.
    """
    test_url = "postgresql+psycopg2://user:pass@localhost:5432/testdb"

    # Arrange: set env vars
    monkeypatch.setenv("DATABASE_URL", test_url)
    monkeypatch.setenv("POSTGRES_USER", "ignored")  # should not break settings

    # Act: clear cache and read settings
    get_settings.cache_clear()
    settings = get_settings()

    # Assert: value comes from env; extra env var didn't cause errors
    assert settings.DATABASE_URL == test_url
    assert isinstance(settings.DATABASE_URL, str) and settings.DATABASE_URL

    # Cleanup: clear cache; remove env
    get_settings.cache_clear()
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("POSTGRES_USER", raising=False)


def test_itemcreate_valid_and_invalid_inputs() -> None:
    """
    - Accepts valid payload with required fields.
    - Raises ValidationError when required data is missing.
    """
    # Valid
    obj = ItemCreate(name="ball", description="red")
    assert obj.name == "ball"
    assert obj.description == "red"

    # Missing required field -> error
    with pytest.raises(ValidationError):
        ItemCreate(description="no-name")
