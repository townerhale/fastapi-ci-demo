# tests/integration/test_item_api.py
from __future__ import annotations

from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.item import Item as ItemORM


def test_health_ok(client: TestClient) -> None:
    """`GET /health` returns 200 and the expected payload."""
    resp = client.get("/health")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json() == {"status": "ok"}


def test_create_item_persists(client: TestClient, db_session: Session) -> None:
    """
    `POST /items/` creates an item in the real database.

    After creating via the API, query the DB directly with `db_session`
    to verify the row was actually inserted and the data matches.
    """
    payload = {"name": "ball", "description": "red"}

    # Create via API
    resp = client.post("/items/", json=payload)
    assert resp.status_code == status.HTTP_201_CREATED
    body = resp.json()
    assert body["name"] == payload["name"]
    assert body["description"] == payload["description"]
    assert isinstance(body["id"], int) and body["id"] > 0

    # Verify directly in the DB
    created_id = body["id"]
    row = db_session.get(ItemORM, created_id)
    assert row is not None, "Row should exist in the database"
    assert row.name == payload["name"]
    assert row.description == payload["description"]

    # As an additional check, ensure it's discoverable via a SELECT
    one = db_session.execute(
        select(ItemORM).where(ItemORM.id == created_id)
    ).scalars().first()
    assert one is not None
    assert one.id == created_id


def test_get_missing_item_404(client: TestClient) -> None:
    """`GET /items/{id}` returns 404 for a non-existent record."""
    resp = client.get("/items/999999")
    assert resp.status_code == status.HTTP_404_NOT_FOUND
