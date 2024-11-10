# backend/app/api/__init__.py
"""
backend/app/api/__init__.py
API routes package.
"""
from fastapi import APIRouter
from .auth import router as auth_router
from .contacts import router as contacts_router
from .users import router as users_router

router = APIRouter()
router.include_router(auth_router, prefix="/auth", tags=["auth"])
router.include_router(contacts_router, prefix="/contacts", tags=["contacts"])
router.include_router(users_router, prefix="/users", tags=["users"])