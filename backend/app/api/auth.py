# backend/app/api/auth.py
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
import secrets

from ..core.security import SecurityUtils, ACCESS_TOKEN_EXPIRE_MINUTES
from ..db.session import get_db
from ..models.models import User, FailedLoginAttempt
from ..schemas.auth import Token, TokenData, UserCreate, UserLogin, TwoFactorResponse
from ..services.email import EmailService

router = APIRouter()

@router.post("/register", response_model=Token)
async def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    # Check if user exists
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Validate password
    if not SecurityUtils.validate_password(user_data.password):
        raise HTTPException(
            status_code=400,
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
    
    # Generate access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
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
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not SecurityUtils.verify_password(form_data.password, user.hashed_password):
        # Log failed attempt
        failed_attempt = FailedLoginAttempt(
            username=form_data.username,
            ip_address=request.client.host
        )
        db.add(failed_attempt)
        db.commit()
        
        # Notify admin
        SecurityUtils.log_failed_login(form_data.username, request.client.host)
        
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )
    
    # Generate and send 2FA token
    two_factor_token = SecurityUtils.generate_2fa_token(user.email)
    
    # Store token temporarily (e.g., in Redis with short expiration)
    # This is handled by the SecurityUtils.generate_2fa_token method
    
    return {"message": "2FA code sent to your email"}

@router.post("/verify-2fa", response_model=Token)
async def verify_2fa(
    token: str,
    email: str,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials"
        )
    
    # Verify 2FA token
    if not SecurityUtils.verify_2fa_token(token, email):
        raise HTTPException(
            status_code=401,
            detail="Invalid 2FA token"
        )
    
    # Generate access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = SecurityUtils.create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/change-password")
async def change_password(
    current_password: str,
    new_password: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not SecurityUtils.verify_password(current_password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect password"
        )
    
    if not SecurityUtils.validate_password(new_password):
        raise HTTPException(
            status_code=400,
            detail="New password does not meet security requirements"
        )
    
    user.hashed_password = SecurityUtils.get_password_hash(new_password)
    db.commit()
    
    return {"message": "Password updated successfully"}

@router.post("/reset-password-request")
async def request_password_reset(
    email: str,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        # Return success even if user doesn't exist to prevent email enumeration
        return {"message": "If a user with this email exists, they will receive reset instructions"}
    
    # Generate reset token
    reset_token = secrets.token_urlsafe(32)
    user.reset_token = reset_token
    user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
    db.commit()
    
    # Send reset email
    EmailService.send_password_reset_email(user.email, reset_token)
    
    return {"message": "If a user with this email exists, they will receive reset instructions"}
