# backend/tests/test_contacts.py
import pytest
from fastapi import status
from .utils import create_test_auth_headers

def test_create_contact(client, test_user, auth_headers):
    """Test contact creation."""
    response = client.post(
        "/api/contacts/",
        json={
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane@example.com",
            "mobile_phone": "0987654321"
        },
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["first_name"] == "Jane"
    assert data["last_name"] == "Doe"

def test_get_contacts(client, test_contact, auth_headers):
    """Test getting all contacts."""
    response = client.get(
        "/api/contacts/",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) > 0

def test_get_contact(client, test_contact, auth_headers):
    """Test getting a specific contact."""
    response = client.get(
        f"/api/contacts/{test_contact.id}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == test_contact.id

def test_update_contact(client, test_contact, auth_headers):
    """Test updating a contact."""
    response = client.put(
        f"/api/contacts/{test_contact.id}",
        json={
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane@example.com"
        },
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["first_name"] == "Jane"

def test_delete_contact(client, test_contact, auth_headers):
    """Test deleting a contact."""
    response = client.delete(
        f"/api/contacts/{test_contact.id}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
