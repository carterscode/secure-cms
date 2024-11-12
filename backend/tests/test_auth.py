# backend/tests/test_auth.py
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.user import User

def test_create_user(client: TestClient, db_session: Session):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "Test123!@#$",
            "is_active": True,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_create_user_weak_password(client: TestClient, db_session: Session):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "weak",
            "is_active": True,
        },
    )
    assert response.status_code == 400
    assert "Password does not meet security requirements" in response.json()["detail"]

def test_login_user(client: TestClient, db_session: Session):
    # Create test user
    hashed_password = get_password_hash("Test123!@#$")
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=hashed_password,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()

    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "Test123!@#$",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client: TestClient, db_session: Session):
    # Create test user
    hashed_password = get_password_hash("Test123!@#$")
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=hashed_password,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()

    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "wrongpassword",
        },
    )
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]
