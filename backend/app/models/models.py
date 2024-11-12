# backend/app/models/models.py
from datetime import datetime
from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, Table, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..db.base import Base

# Association table for contact tags
# Must be defined after Base but before the classes that use it
contact_tags = Table(
    'contact_tags',
    Base.metadata,
    Column('contact_id', Integer, ForeignKey('contacts.id', ondelete='CASCADE'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True),
    extend_existing=True
)

class Contact(Base):
    __tablename__ = 'contacts'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    job_title = Column(String, nullable=True)
    company = Column(String, nullable=True)
    email = Column(String, index=True, nullable=True)
    phone = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    owner_id = Column(Integer, ForeignKey("users.id", ondelete='CASCADE'))

    # Relationships
    owner = relationship("User", back_populates="contacts")
    tags = relationship("Tag", secondary=contact_tags, back_populates="contacts")

class Tag(Base):
    __tablename__ = 'tags'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    contacts = relationship("Contact", secondary=contact_tags, back_populates="tags")

class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    two_factor_secret = Column(String, nullable=True)

    # Relationships
    contacts = relationship("Contact", back_populates="owner", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLogEntry", back_populates="user", cascade="all, delete-orphan")

class AuditLogEntry(Base):
    __tablename__ = 'audit_logs'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete='CASCADE'))
    action = Column(String, nullable=False)
    details = Column(Text)
    ip_address = Column(String)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="audit_logs")
