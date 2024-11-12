# backend/tests/conftest.py
import os
import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Set test environment before imports
os.environ.update({
    "TESTING": "true",
    "DATABASE_URL": "sqlite:///:memory:",
    "SECRET_KEY": "test-secret-key",
    "BACKEND_CORS_ORIGINS": '["http://localhost:3000","http://localhost:8000"]'
})

from app.db.base import Base
from app.models.models import User, Contact, Tag, AuditLogEntry, contact_tags  # noqa
from app.db.session import get_db
from app.main import app

def get_test_db_url():
    return "sqlite:///:memory:"

@pytest.fixture(scope="session")
def engine():
    engine = create_engine(
        get_test_db_url(),
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Enable foreign keys for SQLite
    def _enable_foreign_keys(connection, connection_record):
        connection.execute('PRAGMA foreign_keys=ON')
    
    event.listen(engine, 'connect', _enable_foreign_keys)
    
    # Create all tables
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    return engine

@pytest.fixture(scope="function")
def db_session(engine) -> Generator[Session, None, None]:
    connection = engine.connect()
    transaction = connection.begin()
    session = sessionmaker(autocommit=False, autoflush=False, bind=connection)()

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    app.dependency_overrides[get_db] = lambda: db_session
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def test_user(db_session: Session) -> User:
    from app.core.security import get_password_hash
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("testpassword123!"),
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture(scope="function")
def test_tag(db_session: Session) -> Tag:
    tag = Tag(name="test-tag")
    db_session.add(tag)
    db_session.commit()
    db_session.refresh(tag)
    return tag

@pytest.fixture(scope="function")
def test_contact(db_session: Session, test_user: User) -> Contact:
    contact = Contact(
        first_name="Test",
        last_name="Contact",
        email="contact@example.com",
        owner_id=test_user.id
    )
    db_session.add(contact)
    db_session.commit()
    db_session.refresh(contact)
    return contact
