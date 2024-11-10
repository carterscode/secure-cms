# backend/app/api/tags.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ..core.dependencies import get_current_user, get_current_admin_user
from ..db.session import get_db
from ..models.models import Tag, User, AuditLogEntry
from ..schemas.contact import TagCreate, Tag as TagSchema

router = APIRouter()

@router.get("/", response_model=List[TagSchema])
async def list_tags(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all available tags.
    """
    tags = db.query(Tag).all()
    return tags

@router.post("/", response_model=TagSchema)
async def create_tag(
    tag: TagCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new tag.
    """
    try:
        db_tag = Tag(name=tag.name)
        db.add(db_tag)
        
        # Log the action
        audit_log = AuditLogEntry(
            user_id=current_user.id,
            action="create_tag",
            details=f"Created tag: {tag.name}"
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
    tag_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific tag by ID.
    """
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
    return tag

@router.put("/{tag_id}", response_model=TagSchema)
async def update_tag(
    tag_id: int,
    tag_update: TagCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a tag.
    """
    db_tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not db_tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
    
    try:
        db_tag.name = tag_update.name
        
        # Log the action
        audit_log = AuditLogEntry(
            user_id=current_user.id,
            action="update_tag",
            details=f"Updated tag {tag_id}: {tag_update.name}"
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
    tag_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Delete a tag. Only accessible by admin users.
    """
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
    
    # Log the action
    audit_log = AuditLogEntry(
        user_id=current_user.id,
        action="delete_tag",
        details=f"Deleted tag: {tag.name}"
    )
    db.add(audit_log)
    
    db.delete(tag)
    db.commit()
    
    return {"message": "Tag deleted successfully"}

@router.get("/search/{name}", response_model=List[TagSchema])
async def search_tags(
    name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Search tags by name.
    """
    tags = db.query(Tag).filter(Tag.name.ilike(f"%{name}%")).all()
    return tags

@router.get("/stats/usage", response_model=List[dict])
async def get_tag_usage_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get usage statistics for tags.
    """
    tags = db.query(Tag).all()
    stats = [
        {
            "id": tag.id,
            "name": tag.name,
            "contact_count": len(tag.contacts)
        }
        for tag in tags
    ]
    return stats

@router.post("/merge/{source_id}/{target_id}")
async def merge_tags(
    source_id: int,
    target_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Merge two tags. Moves all contacts from source tag to target tag.
    Only accessible by admin users.
    """
    source_tag = db.query(Tag).filter(Tag.id == source_id).first()
    target_tag = db.query(Tag).filter(Tag.id == target_id).first()
    
    if not source_tag or not target_tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or both tags not found"
        )
    
    if source_id == target_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot merge tag with itself"
        )
    
    # Move all contacts from source to target
    for contact in source_tag.contacts:
        if target_tag not in contact.tags:
            contact.tags.append(target_tag)
    
    # Log the action
    audit_log = AuditLogEntry(
        user_id=current_user.id,
        action="merge_tags",
        details=f"Merged tag {source_tag.name} into {target_tag.name}"
    )
    db.add(audit_log)
    
    # Delete source tag
    db.delete(source_tag)
    db.commit()
    
    return {
        "message": f"Successfully merged tag '{source_tag.name}' into '{target_tag.name}'"
    }
