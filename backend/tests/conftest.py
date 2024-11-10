# backend/tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import Settings, settings
from app.db.session import Base, get_db
from app.main import app

# Override settings for testing
def get_settings_override():
    return Settings(
        TESTING=True,
        DEBUG=True,
        POSTGRES_DB="test_db",
        POSTGRES_USER="test_user",
        POSTGRES_PASSWORD="test_pass",
        POSTGRES_SERVER="localhost",
        SECRET_KEY="test_secret_key",
    )

@pytest.fixture(scope="session")
def test_settings():
    return get_settings_override()

@pytest.fixture(scope="session")
def db_engine(test_settings):
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(db_engine):
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture(scope="function")
def client(db_session, test_settings):
    app.dependency_overrides[get_db] = lambda: db_session
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

@pytest.fixture
def test_password() -> str:
    return "Test1234!"

@pytest.fixture
def test_user(db_session, test_password):
    from app.models.models import User
    from app.core.security import SecurityUtils
    
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=SecurityUtils.get_password_hash(test_password),
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user
