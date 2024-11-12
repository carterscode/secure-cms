# backend/app/api/__init__.py
"""API module initialization."""
from fastapi import APIRouter
from .auth import router as auth_router
from .contacts import router as contacts_router

router = APIRouter()
router.include_router(auth_router, prefix="/auth", tags=["auth"])
router.include_router(contacts_router, prefix="/contacts", tags=["contacts"])

__all__ = ['router']
