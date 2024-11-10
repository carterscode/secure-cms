# backend/Dockerfile
FROM python:3.11-slim as python-base

# Python build stage
FROM python-base as builder-base

# Install system build dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
        pkg-config \
        python3-dev \
        libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Install poetry
ENV POETRY_VERSION=1.8.4
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VENV=/opt/poetry-venv
ENV POETRY_CACHE_DIR=/opt/.cache

# Install poetry separated from system interpreter
RUN python3 -m venv $POETRY_VENV \
    && $POETRY_VENV/bin/pip install -U pip setuptools \
    && $POETRY_VENV/bin/pip install poetry==${POETRY_VERSION}

# Add `poetry` to PATH
ENV PATH="${PATH}:${POETRY_VENV}/bin"

WORKDIR /app

# Install dependencies
COPY poetry.lock pyproject.toml ./
RUN poetry install --no-interaction --no-cache --no-root

# Production stage
FROM python-base as production
ENV FASTAPI_ENV=production
ENV PYTHONPATH=/app

# Install runtime dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Copy poetry installation from builder
COPY --from=builder-base ${POETRY_VENV} ${POETRY_VENV}
ENV PATH="${PATH}:${POETRY_VENV}/bin"

WORKDIR /app

# Create data directory for SQLite
RUN mkdir -p /app/data && chown -R nobody:nogroup /app/data

# Copy application code
COPY --chown=nobody:nogroup . .

# Install dependencies
RUN poetry install --no-interaction --no-dev

# Switch to non-root user
USER nobody

CMD ["poetry", "run", "gunicorn", "app.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
