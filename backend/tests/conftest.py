# backend/tests/conftest.py
import pytest
from typing import Dict, Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.core.config import Settings, settings
from app.core.security import SecurityUtils
from app.db.session import Base, get_db
from app.main import app
from app.models.models import User, Contact, Tag, AuditLogEntry
from .utils import create_test_token, random_email, random_lower_string

# Test database URL
TEST_DATABASE_URL = "sqlite:///:memory:"

# Create test database engine
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

# Create test session factory
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override settings for testing
def get_settings_override() -> Settings:
    return Settings(
        TESTING=True,
        DEBUG=True,
        DATABASE_URL=TEST_DATABASE_URL,
        SECRET_KEY="test_secret_key",
        BACKEND_CORS_ORIGINS=["http://test.com"],
        TWO_FACTOR_AUTHENTICATION_ENABLED=False,
        SMTP_HOST="localhost",
        SMTP_PORT=25
    )

@pytest.fixture(scope="session")
def db_engine() -> Generator:
    """Create test database engine."""
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(autouse=True)
def db() -> Generator[Session, None, None]:
    """Create a fresh database session for each test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db: Session) -> Generator:
    """Create a test client with database session."""
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[Settings] = get_settings_override
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

@pytest.fixture
def test_password() -> str:
    """Provide a test password."""
    return "Test1234!"

@pytest.fixture
def test_user(db: Session) -> User:
    """Create a test user."""
    user = User(
        email=random_email(),
        username=random_lower_string(),
        hashed_password=SecurityUtils.get_password_hash("Test1234!"),
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def test_admin(db: Session) -> User:
    """Create a test admin user."""
    admin = User(
        email=random_email(),
        username=random_lower_string(),
        hashed_password=SecurityUtils.get_password_hash("Test1234!"),
        is_active=True,
        is_admin=True
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin

@pytest.fixture
def test_contact(db: Session, test_user: User) -> Contact:
    """Create a test contact."""
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
def test_tag(db: Session) -> Tag:
    """Create a test tag."""
    tag = Tag(name="Test Tag")
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag

@pytest.fixture
def auth_headers(test_user: User) -> Dict[str, str]:
    """Get authentication headers."""
    access_token = create_test_token(test_user.email)
    return {"Authorization": f"Bearer {access_token}"}

@pytest.fixture
def admin_headers(test_admin: User) -> Dict[str, str]:
    """Get admin authentication headers."""
    access_token = create_test_token(test_admin.email)
    return {"Authorization": f"Bearer {access_token}"}

@pytest.fixture
def audit_log(db: Session, test_user: User) -> AuditLogEntry:
    """Create a test audit log entry."""
    log = AuditLogEntry(
        user_id=test_user.id,
        action="test_action",
        details="Test audit log entry",
        ip_address="127.0.0.1"
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log

@pytest.fixture
def clean_db(db: Session) -> None:
    """Clean up the database after tests."""
    yield
    db.query(Contact).delete()
    db.query(Tag).delete()
    db.query(AuditLogEntry).delete()
    db.query(User).delete()
    db.commit()
