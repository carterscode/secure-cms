# backend/app/schemas/auth.py
from typing import Optional, List
from pydantic import BaseModel, EmailStr, constr, field_validator
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: Optional[str] = None
    scopes: List[str] = []

class UserBase(BaseModel):
    email: EmailStr
    username: constr(min_length=3, max_length=50)
    is_active: bool = True
    is_admin: bool = False

    model_config = {
        "from_attributes": True
    }

class UserCreate(UserBase):
    password: constr(min_length=12)

    @field_validator('password')
    def validate_password(cls, v):
        # Password validation logic will be handled in the service layer
        return v

class UserUpdate(UserBase):
    email: Optional[EmailStr] = None
    username: Optional[constr(min_length=3, max_length=50)] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None

class UserInDB(UserBase):
    id: int
    hashed_password: str
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

class PasswordReset(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str
