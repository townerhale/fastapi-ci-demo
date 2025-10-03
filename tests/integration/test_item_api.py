"""Integration tests for the public HTTP API."""

from fastapi.testclient import TestClient


def test_health_ok(client: TestClient) -> None:
    """`GET /health` returns 200 and the expected JSON payload."""
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_create_item_201(client: TestClient) -> None:
    """`POST /items/` creates an item and returns 201."""
    payload = {"name": "ball", "description": "red"}
    resp = client.post("/items/", json=payload)
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "ball"
    assert body["description"] == "red"
    assert isinstance(body["id"], int) and body["id"] >= 1


def test_get_missing_item_404(client: TestClient) -> None:
    """`GET /items/{id}` returns 404 for a non-existent item."""
    resp = client.get("/items/999999")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Item not found"
