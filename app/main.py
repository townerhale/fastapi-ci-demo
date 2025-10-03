"""FastAPI application entrypoint.

Exposes a root info endpoint and a health check, and mounts the in-memory
Items router used for API integration tests and local development.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.item_router import router as item_router

app = FastAPI(
    title="FastAPI CI Demo",
    version="0.1.0",
    description="FastAPI service for CI/CD take-home exercise.",
)

# Permissive CORS for this exercise (allow everything)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["health"])
def health() -> dict:
    """Return a simple liveness probe payload.

    Returns:
        dict: JSON status object, e.g. {"status": "ok"}.
    """
    return {"status": "ok"}


@app.get("/", tags=["meta"])
def root() -> dict:
    """Return basic API metadata and helpful links.

    Returns:
        dict: Name, version, and paths to docs and health endpoints.
    """
    return {
        "app": app.title,
        "version": app.version,
        "health": "/health",
        "docs": "/docs",
        "redoc": "/redoc",
    }


# Mount the Items API router.
app.include_router(item_router)
