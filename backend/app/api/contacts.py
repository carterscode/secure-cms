# backend/app/api/contacts.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Query, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_

from ..core.dependencies import get_current_user
from ..db.session import get_db
from ..models.models import Contact, User, AuditLogEntry, Tag
from ..schemas.contact import ContactCreate, ContactUpdate, ContactResponse
from ..services.vcard_handler import VCardHandler

router = APIRouter()

@router.get("/", response_model=List[ContactResponse])
async def list_contacts(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    tags: Optional[List[str]] = Query(None),
    sort_by: Optional[str] = "name",
    sort_order: Optional[str] = "asc",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all contacts with filtering, sorting, and pagination.
    """
    query = db.query(Contact).filter(Contact.created_by == current_user.id)
    
    # Search functionality
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Contact.first_name.ilike(search_term),
                Contact.last_name.ilike(search_term),
                Contact.email.ilike(search_term),
                Contact.mobile_phone.ilike(search_term),
                Contact.company.ilike(search_term)
            )
        )
    
    # Tag filtering
    if tags:
        query = query.join(Contact.tags).filter(Tag.name.in_(tags))
    
    # Sorting
    if sort_by == "name":
        if sort_order == "asc":
            query = query.order_by(Contact.first_name.asc(), Contact.last_name.asc())
        else:
            query = query.order_by(Contact.first_name.desc(), Contact.last_name.desc())
    elif sort_by == "created":
        if sort_order == "asc":
            query = query.order_by(Contact.created_at.asc())
        else:
            query = query.order_by(Contact.created_at.desc())
    
    # Get total count before pagination
    total = query.count()
    
    # Apply pagination
    contacts = query.offset(skip).limit(limit).all()
    
    # Log the action
    audit_log = AuditLogEntry(
        user_id=current_user.id,
        action="list_contacts",
        details=f"Listed contacts with filters: search={search}, tags={tags}",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    db.add(audit_log)
    db.commit()
    
    return {
        "items": contacts,
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.post("/", response_model=ContactResponse)
async def create_contact(
    request: Request,
    contact: ContactCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new contact."""
    db_contact = Contact(**contact.dict(exclude={'tags'}), created_by=current_user.id)
    
    # Handle tags
    if contact.tags:
        for tag_name in contact.tags:
            tag = db.query(Tag).filter(Tag.name == tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.add(tag)
            db_contact.tags.append(tag)
    
    db.add(db_contact)
    
    # Log the action
    audit_log = AuditLogEntry(
        user_id=current_user.id,
        action="create_contact",
        details=f"Created contact: {contact.first_name} {contact.last_name}",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    db.add(audit_log)
    
    db.commit()
    db.refresh(db_contact)
    
    return db_contact

@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    request: Request,
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
    
    # Log the action
    audit_log = AuditLogEntry(
        user_id=current_user.id,
        action="view_contact",
        details=f"Viewed contact: {contact.id}",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    db.add(audit_log)
    db.commit()
    
    return contact

@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    request: Request,
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
    
    # Update basic fields
    update_data = contact_update.dict(exclude_unset=True, exclude={'tags'})
    for field, value in update_data.items():
        setattr(db_contact, field, value)
    
    # Update tags
    if contact_update.tags is not None:
        db_contact.tags = []
        for tag_name in contact_update.tags:
            tag = db.query(Tag).filter(Tag.name == tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.add(tag)
            db_contact.tags.append(tag)
    
    # Log the action
    audit_log = AuditLogEntry(
        user_id=current_user.id,
        action="update_contact",
        details=f"Updated contact: {contact_id}",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    db.add(audit_log)
    
    db.commit()
    db.refresh(db_contact)
    
    return db_contact

@router.delete("/{contact_id}")
async def delete_contact(
    request: Request,
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
    
    # Log the action before deletion
    audit_log = AuditLogEntry(
        user_id=current_user.id,
        action="delete_contact",
        details=f"Deleted contact: {contact.first_name} {contact.last_name}",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    db.add(audit_log)
    
    db.delete(contact)
    db.commit()
    
    return {"message": "Contact deleted"}

@router.post("/import")
async def import_contacts(
    request: Request,
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
            details=f"Imported {len(result['imported'])} contacts",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent")
        )
        db.add(audit_log)
        db.commit()
    
    return result

@router.post("/export")
async def export_contacts(
    request: Request,
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
        details=f"Exported {len(contacts)} contacts",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    db.add(audit_log)
    db.commit()
    
    return {
        "content": vcard_content,
        "filename": "contacts.vcf"
    }
