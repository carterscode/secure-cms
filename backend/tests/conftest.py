# backend/tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import timedelta

from app.core.config import Settings
from app.db.session import Base, get_db
from app.main import app
from app.core.security import SecurityUtils
from app.core.dependencies import get_current_user, get_current_admin_user

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override settings for testing
def get_settings_override():
    return Settings(
        TESTING=True,
        SECRET_KEY="test_secret_key",
        ACCESS_TOKEN_EXPIRE_MINUTES=30,
        DATABASE_URL=SQLALCHEMY_DATABASE_URL,
    )

@pytest.fixture(scope="session")
def db_engine():
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            db.close()
    
    def override_get_current_user():
        return test_user(db)
    
    def override_get_current_admin_user():
        return test_admin(db)
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_current_admin_user] = override_get_current_admin_user
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

@pytest.fixture
def test_password() -> str:
    return "Test1234!"

@pytest.fixture
def test_user(db):
    from app.models.models import User
    
    user = db.query(User).filter(User.email == "test@example.com").first()
    if not user:
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password=SecurityUtils.get_password_hash("Test1234!"),
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

@pytest.fixture
def test_admin(db):
    from app.models.models import User
    
    admin = db.query(User).filter(User.email == "admin@example.com").first()
    if not admin:
        admin = User(
            email="admin@example.com",
            username="admin",
            hashed_password=SecurityUtils.get_password_hash("Test1234!"),
            is_active=True,
            is_admin=True
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
    return admin

@pytest.fixture
def auth_headers(test_user):
    access_token = SecurityUtils.create_access_token(
        data={"sub": test_user.email},
        expires_delta=timedelta(minutes=30)
    )
    return {"Authorization": f"Bearer {access_token}"}

@pytest.fixture
def admin_headers(test_admin):
    access_token = SecurityUtils.create_access_token(
        data={"sub": test_admin.email},
        expires_delta=timedelta(minutes=30)
    )
    return {"Authorization": f"Bearer {access_token}"}

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

@pytest.fixture
def test_tag(db):
    from app.models.models import Tag
    
    tag = Tag(name="Test Tag")
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag
