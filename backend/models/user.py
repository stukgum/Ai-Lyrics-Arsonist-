from sqlalchemy import Column, String, DateTime, Boolean, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
import uuid

Base = declarative_base()

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"
    REVIEWER = "reviewer"

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=True)
    full_name = Column(String, nullable=True)
    
    # Authentication
    auth_provider = Column(String, default="auth0")  # auth0, clerk, etc.
    auth_provider_id = Column(String, nullable=True)
    
    # Role and permissions
    role = Column(String, default=UserRole.USER)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Billing
    stripe_customer_id = Column(String, nullable=True)
    subscription_tier = Column(String, default="free")  # free, pro, enterprise
    credits_remaining = Column(Integer, default=3)  # Free tier credits
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    audio_jobs = relationship("AudioJob", back_populates="user")
    generations = relationship("Generation", back_populates="user")
    feedback = relationship("Feedback", back_populates="user")
