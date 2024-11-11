# backend/app/api/users.py
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from typing import List

from ..core.security import SecurityUtils
from ..core.dependencies import get_current_user, get_current_admin_user
from ..db.session import get_db
from ..models.models import User, AuditLogEntry
from ..schemas.auth import (
    UserCreate, 
    UserUpdate, 
    UserResponse, 
    UserListResponse,
    PasswordChange
)
from ..services.email import email_service

router = APIRouter()

@router.get("/", response_model=List[UserListResponse])
async def list_users(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    List all users. Only accessible by admin users.
    """
    users = db.query(User).offset(skip).limit(limit).all()
    
    # Log action
    audit_log = AuditLogEntry(
        user_id=current_user.id,
        action="list_users",
        details=f"Listed users (skip={skip}, limit={limit})",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    db.add(audit_log)
    db.commit()
    
    return users

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user information.
    """
    return current_user

@router.patch("/me", response_model=UserResponse)
async def update_current_user(
    request: Request,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user information.
    """
    # Prevent changing admin status through this endpoint
    user_update_dict = user_update.dict(exclude_unset=True)
    user_update_dict.pop('is_admin', None)
    
    for field, value in user_update_dict.items():
        setattr(current_user, field, value)
    
    # Log action
    audit_log = AuditLogEntry(
        user_id=current_user.id,
        action="update_self",
        details="Updated own user profile",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    db.add(audit_log)
    
    db.commit()
    db.refresh(current_user)
    return current_user

@router.post("/", response_model=UserResponse)
async def create_user(
    request: Request,
    user_data: UserCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Create new user. Only accessible by admin users.
    """
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    if not SecurityUtils.validate_password(user_data.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password does not meet security requirements"
        )
    
    hashed_password = SecurityUtils.get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        is_admin=user_data.is_admin,
        is_active=True
    )
    
    db.add(db_user)
    
    # Log action
    audit_log = AuditLogEntry(
        user_id=current_user.id,
        action="create_user",
        details=f"Created user: {user_data.email}",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    db.add(audit_log)
    
    db.commit()
    db.refresh(db_user)
    
    # Send welcome email
    email_service.send_welcome_email(db_user.email)

    return db_user

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    request: Request,
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get user by ID. Only accessible by admin users.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Log action
    audit_log = AuditLogEntry(
        user_id=current_user.id,
        action="view_user",
        details=f"Viewed user: {user.email}",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    db.add(audit_log)
    db.commit()
    
    return user

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    request: Request,
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Update user information. Only accessible by admin users.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Prevent self-demotion
    if user.id == current_user.id and user_update.is_admin is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove own admin status"
        )

    for field, value in user_update.dict(exclude_unset=True).items():
        setattr(user, field, value)

    # Log action
    audit_log = AuditLogEntry(
        user_id=current_user.id,
        action="update_user",
        details=f"Updated user: {user.email}",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    db.add(audit_log)
    
    db.commit()
    db.refresh(user)
    return user

@router.delete("/{user_id}")
async def delete_user(
    request: Request,
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Delete user. Only accessible by admin users.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )

    # Log action before deletion
    audit_log = AuditLogEntry(
        user_id=current_user.id,
        action="delete_user",
        details=f"Deleted user: {user.email}",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    db.add(audit_log)

    db.delete(user)
    db.commit()

    return {"message": "User deleted successfully"}
