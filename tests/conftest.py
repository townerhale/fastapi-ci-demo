# tests/conftest.py
from __future__ import annotations

import contextlib
from typing import Any, Dict, Iterable, Iterator, List, Optional

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import get_db
from app.models.item import Item as ItemORM


# ----- Minimal SQLAlchemy-like result wrapper ---------------------------------
class _Result:
    """Mimic SQLAlchemy Result for .scalars().all() used by read_items."""

    def __init__(self, items: Iterable[Any]) -> None:
        self._items = list(items)

    # SQLAlchemy's Result.scalars() returns a ScalarResult, but we can just
    # return self and implement .all() on the same object for our use case.
    def scalars(self) -> "._Result":
        return self

    def all(self) -> List[Any]:
        return list(self._items)


# ----- In-memory "Session" mock -----------------------------------------------
class _MockDB:
    """
    Tiny in-memory stand-in for SQLAlchemy Session.
    Supports the subset of methods our API uses:
      - add(), commit(), refresh()
      - get(Model, pk)
      - execute(select(Model)) -> .scalars().all()
    """

    def __init__(self) -> None:
        self._store: Dict[int, ItemORM] = {}
        self._pk = 0
        self._pending: Optional[ItemORM] = None

    # --- Session API used in create_item --------------------------------------
    def add(self, obj: ItemORM) -> None:
        # Defer assigning an ID until commit() (like DB would)
        self._pending = obj

    def commit(self) -> None:
        if self._pending is not None:
            self._pk += 1
            obj = self._pending
            # Assign an ID to mimic DB identity
            obj.id = self._pk  # type: ignore[attr-defined]
            self._store[obj.id] = obj  # type: ignore[index]
            self._pending = None

    def refresh(self, obj: ItemORM) -> None:
        # No-op for the mock; in real DB this would reload defaults/server values
        return

    # --- Session API used in read_item ----------------------------------------
    def get(self, model: Any, pk: int) -> Optional[ItemORM]:
        # Model arg is ignored; we only have Item
        return self._store.get(pk)

    # --- Session API used in read_items ---------------------------------------
    def execute(self, _stmt: Any) -> _Result:
        # We ignore the actual SQLAlchemy select() object and just return all
        # items as if "SELECT * FROM items" had been executed.
        return _Result(self._store.values())

    # Optional: make it safe for "with" blocks if ever used
    def close(self) -> None:
        return

    def __enter__(self) -> "_MockDB":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()


# ----- Fixtures ----------------------------------------------------------------
@pytest.fixture(scope="session")
def client() -> Iterator[TestClient]:
    """
    Session-scoped TestClient for the FastAPI app.
    (Fast to reuse across tests.)
    """
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def override_db_dependency() -> Iterator[None]:
    """
    Automatically override get_db with the in-memory _MockDB for all tests.
    Ensures tests don't need a real Postgres connection.
    """
    mock_db = _MockDB()

    def _get_db_override() -> Iterator[_MockDB]:
        try:
            yield mock_db  # <- FastAPI receives the actual "session"-like object
        finally:
            mock_db.close()

    # Apply the override
    app.dependency_overrides[get_db] = _get_db_override
    try:
        yield
    finally:
        # Restore original dependency after each test
        app.dependency_overrides.pop(get_db, None)
