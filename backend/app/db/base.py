# backend/app/db/base.py
"""Base class for database models."""
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declared_attr

class CustomBase:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    # Common columns can be added here
    id = None  # Will be defined in specific models

Base = declarative_base(cls=CustomBase)
