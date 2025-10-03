# API.md

## Overview
FastAPI service with a health check, root info, and an in-memory Items resource.

**Base URL:** `http://localhost:8000`

---

## Root

**GET /** — Returns basic API metadata.

**Response 200**
    {
      "app": "FastAPI CI Demo",
      "version": "0.1.0",
      "health": "/health",
      "docs": "/docs",
      "redoc": "/redoc"
    }

---

## Health

**GET /health** — Simple liveness probe.

**Response 200**
    { "status": "ok" }

---

## Items

### Create Item
**POST /items/**

**Request body**
    {
      "name": "ball",
      "description": "red"
    }

**Response 201**
    {
      "id": 1,
      "name": "ball",
      "description": "red"
    }

**Example**
    curl -sS -X POST http://localhost:8000/items/ \
      -H "content-type: application/json" \
      -d '{"name":"ball","description":"red"}'

### List Items
**GET /items/**

**Response 200**
    [
      { "id": 1, "name": "ball", "description": "red" }
    ]

**Example**
    curl -sS http://localhost:8000/items/

### Get Item by ID
**GET /items/{item_id}**

**Path params**
- `item_id` (integer, ≥ 1)

**Response 200**
    { "id": 1, "name": "ball", "description": "red" }

**Response 404**
    { "detail": "Item not found" }

**Example**
    curl -sS http://localhost:8000/items/1
