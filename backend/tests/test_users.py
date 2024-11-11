# backend/tests/test_users.py
import pytest
from fastapi import status

def test_create_user(client, test_admin, admin_headers):
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
    created_user = response.json()
    assert created_user["email"] == "new@example.com"
    assert "hashed_password" not in created_user

def test_create_user_duplicate_email(client, test_admin, admin_headers):
    response = client.post(
        "/api/users/",
        json={
            "email": "test@example.com",  # Already exists
            "username": "newuser",
            "password": "NewPassword123!",
            "is_admin": False
        },
        headers=admin_headers
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_get_users(client, test_admin, admin_headers):
    response = client.get(
        "/api/users/",
        headers=admin_headers
    )
    assert response.status_code == status.HTTP_200_OK
    users = response.json()
    assert len(users) > 0
    assert all(isinstance(user["id"], int) for user in users)

def test_get_current_user(client, test_user, auth_headers):
    response = client.get(
        "/api/users/me",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == test_user.email
    assert data["username"] == test_user.username

def test_update_current_user(client, test_user, auth_headers):
    response = client.patch(
        "/api/users/me",
        json={"username": "updated_username"},
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == "updated_username"

def test_get_user_by_id(client, test_user, test_admin, admin_headers):
    response = client.get(
        f"/api/users/{test_user.id}",
        headers=admin_headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["email"] == test_user.email

def test_get_user_by_id_not_found(client, admin_headers):
    response = client.get(
        "/api/users/99999",
        headers=admin_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_delete_user(client, test_user, test_admin, admin_headers):
    response = client.delete(
        f"/api/users/{test_user.id}",
        headers=admin_headers
    )
    assert response.status_code == status.HTTP_200_OK
    
    # Verify user is deleted
    get_response = client.get(
        f"/api/users/{test_user.id}",
        headers=admin_headers
    )
    assert get_response.status_code == status.HTTP_404_NOT_FOUND

def test_activate_deactivate_user(client, test_user, test_admin, admin_headers):
    # Deactivate user
    response = client.post(
        f"/api/users/{test_user.id}/deactivate",
        headers=admin_headers
    )
    assert response.status_code == status.HTTP_200_OK
    
    # Activate user
    response = client.post(
        f"/api/users/{test_user.id}/activate",
        headers=admin_headers
    )
    assert response.status_code == status.HTTP_200_OK
