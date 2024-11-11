# backend/app/core/security.py
from datetime import datetime, timedelta
from typing import Optional, Union
import jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
import pyotp
import secrets
from email.mime.text import MIMEText
import smtplib
import logging
from .config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class SecurityUtils:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def validate_password(password: str) -> bool:
        """Validate password complexity requirements"""
        import re
        if len(password) < settings.PASSWORD_MIN_LENGTH:
            return False
        # Check for uppercase, lowercase, number and special character
        if not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]", password):
            return False
        return True

    @staticmethod
    def create_access_token(
        data: dict,
        expires_delta: Optional[timedelta] = None
    ) -> str:
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

    @classmethod
    def generate_2fa_token(cls, email: str) -> str:
        """Generate a time-based one-time password"""
        totp = pyotp.TOTP(pyotp.random_base32(), interval=settings.TWO_FACTOR_CODE_TTL_SECONDS)
        token = totp.now()
        
        try:
            cls._send_2fa_email(email, token)
        except Exception as e:
            logging.error(f"Failed to send 2FA email: {str(e)}")
            raise
            
        return token

    @staticmethod
    def verify_2fa_token(token: str, stored_token: str) -> bool:
        """Verify a 2FA token"""
        return secrets.compare_digest(token, stored_token)

    @staticmethod
    def _send_2fa_email(email: str, token: str) -> None:
        """Send 2FA token via email"""
        msg = MIMEText(f"Your authentication code is: {token}")
        msg['Subject'] = "Secure CMS - Authentication Code"
        msg['From'] = settings.SMTP_FROM_EMAIL
        msg['To'] = email
        
        try:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                if settings.SMTP_TLS:
                    server.starttls()
                if settings.SMTP_USER and settings.SMTP_PASSWORD:
                    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
        except Exception as e:
            logging.error(f"Failed to send email: {str(e)}")
            raise

    @staticmethod
    def log_failed_login(username: str, ip_address: str) -> None:
        """Log failed login attempts"""
        logging.warning(f"Failed login attempt for user {username} from IP {ip_address}")
        # Admin notification will be implemented here

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
