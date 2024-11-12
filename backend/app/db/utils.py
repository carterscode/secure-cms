# backend/app/db/utils.py
from sqlalchemy.orm import Session
from ..models.models import Base
from .session import engine

def init_db(db: Session) -> None:
    """Initialize database."""
    Base.metadata.create_all(bind=engine)

def close_db() -> None:
    """Close database connections."""
    engine.dispose()
