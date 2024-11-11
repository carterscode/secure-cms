# backend/tests/utils.py
from typing import Dict, Optional

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

def create_test_user(
    client: TestClient,
    email: str = "test@example.com",
    password: str = "Test1234!",
    is_admin: bool = False
) -> Dict:
    response = client.post(
        "/api/auth/register",
        json={
            "email": email,
            "username": email.split("@")[0],
            "password": password,
            "is_admin": is_admin
        },
    )
    return response.json()

def get_token_headers(client: TestClient, email: str = "test@example.com", password: str = "Test1234!") -> Dict:
    login_data = {
        "username": email,
        "password": password,
    }
    response = client.post("/api/auth/token", data=login_data)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def create_random_user(db: Session, password: str = "Test1234!") -> Dict:
    from app.models.models import User
    from app.core.security import SecurityUtils
    import random
    import string
    
    random_string = ''.join(random.choices(string.ascii_lowercase, k=10))
    email = f"{random_string}@example.com"
    
    user = User(
        email=email,
        username=random_string,
        hashed_password=SecurityUtils.get_password_hash(password),
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return {"email": email, "password": password}
