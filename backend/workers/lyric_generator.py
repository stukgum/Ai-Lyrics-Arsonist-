from celery import current_task
import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from workers.celery_app import celery_app
from models.generation import Generation, GenerationStatus
from models.audio import AudioJob
from database import get_db
from utils.llm_orchestrator import LLMOrchestrator
from utils.syllable_counter import SyllableCounter
from utils.rhyme_detector import RhymeDetector
from utils.content_moderator import ContentModerator
from utils.lyric_postprocessor import LyricPostProcessor

logger = logging.getLogger(__name__)

@celery_app.task(bind=True)
def generate_lyrics(self, generation_id: str):
    """Generate lyrics using AI with comprehensive post-processing"""
    
    try:
        # Update generation status
        update_generation_status(generation_id, GenerationStatus.GENERATING, 0.1, "Starting lyric generation...")
        
        # Get generation and job data
        with get_db() as db:
            generation = db.query(Generation).filter(Generation.id == generation_id).first()
            if not generation:
                raise ValueError("Generation not found")
            
            job = db.query(AudioJob).filter(AudioJob.id == generation.job_id).first()
            if not job or not job.features:
                raise ValueError("Audio job or features not found")
        
        # Initialize components
        llm_orchestrator = LLMOrchestrator()
        syllable_counter = SyllableCounter()
        rhyme_detector = RhymeDetector()
        content_moderator = ContentModerator()
        post_processor = LyricPostProcessor(syllable_counter, rhyme_detector)
        
        # Prepare input for LLM
        update_generation_status(generation_id, GenerationStatus.GENERATING, 0.2, "Preparing audio features...")
        llm_input = prepare_llm_input(generation, job.features)
        
        # Generate lyrics with LLM
        update_generation_status(generation_id, GenerationStatus.GENERATING, 0.4, "Generating lyrics with AI...")
        raw_lyrics = llm_orchestrator.generate_lyrics(llm_input)
        
        # Content moderation
        update_generation_status(generation_id, GenerationStatus.GENERATING, 0.6, "Checking content safety...")
        moderation_result = content_moderator.moderate_lyrics(raw_lyrics)
        if not moderation_result.is_safe:
            raise ValueError(f"Content moderation failed: {moderation_result.reason}")
        
        # Post-process lyrics
        update_generation_status(generation_id, GenerationStatus.GENERATING, 0.8, "Post-processing lyrics...")
        processed_lyrics = post_processor.process_lyrics(raw_lyrics, job.features)
        
        # Calculate quality metrics
        quality_metrics = calculate_quality_metrics(processed_lyrics, generation)
        
        # Save results
        update_generation_status(generation_id, GenerationStatus.GENERATING, 0.9, "Saving results...")
        save_generation_results(generation_id, processed_lyrics, quality_metrics)
        
        # Complete generation
        update_generation_status(generation_id, GenerationStatus.COMPLETED, 1.0, "Lyric generation completed")
        
    except Exception as e:
        logger.error(f"Lyric generation failed for {generation_id}: {str(e)}")
        update_generation_status(generation_id, GenerationStatus.FAILED, 0.0, f"Generation failed: {str(e)}")
        raise

def prepare_llm_input(generation: Generation, audio_features: Dict[str, Any]) -> Dict[str, Any]:
    """Prepare input JSON for LLM according to specification"""
    
    # Extract relevant features
    bpm = audio_features.get('bpm', 120)
    bars = audio_features.get('bars', [])
    key = audio_features.get('key', 'C major')
    tempo_confidence = audio_features.get('tempo_confidence', 0.8)
    sections = audio_features.get('sections', [])
    
    # Convert bars to simplified format
    simplified_bars = [
        {
            "start": bar.get('start', 0),
            "end": bar.get('end', 2),
            "beats": bar.get('beat_count', 4)
        }
        for bar in bars[:32]  # Limit to first 32 bars for manageable generation
    ]
    
    # Convert sections to simplified format
    simplified_sections = [
        {
            "name": section.get('name', 'verse'),
            "bars": section.get('bars', [])[:8]  # Limit bars per section
        }
        for section in sections
    ]
    
    return {
        "bpm": bpm,
        "bars": simplified_bars,
        "key": key,
        "tempo_confidence": tempo_confidence,
        "sections": simplified_sections,
        "user": {
            "genre": generation.genre,
            "mood": generation.mood,
            "explicit": generation.explicit,
            "language": generation.language,
            "rhyme": generation.rhyme_scheme,
            "syllables_per_beat": generation.syllables_per_beat
        }
    }

def calculate_quality_metrics(lyrics: Dict[str, Any], generation: Generation) -> Dict[str, float]:
    """Calculate quality metrics for generated lyrics"""
    
    rhyme_detector = RhymeDetector()
    syllable_counter = SyllableCounter()
    
    total_lines = 0
    correct_rhymes = 0
    syllable_accuracy = 0
    
    for section in lyrics.get('sections', []):
        for line in section.get('lines', []):
            total_lines += 1
            
            # Check syllable accuracy
            actual_syllables = syllable_counter.count_syllables(line['text'])
            target_syllables = line['syllable_target']
            if abs(actual_syllables - target_syllables) <= 1:  # Allow ±1 syllable tolerance
                syllable_accuracy += 1
    
    # Calculate rhyme accuracy (simplified)
    rhyme_accuracy = 0.8  # Placeholder - would need more complex rhyme scheme validation
    
    return {
        "rhyme_accuracy": rhyme_accuracy,
        "syllable_accuracy": syllable_accuracy / max(total_lines, 1),
        "structure_match": 0.9  # Placeholder - would validate against target structure
    }

def update_generation_status(generation_id: str, status: GenerationStatus, progress: float, message: str):
    """Update generation status in database"""
    
    with get_db() as db:
        generation = db.query(Generation).filter(Generation.id == generation_id).first()
        if generation:
            generation.status = status
            generation.progress = progress
            generation.status_message = message
            if status == GenerationStatus.COMPLETED:
                generation.completed_at = datetime.utcnow()
            db.commit()

def save_generation_results(generation_id: str, lyrics: Dict[str, Any], quality_metrics: Dict[str, float]):
    """Save generation results to database"""
    
    with get_db() as db:
        generation = db.query(Generation).filter(Generation.id == generation_id).first()
        if generation:
            generation.lyrics_json = lyrics
            generation.title = lyrics.get('title', 'Untitled')
            generation.estimated_syllables = lyrics.get('metadata', {}).get('estimated_total_syllables', 0)
            generation.rhyme_accuracy = quality_metrics.get('rhyme_accuracy')
            generation.syllable_accuracy = quality_metrics.get('syllable_accuracy')
            generation.structure_match = quality_metrics.get('structure_match')
            db.commit()
