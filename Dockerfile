# --- builder stage (unchanged) ---
FROM python:3.11 AS builder
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# --- runtime stage ---
FROM python:3.11-slim AS runtime
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
RUN groupadd -g 10001 appuser && useradd -m -u 10001 -g 10001 appuser
WORKDIR /app

# Copy the venv from builder
COPY --from=builder /opt/venv /opt/venv

# Copy application code + alembic config/migrations into the image
COPY app ./app
COPY alembic.ini ./alembic.ini
COPY migrations ./migrations

USER appuser

# Default command (uvicorn)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
