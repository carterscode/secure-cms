# backend/app/api/contacts.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from ..core.dependencies import get_current_active_user
from ..db.session import get_db
from ..models.models import Contact, User, AuditLogEntry, Tag
from ..schemas.contact import ContactCreate, ContactUpdate, ContactResponse

router = APIRouter()

@router.get("/", response_model=List[ContactResponse])
async def list_contacts(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100,
    tag: Optional[str] = None
):
    query = db.query(Contact).filter(Contact.owner_id == current_user.id)
    
    if tag:
        query = query.join(Contact.tags).filter(Tag.name == tag)
    
    contacts = query.offset(skip).limit(limit).all()
    
    # Log action
    audit_log = AuditLogEntry(
        user_id=current_user.id,
        action="list_contacts",
        details=f"Listed contacts with filters: skip={skip}, limit={limit}, tag={tag}",
        ip_address=request.client.host
    )
    db.add(audit_log)
    db.commit()
    
    return contacts

@router.post("/", response_model=ContactResponse)
async def create_contact(
    request: Request,
    contact_in: ContactCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    contact = Contact(**contact_in.dict(), owner_id=current_user.id)
    db.add(contact)
    
    # Log action
    audit_log = AuditLogEntry(
        user_id=current_user.id,
        action="create_contact",
        details=f"Created contact: {contact_in.first_name} {contact_in.last_name}",
        ip_address=request.client.host
    )
    db.add(audit_log)
    
    db.commit()
    db.refresh(contact)
    return contact
