# backend/app/core/__init__.py
"""
Core functionality package for Secure CMS.

This package contains core application functionality including:
- Security utilities and configurations
- Application settings and configuration
- Dependency management
- Core application constants
"""

from .config import Settings, settings
from .security import (
    SecurityUtils,
    SECURITY_HEADERS,
    JWT_ALGORITHM,
    JWT_SECRET_KEY,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    TOTP_LENGTH,
    TOTP_INTERVAL,
    PASSWORD_MIN_LENGTH,
    PASSWORD_REGEX,
)
from .dependencies import (
    get_current_user,
    get_current_active_user,
    get_current_admin_user,
    verify_token,
    oauth2_scheme,
)

# Version information
__version__ = "1.0.0"
__author__ = "Secure CMS Team"

# Security settings
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ["*"]
CORS_ALLOW_HEADERS = ["*"]

# Rate limiting settings
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX_REQUESTS = 100

# File upload settings
MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif'}

# Audit settings
AUDIT_LOG_ENABLED = True
AUDIT_LOG_RETENTION_DAYS = 90

# Cache settings
CACHE_TTL = 300  # seconds
CACHE_PREFIX = "secure_cms:"

# Export all public interfaces
__all__ = [
    # Classes
    "Settings",
    "SecurityUtils",
    
    # Settings instances
    "settings",
    
    # Security constants
    "SECURITY_HEADERS",
    "JWT_ALGORITHM",
    "JWT_SECRET_KEY",
    "ACCESS_TOKEN_EXPIRE_MINUTES",
    "TOTP_LENGTH",
    "TOTP_INTERVAL",
    "PASSWORD_MIN_LENGTH",
    "PASSWORD_REGEX",
    
    # Dependencies
    "get_current_user",
    "get_current_active_user",
    "get_current_admin_user",
    "verify_token",
    "oauth2_scheme",
    
    # Configuration constants
    "CORS_ALLOW_CREDENTIALS",
    "CORS_ALLOW_METHODS",
    "CORS_ALLOW_HEADERS",
    "RATE_LIMIT_WINDOW",
    "RATE_LIMIT_MAX_REQUESTS",
    "MAX_UPLOAD_SIZE",
    "ALLOWED_EXTENSIONS",
    "AUDIT_LOG_ENABLED",
    "AUDIT_LOG_RETENTION_DAYS",
    "CACHE_TTL",
    "CACHE_PREFIX",
]

def get_version():
    """Return the current version of the application."""
    return __version__

def get_security_context():
    """Return the current security context."""
    return {
        "jwt_algorithm": JWT_ALGORITHM,
        "access_token_expire_minutes": ACCESS_TOKEN_EXPIRE_MINUTES,
        "password_min_length": PASSWORD_MIN_LENGTH,
        "totp_enabled": True,
        "audit_enabled": AUDIT_LOG_ENABLED,
    }

def initialize_core():
    """Initialize core components."""
    # Verify security settings
    assert len(JWT_SECRET_KEY) >= 32, "JWT secret key must be at least 32 characters"
    assert PASSWORD_MIN_LENGTH >= 12, "Minimum password length must be at least 12"
    
    # Verify file upload settings
    assert MAX_UPLOAD_SIZE > 0, "Maximum upload size must be positive"
    assert len(ALLOWED_EXTENSIONS) > 0, "Must allow at least one file extension"
    
    # Verify rate limiting settings
    assert RATE_LIMIT_WINDOW > 0, "Rate limit window must be positive"
    assert RATE_LIMIT_MAX_REQUESTS > 0, "Maximum requests must be positive"
    
    # Verify audit settings
    assert AUDIT_LOG_RETENTION_DAYS > 0, "Audit log retention days must be positive"
    
    # Verify cache settings
    assert CACHE_TTL > 0, "Cache TTL must be positive"
    assert CACHE_PREFIX, "Cache prefix must not be empty"

def get_settings():
    """Return application settings."""
    return settings

def validate_security_settings():
    """Validate security settings."""
    security_context = get_security_context()
    assert all(security_context.values()), "All security settings must be enabled"
