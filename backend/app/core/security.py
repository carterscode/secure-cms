# backend/app/core/security.py
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
import pyotp
import secrets
import logging

from .config import settings

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
JWT_SECRET_KEY = settings.SECRET_KEY
JWT_ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

# 2FA configuration
TOTP_LENGTH = 6
TOTP_INTERVAL = settings.TWO_FACTOR_CODE_TTL_SECONDS

# Password requirements
PASSWORD_MIN_LENGTH = settings.PASSWORD_MIN_LENGTH
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
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def validate_password(password: str) -> bool:
        """Validate password complexity requirements"""
        import re
        if len(password) < PASSWORD_MIN_LENGTH:
            return False
        if not re.match(PASSWORD_REGEX, password):
            return False
        return True

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    @staticmethod
    def decode_token(token: str) -> Optional[dict]:
        try:
            return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        except jwt.JWTError:
            return None

    @staticmethod
    def generate_2fa_token() -> tuple[str, str]:
        """Generate a new 2FA secret and token"""
        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret, interval=TOTP_INTERVAL)
        return secret, totp.now()

    @staticmethod
    def verify_2fa_token(token: str, secret: str) -> bool:
        """Verify a 2FA token"""
        if not secret or not token:
            return False
        totp = pyotp.TOTP(secret, interval=TOTP_INTERVAL)
        return totp.verify(token)

    @staticmethod
    def log_failed_login(username: str, ip_address: str):
        """Log failed login attempts"""
        logging.warning(f"Failed login attempt for user {username} from IP {ip_address}")

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
