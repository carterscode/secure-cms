# backend/tests/test_users.py
import pytest
from fastapi import status
from tests.utils import create_test_auth_headers

def test_create_user(client, admin_headers):
    """Test user creation."""
    response = client.post(
        "/api/users/",
        json={
            "email": "new@example.com",
            "username": "newuser",
            "password": "NewPassword123!",
            "is_admin": False
        },
        headers=admin_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == "new@example.com"

def test_get_users(client, admin_headers):
    """Test getting all users."""
    response = client.get(
        "/api/users/",
        headers=admin_headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) > 0

def test_get_current_user(client, auth_headers):
    """Test getting current user info."""
    response = client.get(
        "/api/users/me",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK

def test_update_user(client, test_user, admin_headers):
    """Test updating a user."""
    response = client.put(
        f"/api/users/{test_user.id}",
        json={
            "username": "updatedname"
        },
        headers=admin_headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == "updatedname"
