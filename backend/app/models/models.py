# backend/app/models/models.py
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Table, Text, LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Association table for contact tags (many-to-many)
contact_tags = Table('contact_tags', Base.metadata,
    Column('contact_id', Integer, ForeignKey('contacts.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    two_factor_secret = Column(String)

class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    job_title = Column(String)
    company = Column(String)
    photo = Column(LargeBinary)  # Limited to 5MB
    
    # Phone numbers
    mobile_phone = Column(String)
    home_phone = Column(String)
    work_phone = Column(String)
    main_phone = Column(String)
    iphone = Column(String)
    other_phone = Column(String)
    
    # Emails
    email = Column(String)
    work_email = Column(String)
    home_email = Column(String)
    icloud_email = Column(String)
    other_email = Column(String)
    
    # Web presence
    homepage = Column(String)
    facebook = Column(String)
    linkedin = Column(String)
    slack = Column(String)
    game_center = Column(String)
    facebook_messenger = Column(String)
    
    # Addresses
    home_address = Column(Text)
    work_address = Column(Text)
    other_address = Column(Text)
    
    birthday = Column(DateTime)
    notes = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    tags = relationship("Tag", secondary=contact_tags, back_populates="contacts")
    creator = relationship("User")

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    contacts = relationship("Contact", secondary=contact_tags, back_populates="tags")

class AuditLogEntry(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String)
    details = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    ip_address = Column(String)

    user = relationship("User")

class FailedLoginAttempt(Base):
    __tablename__ = "failed_login_attempts"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    ip_address = Column(String)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
