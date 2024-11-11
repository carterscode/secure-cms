# backend/tests/test_auth.py
import pytest
from fastapi import status
from jose import jwt

from app.core.config import settings

def test_login_success(client, test_user, test_password):
    response = client.post(
        "/api/auth/login",
        data={
            "username": test_user.email,
            "password": test_password
        }
    )
    assert response.status_code == status.HTTP_200_OK
    assert "message" in response.json()  # 2FA message

def test_login_wrong_password(client, test_user):
    response = client.post(
        "/api/auth/login",
        data={
            "username": test_user.email,
            "password": "wrongpassword"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_login_nonexistent_user(client):
    response = client.post(
        "/api/auth/login",
        data={
            "username": "nonexistent@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_verify_2fa_success(client, test_user):
    # First login
    login_response = client.post(
        "/api/auth/login",
        data={
            "username": test_user.email,
            "password": "Test1234!"
        }
    )
    assert login_response.status_code == status.HTTP_200_OK
    
    # Then verify 2FA
    verify_response = client.post(
        "/api/auth/verify-2fa",
        json={
            "token": "123456",
            "email": test_user.email
        }
    )
    assert verify_response.status_code == status.HTTP_200_OK
    data = verify_response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"

    # Verify token is valid JWT
    token = data["access_token"]
    payload = jwt.decode(
        token, 
        settings.SECRET_KEY, 
        algorithms=[settings.JWT_ALGORITHM]
    )
    assert payload["sub"] == test_user.email

def test_verify_2fa_invalid_token(client, test_user):
    response = client.post(
        "/api/auth/verify-2fa",
        json={
            "token": "invalid",
            "email": test_user.email
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_verify_2fa_invalid_email(client):
    response = client.post(
        "/api/auth/verify-2fa",
        json={
            "token": "123456",
            "email": "nonexistent@example.com"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_change_password(client, test_user, auth_headers):
    response = client.post(
        "/api/auth/change-password",
        json={
            "current_password": "Test1234!",
            "new_password": "NewTest1234!"
        },
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert "message" in response.json()

def test_change_password_wrong_current(client, test_user, auth_headers):
    response = client.post(
        "/api/auth/change-password",
        json={
            "current_password": "wrong",
            "new_password": "NewTest1234!"
        },
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_change_password_invalid_new(client, test_user, auth_headers):
    response = client.post(
        "/api/auth/change-password",
        json={
            "current_password": "Test1234!",
            "new_password": "weak"
        },
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
