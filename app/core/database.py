# app/core/database.py
"""Database scaffolding (SQLAlchemy engine/session).

Creates a SQLAlchemy Engine from the configured DATABASE_URL, a SessionLocal
factory for per-request sessions, and a FastAPI dependency (`get_db`) that
yields a session and guarantees cleanup.

This file is production-leaning and works with SQLAlchemy 2.x.
"""

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import get_settings

# Load settings once (cached in get_settings)
settings = get_settings()

# Create the SQLAlchemy Engine (sync) using the configured DATABASE_URL
# Example: postgresql+psycopg2://postgres:postgres@localhost:5432/appdb
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # helps avoid stale (broken) connections
    future=True,         # use SQLAlchemy 2.x style
)

# Declarative base for ORM models (you'll subclass this for real tables)
Base = declarative_base()

# Session factory: use per-request sessions via get_db()
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    future=True,  # SQLAlchemy 2.x style
)


def get_db() -> Generator:
    """FastAPI dependency that yields a DB session and ensures proper cleanup.

    Yields:
        sqlalchemy.orm.Session: A database session bound to `engine`.

    Ensures:
        The session is closed after the endpoint handler returns.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
