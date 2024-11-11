# backend/tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import timedelta

from app.core.config import Settings, settings
from app.core.security import SecurityUtils
from app.db.session import Base, get_db
from app.main import app
from app.models.models import User, Contact, Tag

# Create test database engine
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def db_engine():
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db(db_engine):
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
    
    app.dependency_overrides.clear()

@pytest.fixture
def test_password() -> str:
    return "Test1234!"

@pytest.fixture
def test_user(db):
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
    tag = Tag(name="Test Tag")
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag

@pytest.fixture
def user_token_headers(test_user):
    access_token = SecurityUtils.create_access_token(
        data={"sub": test_user.email},
        expires_delta=timedelta(minutes=30)
    )
    return {"Authorization": f"Bearer {access_token}"}

@pytest.fixture
def admin_token_headers(test_admin):
    access_token = SecurityUtils.create_access_token(
        data={"sub": test_admin.email},
        expires_delta=timedelta(minutes=30)
    )
    return {"Authorization": f"Bearer {access_token}"}

@pytest.fixture
def auth_headers(user_token_headers):
    """Alias for user_token_headers for backward compatibility"""
    return user_token_headers

@pytest.fixture
def async_client(client):
    """Wrapper for sync client to be used in async tests"""
    class AsyncClientWrapper:
        def __init__(self, sync_client):
            self._client = sync_client

        async def get(self, *args, **kwargs):
            return self._client.get(*args, **kwargs)

        async def post(self, *args, **kwargs):
            return self._client.post(*args, **kwargs)

        async def put(self, *args, **kwargs):
            return self._client.put(*args, **kwargs)

        async def delete(self, *args, **kwargs):
            return self._client.delete(*args, **kwargs)

    return AsyncClientWrapper(client)

# Override settings for testing
@pytest.fixture(autouse=True)
def override_settings():
    app.dependency_overrides[Settings] = lambda: Settings(
        TESTING=True,
        DATABASE_URL="sqlite:///:memory:",
        SECRET_KEY="test_secret_key",
        BACKEND_CORS_ORIGINS=["http://test.com"],
        TWO_FACTOR_AUTHENTICATION_ENABLED=False
    )
    yield
    app.dependency_overrides.clear()
