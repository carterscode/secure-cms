# backend/app/schemas/contact.py
from typing import List, Optional
from datetime import datetime
from pydantic import EmailStr
from .base import BaseSchema, TimestampedSchema

class TagBase(BaseSchema):
    name: str

class TagCreate(TagBase):
    pass

class Tag(TagBase):
    id: int

class ContactBase(BaseSchema):
    first_name: str
    last_name: str
    job_title: Optional[str] = None
    company: Optional[str] = None
    mobile_phone: Optional[str] = None
    home_phone: Optional[str] = None
    work_phone: Optional[str] = None
    main_phone: Optional[str] = None
    iphone: Optional[str] = None
    other_phone: Optional[str] = None
    email: Optional[EmailStr] = None
    work_email: Optional[EmailStr] = None
    home_email: Optional[EmailStr] = None
    icloud_email: Optional[EmailStr] = None
    other_email: Optional[EmailStr] = None
    homepage: Optional[str] = None
    facebook: Optional[str] = None
    linkedin: Optional[str] = None
    slack: Optional[str] = None
    game_center: Optional[str] = None
    facebook_messenger: Optional[str] = None
    home_address: Optional[str] = None
    work_address: Optional[str] = None
    other_address: Optional[str] = None
    birthday: Optional[datetime] = None
    notes: Optional[str] = None
    tags: List[str] = []

class ContactCreate(ContactBase):
    pass

class ContactUpdate(ContactBase):
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class Contact(ContactBase, TimestampedSchema):
    id: int
    created_by: int
    tags: List[Tag] = []

class ContactResponse(Contact):
    pass

class ContactImportPreview(BaseSchema):
    contacts: List[ContactBase]
    duplicates: List[ContactBase]
    total: int
