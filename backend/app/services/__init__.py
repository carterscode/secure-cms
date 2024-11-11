# backend/app/services/__init__.py
"""Services package."""

from .email import email_service
from .vcard_handler import VCardHandler

__all__ = [
    "email_service",
    "VCardHandler",
]
