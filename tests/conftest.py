# tests/conftest.py
from __future__ import annotations

import os
from typing import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine, Connection
from sqlalchemy.orm import Session, sessionmaker

from alembic import command
from alembic.config import Config

from app.main import app
from app.core.database import get_db


# -----------------------------------------------------------------------------
# Session-scoped engine + Alembic migrations
# -----------------------------------------------------------------------------
@pytest.fixture(scope="session")
def db_engine() -> Iterator[Engine]:
    """
    Create a SQLAlchemy Engine for the *test* database, run Alembic migrations
    up to 'head' before any tests, and tear down afterwards.

    The database URL is read from:
      1) TEST_DATABASE_URL  (preferred)
      2) DATABASE_URL       (fallback)

    Example (host machine):
      export TEST_DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5432/appdb"
    """
    url = os.getenv("TEST_DATABASE_URL") or os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError(
            "Set TEST_DATABASE_URL (preferred) or DATABASE_URL for the test DB, "
            "e.g. postgresql+psycopg2://user:pass@localhost:5432/appdb"
        )

    # Create engine (no pool pre-ping—fail fast in tests if DB is unreachable)
    engine = create_engine(url, future=True)

    # Run Alembic migrations up to head so the schema exists
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", url)
    alembic_cfg.set_main_option("script_location", "migrations")
    command.upgrade(alembic_cfg, "head")

    try:
        yield engine
    finally:
        # Prefer a clean database for subsequent runs: downgrade to base.
        # (If you prefer to retain data between runs, comment this out.)
        try:
            command.downgrade(alembic_cfg, "base")
        finally:
            engine.dispose()


# -----------------------------------------------------------------------------
# Function-scoped transaction/session with automatic rollback
# -----------------------------------------------------------------------------
@pytest.fixture(scope="function")
def db_session(db_engine: Engine) -> Iterator[Session]:
    """
    Provide a real SQLAlchemy Session bound to a single transaction per test.
    The outer transaction is rolled back at the end of the test to ensure
    isolation and a clean slate (no data leakage between tests).
    """
    # Dedicated DBAPI connection for this test
    connection: Connection = db_engine.connect()

    # Start an explicit outer transaction
    outer_tx = connection.begin()

    # Session bound to the same connection
    SessionLocal = sessionmaker(
        bind=connection, autoflush=False, expire_on_commit=False, future=True
    )
    session: Session = SessionLocal()

    # Start a SAVEPOINT (nested transaction) so that flushes/commits inside
    # the app code won't end our outer transaction. This mirrors the common
    # SQLAlchemy testing pattern.
    nested_tx = session.begin_nested()

    # When the nested transaction ends (e.g., session commits), start a new one
    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(sess: Session, trans) -> None:  # type: ignore[no-redef]
        # Re-open a savepoint if the outer transaction is still active
        if trans.nested and not trans._parent.nested:  # type: ignore[attr-defined]
            sess.begin_nested()

    # Optional: relax constraints to avoid ordering issues with FK checks
    try:
        connection.execute(text("SET CONSTRAINTS ALL DEFERRED"))
    except Exception:
        # Not all backends support this; ignore if it fails.
        pass

    try:
        yield session
    finally:
        # Clean up in reverse order
        session.close()
        # Roll back the outer transaction, wiping all test data
        outer_tx.rollback()
        connection.close()


# -----------------------------------------------------------------------------
# FastAPI TestClient that uses the real db_session via dependency override
# -----------------------------------------------------------------------------
@pytest.fixture(scope="function")
def client(db_session: Session) -> Iterator[TestClient]:
    """
    A TestClient that wires FastAPI's get_db dependency to the per-test
    transaction-backed session provided by db_session above.
    """

    def _get_db():
        try:
            yield db_session
        finally:
            # Session lifetime is managed by the db_session fixture
            pass

    # Override the app's dependency to use our test session
    app.dependency_overrides[get_db] = _get_db

    try:
        with TestClient(app) as c:
            yield c
    finally:
        # Restore original dependency after each test
        app.dependency_overrides.pop(get_db, None)
