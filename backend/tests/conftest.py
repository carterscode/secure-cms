# backend/tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import Settings
from app.db.session import Base, get_db
from app.main import app
from app.core.security import SecurityUtils
from datetime import timedelta

# Test database URL
TEST_DATABASE_URL = "sqlite:///:memory:"

# Create test engine
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Create test session factory
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_settings_override():
    return Settings(
        TESTING=True,
        DATABASE_URL=TEST_DATABASE_URL,
        SECRET_KEY="test_secret_key",
        BACKEND_CORS_ORIGINS=["http://test.com"],
        ACCESS_TOKEN_EXPIRE_MINUTES=60
    )

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Create test database tables."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(autouse=True)
def db():
    """Create a fresh database session for each test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    # Create tables for test
    Base.metadata.create_all(bind=engine)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db):
    """Create test client with overridden dependencies."""
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[Settings] = get_settings_override
    
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def test_user(db):
    """Create test user."""
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
    """Create test admin user."""
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
    """Create test contact."""
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
def test_tag(db):
    """Create test tag."""
    from app.models.models import Tag
    
    tag = Tag(name="Test Tag")
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag

@pytest.fixture
def test_password() -> str:
    """Provide test password."""
    return "Test1234!"

@pytest.fixture
def auth_headers(test_user):
    """Create authentication headers for test user."""
    settings = get_settings_override()
    access_token = SecurityUtils.create_access_token(
        data={"sub": test_user.email},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"Authorization": f"Bearer {access_token}"}

@pytest.fixture
def admin_headers(test_admin):
    """Create authentication headers for admin user."""
    settings = get_settings_override()
    access_token = SecurityUtils.create_access_token(
        data={"sub": test_admin.email},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"Authorization": f"Bearer {access_token}"}
