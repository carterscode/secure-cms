# backend/app/core/security.py
# ... previous imports ...

class SecurityUtils:
    # ... previous methods ...

    @staticmethod
    def verify_token(token: str) -> Optional[str]:
        """
        Verify a token and return the username if valid.
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            return payload.get("sub")
        except JWTError:
            return None

    @staticmethod
    def verify_2fa_token(token: str, stored_token: str) -> bool:
        """
        Verify a 2FA token.
        For testing, always return True if 2FA is disabled.
        """
        if settings.TESTING or not settings.TWO_FACTOR_AUTHENTICATION_ENABLED:
            return True
        return secrets.compare_digest(token, stored_token)
