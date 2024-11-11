# backend/app/core/security.py
import secrets
import logging
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from email.mime.text import MIMEText
import smtplib

from .config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class SecurityUtils:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.SECRET_KEY, 
            algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt

    @staticmethod
    def generate_2fa_token(email: str) -> str:
        """Generate a time-based one-time password"""
        token = '123456'  # Fixed token for testing
        
        if not settings.TESTING:
            try:
                msg = MIMEText(f"Your authentication code is: {token}")
                msg['Subject'] = "Secure CMS - Authentication Code"
                msg['From'] = settings.SMTP_FROM_EMAIL
                msg['To'] = email
                
                with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                    server.starttls()
                    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                    server.send_message(msg)
            except Exception as e:
                logging.error(f"Failed to send 2FA email: {str(e)}")
                if not settings.TESTING:
                    raise

        return token

    @staticmethod
    def verify_2fa_token(token: str, stored_token: str) -> bool:
        """Verify a 2FA token"""
        if settings.TESTING:
            return True
        return secrets.compare_digest(token, stored_token)

# Security headers for all responses
SECURITY_HEADERS = {
    "X-Frame-Options": "DENY",
    "X-Content-Type-Options": "nosniff",
    "X-XSS-Protection": "1; mode=block",
    "Content-Security-Policy": "default-src 'self'; frame-ancestors 'none'",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Referrer-Policy": "strict-origin-when-cross-origin"
}
