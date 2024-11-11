# backend/tests/test_users.py
import pytest
from fastapi import status

def test_create_user(client, admin_token_headers):
    response = client.post(
        "/api/users/",
        headers=admin_token_headers,
        json={
            "email": "new@example.com",
            "username": "newuser",
            "password": "Test1234!",
            "is_admin": False
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == "new@example.com"
    assert "hashed_password" not in data

def test_get_users(client, admin_token_headers, test_user):
    response = client.get(
        "/api/users/",
        headers=admin_token_headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) > 0

def test_get_current_user(client, user_token_headers, test_user):
    response = client.get(
        "/api/users/me",
        headers=user_token_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == test_user.email

def test_update_user(client, admin_token_headers, test_user):
    response = client.put(
        f"/api/users/{test_user.id}",
        headers=admin_token_headers,
        json={"username": "updated_user"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == "updated_user"

def test_unauthorized_access(client):
    response = client.get("/api/users/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_non_admin_access(client, user_token_headers):
    response = client.get(
        "/api/users/",
        headers=user_token_headers
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.asyncio
async def test_async_user_operations(async_client, admin_token_headers):
    response = await async_client.post(
        "/api/users/",
        headers=admin_token_headers,
        json={
            "email": "async@example.com",
            "username": "asyncuser",
            "password": "Test1234!",
            "is_admin": False
        }
    )
    assert response.status_code == status.HTTP_200_OK
