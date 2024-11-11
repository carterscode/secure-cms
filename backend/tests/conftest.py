# backend/tests/conftest.py
import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.db.session import SessionLocal
from app.main import app
from app.models.models import Base, User
from app.core.security import SecurityUtils
import uuid

# Use SQLite in-memory database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session() -> Generator:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session: SessionLocal) -> Generator:
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides = {}
    yield TestClient(app)
    app.dependency_overrides = {}

@pytest.fixture
def test_password() -> str:
    return "Test1234!"

@pytest.fixture
def test_user(db_session: SessionLocal, test_password: str) -> User:
    unique_email = f"test_{uuid.uuid4()}@example.com"
    unique_username = f"test_user_{uuid.uuid4()}"
    
    user = User(
        email=unique_email,
        username=unique_username,
        hashed_password=SecurityUtils.get_password_hash(test_password),
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def test_admin(db_session: SessionLocal, test_password: str) -> User:
    unique_email = f"admin_{uuid.uuid4()}@example.com"
    unique_username = f"admin_user_{uuid.uuid4()}"
    
    admin = User(
        email=unique_email,
        username=unique_username,
        hashed_password=SecurityUtils.get_password_hash(test_password),
        is_active=True,
        is_admin=True
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin

@pytest.fixture
def auth_headers(test_user: User) -> dict:
    access_token = SecurityUtils.create_access_token(data={"sub": test_user.email})
    return {"Authorization": f"Bearer {access_token}"}

@pytest.fixture
def admin_headers(test_admin: User) -> dict:
    access_token = SecurityUtils.create_access_token(data={"sub": test_admin.email})
    return {"Authorization": f"Bearer {access_token}"}
