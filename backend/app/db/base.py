# backend/app/db/base.py
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Import all models here for Alembic
from ..models.models import User, Contact, Tag, AuditLogEntry  # noqa
