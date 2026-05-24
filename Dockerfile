# syntax=docker/dockerfile:1
FROM python:3.11-slim

WORKDIR /app

# Prevent Python from writing pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install uv for fast dependency resolution
RUN pip install --no-cache-dir uv

# Copy dependency metadata first for layer caching
COPY pyproject.toml uv.lock ./

# Sync dependencies into a local venv (no dev packages)
RUN uv sync --no-dev

# Copy application code
COPY . .

# Ensure upload directory exists
RUN mkdir -p static/uploads

# Expose FastAPI port
EXPOSE 8000

# Run with uvicorn via uv run (uses the synced .venv)
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
