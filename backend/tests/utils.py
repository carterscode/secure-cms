# backend/tests/utils.py
from typing import Dict
from datetime import timedelta

from app.core.security import SecurityUtils
from app.core.config import settings
from app.models.models import User

def create_test_auth_headers(user: User) -> Dict[str, str]:
    """Create authentication headers for testing."""
    access_token = SecurityUtils.create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"Authorization": f"Bearer {access_token}"}

def create_test_user_data() -> Dict[str, str]:
    """Create test user data."""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "Test1234!",
        "is_active": True,
        "is_admin": False
    }

def create_test_contact_data() -> Dict[str, str]:
    """Create test contact data."""
    return {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "mobile_phone": "1234567890"
    }
