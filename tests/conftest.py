"""Pytest fixtures for API and configuration tests.

Provides:
  * `client` - a session-scoped FastAPI TestClient.
  * `mock_db` - a simple object used to override the DB dependency during tests.
"""

from typing import Generator

import pytest
from fastapi.testclient import TestClient

from app.core.database import get_db
from app.main import app


class _MockDB:
    """Very small stand-in for a DB session used by dependency override."""

    def close(self) -> None:
        """No-op close to mirror SQLAlchemy Session API."""
        return None


@pytest.fixture(scope="session")
def client() -> Generator[TestClient, None, None]:
    """Provide a session-scoped TestClient for API tests.

    Yields:
        TestClient: HTTP client bound to the FastAPI app.
    """
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def mock_db(monkeypatch: pytest.MonkeyPatch) -> Generator[_MockDB, None, None]:
    """Override the `get_db` dependency globally so endpoints don't touch a real DB.

    Args:
        monkeypatch: Pytest helper for temporary attribute patching.

    Yields:
        _MockDB: A minimal object that has a `close()` method.
    """

    def _fake_get_db():
        db = _MockDB()
        try:
            yield db
        finally:
            db.close()

    # Apply override
    app.dependency_overrides[get_db] = _fake_get_db
    try:
        yield _MockDB()
    finally:
        # Remove override after each test
        app.dependency_overrides.pop(get_db, None)
