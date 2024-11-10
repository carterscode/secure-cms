# backend/tests/utils.py
from datetime import timedelta
from app.core.security import SecurityUtils
from app.core.config import settings

def create_test_auth_headers(test_user):
    """Create authentication headers for testing."""
    access_token = SecurityUtils.create_access_token(
        data={"sub": test_user.email},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"Authorization": f"Bearer {access_token}"}
