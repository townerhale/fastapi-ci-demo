"""
Integration tests for the FastAPI app using the TestClient fixture and the
mocked DB fixture from tests/conftest.py.

Covers:
1) GET /health -> 200 and expected JSON.
2) POST /items/ -> 201 and created item payload.
3) GET /items/{id} for a non-existent id -> 404.
"""

from __future__ import annotations

import pytest

# Reach into the in-memory router store to keep tests isolated
from app.api import item_router as items_mod


@pytest.fixture(autouse=True)
def reset_items_store():
    """
    Automatically reset the in-memory items store before and after each test
    so tests don't affect each other.
    """
    items_mod._items.clear()
    items_mod._next_id = 1
    yield
    items_mod._items.clear()
    items_mod._next_id = 1


def test_health_ok(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_create_item_201(client):
    payload = {"name": "ball", "description": "red"}
    resp = client.post("/items/", json=payload)
    assert resp.status_code == 201

    data = resp.json()
    assert data["id"] == 1  # first item after reset
    assert data["name"] == payload["name"]
    assert data["description"] == payload["description"]


def test_get_nonexistent_item_404(client):
    resp = client.get("/items/999")
    assert resp.status_code == 404
    assert resp.json() == {"detail": "Item not found"}