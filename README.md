# FastAPI CircleCI Demo 

<!-- CircleCI status badge  -->
[![CircleCI](https://dl.circleci.com/status-badge/img/circleci/8HtgVYvZzHXTNWwbEA1e4V/JZaFfpd2Su7GMfzEDR7Z3D/tree/main.svg?style=svg&circle-token=CCIPRJ_HFt4jzZHswD2PzRy6ugq8x_14d59092a749a588aec66964a4e594e6e54e7c1c)](https://dl.circleci.com/status-badge/redirect/circleci/8HtgVYvZzHXTNWwbEA1e4V/JZaFfpd2Su7GMfzEDR7Z3D/tree/main)

A minimal FastAPI service to showcase a production-minded CI/CD workflow:
- Unit + integration tests with coverage
- Multi-stage Docker build
- Local orchestration with Docker Compose

It exposes a health check, a root info endpoint, and an in-memory `Items` resource so the focus stays on the pipeline.

---

## Tech Stack
- **FastAPI** (Starlette + Pydantic v2) • **Uvicorn**
- **SQLAlchemy** (engine/session scaffolding; DB mocked in tests)
- **Pytest** + **pytest-cov** (70%+ coverage gate)
- **Docker** (multi-stage) • **Docker Compose**
- **pydantic-settings** for env config

---

## Local Development Setup

> Prereqs: Python 3.11+, pip, virtualenv. (Docker Desktop optional but recommended.)

~~~bash
# 1) Clone & venv
git clone https://github.com/townerhale/fastapi-ci-demo.git
cd fastapi-ci-demo
python3 -m venv .venv && source .venv/bin/activate

# 2) Install deps
pip install -U pip
pip install -r requirements.txt

# 3) Environment
cp .env.example .env
# If you'll use docker-compose, set host to "db" in .env:
# DATABASE_URL=postgresql+psycopg2://postgres:postgres@db:5432/appdb

# 4) Run the app
uvicorn app.main:app --reload --port 8000

# 5) Smoke test
curl -s http://127.0.0.1:8000/health
~~~

---

## Build & Run with Docker

### Option A — Plain Docker

~~~bash
# Build
docker build -t fastapi-ci-demo:local .

# Run
docker run --rm -p 8000:8000 fastapi-ci-demo:local

# Check
curl -s http://127.0.0.1:8000/health
~~~

Validate the build with the helper script:

~~~bash
./tests/test_docker_build.sh
~~~

### Option B — Docker Compose (app + Postgres)

Compose reads **.env** in the repo root. Ensure `DATABASE_URL` uses host **db**.

~~~bash
docker compose up -d
curl -s http://127.0.0.1:8000/health

# Logs / Stop
docker compose logs -f app
docker compose down
~~~

---

## Running the Test Suite

`pytest.ini` discovers tests and enforces ≥70% coverage (excludes `__init__.py` via `.coveragerc`).

~~~bash
source .venv/bin/activate
pytest
~~~

---

## API Quick Reference

- **GET** `/health` → `{"status":"ok"}`
- **GET** `/` → basic API metadata
- **POST** `/items/` → create in-memory item (`{"name":"...","description":"..."}`)
- **GET** `/items/` → list items
- **GET** `/items/{id}` → fetch by id (404 if missing)

See `API.md` for examples.

---

## Environment Variables

- `DATABASE_URL` — SQLAlchemy connection string  
  Example (local dev): `postgresql+psycopg2://postgres:postgres@localhost:5432/appdb`  
  Example (compose):   `postgresql+psycopg2://postgres:postgres@db:5432/appdb`

> Commit `.env.example`, do **not** commit `.env` (ignored).

---

## CI/CD Notes (Preview)

- Run tests with coverage (DB mocked)
- Build Docker image (multi-stage, cache-friendly)
- Future: OIDC to AWS → push to **ECR**
- Future: publish a deploy manifest to **S3**

---

## Troubleshooting

- Port 8000 busy → free the port or change `--port`.
- Docker not running → open Docker Desktop; `docker info` should succeed.
- `.env` vs `.env.example` → copy example to `.env`; don’t commit secrets.
# Updated README
# Testing feature branch workflow
