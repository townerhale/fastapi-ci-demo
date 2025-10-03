"""Database scaffolding (SQLAlchemy engine/session).

This module exposes an Engine, SessionLocal factory, declarative Base, and a
FastAPI dependency (`get_db`) for endpoint functions that need a DB session.
"""

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import get_settings

settings = get_settings()

# Create the SQLAlchemy Engine (sync) using the configured DATABASE_URL
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # helps avoid stale connections
    future=True,  # SQLAlchemy 2.x style
)

# Session factory
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    future=True,
)

# Base class for ORM models
Base = declarative_base()


def get_db() -> Generator:
    """Yield a database session and ensure proper cleanup.

    Yields:
        Session: A SQLAlchemy session bound to the configured engine.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
