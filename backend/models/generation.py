from sqlalchemy import Column, String, DateTime, Boolean, Integer, Float, Text, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

Base = declarative_base()

class GenerationStatus(str, Enum):
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"

class Generation(Base):
    __tablename__ = "generations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    job_id = Column(String, ForeignKey("audio_jobs.id"), nullable=False)
    
    # Generation parameters
    genre = Column(String, nullable=False)
    mood = Column(String, nullable=False)
    explicit = Column(Boolean, default=False)
    language = Column(String, default="en")
    rhyme_scheme = Column(String, default="AABB")
    syllables_per_beat = Column(Float, default=1.4)
    
    # Structure preferences
    target_structure = Column(JSON, nullable=True)  # {"intro": 4, "verse": 16, "chorus": 8}
    
    # Generation results
    status = Column(String, default=GenerationStatus.PENDING)
    progress = Column(Float, default=0.0)
    status_message = Column(Text, nullable=True)
    
    # Generated content
    lyrics_json = Column(JSON, nullable=True)
    title = Column(String, nullable=True)
    estimated_syllables = Column(Integer, nullable=True)
    
    # Quality metrics
    rhyme_accuracy = Column(Float, nullable=True)
    syllable_accuracy = Column(Float, nullable=True)
    structure_match = Column(Float, nullable=True)
    
    # Export URLs
    lrc_url = Column(String, nullable=True)
    srt_url = Column(String, nullable=True)
    txt_url = Column(String, nullable=True)
    pdf_url = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="generations")
    job = relationship("AudioJob", back_populates="generations")
    feedback = relationship("Feedback", back_populates="generation")

# Pydantic models for API
class LyricLine(BaseModel):
    line_index: int
    text: str
    syllable_target: int
    rhyme_tag: str
    suggested_bar_start: int
    timestamp_start: Optional[float] = None
    timestamp_end: Optional[float] = None

class LyricSection(BaseModel):
    name: str  # verse, chorus, bridge, intro, outro, prechorus
    bars: List[int]
    lines: List[LyricLine]

class GeneratedLyrics(BaseModel):
    title: str
    sections: List[LyricSection]
    metadata: Dict[str, Any]

class GenerationRequest(BaseModel):
    job_id: str
    genre: str
    mood: str
    explicit: bool = False
    language: str = "en"
    rhyme_scheme: str = "AABB"
    syllables_per_beat: float = 1.4
    target_structure: Optional[Dict[str, int]] = None

class GenerationResponse(BaseModel):
    generation_id: str
    status: GenerationStatus
    message: str
