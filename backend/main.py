import logging
import os
import re
import uuid
from datetime import datetime
from typing import Optional, List

import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, validator

from database import get_db, create_tables
from models.audio import AudioJob, AudioFeatures, JobStatus
from utils.storage import upload_file_to_s3
from workers.audio_processor import process_audio_file, process_audio_url
from workers.celery_app import celery_app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="BeatLyrics API",
    description="AI-powered beat-synced lyric generation",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
create_tables()

class UploadResponse(BaseModel):
    job_id: str
    message: str

class URLIngestRequest(BaseModel):
    url: str
    confirm_rights: bool
    metadata_only: Optional[bool] = False
    
    @validator('url')
    def validate_url(cls, v):
        if not v or not v.strip():
            raise ValueError('URL cannot be empty')
        
        v = v.strip()
        
        # Validate URL starts with http/https
        if not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError('URL must start with http:// or https://')
        
        # Validate URL structure
        try:
            from urllib.parse import urlparse
            parsed = urlparse(v)
            if not parsed.netloc:
                raise ValueError('Invalid URL: no domain found')
            return v
        except Exception as e:
            raise ValueError(f'Invalid URL format: {str(e)}')

class JobStatusResponse(BaseModel):
    job_id: str
    status: JobStatus
    progress: float
    message: str
    created_at: datetime
    updated_at: datetime

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@app.post("/api/v1/upload", response_model=UploadResponse)
async def upload_audio(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user_id: Optional[str] = Form(None)
):
    """Upload audio file for processing"""
    
    # Validate file type and size
    allowed_types = ['audio/wav', 'audio/mpeg', 'audio/mp4', 'audio/aac', 'audio/ogg', 'audio/flac']
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Unsupported audio format")
    
    # Check file size (200MB limit)
    file_size = 0
    content = await file.read()
    file_size = len(content)
    if file_size > 200 * 1024 * 1024:  # 200MB
        raise HTTPException(status_code=400, detail="File too large (max 200MB)")
    
    # Generate job ID and upload to S3
    job_id = str(uuid.uuid4())
    file_key = f"uploads/{job_id}/{file.filename}"
    
    try:
        # Upload to S3
        upload_url = upload_file_to_s3(content, file_key, file.content_type)
        
        # Create job record
        with get_db() as db:
            job = AudioJob(
                id=job_id,
                user_id=user_id,
                filename=file.filename,
                file_size=file_size,
                file_url=upload_url,
                status=JobStatus.PENDING,
                created_at=datetime.utcnow()
            )
            db.add(job)
            db.commit()
        
        # Queue processing task
        process_audio_file.delay(job_id, file_key)
        
        return UploadResponse(
            job_id=job_id,
            message="File uploaded successfully, processing started"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/api/v1/ingest-url", response_model=UploadResponse)
async def ingest_url(request: URLIngestRequest):
    """Process audio from URL with rights confirmation"""
    
    if not request.confirm_rights and not request.metadata_only:
        raise HTTPException(
            status_code=400, 
            detail="Rights confirmation required for audio download"
        )
    
    job_id = str(uuid.uuid4())
    
    try:
        # Create job record
        with get_db() as db:
            job = AudioJob(
                id=job_id,
                source_url=request.url,
                rights_confirmed=request.confirm_rights,
                metadata_only=request.metadata_only,
                status=JobStatus.PENDING,
                created_at=datetime.utcnow()
            )
            db.add(job)
            db.commit()
        
        # Queue URL processing task
        process_audio_url.delay(job_id, request.url, request.confirm_rights, request.metadata_only)
        
        return UploadResponse(
            job_id=job_id,
            message="URL processing started"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"URL processing failed: {str(e)}")

@app.get("/api/v1/jobs/{job_id}/status", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """Get job processing status"""
    
    with get_db() as db:
        job = db.query(AudioJob).filter(AudioJob.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return JobStatusResponse(
            job_id=job.id,
            status=job.status,
            progress=job.progress or 0.0,
            message=job.status_message or "",
            created_at=job.created_at,
            updated_at=job.updated_at or job.created_at
        )

@app.get("/api/v1/jobs/{job_id}/features")
async def get_job_features(job_id: str):
    """Get extracted audio features"""
    
    with get_db() as db:
        job = db.query(AudioJob).filter(AudioJob.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        if job.status != JobStatus.COMPLETED:
            raise HTTPException(status_code=400, detail="Job not completed yet")
        
        if not job.features:
            raise HTTPException(status_code=404, detail="Features not found")
        
        return job.features

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
