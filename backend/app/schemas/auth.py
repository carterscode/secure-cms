# backend/app/schemas/auth.py
from typing import Optional
from pydantic import BaseModel, EmailStr, constr, validator
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    username: constr(min_length=3, max_length=50)
    is_admin: bool = False

    class Config:
        from_attributes = True

class UserCreate(UserBase):
    password: constr(min_length=12)
    email: EmailStr
    username: constr(min_length=3, max_length=50)
    is_admin: bool = False

    @validator('password')
    def validate_password(cls, v):
        from ..core.security import SecurityUtils
        if not SecurityUtils.validate_password(v):
            raise ValueError(
                'Password must contain at least one uppercase letter, '
                'one lowercase letter, one number, and one special character'
            )
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "username": "testuser",
                "password": "Test1234!",
                "is_admin": False
            }
        }
