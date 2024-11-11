# backend/tests/test_contacts.py
import pytest
from fastapi import status

def test_create_contact(client, test_user, auth_headers):
    response = client.post(
        "/api/contacts/",
        json={
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane@example.com",
            "mobile_phone": "0987654321",
            "tags": ["Friend"]
        },
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    created_contact = response.json()
    assert created_contact["first_name"] == "Jane"
    assert created_contact["last_name"] == "Doe"
    assert created_contact["email"] == "jane@example.com"

def test_get_contacts(client, test_contact, auth_headers):
    response = client.get(
        "/api/contacts/",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    contacts = response.json()
    assert len(contacts["items"]) > 0
    assert contacts["total"] > 0

def test_get_contacts_with_search(client, test_contact, auth_headers):
    response = client.get(
        "/api/contacts/?search=John",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    contacts = response.json()
    assert len(contacts["items"]) > 0
    assert all("John" in contact["first_name"] for contact in contacts["items"])

def test_get_contact(client, test_contact, auth_headers):
    response = client.get(
        f"/api/contacts/{test_contact.id}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    contact = response.json()
    assert contact["id"] == test_contact.id
    assert contact["first_name"] == test_contact.first_name

def test_get_contact_not_found(client, auth_headers):
    response = client.get(
        "/api/contacts/99999",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_update_contact(client, test_contact, auth_headers):
    response = client.put(
        f"/api/contacts/{test_contact.id}",
        json={
            "first_name": "Johnny",
            "last_name": "Doe",
            "email": "johnny@example.com"
        },
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    updated_contact = response.json()
    assert updated_contact["first_name"] == "Johnny"
    assert updated_contact["email"] == "johnny@example.com"

def test_delete_contact(client, test_contact, auth_headers):
    response = client.delete(
        f"/api/contacts/{test_contact.id}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    
    # Verify contact is deleted
    get_response = client.get(
        f"/api/contacts/{test_contact.id}",
        headers=auth_headers
    )
    assert get_response.status_code == status.HTTP_404_NOT_FOUND

def test_import_contacts(client, auth_headers):
    # Create a test vCard file
    vcard_content = """BEGIN:VCARD
VERSION:3.0
FN:John Smith
N:Smith;John;;;
EMAIL:john.smith@example.com
TEL:+1234567890
END:VCARD"""

    files = {
        'file': ('contacts.vcf', vcard_content, 'text/vcard')
    }
    
    response = client.post(
        "/api/contacts/import",
        files=files,
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    assert "imported" in result
    assert len(result["imported"]) > 0

def test_export_contacts(client, test_contact, auth_headers):
    response = client.post(
        "/api/contacts/export",
        json=[test_contact.id],
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    assert "content" in result
    assert "filename" in result
    assert result["filename"] == "contacts.vcf"

def test_filter_contacts_by_tag(client, test_contact, test_tag, auth_headers):
    # Add tag to contact
    response = client.put(
        f"/api/contacts/{test_contact.id}",
        json={
            "first_name": test_contact.first_name,
            "last_name": test_contact.last_name,
            "tags": [test_tag.name]
        },
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK

    # Filter contacts by tag
    response = client.get(
        f"/api/contacts/?tags={test_tag.name}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    contacts = response.json()
    assert len(contacts["items"]) > 0
    assert all(test_tag.name in [t["name"] for t in contact["tags"]] 
              for contact in contacts["items"])
