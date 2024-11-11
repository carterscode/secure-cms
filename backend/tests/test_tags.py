# backend/tests/test_tags.py
import pytest
from fastapi import status

def test_create_tag(client, auth_headers):
    """Test creating a new tag."""
    response = client.post(
        "/api/tags/",
        json={"name": "New Tag"},
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    created_tag = response.json()
    assert created_tag["name"] == "New Tag"
    assert "id" in created_tag

def test_create_duplicate_tag(client, test_tag, auth_headers):
    """Test creating a tag with a duplicate name."""
    response = client.post(
        "/api/tags/",
        json={"name": test_tag.name},
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already exists" in response.json()["detail"].lower()

def test_get_tags(client, test_tag, auth_headers):
    """Test getting all tags."""
    response = client.get(
        "/api/tags/",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    tags = response.json()
    assert len(tags) > 0
    assert any(tag["name"] == test_tag.name for tag in tags)

def test_get_tag(client, test_tag, auth_headers):
    """Test getting a specific tag by ID."""
    response = client.get(
        f"/api/tags/{test_tag.id}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    tag = response.json()
    assert tag["id"] == test_tag.id
    assert tag["name"] == test_tag.name

def test_get_nonexistent_tag(client, auth_headers):
    """Test getting a tag that doesn't exist."""
    response = client.get(
        "/api/tags/99999",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_update_tag(client, test_tag, auth_headers):
    """Test updating a tag's name."""
    new_name = "Updated Tag Name"
    response = client.put(
        f"/api/tags/{test_tag.id}",
        json={"name": new_name},
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    updated_tag = response.json()
    assert updated_tag["id"] == test_tag.id
    assert updated_tag["name"] == new_name

def test_update_tag_duplicate_name(client, test_tag, auth_headers):
    """Test updating a tag with a name that already exists."""
    # First create another tag
    client.post(
        "/api/tags/",
        json={"name": "Another Tag"},
        headers=auth_headers
    )
    
    # Try to update the test_tag with the same name
    response = client.put(
        f"/api/tags/{test_tag.id}",
        json={"name": "Another Tag"},
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already exists" in response.json()["detail"].lower()

def test_delete_tag(client, test_tag, auth_headers):
    """Test deleting a tag."""
    response = client.delete(
        f"/api/tags/{test_tag.id}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    
    # Verify tag is deleted
    get_response = client.get(
        f"/api/tags/{test_tag.id}",
        headers=auth_headers
    )
    assert get_response.status_code == status.HTTP_404_NOT_FOUND

def test_delete_tag_with_contacts(client, test_tag, test_contact, auth_headers):
    """Test deleting a tag that is associated with contacts."""
    # First associate the tag with a contact
    client.put(
        f"/api/contacts/{test_contact.id}",
        json={
            "first_name": test_contact.first_name,
            "last_name": test_contact.last_name,
            "tags": [test_tag.name]
        },
        headers=auth_headers
    )
    
    # Try to delete the tag
    response = client.delete(
        f"/api/tags/{test_tag.id}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "in use" in response.json()["detail"].lower()

def test_search_tags(client, test_tag, auth_headers):
    """Test searching for tags by name."""
    response = client.get(
        f"/api/tags/search/{test_tag.name[:3]}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    tags = response.json()
    assert len(tags) > 0
    assert any(tag["name"] == test_tag.name for tag in tags)

def test_get_tag_usage_stats(client, test_tag, test_contact, auth_headers):
    """Test getting usage statistics for tags."""
    # First associate the tag with a contact
    client.put(
        f"/api/contacts/{test_contact.id}",
        json={
            "first_name": test_contact.first_name,
            "last_name": test_contact.last_name,
            "tags": [test_tag.name]
        },
        headers=auth_headers
    )
    
    response = client.get(
        "/api/tags/stats/usage",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    stats = response.json()
    assert len(stats) > 0
    tag_stat = next(stat for stat in stats if stat["id"] == test_tag.id)
    assert tag_stat["contact_count"] > 0

def test_merge_tags(client, test_tag, auth_headers, admin_headers):
    """Test merging two tags."""
    # Create a second tag
    create_response = client.post(
        "/api/tags/",
        json={"name": "Tag to Merge"},
        headers=auth_headers
    )
    source_tag_id = create_response.json()["id"]
    
    # Merge the tags
    response = client.post(
        f"/api/tags/merge/{source_tag_id}/{test_tag.id}",
        headers=admin_headers
    )
    assert response.status_code == status.HTTP_200_OK
    
    # Verify source tag is deleted
    get_response = client.get(
        f"/api/tags/{source_tag_id}",
        headers=auth_headers
    )
    assert get_response.status_code == status.HTTP_404_NOT_FOUND

def test_merge_nonexistent_tags(client, test_tag, admin_headers):
    """Test merging when one or both tags don't exist."""
    response = client.post(
        f"/api/tags/merge/99999/{test_tag.id}",
        headers=admin_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_merge_same_tag(client, test_tag, admin_headers):
    """Test attempting to merge a tag with itself."""
    response = client.post(
        f"/api/tags/merge/{test_tag.id}/{test_tag.id}",
        headers=admin_headers
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "cannot merge tag with itself" in response.json()["detail"].lower()
