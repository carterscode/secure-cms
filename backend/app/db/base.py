# backend/app/db/base.py
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declared_attr

class CustomBase:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

Base = declarative_base(cls=CustomBase)

# Import all models to register them
from ..models.models import User, Contact, Tag, AuditLogEntry  # noqa
