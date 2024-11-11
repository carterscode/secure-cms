# backend/tests/test_settings.py
"""
Test settings override for the application.
"""

def get_test_settings():
    """Return test settings."""
    return {
        "TESTING": True,
        "DATABASE_URL": "sqlite:///:memory:",
        "SECRET_KEY": "test_secret_key",
        "TWO_FACTOR_AUTHENTICATION_ENABLED": False,
        "BACKEND_CORS_ORIGINS": ["http://testserver"],
        "EMAIL_ENABLED": False
    }

def override_settings():
    """Override settings for testing."""
    from app.core.config import settings
    test_settings = get_test_settings()
    for key, value in test_settings.items():
        setattr(settings, key, value)
