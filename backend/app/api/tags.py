# backend/app/api/tags.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ..core.dependencies import get_current_user, get_current_admin_user
from ..db.session import get_db
from ..models.models import Tag, User, AuditLogEntry
from ..schemas.contact import TagCreate, Tag as TagSchema

router = APIRouter()

@router.get("/", response_model=List[TagSchema])
async def list_tags(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all available tags."""
    tags = db.query(Tag).all()
    
    # Log action
    audit_log = AuditLogEntry(
        user_id=current_user.id,
        action="list_tags",
        details="Listed all tags",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    db.add(audit_log)
    db.commit()
    
    return tags

@router.post("/", response_model=TagSchema)
async def create_tag(
    request: Request,
    tag: TagCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new tag."""
    try:
        db_tag = Tag(name=tag.name)
        db.add(db_tag)
        
        # Log action
        audit_log = AuditLogEntry(
            user_id=current_user.id,
            action="create_tag",
            details=f"Created tag: {tag.name}",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent")
        )
        db.add(audit_log)
        
        db.commit()
        db.refresh(db_tag)
        return db_tag
        
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tag already exists"
        )

@router.get("/{tag_id}", response_model=TagSchema)
async def get_tag(
    request: Request,
    tag_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific tag by ID."""
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
    
    # Log action
    audit_log = AuditLogEntry(
        user_id=current_user.id,
        action="view_tag",
        details=f"Viewed tag: {tag.name}",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    db.add(audit_log)
    db.commit()
    
    return tag

@router.put("/{tag_id}", response_model=TagSchema)
async def update_tag(
    request: Request,
    tag_id: int,
    tag_update: TagCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a tag."""
    db_tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not db_tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
    
    try:
        db_tag.name = tag_update.name
        
        # Log action
        audit_log = AuditLogEntry(
            user_id=current_user.id,
            action="update_tag",
            details=f"Updated tag {tag_id}: {tag_update.name}",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent")
        )
        db.add(audit_log)
        
        db.commit()
        db.refresh(db_tag)
        return db_tag
        
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tag name already exists"
        )

@router.delete("/{tag_id}")
async def delete_tag(
    request: Request,
    tag_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Delete a tag. Only accessible by admin users."""
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
    
    # Check if tag is in use
    if len(tag.contacts) > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete tag while it is in use"
        )
    
    # Log action
    audit_log = AuditLogEntry(
        user_id=current_user.id,
        action="delete_tag",
        details=f"Deleted tag: {tag.name}",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    db.add(audit_log)
    
    db.delete(tag)
    db.commit()
    
    return {"message": "Tag deleted successfully"}
