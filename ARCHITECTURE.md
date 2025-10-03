# ARCHITECTURE.md

## Overview
This repository contains a minimal FastAPI service designed to demonstrate CI/CD best practices. It focuses on clean structure, testability, and containerization (multi-stage Docker builds and local orchestration via Docker Compose).

---

## Repository Layout (high level)
- `app/` – Application code (FastAPI app, routers, schemas, config, DB scaffolding)
- `tests/` – Unit & integration tests, pytest fixtures, build checks
- `scripts/` – Reserved for helper scripts and utilities (optional, can be added later)
- Root files – Project entrypoints and infrastructure (Dockerfile, docker-compose, Makefile, etc.)

---

## app/ (application code)

**Purpose:** Encapsulates all runtime code for the FastAPI service. The structure is intentionally simple and production-leaning.

- `app/main.py`  
  FastAPI application entrypoint. Creates the `FastAPI()` instance, configures permissive CORS for local/dev, exposes:
  - `GET /health` – Liveness probe (`{"status": "ok"}`)
  - `GET /` – API metadata (title, version, docs links)
  - Includes the Items router from `app/api/item_router.py`.

- `app/api/`  
  Routers (HTTP endpoints) grouped by domain.
  - `app/api/item_router.py` – In-memory CRUD surface for `Item`:
    - `POST /items/` – Create item
    - `GET /items/` – List items
    - `GET /items/{id}` – Get item by id  
    This keeps the pipeline demo fast and DB-independent; later you can swap to real persistence.

- `app/schemas/`  
  Pydantic models for request/response contracts.
  - `app/schemas/item.py` – `ItemCreate` (input) and `Item` (output)

- `app/models/`  
  ORM models (SQLAlchemy) live here when persistence is added.
  - `app/models/item.py` – Placeholder for a future `Item` ORM model (not required for the in-memory demo).

- `app/core/`  
  Cross-cutting application concerns.
  - `app/core/config.py` – Configuration via `pydantic-settings`; exposes `get_settings()` for safe, cached access to `DATABASE_URL`. Ignores unknown env vars so docker-compose’s `POSTGRES_*` don’t break parsing.
  - `app/core/database.py` – SQLAlchemy engine/session scaffolding and `get_db()` FastAPI dependency. Present for realism even though the current Items API uses an in-memory store.

---

## tests/ (test suite)

**Purpose:** Validate behavior quickly and deterministically; enforce coverage thresholds.

- `tests/conftest.py`  
  Pytest fixtures:
  - `client` – Session-scoped `fastapi.testclient.TestClient` for HTTP calls.
  - `mock_db` – Overrides the app’s `get_db()` dependency so tests don’t require a real DB.

- `tests/unit/`  
  Unit tests for small, isolated pieces.
  - `tests/unit/test_core_components.py` – Ensures settings load correctly and `ItemCreate` schema validates inputs.

- `tests/integration/`  
  End-to-end tests hitting HTTP endpoints.
  - `tests/integration/test_item_api.py` – Tests `/health`, `POST /items/`, and 404 on missing item.

- `tests/test_docker_build.sh`  
  Simple shell check to ensure the Docker image builds successfully (used locally or in CI).

- **Test config files**
  - `pytest.ini` – Test discovery and coverage settings (enforces minimum coverage).
  - `.coveragerc` – Excludes `__init__.py` from coverage (if present).
  - `pyproject.toml` – `interrogate` configuration enforcing docstring coverage (≥ 80%).

---

## scripts/ (optional)
A home for local tooling (e.g., DB migration helpers, data seeding, one-off maintenance scripts).  
_This folder is created by the project plan; you can add scripts here over time. For now, the Docker build check lives under `tests/`._

---

## Root Files (tooling & infra)

- `Dockerfile`  
  Multi-stage build:
  - **Stage 1 (builder):** Creates a Python virtualenv and installs dependencies using only `requirements.txt` first to maximize Docker layer caching.
  - **Stage 2 (runtime):** Uses `python:3.11-slim`, creates a non-root user, copies the virtualenv and app code, and starts with `uvicorn app.main:app`.

- `docker-compose.yml`  
  Local orchestration with two services:
  - `app` – Builds from the local `Dockerfile`, exposes `8000:8000`, and reads env vars from `.env`.
  - `db` – `postgres:15-alpine`, configured via `POSTGRES_*` variables. Health-checked before `app` starts.

- `Makefile`  
  Common developer commands:
  - `make install` – Create venv and install dependencies
  - `make test` – Run pytest with coverage
  - `make docker-build` – Build the Docker image (`circleci-field-app`)
  - `make run` – Start via `run.py` using your venv Python

- `run.py`  
  Convenience script to run `uvicorn app.main:app` locally with the right host/port.

- `requirements.txt`  
  Python dependencies (FastAPI, Uvicorn, SQLAlchemy, psycopg2-binary, pytest stack, httpx, pydantic-settings).

- `README.md`  
  Project description, local setup, Docker usage, and testing instructions.

- `API.md`  
  Human-readable endpoint reference (paths, example requests/responses).

- `.env.example` / `.env`  
  Environment variables. Commit the example (safe). Do **not** commit `.env` (ignored via `.gitignore`).  
  - Local dev: `DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/appdb`
  - Compose:   `DATABASE_URL=postgresql+psycopg2://postgres:postgres@db:5432/appdb`

- `.gitignore`  
  Ignores Python caches, virtualenvs, IDE files, logs, local `.env`, etc.

---

## Request Lifecycle (at a glance)
1. Client -> `uvicorn` -> FastAPI `app`.
2. Routing -> `app/api/item_router.py`.
3. Pydantic validation:
   - Request bodies via `ItemCreate`
   - Responses via `Item`
4. Business logic (currently in-memory store for speed).
5. Response returned; no DB round-trip required for the demo.

---

## Configuration & Dependencies
- Configuration is centralized in `app/core/config.py` using `pydantic-settings`.
- Database resources (engine/session) are defined in `app/core/database.py` and injected via `get_db()` when persistence is added.
- Tests override `get_db()` to keep integration tests hermetic and fast.

---

## Containerization & Local Orchestration
- **Dockerfile:** Multi-stage to keep the final image small and build fast via layer caching.
- **Docker Compose:** Brings up `app` and `db` together, waits for Postgres health, and exposes the API on `localhost:8000`.

---

## Testing Strategy
- **Unit tests** focus on schemas and configuration.
- **Integration tests** exercise real HTTP endpoints using TestClient.
- **Coverage gate** (≥ 70%) enforced by `pytest.ini`.
- **Docstring coverage** (≥ 80%) enforced by `interrogate` (see `pyproject.toml`).

---

## Extensibility (future)
- Swap in real SQLAlchemy models under `app/models/` and wire the router to use `get_db()`.
- Introduce migrations (e.g., Alembic) and add migration scripts under `scripts/`.
- Extend CI to:
  - Run tests + coverage
  - Build/push image to ECR (OIDC auth)
  - Publish a deployment manifest to S3
- Add linting (`ruff`) and formatting (`black`) checks as CI jobs.

---
