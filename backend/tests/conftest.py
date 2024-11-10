# backend/tests/conftest.py
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
from datetime import timedelta

from app.core.config import Settings
from app.db.session import get_db, Base
from app.main import app
from app.core.security import SecurityUtils

# Enable foreign key support for SQLite
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# Create test database
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_settings_override():
    """Override settings for testing."""
    return Settings(
        TESTING=True,
        DATABASE_URL=TEST_DATABASE_URL,
        SECRET_KEY="test_secret_key",
        TWO_FACTOR_AUTHENTICATION_ENABLED=False,
        ACCESS_TOKEN_EXPIRE_MINUTES=30
    )

@pytest.fixture(scope="session", autouse=True)
def override_settings():
    """Override settings for all tests."""
    app.dependency_overrides[Settings] = get_settings_override
    return get_settings_override()

@pytest.fixture(autouse=True)
def db():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db):
    """Create a test client."""
    def override_get_db():
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def test_password() -> str:
    """Test password."""
    return "Test1234!"

@pytest.fixture
def test_user(db, test_password):
    """Create a test user."""
    from app.models.models import User
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=SecurityUtils.get_password_hash(test_password),
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def auth_headers(test_user):
    """Create authentication headers."""
    settings = get_settings_override()
    access_token = SecurityUtils.create_access_token(
        data={"sub": test_user.email},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"Authorization": f"Bearer {access_token}"}

@pytest.fixture
def test_admin(db, test_password):
    """Create a test admin user."""
    from app.models.models import User
    admin = User(
        email="admin@example.com",
        username="admin",
        hashed_password=SecurityUtils.get_password_hash(test_password),
        is_active=True,
        is_admin=True
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin

@pytest.fixture
def admin_headers(test_admin):
    """Create admin authentication headers."""
    settings = get_settings_override()
    access_token = SecurityUtils.create_access_token(
        data={"sub": test_admin.email},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"Authorization": f"Bearer {access_token}"}

@pytest.fixture
def test_contact(db, test_user):
    """Create a test contact."""
    from app.models.models import Contact
    contact = Contact(
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        mobile_phone="1234567890",
        created_by=test_user.id
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact
