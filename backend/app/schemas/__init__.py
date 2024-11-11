# backend/app/schemas/__init__.py
"""Schema package for the application."""

from .auth import (
    Token,
    TokenData,
    UserBase,
    UserCreate,
    UserUpdate,
    UserLogin,
    UserInDB,
    UserResponse,
    UserListResponse,
    TwoFactorSetup,
    TwoFactorResponse,
    TwoFactorVerify,
    TwoFactorConfig,
    PasswordChange,
    PasswordReset,
    PasswordResetConfirm,
    AuditLogEntry,
    FailedLoginAttempt,
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
    "UserInDB",
    "UserResponse",
    "UserListResponse",
    "TwoFactorSetup",
    "TwoFactorResponse",
    "TwoFactorVerify",
    "TwoFactorConfig",
    "PasswordChange",
    "PasswordReset",
    "PasswordResetConfirm",
    "AuditLogEntry",
    "FailedLoginAttempt",
    
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
