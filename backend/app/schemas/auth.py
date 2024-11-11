# backend/app/schemas/auth.py
from typing import Optional, List
from pydantic import BaseModel, EmailStr, constr, validator
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: List[str] = []

class UserBase(BaseModel):
    email: EmailStr
    username: constr(min_length=3, max_length=50)
    is_active: bool = True
    is_admin: bool = False

    class Config:
        from_attributes = True

class UserCreate(UserBase):
    password: constr(min_length=12)

    @validator('password')
    def validate_password(cls, v):
        from ..core.security import SecurityUtils
        if not SecurityUtils.validate_password(v):
            raise ValueError('Password must meet security requirements')
        return v

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[constr(min_length=3, max_length=50)] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None

    class Config:
        from_attributes = True

class UserInDB(UserBase):
    id: int
    hashed_password: str
    created_at: datetime
    updated_at: Optional[datetime] = None

class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TwoFactorResponse(BaseModel):
    message: str

class TwoFactorVerify(BaseModel):
    token: str
    email: EmailStr

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

    @validator('new_password')
    def validate_new_password(cls, v):
        from ..core.security import SecurityUtils
        if not SecurityUtils.validate_password(v):
            raise ValueError('Password must meet security requirements')
        return v
