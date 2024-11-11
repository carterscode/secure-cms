# backend/app/core/__init__.py
"""Core package for application functionality."""
from .config import Settings, settings
from .security import SecurityUtils, SECURITY_HEADERS
from .dependencies import get_current_user, get_current_admin_user

__version__ = "1.0.0"

def get_version():
    """Return the current version of the application."""
    return __version__

def initialize_core():
    """Initialize core application components."""
    # Initialize security components
    SecurityUtils.initialize()
    # Validate settings
    settings.validate()
    return True

__all__ = [
    'Settings',
    'settings',
    'SecurityUtils',
    'SECURITY_HEADERS',
    'get_current_user',
    'get_current_admin_user',
    'get_version',
    'initialize_core',
]
