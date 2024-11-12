# backend/app/models/__init__.py
"""Models module initialization."""
from .models import User, Contact, Tag, AuditLogEntry

# This prevents the models from being registered twice
__all__ = ["User", "Contact", "Tag", "AuditLogEntry"]
