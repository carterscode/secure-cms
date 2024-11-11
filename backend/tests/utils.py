# backend/tests/utils.py
import random
import string
from datetime import datetime, timedelta
from typing import Dict, Optional

from app.core.security import SecurityUtils
from app.core.config import settings

def random_lower_string(length: int = 32) -> str:
    """Generate a random lowercase string."""
    return ''.join(random.choices(string.ascii_lowercase, k=length))

def random_email() -> str:
    """Generate a random email address."""
    return f"{random_lower_string(10)}@{random_lower_string(6)}.com"

def random_phone() -> str:
    """Generate a random phone number."""
    return f"+1{''.join(random.choices(string.digits, k=10))}"

def create_test_token(email: str, expires_delta: Optional[timedelta] = None) -> str:
    """Create a test JWT token."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    return SecurityUtils.create_access_token(
        data={"sub": email, "exp": expire}
    )

def get_test_db_url() -> str:
    """Get test database URL."""
    return "sqlite:///:memory:"

def create_test_headers(email: str) -> Dict[str, str]:
    """Create test authentication headers."""
    token = create_test_token(email)
    return {"Authorization": f"Bearer {token}"}

def generate_test_password() -> str:
    """Generate a valid test password."""
    return "".join([
        random.choice(string.ascii_uppercase),
        random.choice(string.ascii_lowercase),
        random.choice(string.digits),
        random.choice("@$!%*?&"),
        random_lower_string(8)
    ])

def mock_2fa_token() -> str:
    """Generate a mock 2FA token."""
    return ''.join(random.choices(string.digits, k=6))

def create_test_file_content(size_bytes: int) -> bytes:
    """Create test file content of specified size."""
    return random_lower_string(size_bytes).encode()

def get_vcard_test_data() -> str:
    """Get test vCard data."""
    return """BEGIN:VCARD
VERSION:3.0
FN:John Doe
N:Doe;John;;;
EMAIL:john.doe@example.com
TEL:+11234567890
END:VCARD"""

def assert_valid_jwt(token: str) -> bool:
    """Assert that a token is a valid JWT."""
    try:
        SecurityUtils.decode_token(token)
        return True
    except:
        return False

def get_test_contact_data() -> Dict:
    """Get test contact data."""
    return {
        "first_name": "Test",
        "last_name": "Contact",
        "email": random_email(),
        "mobile_phone": random_phone(),
        "tags": ["Test"]
    }

def get_test_audit_data(user_id: int) -> Dict:
    """Get test audit log data."""
    return {
        "user_id": user_id,
        "action": "test_action",
        "details": "Test audit log entry",
        "ip_address": "127.0.0.1"
    }

def cleanup_test_files() -> None:
    """Clean up any test files created during testing."""
    import os
    import glob
    
    patterns = [
        "test_*.db",
        "*.test",
        "*.tmp"
    ]
    
    for pattern in patterns:
        for file in glob.glob(pattern):
            try:
                os.remove(file)
            except OSError:
                pass

def create_test_tag_data() -> Dict:
    """Get test tag data."""
    return {
        "name": f"Test Tag {random_lower_string(4)}"
    }
