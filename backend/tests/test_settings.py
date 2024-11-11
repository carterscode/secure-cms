# backend/tests/test_settings.py
import pytest
from pydantic import ValidationError

from app.core.config import Settings

def test_settings_validation():
    """Test settings validation."""
    # Test valid settings
    settings = Settings(
        SECRET_KEY="test_key",
        BACKEND_CORS_ORIGINS=["http://localhost:3000"]
    )
    assert settings.SECRET_KEY == "test_key"
    assert len(settings.BACKEND_CORS_ORIGINS) == 1

def test_cors_origins_validation():
    """Test CORS origins validation."""
    # Test with string input
    settings = Settings(
        BACKEND_CORS_ORIGINS="http://localhost:3000,http://localhost:8000"
    )
    assert len(settings.BACKEND_CORS_ORIGINS) == 2
    assert all(isinstance(origin, str) for origin in settings.BACKEND_CORS_ORIGINS)

def test_database_url():
    """Test database URL generation."""
    settings = Settings(
        TESTING=True
    )
    assert "sqlite" in settings.DATABASE_URL

    settings = Settings(
        TESTING=False,
        DATABASE_FILENAME="test.db"
    )
    assert "test.db" in settings.DATABASE_URL

def test_password_settings():
    """Test password-related settings."""
    settings = Settings()
    assert settings.PASSWORD_MIN_LENGTH >= 12
    assert settings.PASSWORD_MAX_LENGTH > settings.PASSWORD_MIN_LENGTH

def test_jwt_settings():
    """Test JWT-related settings."""
    settings = Settings()
    assert settings.JWT_ALGORITHM == "HS256"
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES > 0

def test_email_settings():
    """Test email settings validation."""
    settings = Settings(
        SMTP_HOST="smtp.test.com",
        SMTP_PORT=587,
        SMTP_USER="test@test.com",
        SMTP_PASSWORD="password"
    )
    assert settings.SMTP_TLS is True
    assert settings.SMTP_PORT == 587

def test_file_upload_settings():
    """Test file upload settings."""
    settings = Settings()
    assert settings.MAX_UPLOAD_SIZE > 0
    assert len(settings.ALLOWED_UPLOAD_EXTENSIONS) > 0
    assert ".jpg" in settings.ALLOWED_UPLOAD_EXTENSIONS

def test_security_settings():
    """Test security-related settings."""
    settings = Settings()
    assert settings.TWO_FACTOR_AUTHENTICATION_ENABLED is True
    assert settings.TWO_FACTOR_CODE_TTL_SECONDS > 0
    assert settings.RATE_LIMIT_ATTEMPTS > 0

def test_audit_settings():
    """Test audit log settings."""
    settings = Settings()
    assert settings.AUDIT_LOG_RETENTION_DAYS > 0

def test_invalid_settings():
    """Test invalid settings handling."""
    with pytest.raises(ValidationError):
        Settings(
            PASSWORD_MIN_LENGTH=-1
        )

    with pytest.raises(ValidationError):
        Settings(
            SMTP_PORT="invalid"
        )

def test_environment_settings():
    """Test environment-specific settings."""
    settings = Settings(
        ENV="development"
    )
    assert settings.DEBUG is False

    settings = Settings(
        ENV="production"
    )
    assert settings.DEBUG is False
