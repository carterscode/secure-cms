# backend/tests/test_contacts.py
import pytest
from fastapi import status

@pytest.fixture
def test_contact(db, test_user):
    from app.models.models import Contact
    contact = Contact(
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        mobile_phone="1234567890",
        created_by=test_user.id
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact

def test_create_contact(client, test_user):
    response = client.post(
        "/api/contacts/",
        json={
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane@example.com",
            "mobile_phone": "0987654321"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    created_contact = response.json()
    assert created_contact["first_name"] == "Jane"
    assert created_contact["last_name"] == "Doe"

def test_get_contacts(client, test_contact):
    response = client.get("/api/contacts/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) > 0

def test_get_contact(client, test_contact):
    response = client.get(f"/api/contacts/{test_contact.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == test_contact.id

def test_update_contact(client, test_contact):
    response = client.put(
        f"/api/contacts/{test_contact.id}",
        json={
            "first_name": "Johnny",
            "last_name": "Doe",
            "email": "johnny@example.com"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["first_name"] == "Johnny"

def test_delete_contact(client, test_contact):
    response = client.delete(f"/api/contacts/{test_contact.id}")
    assert response.status_code == status.HTTP_200_OK
    
    # Verify contact is deleted
    get_response = client.get(f"/api/contacts/{test_contact.id}")
    assert get_response.status_code == status.HTTP_404_NOT_FOUND
