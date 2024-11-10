# backend/app/api/users.py
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from typing import List

from ..core.security import SecurityUtils, get_current_user, get_current_admin_user
from ..db.session import get_db
from ..models.models import User, AuditLogEntry
from ..schemas.user import (
    UserCreate, 
    UserUpdate, 
    UserResponse, 
    UserListResponse,
    PasswordChange
)

router = APIRouter()

@router.get("/", response_model=List[UserListResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    List all users. Only accessible by admin users.
    """
    users = db.query(User).offset(skip).limit(limit).all()
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
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user information.
    """
    for field, value in user_update.dict(exclude_unset=True).items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    return current_user

@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change user password.
    """
    if not SecurityUtils.verify_password(
        password_data.current_password, 
        current_user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password"
        )

    if not SecurityUtils.validate_password(password_data.new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password does not meet security requirements"
        )

    current_user.hashed_password = SecurityUtils.get_password_hash(
        password_data.new_password
    )
    db.commit()

    # Log the password change
    audit_log = AuditLogEntry(
        user_id=current_user.id,
        action="change_password",
        details="Password changed successfully"
    )
    db.add(audit_log)
    db.commit()

    return {"message": "Password updated successfully"}

@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Create new user. Only accessible by admin users.
    """
    # Check if user exists
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate password
    if not SecurityUtils.validate_password(user_data.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password does not meet security requirements"
        )
    
    # Create user
    hashed_password = SecurityUtils.get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        is_admin=user_data.is_admin,
        is_active=True
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Log user creation
    audit_log = AuditLogEntry(
        user_id=current_user.id,
        action="create_user",
        details=f"Created user: {user_data.email}"
    )
    db.add(audit_log)
    db.commit()

    return db_user

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
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
    return user

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
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

    for field, value in user_update.dict(exclude_unset=True).items():
        setattr(user, field, value)

    # Log user update
    audit_log = AuditLogEntry(
        user_id=current_user.id,
        action="update_user",
        details=f"Updated user: {user.email}"
    )
    db.add(audit_log)
    
    db.commit()
    db.refresh(user)
    return user

@router.delete("/{user_id}")
async def delete_user(
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

    # Log user deletion
    audit_log = AuditLogEntry(
        user_id=current_user.id,
        action="delete_user",
        details=f"Deleted user: {user.email}"
    )
    db.add(audit_log)

    db.delete(user)
    db.commit()

    return {"message": "User deleted successfully"}

@router.post("/{user_id}/activate")
async def activate_user(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Activate user account. Only accessible by admin users.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.is_active = True

    # Log user activation
    audit_log = AuditLogEntry(
        user_id=current_user.id,
        action="activate_user",
        details=f"Activated user: {user.email}"
    )
    db.add(audit_log)

    db.commit()
    return {"message": "User activated successfully"}

@router.post("/{user_id}/deactivate")
async def deactivate_user(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Deactivate user account. Only accessible by admin users.
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
            detail="Cannot deactivate your own account"
        )

    user.is_active = False

    # Log user deactivation
    audit_log = AuditLogEntry(
        user_id=current_user.id,
        action="deactivate_user",
        details=f"Deactivated user: {user.email}"
    )
    db.add(audit_log)

    db.commit()
    return {"message": "User deactivated successfully"}

@router.post("/{user_id}/toggle-admin")
async def toggle_admin_status(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Toggle user's admin status. Only accessible by admin users.
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
            detail="Cannot modify your own admin status"
        )

    user.is_admin = not user.is_admin

    # Log admin status change
    audit_log = AuditLogEntry(
        user_id=current_user.id,
        action="toggle_admin",
        details=f"{'Granted' if user.is_admin else 'Revoked'} admin status for user: {user.email}"
    )
    db.add(audit_log)

    db.commit()
    return {"message": f"User admin status {'granted' if user.is_admin else 'revoked'} successfully"}
