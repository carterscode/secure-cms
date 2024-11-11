# backend/tests/conftest.py
import os
import pytest
from typing import Generator, Dict
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from databases import Database

from app.core.config import settings
from app.db.session import get_db
from app.models import Base
from app.main import app

# Test database URL
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL", "postgresql://test:test@localhost:5432/test_db"
)

# Create test database engine
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def db_engine():
    """Create test database tables"""
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(db_engine: Generator) -> Generator:
    """Creates a fresh test database session for each test"""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db_session: Generator) -> Generator:
    """Create a test client with a fresh database session"""
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

@pytest.fixture
def test_user() -> Dict[str, str]:
    """Create a test user for authentication tests"""
    return {
        "email": "test@example.com",
        "password": "Test123!@#",
        "username": "testuser",
        "is_admin": False
    }

@pytest.fixture
def test_admin() -> Dict[str, str]:
    """Create a test admin user for admin-required tests"""
    return {
        "email": "admin@example.com",
        "password": "Admin123!@#",
        "username": "adminuser",
        "is_admin": True
    }

@pytest.fixture
def test_contact() -> Dict[str, str]:
    """Create a test contact for contact-related tests"""
    return {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "mobile_phone": "+1234567890",
        "company": "Test Company",
        "tags": ["test", "example"]
    }

@pytest.fixture
async def token_header(client: TestClient, test_user: Dict[str, str]) -> Dict[str, str]:
    """Create an authentication token for test requests"""
    response = client.post(
        "/api/auth/register",
        json=test_user
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
async def admin_token_header(client: TestClient, test_admin: Dict[str, str]) -> Dict[str, str]:
    """Create an admin authentication token for test requests"""
    response = client.post(
        "/api/auth/register",
        json=test_admin
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def mock_email_sender(monkeypatch):
    """Mock email sending functionality for tests"""
    sent_emails = []
    
    def mock_send_email(to_email: str, subject: str, body: str):
        sent_emails.append({
            "to": to_email,
            "subject": subject,
            "body": body
        })
        return True
    
    monkeypatch.setattr("app.services.email.send_email", mock_send_email)
    return sent_emails
