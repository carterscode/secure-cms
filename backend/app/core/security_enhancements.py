# backend/app/core/security_enhancements.py
import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from typing import Optional

class DatabaseEncryption:
    """Handle database encryption for sensitive fields."""
    
    def __init__(self, key: Optional[str] = None):
        if key is None:
            key = os.getenv('DB_ENCRYPTION_KEY', None)
            if key is None:
                key = self._generate_key()
        self.fernet = Fernet(key)
    
    @staticmethod
    def _generate_key() -> bytes:
        """Generate a new encryption key."""
        salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(os.urandom(32)))
        return key
    
    def encrypt(self, data: str) -> str:
        """Encrypt sensitive data."""
        return self.fernet.encrypt(data.encode()).decode()
    
    def decrypt(self, data: str) -> str:
        """Decrypt sensitive data."""
        return self.fernet.decrypt(data.encode()).decode()

# SQLite security enhancements
SQLITE_SECURITY_PRAGMAS = [
    "PRAGMA journal_mode=WAL",           # Write-Ahead Logging for crash safety
    "PRAGMA synchronous=NORMAL",         # Balance between safety and performance
    "PRAGMA foreign_keys=ON",            # Enforce foreign key constraints
    "PRAGMA temp_store=MEMORY",          # Store temp tables in memory
    "PRAGMA auto_vacuum=FULL",           # Automatically reclaim unused space
    "PRAGMA secure_delete=ON",           # Overwrite deleted content
    "PRAGMA case_sensitive_like=ON",     # Make LIKE case-sensitive
]

# Additional security headers
SECURITY_HEADERS = {
    "X-Frame-Options": "DENY",
    "X-Content-Type-Options": "nosniff",
    "X-XSS-Protection": "1; mode=block",
    "Content-Security-Policy": (
        "default-src 'self'; "
        "img-src 'self' data:; "
        "style-src 'self' 'unsafe-inline'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
        "connect-src 'self'"
    ),
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
}

# File upload security
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.vcf'}
MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5MB

def validate_file(filename: str, content: bytes) -> bool:
    """Validate file upload."""
    # Check file extension
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False
    
    # Check file size
    if len(content) > MAX_UPLOAD_SIZE:
        return False
    
    # Check file content (basic mime type validation)
    import magic
    mime = magic.from_buffer(content, mime=True)
    
    # Define allowed mime types
    allowed_mimes = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.vcf': 'text/vcard'
    }
    
    return mime == allowed_mimes.get(ext, '')

# Database connection security
DB_CONNECTION_TIMEOUT = 30  # seconds
MAX_CONNECTIONS = 20
CONNECTION_RECYCLE_TIME = 3600  # 1 hour

# Rate limiting configuration
RATE_LIMIT_RULES = {
    "login": {"limit": 5, "period": 300},  # 5 attempts per 5 minutes
    "2fa": {"limit": 3, "period": 300},    # 3 attempts per 5 minutes
    "api": {"limit": 100, "period": 60}    # 100 requests per minute
}
