"""Unit tests for configuration and schema validation."""

from app.core.config import get_settings
from app.schemas.item import ItemCreate
import pytest


def test_settings_loads_database_url() -> None:
    """Settings loads and exposes a DATABASE_URL string."""
    url = get_settings().DATABASE_URL
    assert isinstance(url, str)
    assert "://" in url


@pytest.mark.parametrize(
    "payload",
    [
        {"name": "ball", "description": "red"},
        {"name": "book", "description": "paper"},
    ],
)
def test_itemcreate_validates(payload) -> None:
    """ItemCreate validates the required fields."""
    obj = ItemCreate(**payload)
    assert obj.name
    assert obj.description
