# backend/app/db/session.py
import os
from contextlib import contextmanager
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base

from ..core.config import settings

# Enable SQLite optimizations
@event.listens_for(Engine, "connect")
def set_sqlite_pragmas(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys=ON")
    # Enable WAL mode for better concurrency
    cursor.execute("PRAGMA journal_mode=WAL")
    # Set synchronous mode for better performance while maintaining safety
    cursor.execute("PRAGMA synchronous=NORMAL")
    # Enable memory-mapped I/O for better performance
    cursor.execute("PRAGMA mmap_size=30000000000")
    # Set page size for better performance
    cursor.execute("PRAGMA page_size=4096")
    # Set cache size (in pages)
    cursor.execute("PRAGMA cache_size=-2000")  # ~8MB cache
    cursor.close()

def get_engine(url=None):
    """Create database engine with proper configuration."""
    return create_engine(
        url or settings.DATABASE_URL,
        connect_args={
            "check_same_thread": False,
            "timeout": 30  # Connection timeout in seconds
        },
        pool_pre_ping=True,
        pool_recycle=3600,  # Recycle connections every hour
    )

# Create engine
engine = get_engine()

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Create declarative base
Base = declarative_base()

@contextmanager
def get_db_session():
    """Context manager for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db():
    """Dependency for database sessions."""
    with get_db_session() as db:
        yield db

def init_db():
    """Initialize database and create tables."""
    if not settings.TESTING:
        # Create data directory if it doesn't exist
        os.makedirs(settings.DATABASE_DIR, exist_ok=True)
        
        # Set secure permissions
        os.chmod(settings.DATABASE_DIR, 0o700)
        
        # Create database file with secure permissions
        db_path = settings.DATABASE_URL.replace('sqlite:///', '')
        if not os.path.exists(db_path):
            open(db_path, 'a').close()
            os.chmod(db_path, 0o600)
    
    # Import all models
    from ..models.models import User, Contact, Tag, AuditLogEntry, FailedLoginAttempt  # noqa
    
    # Create tables
    Base.metadata.create_all(bind=engine)

def backup_database():
    """Create a backup of the database."""
    if settings.TESTING:
        return
        
    import shutil
    from datetime import datetime
    
    # Create backup directory
    backup_dir = os.path.join(settings.DATABASE_DIR, 'backups')
    os.makedirs(backup_dir, exist_ok=True)
    os.chmod(backup_dir, 0o700)
    
    # Create backup file
    db_path = settings.DATABASE_URL.replace('sqlite:///', '')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(backup_dir, f'backup_{timestamp}.db')
    
    # Perform backup
    with get_db_session() as db:
        db.execute('VACUUM')  # Optimize database before backup
        shutil.copy2(db_path, backup_path)
        os.chmod(backup_path, 0o600)

def vacuum_database():
    """Optimize database by removing unused space."""
    with get_db_session() as db:
        db.execute('VACUUM')
