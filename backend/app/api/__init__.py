# backend/app/api/__init__.py
"""API routes package."""
from fastapi import APIRouter

from .auth import router as auth_router
from .contacts import router as contacts_router
from .users import router as users_router
from .tags import router as tags_router

# Create API router
api_router = APIRouter()

# Include all routers with prefixes and tags
api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(contacts_router, prefix="/contacts", tags=["contacts"])
api_router.include_router(tags_router, prefix="/tags", tags=["tags"])

__all__ = ["api_router"]
