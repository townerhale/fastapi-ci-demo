from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import the module, then access router explicitly
from app.api import item_router as item_router_module

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
    return {"status": "ok"}


@app.get("/", tags=["meta"])
def root() -> dict:
    return {
        "app": app.title,
        "version": app.version,
        "health": "/health",
        "docs": "/docs",
        "redoc": "/redoc",
    }


# Mount item routes explicitly via module.attribute
app.include_router(item_router_module.router)
