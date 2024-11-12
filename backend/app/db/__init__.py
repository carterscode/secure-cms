# backend/app/db/__init__.py
"""Database module initialization."""
# Import models first to ensure they are registered
from ..models.models import Base, User, Contact, Tag, AuditLogEntry, contact_tags  # noqa
from .session import get_db, SessionLocal, engine

__all__ = [
    'Base',
    'get_db',
    'SessionLocal',
    'engine',
    'User',
    'Contact',
    'Tag',
    'AuditLogEntry'
]
