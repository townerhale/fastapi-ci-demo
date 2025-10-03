"""
Shared pytest fixtures for the FastAPI app.

- `client` (session-scoped): a FastAPI TestClient for making HTTP requests in tests.
- `fake_db` (session-scoped): overrides the `get_db` dependency to use a simple
  fake session object so tests can run without a real database connection.
"""

from __future__ import annotations

from typing import Generator
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import get_db


class FakeSession:
    """
    Minimal stand-in for a DB session.
    Extend this with methods your tests need, e.g. add(), commit(), query(), etc.
    For now, it’s just a placeholder to prove dependency overrides work.
    """
    def __init__(self) -> None:
        self.closed = False

    # Optional no-op methods to mimic a SQLAlchemy Session API shape
    def add(self, *_args, **_kwargs):  # pragma: no cover - only for compatibility
        return None

    def commit(self):  # pragma: no cover
        return None

    def refresh(self, *_args, **_kwargs):  # pragma: no cover
        return None

    def close(self) -> None:
        self.closed = True


@pytest.fixture(scope="session")
def fake_db() -> Generator[FakeSession, None, None]:
    """
    Session-scoped fixture that:
    - creates a FakeSession,
    - overrides FastAPI's get_db dependency to yield that fake,
    - returns the FakeSession to tests (if they want to inspect/extend it),
    - and finally removes the override.

    This lets API tests run without a real Postgres connection.
    """
    fake = FakeSession()

    def _override_get_db() -> Generator[FakeSession, None, None]:
        try:
            yield fake
        finally:
            # We purposely don't close here so the same FakeSession is shared
            # for the whole session. We'll close in the teardown below.
            pass

    # Apply the override before tests run
    app.dependency_overrides[get_db] = _override_get_db
    try:
        yield fake
    finally:
        # Remove override & clean up the fake session
        app.dependency_overrides.pop(get_db, None)
        fake.close()


@pytest.fixture(scope="session")
def client(fake_db: FakeSession) -> Generator[TestClient, None, None]:
    """
    Session-scoped TestClient for the app.
    Depends on `fake_db` so the DB override is in place before the client starts.
    """
    with TestClient(app) as c:
        yield c