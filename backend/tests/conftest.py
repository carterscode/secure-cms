# backend/tests/conftest.py
import os
import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Set test environment before imports
os.environ.update({
    "TESTING": "true",
    "DATABASE_URL": "sqlite:///:memory:",
    "SECRET_KEY": "test-secret-key",
    "BACKEND_CORS_ORIGINS": '["http://localhost:3000","http://localhost:8000"]'
})

from app.db.base import Base
from app.db.session import get_db
from app.main import app

def get_test_db_url() -> str:
    """Get test database URL."""
    return "sqlite:///:memory:"

@pytest.fixture(scope="session")
def test_engine():
    """Create test engine."""
    engine = create_engine(
        get_test_db_url(),
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(test_engine: Generator) -> Generator:
    """Create test database session."""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(autocommit=False, autoflush=False, bind=connection)()

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db_session: Generator) -> Generator:
    """Create test client."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()

@pytest.fixture(autouse=True)
def _init_db(test_engine):
    """Ensure database is initialized for each test."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)
