# backend/Dockerfile
FROM python:3.11-slim as python-base

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.8.2 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

# Build stage
FROM python-base as builder-base

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    libpq-dev \
    libsnappy-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR $PYSETUP_PATH
COPY poetry.lock pyproject.toml ./

# Install runtime dependencies
RUN poetry install --no-dev --no-root

# Development stage
FROM builder-base as development
ENV FASTAPI_ENV=development

WORKDIR $PYSETUP_PATH
COPY . .
RUN poetry install

CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production stage
FROM python-base as production
ENV FASTAPI_ENV=production

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libsnappy1v5 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder-base $VENV_PATH $VENV_PATH
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH

WORKDIR $PYSETUP_PATH
COPY . .

RUN useradd -r -s /bin/false app && \
    chown -R app:app $PYSETUP_PATH

USER app

CMD ["gunicorn", "app.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
