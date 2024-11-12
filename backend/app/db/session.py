# backend/app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Generator
import os

from ..core.config import settings
from .base import Base

# Create database directory if it doesn't exist
db_path = settings.DATABASE_URL.replace('sqlite:///', '')
if db_path != ':memory:':
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)

# Create SQLite engine with proper configuration
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    """
    Get database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db() -> None:
    """
    Initialize database tables.
    """
    Base.metadata.create_all(bind=engine)

def close_db() -> None:
    """
    Close database connections.
    """
    engine.dispose()
