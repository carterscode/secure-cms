# backend/tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
from datetime import timedelta

from app.core.config import Settings, settings
from app.db.session import Base
from app.main import app
from app.core.security import SecurityUtils

# Test database URL
TEST_DATABASE_URL = "sqlite:///:memory:"

# Create test engine
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Enable foreign key support for SQLite
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

@pytest.fixture(scope="session")
def db_engine():
    """Create test database engine."""
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db(db_engine):
    """Create a fresh test database session."""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db):
    """Test client with database session."""
    def get_test_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides["get_db"] = get_test_db
    
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def test_password() -> str:
    """Test password fixture."""
    return "Test1234!"

@pytest.fixture
def test_user(db):
    """Create a test user."""
    from app.models.models import User
    
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=SecurityUtils.get_password_hash("Test1234!"),
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def test_admin(db):
    """Create a test admin user."""
    from app.models.models import User
    
    admin = User(
        email="admin@example.com",
        username="admin",
        hashed_password=SecurityUtils.get_password_hash("Test1234!"),
        is_active=True,
        is_admin=True
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin

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

@pytest.fixture
def auth_headers(test_user):
    """Get authentication headers."""
    access_token = SecurityUtils.create_access_token(
        data={"sub": test_user.email},
        expires_delta=timedelta(minutes=30)
    )
    return {"Authorization": f"Bearer {access_token}"}

@pytest.fixture
def admin_headers(test_admin):
    """Get admin authentication headers."""
    access_token = SecurityUtils.create_access_token(
        data={"sub": test_admin.email},
        expires_delta=timedelta(minutes=30)
    )
    return {"Authorization": f"Bearer {access_token}"}

@pytest.fixture(autouse=True)
def override_settings():
    """Override settings for testing."""
    app.dependency_overrides[Settings] = lambda: Settings(
        TESTING=True,
        DATABASE_URL=TEST_DATABASE_URL,
        SECRET_KEY="test_secret_key",
        TWO_FACTOR_AUTHENTICATION_ENABLED=False
    )
    return app.dependency_overrides[Settings]()
