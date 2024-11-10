# backend/app/api/contacts.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Query
from sqlalchemy.orm import Session

from ..core.dependencies import get_current_user
from ..db.session import get_db
from ..models.models import Contact, User, AuditLogEntry, Tag
from ..schemas.contact import ContactCreate, ContactUpdate, ContactResponse
from ..services.vcard_handler import VCardHandler

router = APIRouter()

@router.get("/", response_model=List[ContactResponse])
async def list_contacts(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    tags: Optional[List[str]] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all contacts with optional filtering."""
    query = db.query(Contact).filter(Contact.created_by == current_user.id)
    
    if search:
        query = query.filter(
            (Contact.first_name.ilike(f"%{search}%")) |
            (Contact.last_name.ilike(f"%{search}%")) |
            (Contact.email.ilike(f"%{search}%")) |
            (Contact.mobile_phone.ilike(f"%{search}%"))
        )
    
    if tags:
        query = query.join(Contact.tags).filter(Tag.name.in_(tags))
    
    total = query.count()
    contacts = query.offset(skip).limit(limit).all()
    
    return {
        "items": contacts,
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.post("/", response_model=ContactResponse)
async def create_contact(
    contact: ContactCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new contact."""
    db_contact = Contact(**contact.dict(), created_by=current_user.id)
    
    # Handle tags
    if contact.tags:
        for tag_name in contact.tags:
            tag = db.query(Tag).filter(Tag.name == tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.add(tag)
            db_contact.tags.append(tag)
    
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    
    # Log the action
    audit_log = AuditLogEntry(
        user_id=current_user.id,
        action="create_contact",
        details=f"Created contact {db_contact.id}"
    )
    db.add(audit_log)
    db.commit()
    
    return db_contact

@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific contact."""
    contact = db.query(Contact).filter(
        Contact.id == contact_id,
        Contact.created_by == current_user.id
    ).first()
    
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: int,
    contact_update: ContactUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a contact."""
    db_contact = db.query(Contact).filter(
        Contact.id == contact_id,
        Contact.created_by == current_user.id
    ).first()
    
    if not db_contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    update_data = contact_update.dict(exclude_unset=True)
    
    # Handle tags update
    if 'tags' in update_data:
        db_contact.tags = []
        for tag_name in update_data['tags']:
            tag = db.query(Tag).filter(Tag.name == tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.add(tag)
            db_contact.tags.append(tag)
        del update_data['tags']
    
    for field, value in update_data.items():
        setattr(db_contact, field, value)
    
    db.commit()
    db.refresh(db_contact)
    
    # Log the action
    audit_log = AuditLogEntry(
        user_id=current_user.id,
        action="update_contact",
        details=f"Updated contact {contact_id}"
    )
    db.add(audit_log)
    db.commit()
    
    return db_contact

@router.delete("/{contact_id}")
async def delete_contact(
    contact_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a contact."""
    contact = db.query(Contact).filter(
        Contact.id == contact_id,
        Contact.created_by == current_user.id
    ).first()
    
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    db.delete(contact)
    
    # Log the action
    audit_log = AuditLogEntry(
        user_id=current_user.id,
        action="delete_contact",
        details=f"Deleted contact {contact_id}"
    )
    db.add(audit_log)
    db.commit()
    
    return {"message": "Contact deleted"}

@router.post("/import")
async def import_contacts(
    file: UploadFile = File(...),
    preview: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Import contacts from a VCard file."""
    if not file.filename.endswith('.vcf'):
        raise HTTPException(
            status_code=400,
            detail="Only VCard (.vcf) files are supported"
        )
    
    result = await VCardHandler.import_contacts(
        db=db,
        file=file,
        user_id=current_user.id,
        preview_only=preview
    )
    
    if not preview:
        # Log the action
        audit_log = AuditLogEntry(
            user_id=current_user.id,
            action="import_contacts",
            details=f"Imported {len(result['imported'])} contacts"
        )
        db.add(audit_log)
        db.commit()
    
    return result

@router.post("/export")
async def export_contacts(
    contact_ids: List[int],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export contacts to VCard format."""
    contacts = db.query(Contact).filter(
        Contact.id.in_(contact_ids),
        Contact.created_by == current_user.id
    ).all()
    
    if not contacts:
        raise HTTPException(status_code=404, detail="No contacts found")
    
    vcard_content = VCardHandler.export_contacts(contacts)
    
    # Log the action
    audit_log = AuditLogEntry(
        user_id=current_user.id,
        action="export_contacts",
        details=f"Exported {len(contacts)} contacts"
    )
    db.add(audit_log)
    db.commit()
    
    return {
        "content": vcard_content,
        "filename": "contacts.vcf"
    }
