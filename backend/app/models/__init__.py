# backend/app/models/__init__.py
"""Models module initialization."""
from ..db.base import Base
from .user import User
from .contact import Contact

__all__ = ['Base', 'User', 'Contact']
