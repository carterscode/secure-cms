# backend/app/api/auth.py
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..core.config import settings
from ..core.security import SecurityUtils
from ..core.dependencies import get_current_user, get_current_active_user
from ..db.session import get_db
from ..models.models import User, AuditLogEntry, FailedLoginAttempt
from ..schemas.auth import (
    Token,
    UserCreate,
    TwoFactorResponse,
    TwoFactorVerify,
    PasswordChange,
    PasswordReset
)
from ..services.email import email_service

router = APIRouter()

@router.post("/register", response_model=Token)
async def register_user(
    request: Request,
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Register a new user."""
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

    # Create user
    hashed_password = SecurityUtils.get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        is_admin=user_data.is_admin
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Log the registration
    audit_log = AuditLogEntry(
        user_id=db_user.id,
        action="register",
        details="User registration",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    db.add(audit_log)
    db.commit()

    # Generate access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = SecurityUtils.create_access_token(
        data={"sub": db_user.email},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=TwoFactorResponse)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login user and generate 2FA token."""
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user or not SecurityUtils.verify_password(form_data.password, user.hashed_password):
        # Log failed attempt
        failed_attempt = FailedLoginAttempt(
            username=form_data.username,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent")
        )
        db.add(failed_attempt)
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    # Generate and store 2FA token
    secret, token = SecurityUtils.generate_2fa_token()
    user.two_factor_secret = secret
    db.commit()

    # Send 2FA token via email
    email_service.send_2fa_code(user.email, token)

    return {"message": "2FA code sent to your email"}

@router.post("/verify-2fa", response_model=Token)
async def verify_2fa(
    request: Request,
    verify_data: TwoFactorVerify,
    db: Session = Depends(get_db)
):
    """Verify 2FA token and issue access token."""
    user = db.query(User).filter(User.email == verify_data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

    if not SecurityUtils.verify_2fa_token(verify_data.token, user.two_factor_secret):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid 2FA token"
        )

    # Clear 2FA secret after successful verification
    user.two_factor_secret = None
    
    # Log successful login
    audit_log = AuditLogEntry(
        user_id=user.id,
        action="login",
        details="Successful login",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    db.add(audit_log)
    db.commit()

    # Generate access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = SecurityUtils.create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/change-password")
async def change_password(
    request: Request,
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Change user password."""
    if not SecurityUtils.verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password"
        )

    if not SecurityUtils.validate_password(password_data.new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password does not meet security requirements"
        )

    current_user.hashed_password = SecurityUtils.get_password_hash(password_data.new_password)
    
    # Log password change
    audit_log = AuditLogEntry(
        user_id=current_user.id,
        action="change_password",
        details="Password changed",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    db.add(audit_log)
    db.commit()

    return {"message": "Password updated successfully"}

@router.post("/reset-password")
async def request_password_reset(
    request: Request,
    password_reset: PasswordReset,
    db: Session = Depends(get_db)
):
    """Request password reset."""
    user = db.query(User).filter(User.email == password_reset.email).first()
    if user:
        # Generate reset token
        token = SecurityUtils.create_access_token(
            data={"sub": user.email, "type": "reset"},
            expires_delta=timedelta(hours=settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS)
        )
        
        user.password_reset_token = token
        user.password_reset_expires = datetime.utcnow() + timedelta(
            hours=settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS
        )
        
        # Log reset request
        audit_log = AuditLogEntry(
            user_id=user.id,
            action="request_password_reset",
            details="Password reset requested",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent")
        )
        db.add(audit_log)
        db.commit()

        # Send reset email
        email_service.send_password_reset_email(user.email, token)

    # Always return success to prevent email enumeration
    return {"message": "If the email exists, a password reset link has been sent"}
