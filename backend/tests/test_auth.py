# backend/tests/test_auth.py
import pytest
from fastapi import status
from tests.utils import create_test_auth_headers
from app.core.security import SecurityUtils

def test_login_success(client, test_user, test_password):
    """Test successful login."""
    response = client.post(
        "/api/auth/login",
        data={
            "username": test_user.email,
            "password": test_password,
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
            "password": "wrong_password",
            "grant_type": "password"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_verify_2fa_success(client, test_user, mocker):
    """Test successful 2FA verification."""
    # Mock email sending
    mocker.patch('app.services.email.EmailService.send_2fa_code', return_value=True)
    
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
