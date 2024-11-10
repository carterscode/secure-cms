# backend/app/schemas/auth.py
from typing import Optional, List
from pydantic import BaseModel, EmailStr, constr, validator
from datetime import datetime

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: List[str] = []

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    username: constr(min_length=3, max_length=50)
    is_active: bool = True
    is_admin: bool = False

class UserCreate(UserBase):
    password: constr(min_length=12)

    @validator('password')
    def validate_password(cls, v):
        from ..core.security import SecurityUtils
        if not SecurityUtils.validate_password(v):
            raise ValueError(
                'Password must contain at least one uppercase letter, '
                'one lowercase letter, one number, and one special character'
            )
        return v

class UserLogin(BaseModel):
    username: str
    password: str

class UserInDB(UserBase):
    id: int
    hashed_password: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# 2FA schemas
class TwoFactorSetup(BaseModel):
    secret: str
    uri: str

class TwoFactorResponse(BaseModel):
    message: str

class TwoFactorVerify(BaseModel):
    token: str
    email: EmailStr

# Password change/reset schemas
class PasswordChange(BaseModel):
    current_password: str
    new_password: str

    @validator('new_password')
    def validate_new_password(cls, v):
        from ..core.security import SecurityUtils
        if not SecurityUtils.validate_password(v):
            raise ValueError(
                'Password must contain at least one uppercase letter, '
                'one lowercase letter, one number, and one special character'
            )
        return v

class PasswordReset(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

    @validator('new_password')
    def validate_new_password(cls, v):
        from ..core.security import SecurityUtils
        if not SecurityUtils.validate_password(v):
            raise ValueError(
                'Password must contain at least one uppercase letter, '
                'one lowercase letter, one number, and one special character'
            )
        return v
