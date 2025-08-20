from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime

from models.generation import Generation, GenerationStatus, GenerationRequest, GenerationResponse
from models.audio import AudioJob, JobStatus
from database import get_db
from workers.lyric_generator import generate_lyrics
from utils.auth import get_current_user, require_credits

router = APIRouter(prefix="/api/v1", tags=["generation"])

@router.post("/generate", response_model=GenerationResponse)
async def create_generation(
    request: GenerationRequest,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate lyrics for processed audio"""
    
    # Check if user has credits
    if not require_credits(current_user, 1):
        raise HTTPException(status_code=402, detail="Insufficient credits")
    
    # Verify job exists and is completed
    job = db.query(AudioJob).filter(AudioJob.id == request.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Audio job not found")
    
    if job.status != JobStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Audio processing not completed")
    
    if not job.features:
        raise HTTPException(status_code=400, detail="Audio features not available")
    
    # Create generation record
    generation_id = str(uuid.uuid4())
    generation = Generation(
        id=generation_id,
        user_id=current_user.id if current_user else None,
        job_id=request.job_id,
        genre=request.genre,
        mood=request.mood,
        explicit=request.explicit,
        language=request.language,
        rhyme_scheme=request.rhyme_scheme,
        syllables_per_beat=request.syllables_per_beat,
        target_structure=request.target_structure,
        status=GenerationStatus.PENDING,
        created_at=datetime.utcnow()
    )
    
    db.add(generation)
    db.commit()
    
    # Deduct credits
    if current_user:
        current_user.credits_remaining -= 1
        db.commit()
    
    # Queue generation task
    generate_lyrics.delay(generation_id)
    
    return GenerationResponse(
        generation_id=generation_id,
        status=GenerationStatus.PENDING,
        message="Lyric generation started"
    )

@router.get("/generation/{generation_id}")
async def get_generation(
    generation_id: str,
    db: Session = Depends(get_db)
):
    """Get generation results"""
    
    generation = db.query(Generation).filter(Generation.id == generation_id).first()
    if not generation:
        raise HTTPException(status_code=404, detail="Generation not found")
    
    return {
        "generation_id": generation.id,
        "status": generation.status,
        "progress": generation.progress or 0.0,
        "message": generation.status_message or "",
        "lyrics": generation.lyrics_json,
        "title": generation.title,
        "quality_metrics": {
            "rhyme_accuracy": generation.rhyme_accuracy,
            "syllable_accuracy": generation.syllable_accuracy,
            "structure_match": generation.structure_match
        },
        "export_urls": {
            "lrc": generation.lrc_url,
            "srt": generation.srt_url,
            "txt": generation.txt_url,
            "pdf": generation.pdf_url
        },
        "created_at": generation.created_at,
        "completed_at": generation.completed_at
    }

@router.get("/generations")
async def list_generations(
    skip: int = 0,
    limit: int = 20,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List user's generations"""
    
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    generations = db.query(Generation)\
        .filter(Generation.user_id == current_user.id)\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return [
        {
            "generation_id": gen.id,
            "job_id": gen.job_id,
            "status": gen.status,
            "title": gen.title,
            "genre": gen.genre,
            "mood": gen.mood,
            "created_at": gen.created_at,
            "completed_at": gen.completed_at
        }
        for gen in generations
    ]

@router.post("/generation/{generation_id}/regenerate")
async def regenerate_section(
    generation_id: str,
    section_name: str,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Regenerate a specific section"""
    
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    generation = db.query(Generation).filter(
        Generation.id == generation_id,
        Generation.user_id == current_user.id
    ).first()
    
    if not generation:
        raise HTTPException(status_code=404, detail="Generation not found")
    
    if generation.status != GenerationStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Generation not completed")
    
    # Check credits for regeneration
    if not require_credits(current_user, 1):
        raise HTTPException(status_code=402, detail="Insufficient credits for regeneration")
    
    # Deduct credits
    current_user.credits_remaining -= 1
    db.commit()
    
    # Queue regeneration task
    # This would be implemented in the lyric generator
    # regenerate_section.delay(generation_id, section_name)
    
    return {"message": f"Regenerating {section_name} section"}
