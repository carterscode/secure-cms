# backend/tests/test_contacts.py
import pytest
from fastapi import status

def test_create_contact(client, test_user, auth_headers):
    response = client.post(
        "/api/contacts/",
        headers=auth_headers,
        json={
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane@example.com",
            "mobile_phone": "0987654321"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["first_name"] == "Jane"
    assert data["last_name"] == "Doe"
    assert data["email"] == "jane@example.com"

def test_get_contacts(client, test_contact, auth_headers):
    response = client.get(
        "/api/contacts/",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data["items"], list)
    assert len(data["items"]) > 0

def test_get_contact(client, test_contact, auth_headers):
    response = client.get(
        f"/api/contacts/{test_contact.id}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_contact.id
    assert data["first_name"] == test_contact.first_name

def test_update_contact(client, test_contact, auth_headers):
    response = client.put(
        f"/api/contacts/{test_contact.id}",
        headers=auth_headers,
        json={
            "first_name": "Updated",
            "last_name": test_contact.last_name,
            "email": test_contact.email
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["first_name"] == "Updated"

def test_delete_contact(client, test_contact, auth_headers):
    response = client.delete(
        f"/api/contacts/{test_contact.id}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    
    # Verify contact is deleted
    response = client.get(
        f"/api/contacts/{test_contact.id}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.parametrize("invalid_id", [-1, 0, 99999])
def test_get_nonexistent_contact(client, auth_headers, invalid_id):
    response = client.get(
        f"/api/contacts/{invalid_id}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_create_contact_without_auth(client):
    response = client.post(
        "/api/contacts/",
        json={
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane@example.com"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_search_contacts(client, test_contact, auth_headers):
    response = client.get(
        f"/api/contacts/?search={test_contact.first_name}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["items"]) > 0
    assert data["items"][0]["first_name"] == test_contact.first_name
