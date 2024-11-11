# backend/tests/conftest.py
import asyncio
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import pytest_asyncio
from typing import AsyncGenerator, Generator

from app.core.config import Settings, settings
from app.db.session import Base, get_db
from app.main import app
from app.core.security import SecurityUtils
from app.models.models import User

# Test database setup
TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override settings for testing
@pytest.fixture(scope="session")
def test_settings():
    return Settings(
        TESTING=True,
        DATABASE_URL=TEST_SQLALCHEMY_DATABASE_URL,
        SECRET_KEY="test_secret_key",
        BACKEND_CORS_ORIGINS=["http://test.com"],
        TWO_FACTOR_AUTHENTICATION_ENABLED=False
    )

@pytest.fixture(autouse=True)
def override_settings(test_settings):
    app.dependency_overrides[Settings] = lambda: test_settings
    yield
    app.dependency_overrides.clear()

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Setup test database."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db() -> Generator:
    """Get test database session."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db) -> Generator:
    """Get test client."""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def test_password() -> str:
    """Get test password."""
    return "Test1234!"

@pytest.fixture
def test_user(db) -> User:
    """Create test user."""
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
def test_admin(db) -> User:
    """Create test admin user."""
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
def user_token_headers(client: TestClient, test_user: User) -> dict:
    """Get user authentication headers."""
    from app.core.security import SecurityUtils
    from datetime import timedelta
    
    access_token = SecurityUtils.create_access_token(
        data={"sub": test_user.email},
        expires_delta=timedelta(minutes=60)
    )
    return {"Authorization": f"Bearer {access_token}"}

@pytest.fixture
def admin_token_headers(client: TestClient, test_admin: User) -> dict:
    """Get admin authentication headers."""
    from app.core.security import SecurityUtils
    from datetime import timedelta
    
    access_token = SecurityUtils.create_access_token(
        data={"sub": test_admin.email},
        expires_delta=timedelta(minutes=60)
    )
    return {"Authorization": f"Bearer {access_token}"}

@pytest.fixture
async def async_client() -> AsyncGenerator:
    """Get async test client."""
    from httpx import AsyncClient
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
