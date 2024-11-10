# backend/app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

from ..core.config import settings

# Create database engine with connection pooling
engine = create_engine(
    settings.get_database_url(),
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,  # Recycle connections after 30 minutes
    pool_pre_ping=True,  # Enable connection health checks
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Create declarative base
Base = declarative_base()

# Dependency for database sessions
def get_db():
    """
    Dependency provider for database sessions.
    Ensures proper handling of database connections.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Database utilities
def init_db():
    """Initialize database tables"""
    # Import all models to ensure they're registered with SQLAlchemy
    from ..models.models import User, Contact, Tag, AuditLogEntry, FailedLoginAttempt  # noqa
    Base.metadata.create_all(bind=engine)

def close_db():
    """Close database connections"""
    engine.dispose()

# Connection health check
def check_db_connection():
    """Check if database connection is healthy"""
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"Database connection check failed: {e}")
        return False
    finally:
        db.close()

# Import all models to ensure they're registered with SQLAlchemy
from ..models import models  # noqa
