# Multi-stage build for optimized image size
FROM python:3.12-slim as builder

WORKDIR /app

# Install curl and uv
RUN apt-get update && apt-get install -y curl && \
    curl -LsSf https://astral.sh/uv/install.sh | sh && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
ENV PATH="/root/.local/bin:$PATH"

# Copy project files
COPY pyproject.toml uv.lock* README.md ./

# Build dependencies
RUN uv sync --frozen --no-dev


# Runtime stage
FROM python:3.12-slim

WORKDIR /app

# Install uv and postgresql-client for runtime
RUN apt-get update && apt-get install -y curl postgresql-client && \
    curl -LsSf https://astral.sh/uv/install.sh | sh && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
ENV PATH="/root/.local/bin:$PATH"

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Copy project files
COPY pyproject.toml README.md ./
COPY alembic.ini ./

# Copy application code
COPY src/ ./src/
COPY alembic/ ./alembic/
COPY scripts/ ./scripts/
COPY tests/ ./tests/

# Create non-root user and install uv for that user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app && \
    cp -r /root/.local /home/appuser/.local && \
    chown -R appuser:appuser /home/appuser/.local

USER appuser
ENV PATH="/home/appuser/.local/bin:$PATH"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
