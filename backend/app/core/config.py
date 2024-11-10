# backend/app/core/config.py
import secrets
from typing import Any, Dict, List, Optional, Union
from pydantic import AnyHttpUrl, EmailStr, field_validator, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    SERVER_NAME: str = "Secure CMS"
    SERVER_HOST: AnyHttpUrl = "http://localhost:8000"
    
    # CORS Configuration
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",  # React frontend
        "http://localhost:8000",  # Backend
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode='before')
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Database Configuration
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "secure_cms"

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """Compute the database URI from components."""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"

    # Email Configuration
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = 587
    SMTP_HOST: Optional[str] = "smtp.gmail.com"
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None

    # Security Configuration
    PASSWORD_MIN_LENGTH: int = 12
    PASSWORD_MAX_LENGTH: int = 128
    PASSWORD_RESET_TOKEN_EXPIRE_HOURS: int = 24
    JWT_ALGORITHM: str = "HS256"
    
    # Two-Factor Authentication
    TWO_FACTOR_AUTHENTICATION_ENABLED: bool = True
    TWO_FACTOR_CODE_TTL_SECONDS: int = 300  # 5 minutes
    
    # Rate Limiting
    RATE_LIMIT_ATTEMPTS: int = 5
    RATE_LIMIT_PERIOD: int = 300  # 5 minutes
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 5 * 1024 * 1024  # 5MB
    ALLOWED_UPLOAD_EXTENSIONS: List[str] = [".jpg", ".jpeg", ".png", ".gif"]

    # Audit Log
    AUDIT_LOG_RETENTION_DAYS: int = 90

    # Environment settings
    ENV: str = "development"
    DEBUG: bool = False
    TESTING: bool = False

    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow"
    )

    def get_database_url(self) -> str:
        """Get database URL based on environment."""
        if self.TESTING:
            return "sqlite:///./test.db"
        return self.SQLALCHEMY_DATABASE_URI

settings = Settings()
