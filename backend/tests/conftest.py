# backend/tests/conftest.py
import os
import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Set environment variables first
os.environ.update({
    "TESTING": "true",
    "DATABASE_URL": "sqlite:///:memory:",
    "SECRET_KEY": "test-secret-key",
    "BACKEND_CORS_ORIGINS": '["http://localhost:3000","http://localhost:8000"]'
})

# Import Base before any models
from app.db.base import Base

# Then import other dependencies
from app.db.session import get_db
from app.main import app
from app.models.models import User, Contact, Tag

@pytest.fixture(scope="session")
def engine():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Enable foreign keys for SQLite
    def _enable_foreign_keys(connection, connection_record):
        connection.execute('PRAGMA foreign_keys=ON')
    
    event.listen(engine, 'connect', _enable_foreign_keys)
    
    # Create all tables
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    return engine

@pytest.fixture(scope="function")
def db_session(engine) -> Generator[Session, None, None]:
    connection = engine.connect()
    transaction = connection.begin()
    session = sessionmaker(autocommit=False, autoflush=False, bind=connection)()

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
