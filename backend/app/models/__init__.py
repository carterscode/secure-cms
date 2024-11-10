# backend/app/models/__init__.py
"""Models package for the application."""

# Import all models here
from .models import (
    Base,
    User,
    Contact,
    Tag,
    AuditLogEntry,
    FailedLoginAttempt,
    contact_tags
)

__all__ = [
    'Base',
    'User',
    'Contact',
    'Tag',
    'AuditLogEntry',
    'FailedLoginAttempt',
    'contact_tags'
]
