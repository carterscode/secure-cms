# backend/app/schemas/__init__.py
from .auth import (
    Token,
    TokenData,
    UserBase,
    UserCreate,
    UserUpdate,
    UserLogin,
    UserResponse,
    UserInDB,
    TwoFactorResponse,
    TwoFactorVerify,
    PasswordChange,
    PasswordReset,
    PasswordResetConfirm,
)

from .contact import (
    ContactBase,
    ContactCreate,
    ContactUpdate,
    Contact,
    ContactResponse,
    ContactImportPreview,
    TagBase,
    TagCreate,
    Tag,
)

__all__ = [
    # Auth schemas
    "Token",
    "TokenData",
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserLogin",
    "UserResponse",
    "UserInDB",
    "TwoFactorResponse",
    "TwoFactorVerify",
    "PasswordChange",
    "PasswordReset",
    "PasswordResetConfirm",
    
    # Contact schemas
    "ContactBase",
    "ContactCreate",
    "ContactUpdate",
    "Contact",
    "ContactResponse",
    "ContactImportPreview",
    "TagBase",
    "TagCreate",
    "Tag",
]
