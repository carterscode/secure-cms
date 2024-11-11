# backend/app/db/session.py
import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base

from ..core.config import settings

# Enable SQLite foreign key support
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging for better concurrency
    cursor.close()

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},  # Required for SQLite
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

def get_db():
    """Dependency for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database and create tables."""
    # Create data directory if it doesn't exist
    if not settings.TESTING:
        os.makedirs(settings.DATABASE_DIR, exist_ok=True)
    
    # Import all models to ensure they're registered with SQLAlchemy
    from ..models.models import User, Contact, Tag, AuditLogEntry, FailedLoginAttempt  # noqa
    
    # Create all tables
    Base.metadata.create_all(bind=engine)

def close_db():
    """Close database connections."""
    engine.dispose()

def check_db_connection():
    """Check if database connection is healthy."""
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"Database connection check failed: {e}")
        return False
    finally:
        db.close()

def backup_database():
    """Create a backup of the database."""
    if settings.TESTING:
        return
        
    try:
        import shutil
        from datetime import datetime
        
        # Create backups directory
        backup_dir = os.path.join(settings.DATABASE_DIR, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        # Create backup filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(
            backup_dir, 
            f'backup_{timestamp}_{settings.DATABASE_FILENAME}'
        )
        
        # Copy database file
        db_file = os.path.join(settings.DATABASE_DIR, settings.DATABASE_FILENAME)
        shutil.copy2(db_file, backup_file)
        
        return backup_file
    except Exception as e:
        print(f"Database backup failed: {e}")
        return None
