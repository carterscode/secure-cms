# backend/app/db/base_class.py
"""Import all models here for Alembic."""
from .base import Base  # noqa
from ..models.models import User, Contact, Tag, AuditLogEntry  # noqa
