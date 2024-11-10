# backend/tests/test_users.py
import pytest
from fastapi import status

def test_create_user(client, db):
    response = client.post(
        "/api/users/",
        json={
            "email": "new@example.com",
            "username": "newuser",
            "password": "NewPassword123!",
            "is_admin": False
        }
    )
    assert response.status_code == status.HTTP_200_OK
    created_user = response.json()
    assert created_user["email"] == "new@example.com"
    assert "hashed_password" not in created_user

def test_get_users(client, test_user):
    response = client.get("/api/users/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) > 0

def test_get_current_user(client, test_user):
    response = client.get("/api/users/me")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == test_user.email

def test_update_user(client, test_user):
    response = client.patch(
        f"/api/users/{test_user.id}",
        json={"username": "updatedname"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == "updatedname"
