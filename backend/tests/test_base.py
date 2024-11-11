# backend/tests/test_base.py
from fastapi.testclient import TestClient

def test_health_check(client: TestClient):
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_unauthorized_access(client: TestClient):
    """Test that protected endpoints require authentication"""
    response = client.get("/api/contacts")
    assert response.status_code == 401
    assert "detail" in response.json()

def test_auth_flow(client: TestClient, test_user):
    """Test the basic authentication flow"""
    # Register
    register_response = client.post(
        "/api/auth/register",
        json=test_user
    )
    assert register_response.status_code == 200
    assert "access_token" in register_response.json()

    # Login
    login_response = client.post(
        "/api/auth/login",
        data={
            "username": test_user["email"],
            "password": test_user["password"]
        }
    )
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()
