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
    VENV_PATH="/opt/pysetup/.venv" \
    APP_DATA="/app/data"

ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

# Build stage
FROM python-base as builder-base

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR $PYSETUP_PATH
COPY poetry.lock pyproject.toml ./
RUN poetry install --no-dev --no-root

# Development stage
FROM builder-base as development
ENV FASTAPI_ENV=development

WORKDIR $PYSETUP_PATH
COPY . .
RUN poetry install

# Create data directory for SQLite
RUN mkdir -p $APP_DATA && \
    chmod 777 $APP_DATA

CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production stage
FROM python-base as production
ENV FASTAPI_ENV=production

# Copy poetry installation and dependencies
COPY --from=builder-base $POETRY_HOME $POETRY_HOME
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH

WORKDIR $PYSETUP_PATH
COPY . .

# Create data directory for SQLite and set permissions
RUN mkdir -p $APP_DATA && \
    chmod 777 $APP_DATA && \
    useradd -r -s /bin/false app && \
    chown -R app:app $PYSETUP_PATH $APP_DATA

USER app

CMD ["gunicorn", "app.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
