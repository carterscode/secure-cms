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
        libsnappy-dev \  # Added for python-snappy
        pkg-config \
        gcc \
        g++ \
        libpq-dev \
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

# Development stage
FROM python-base as development
ENV FASTAPI_ENV=development
ENV PYTHONPATH=/app

# Install runtime dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libsnappy1v5 \
        libpq5 \
        libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Copy poetry installation from builder
COPY --from=builder-base ${POETRY_VENV} ${POETRY_VENV}
ENV PATH="${PATH}:${POETRY_VENV}/bin"

WORKDIR /app
COPY --from=builder-base /app/poetry.lock /app/pyproject.toml ./

# Copy application code
COPY . .

# Install dependencies
RUN poetry install --no-interaction

CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production stage
FROM python-base as production
ENV FASTAPI_ENV=production
ENV PYTHONPATH=/app

# Install runtime dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libsnappy1v5 \
        libpq5 \
        libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Copy poetry installation from builder
COPY --from=builder-base ${POETRY_VENV} ${POETRY_VENV}
ENV PATH="${PATH}:${POETRY_VENV}/bin"

WORKDIR /app
COPY --from=builder-base /app/poetry.lock /app/pyproject.toml ./

# Copy application code
COPY . .

# Install dependencies
RUN poetry install --no-interaction --no-dev

CMD ["poetry", "run", "gunicorn", "app.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
