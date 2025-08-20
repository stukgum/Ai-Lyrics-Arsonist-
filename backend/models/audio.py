from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

Base = declarative_base()

class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class AudioJob(Base):
    __tablename__ = "audio_jobs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=True)
    filename = Column(String, nullable=True)
    source_url = Column(String, nullable=True)
    file_size = Column(Integer, nullable=True)
    file_url = Column(String, nullable=True)
    processed_file_url = Column(String, nullable=True)
    
    # Rights and legal
    rights_confirmed = Column(Boolean, default=False)
    metadata_only = Column(Boolean, default=False)
    consent_timestamp = Column(DateTime, nullable=True)
    
    # Processing status
    status = Column(String, default=JobStatus.PENDING)
    progress = Column(Float, default=0.0)
    status_message = Column(Text, nullable=True)
    
    # Audio features (JSON)
    features = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

# Pydantic models for API responses
class Beat(BaseModel):
    timestamp: float
    confidence: float

class Downbeat(BaseModel):
    timestamp: float
    confidence: float

class Bar(BaseModel):
    start: float
    end: float
    beat_count: int
    downbeat_timestamp: float

class Section(BaseModel):
    name: str  # intro, verse, chorus, bridge, outro
    start: float
    end: float
    bars: List[int]  # bar indices
    confidence: float

class SpectralFeatures(BaseModel):
    timestamp: float
    energy: float
    spectral_centroid: float
    spectral_rolloff: float
    zero_crossing_rate: float
    mfcc: List[float]

class AudioFeatures(BaseModel):
    # Basic info
    duration: float
    sample_rate: int
    channels: int
    
    # Tempo and rhythm
    bpm: float
    tempo_confidence: float
    time_signature: Optional[str]
    
    # Key and harmony
    key: Optional[str]
    key_confidence: Optional[float]
    
    # Beat tracking
    beats: List[Beat]
    downbeats: List[Downbeat]
    bars: List[Bar]
    
    # Structure
    sections: List[Section]
    
    # Spectral features per beat
    spectral_features: List[SpectralFeatures]
    
    # Analysis metadata
    analysis_version: str
    processing_time: float
    
class AudioMetadata(BaseModel):
    title: Optional[str]
    artist: Optional[str]
    album: Optional[str]
    duration: Optional[float]
    source: str  # "upload", "youtube", "http"
