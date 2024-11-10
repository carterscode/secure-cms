# backend/tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
from datetime import timedelta

from app.core.config import Settings, settings
from app.db.session import get_db, Base
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

@pytest.fixture(scope="session")
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
    """Get authentication headers."""
    access_token = SecurityUtils.create_access_token(
        data={"sub": test_user.email},
        expires_delta=timedelta(minutes=30)
    )
    return {"Authorization": f"Bearer {access_token}"}

@pytest.fixture
def admin_headers(test_user):
    """Get admin authentication headers."""
    test_user.is_admin = True
    access_token = SecurityUtils.create_access_token(
        data={"sub": test_user.email},
        expires_delta=timedelta(minutes=30)
    )
    return {"Authorization": f"Bearer {access_token}"}

# ... rest of the fixtures remain the same ...
