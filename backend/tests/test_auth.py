# backend/tests/test_auth.py
import pytest
from fastapi import status
from datetime import timedelta
from app.core.security import SecurityUtils
from app.core.config import settings

@pytest.fixture
def auth_token(test_user):
    """Create a valid auth token."""
    access_token = SecurityUtils.create_access_token(
        data={"sub": test_user.email},
        expires_delta=timedelta(minutes=30)
    )
    return access_token

@pytest.fixture
def auth_headers(auth_token):
    """Create headers with auth token."""
    return {"Authorization": f"Bearer {auth_token}"}

@pytest.fixture
def admin_token(test_admin):
    """Create a valid admin auth token."""
    access_token = SecurityUtils.create_access_token(
        data={"sub": test_admin.email},
        expires_delta=timedelta(minutes=30)
    )
    return access_token

@pytest.fixture
def admin_headers(admin_token):
    """Create headers with admin auth token."""
    return {"Authorization": f"Bearer {admin_token}"}

def test_login_success(client, test_user):
    """Test successful login."""
    response = client.post(
        "/api/auth/login",
        data={
            "username": test_user.email,
            "password": "Test1234!",
            "grant_type": "password"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    assert "message" in response.json()

def test_login_wrong_password(client, test_user):
    """Test login with wrong password."""
    response = client.post(
        "/api/auth/login",
        data={
            "username": test_user.email,
            "password": "wrongpassword",
            "grant_type": "password"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_verify_2fa_success(client, test_user, db):
    """Test 2FA verification."""
    # Set up 2FA token
    test_user.two_factor_secret = "123456"
    db.commit()
    
    # First login
    response = client.post(
        "/api/auth/login",
        data={
            "username": test_user.email,
            "password": "Test1234!",
            "grant_type": "password"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    
    # Then verify 2FA
    response = client.post(
        "/api/auth/verify-2fa",
        json={
            "token": "123456",
            "email": test_user.email
        }
    )
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
