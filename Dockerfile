# Dockerfile
# Multi-stage build for FastAPI app with best practices:
# - Builder stage: install deps into a virtualenv (cache-friendly)
# - Runtime stage: slim image, non-root user, minimal footprint

########################
# Stage 1: builder
########################
FROM python:3.11 AS builder

# Keep things deterministic & fast
ENV VENV=/opt/venv \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Create virtualenv and put it on PATH
RUN python -m venv "${VENV}"
ENV PATH="${VENV}/bin:${PATH}"

WORKDIR /app

# --- Layer caching critical step ---
# Copy only requirements first; if this file hasn't changed, the layer is reused.
COPY requirements.txt ./

# Install dependencies into the venv
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

########################
# Stage 2: runtime
########################
FROM python:3.11-slim AS runtime

# Environment
ENV VENV=/opt/venv \
    PATH="/opt/venv/bin:${PATH}" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Create a non-root user for security
RUN groupadd -g 10001 appuser && \
    useradd -m -u 10001 -g appuser appuser

# Workdir for the app
WORKDIR /app

# Bring in the virtualenv from the builder
COPY --from=builder /opt/venv /opt/venv

# Copy application code (respects .dockerignore)
COPY app ./app

# Network & runtime config
EXPOSE 8000

# Drop privileges
USER appuser

# Default command: run the API with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
