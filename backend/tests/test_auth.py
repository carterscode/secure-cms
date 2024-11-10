# backend/tests/test_auth.py
import pytest
from fastapi import status
from jose import jwt

from app.core.config import settings
from app.core.security import SecurityUtils

def test_login_success(client, test_user, test_password):
    response = client.post(
        "/api/auth/login",
        data={"username": test_user.email, "password": test_password}
    )
    assert response.status_code == status.HTTP_200_OK
    assert "message" in response.json()  # 2FA message

def test_login_wrong_password(client, test_user):
    response = client.post(
        "/api/auth/login",
        data={"username": test_user.email, "password": "wrongpassword"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_verify_2fa_success(client, test_user):
    # First login
    response = client.post(
        "/api/auth/login",
        data={"username": test_user.email, "password": "Test1234!"}
    )
    assert response.status_code == status.HTTP_200_OK
    
    # Then verify 2FA (mocked token)
    response = client.post(
        "/api/auth/verify-2fa",
        json={"token": "123456", "email": test_user.email}
    )
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert "token_type" in response.json()
    
    # Verify token is valid
    token = response.json()["access_token"]
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    assert payload["sub"] == test_user.email
