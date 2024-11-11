# backend/app/core/security.py
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import secrets
import logging
from email.mime.text import MIMEText
import smtplib
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
import pyotp

from .config import settings

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
JWT_SECRET_KEY = secrets.token_urlsafe(32)  # Generate a secure random key
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 2FA configuration
TOTP_LENGTH = 6
TOTP_INTERVAL = 300  # 5 minutes

# Password requirements
PASSWORD_MIN_LENGTH = 12
PASSWORD_REGEX = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]"

# Security headers
SECURITY_HEADERS = {
    "X-Frame-Options": "DENY",
    "X-Content-Type-Options": "nosniff",
    "X-XSS-Protection": "1; mode=block",
    "Content-Security-Policy": "default-src 'self'; frame-ancestors 'none'",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Referrer-Policy": "strict-origin-when-cross-origin"
}

class SecurityUtils:
    @staticmethod
    def verify_token(token: str) -> Optional[str]:
        """Verify JWT token and return username if valid."""
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            return payload.get("sub")
        except JWTError:
            return None

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Generate password hash."""
        return pwd_context.hash(password)

    @staticmethod
    def validate_password(password: str) -> bool:
        """Validate password complexity requirements."""
        import re
        if len(password) < PASSWORD_MIN_LENGTH:
            return False
        if not re.match(PASSWORD_REGEX, password):
            return False
        return True

    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    @staticmethod
    def generate_2fa_token(email: str) -> str:
        """Generate a time-based one-time password."""
        totp = pyotp.TOTP(pyotp.random_base32(), interval=TOTP_INTERVAL)
        token = totp.now()
        
        try:
            msg = MIMEText(f"Your authentication code is: {token}")
            msg['Subject'] = "Secure CMS - Authentication Code"
            msg['From'] = "noreply@secure-cms.com"
            msg['To'] = email
            
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                if settings.SMTP_TLS:
                    server.starttls()
                if settings.SMTP_USER and settings.SMTP_PASSWORD:
                    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
        except Exception as e:
            logging.error(f"Failed to send 2FA email: {str(e)}")
            raise
            
        return token

    @staticmethod
    def verify_2fa_token(token: str, stored_token: str) -> bool:
        """Verify a 2FA token."""
        return secrets.compare_digest(token, stored_token)

    @staticmethod
    def log_failed_login(username: str, ip_address: str) -> None:
        """Log failed login attempts."""
        logging.warning(f"Failed login attempt for user {username} from IP {ip_address}")

class AuditLog:
    @staticmethod
    def log_action(user_id: int, action: str, details: str) -> None:
        """Log user actions for audit purposes."""
        logging.info(f"AUDIT: User {user_id} performed {action}: {details}")

# OAuth2 password bearer for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
