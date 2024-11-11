# backend/app/api/auth.py
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..core.security import SecurityUtils
from ..core.config import settings
from ..core.dependencies import get_current_active_user
from ..db.session import get_db
from ..models.models import User
from ..schemas.auth import (
    Token,
    UserCreate,
    UserLogin,
    TwoFactorResponse,
    TwoFactorVerify,
    PasswordChange
)

router = APIRouter()

@router.post("/register", response_model=Token)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

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

    access_token = SecurityUtils.create_access_token(data={"sub": db_user.email})
    return Token(access_token=access_token, token_type="bearer")

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not SecurityUtils.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = SecurityUtils.create_access_token(data={"sub": user.email})
    return Token(access_token=access_token, token_type="bearer")

@router.post("/password-change", response_model=dict)
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if not SecurityUtils.verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password"
        )

    hashed_password = SecurityUtils.get_password_hash(password_data.new_password)
    current_user.hashed_password = hashed_password
    db.commit()

    return {"message": "Password updated successfully"}
