# backend/app/schemas/contact.py
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr

class ContactBase(BaseModel):
    first_name: str
    last_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None

class ContactCreate(ContactBase):
    pass

class ContactUpdate(ContactBase):
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class ContactResponse(ContactBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    owner_id: int
    tags: List[str] = []

    class Config:
        from_attributes = True
