# backend/tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import timedelta

from app.core.config import Settings
from app.db.session import Base, get_db
from app.main import app
from app.core.security import SecurityUtils

TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

# Create test engine
engine = create_engine(
    TEST_SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_test_settings():
    return Settings(
        TESTING=True,
        DATABASE_URL=TEST_SQLALCHEMY_DATABASE_URL,
        SECRET_KEY="test_secret_key",
        TWO_FACTOR_AUTHENTICATION_ENABLED=False,
    )

@pytest.fixture(scope="session", autouse=True)
def override_settings():
    app.dependency_overrides[Settings] = get_test_settings
    yield
    app.dependency_overrides.clear()

@pytest.fixture(scope="session")
def db_engine():
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(autouse=True)
def db():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def test_password() -> str:
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
def auth_headers(test_user):
    """Get valid authentication headers."""
    access_token = SecurityUtils.create_access_token(
        data={"sub": test_user.email},
        expires_delta=timedelta(minutes=30)
    )
    return {"Authorization": f"Bearer {access_token}"}

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
def admin_headers(test_admin):
    """Get valid admin authentication headers."""
    access_token = SecurityUtils.create_access_token(
        data={"sub": test_admin.email},
        expires_delta=timedelta(minutes=30)
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
