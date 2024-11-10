# backend/tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.engine import Engine

from app.core.config import Settings
from app.db.session import Base, get_db
from app.main import app
from app.core.security import SecurityUtils
from app.models.models import User, Contact, Tag, AuditLogEntry  # Import all models

# Enable SQLite foreign key support
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# Override settings for testing
def get_settings_override():
    return Settings(
        TESTING=True,
        DEBUG=True,
        DATABASE_URL="sqlite:///:memory:",
        SECRET_KEY="test_secret_key",
        BACKEND_CORS_ORIGINS=["http://test.com"],
        TWO_FACTOR_AUTHENTICATION_ENABLED=False
    )

app.dependency_overrides[Settings] = get_settings_override

# Create test database engine
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def create_test_database():
    """Create the test database."""
    Base.metadata.drop_all(bind=engine)  # Clear any existing tables
    Base.metadata.create_all(bind=engine)  # Create all tables
    yield
    Base.metadata.drop_all(bind=engine)  # Clean up after tests

@pytest.fixture
def db():
    """Create a fresh database session for each test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    # Create tables for this test session
    Base.metadata.create_all(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db):
    """Create a test client with database session."""
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
    """Provide a test password."""
    return "Test1234!"

@pytest.fixture
def test_user(db):
    """Create a test user."""
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
    """Create a test tag."""
    tag = Tag(name="Test Tag")
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag

@pytest.fixture
def auth_headers(client, test_user):
    """Get authentication headers."""
    from datetime import timedelta
    from app.core.config import settings
    
    access_token = SecurityUtils.create_access_token(
        data={"sub": test_user.email},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"Authorization": f"Bearer {access_token}"}

@pytest.fixture
def admin_headers(client, test_admin):
    """Get admin authentication headers."""
    from datetime import timedelta
    from app.core.config import settings
    
    access_token = SecurityUtils.create_access_token(
        data={"sub": test_admin.email},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"Authorization": f"Bearer {access_token}"}

@pytest.fixture(autouse=True)
def _init_test_db(db):
    """Ensure database is initialized for each test."""
    # Drop and recreate all tables for each test
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    db.close()

# Silence SQLAlchemy warnings
@pytest.fixture(autouse=True)
def _silence_sqlalchemy(request):
    import warnings
    from sqlalchemy import exc as sa_exc
    warnings.filterwarnings("ignore", category=sa_exc.SAWarning)
