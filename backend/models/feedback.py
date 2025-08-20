from sqlalchemy import Column, String, DateTime, Integer, Float, Text, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

Base = declarative_base()

class FeedbackType(str, Enum):
    RATING = "rating"
    EDIT = "edit"
    REPORT = "report"
    SUGGESTION = "suggestion"

class Feedback(Base):
    __tablename__ = "feedback"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    generation_id = Column(String, ForeignKey("generations.id"), nullable=False)
    
    # Feedback details
    type = Column(String, nullable=False)
    rating = Column(Integer, nullable=True)  # 1-5 stars
    comment = Column(Text, nullable=True)
    
    # Edit details (if type is "edit")
    edits = Column(JSON, nullable=True)  # {"line_index": 5, "old_text": "...", "new_text": "..."}
    
    # Metadata
    user_agent = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="feedback")
    generation = relationship("Generation", back_populates="feedback")

class FeedbackRequest(BaseModel):
    generation_id: str
    type: FeedbackType
    rating: Optional[int] = None
    comment: Optional[str] = None
    edits: Optional[Dict[str, Any]] = None
