# backend/app/models/__init__.py
"""Models module initialization."""
from .user import User
from .contact import Contact
from ..db.base import Base

__all__ = ['Base', 'User', 'Contact']
