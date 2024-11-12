# backend/app/models/__init__.py
from .models import Base, User, Contact, Tag, contact_tags

__all__ = ["Base", "User", "Contact", "Tag", "contact_tags"]
