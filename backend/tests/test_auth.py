# backend/tests/test_auth.py
from fastapi import status
from datetime import timedelta

def test_login_success(client, test_user, test_password):
    """Test successful login."""
    response = client.post(
        "/api/auth/login",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "username": test_user.email,
            "password": test_password,
            "grant_type": "password"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    assert "message" in response.json()  # 2FA message

def test_login_wrong_password(client, test_user):
    """Test login with wrong password."""
    response = client.post(
        "/api/auth/login",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "username": test_user.email,
            "password": "wrongpassword",
            "grant_type": "password"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_verify_2fa_success(client, test_user):
    """Test 2FA verification."""
    # First login
    login_response = client.post(
        "/api/auth/login",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "username": test_user.email,
            "password": "Test1234!",
            "grant_type": "password"
        }
    )
    assert login_response.status_code == status.HTTP_200_OK

    # Verify 2FA
    response = client.post(
        "/api/auth/verify-2fa",
        json={
            "token": "123456",  # Mock 2FA token
            "email": test_user.email
        }
    )
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert "token_type" in response.json()
