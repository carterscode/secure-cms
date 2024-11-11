# backend/app/api/__init__.py
from fastapi import APIRouter

from .auth import router as auth_router
from .users import router as users_router
from .contacts import router as contacts_router
from .tags import router as tags_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["auth"])
router.include_router(users_router, prefix="/users", tags=["users"])
router.include_router(contacts_router, prefix="/contacts", tags=["contacts"])
router.include_router(tags_router, prefix="/tags", tags=["tags"])

__all__ = ["router"]
