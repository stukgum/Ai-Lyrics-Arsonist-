from celery import current_task
import librosa
import madmom
import aubio
import numpy as np
import soundfile as sf
import subprocess
import tempfile
import os
import json
from typing import List, Tuple, Dict, Any
import yt_dlp
import requests
from urllib.parse import urlparse
import logging

from workers.celery_app import celery_app
from models.audio import AudioJob, JobStatus, AudioFeatures, Beat, Downbeat, Bar, Section, SpectralFeatures
from database import get_db
from utils.storage import download_from_s3, upload_file_to_s3
from utils.youtube import get_youtube_metadata
from utils.audio_analysis import (
    extract_beats_and_tempo,
    extract_key_and_harmony,
    segment_structure,
    extract_spectral_features
)
from utils.universal_url_processor import url_processor, get_universal_metadata

logger = logging.getLogger(__name__)

@celery_app.task(bind=True)
def process_audio_file(self, job_id: str, file_key: str):
    """Process uploaded audio file"""
    
    try:
        # Update job status
        update_job_status(job_id, JobStatus.PROCESSING, 0.1, "Starting audio processing...")
        
        # Download file from S3
        audio_data = download_from_s3(file_key)
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix=".tmp", delete=False) as temp_file:
            temp_file.write(audio_data)
            temp_path = temp_file.name
        
        try:
            # Transcode to WAV
            update_job_status(job_id, JobStatus.PROCESSING, 0.2, "Transcoding audio...")
            wav_path = transcode_to_wav(temp_path)
            
            # Analyze audio
            update_job_status(job_id, JobStatus.PROCESSING, 0.4, "Analyzing audio features...")
            features = analyze_audio(wav_path)
            
            # Upload processed WAV to S3
            update_job_status(job_id, JobStatus.PROCESSING, 0.8, "Saving processed audio...")
            with open(wav_path, 'rb') as f:
                processed_key = f"processed/{job_id}/audio.wav"
                processed_url = upload_file_to_s3(f.read(), processed_key, "audio/wav")
            
            # Save features to database
            update_job_status(job_id, JobStatus.PROCESSING, 0.9, "Saving analysis results...")
            save_features_to_db(job_id, features, processed_url)
            
            # Complete job
            update_job_status(job_id, JobStatus.COMPLETED, 1.0, "Audio processing completed")
            
        finally:
            # Cleanup temporary files
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            if 'wav_path' in locals() and os.path.exists(wav_path):
                os.unlink(wav_path)
                
    except Exception as e:
        logger.error(f"Audio processing failed for job {job_id}: {str(e)}")
        update_job_status(job_id, JobStatus.FAILED, 0.0, f"Processing failed: {str(e)}")
        raise

@celery_app.task(bind=True)
def process_audio_url(self, job_id: str, url: str, confirm_rights: bool, metadata_only: bool):
    """Process audio from URL"""
    
    try:
        update_job_status(job_id, JobStatus.PROCESSING, 0.1, "Processing URL...")
        
        if metadata_only:
            # Extract metadata only
            metadata = extract_url_metadata(url)
            save_metadata_to_db(job_id, metadata)
            update_job_status(job_id, JobStatus.COMPLETED, 1.0, "Metadata extraction completed")
            return
        
        if not confirm_rights:
            raise ValueError("Rights confirmation required for audio download")
        
        # Download audio
        update_job_status(job_id, JobStatus.PROCESSING, 0.2, "Downloading audio...")
        audio_path = download_audio_from_url(url)
        
        try:
            # Transcode to WAV
            update_job_status(job_id, JobStatus.PROCESSING, 0.4, "Transcoding audio...")
            wav_path = transcode_to_wav(audio_path)
            
            # Analyze audio
            update_job_status(job_id, JobStatus.PROCESSING, 0.6, "Analyzing audio features...")
            features = analyze_audio(wav_path)
            
            # Upload processed WAV to S3
            update_job_status(job_id, JobStatus.PROCESSING, 0.8, "Saving processed audio...")
            with open(wav_path, 'rb') as f:
                processed_key = f"processed/{job_id}/audio.wav"
                processed_url = upload_file_to_s3(f.read(), processed_key, "audio/wav")
            
            # Save features to database
            save_features_to_db(job_id, features, processed_url)
            
            # Complete job
            update_job_status(job_id, JobStatus.COMPLETED, 1.0, "URL processing completed")
            
        finally:
            # Cleanup temporary files
            if os.path.exists(audio_path):
                os.unlink(audio_path)
            if 'wav_path' in locals() and os.path.exists(wav_path):
                os.unlink(wav_path)
                
    except Exception as e:
        logger.error(f"URL processing failed for job {job_id}: {str(e)}")
        update_job_status(job_id, JobStatus.FAILED, 0.0, f"URL processing failed: {str(e)}")
        raise

def transcode_to_wav(input_path: str) -> str:
    """Transcode audio to 16-bit 44.1kHz WAV using ffmpeg"""
    
    output_path = input_path.replace('.tmp', '.wav')
    
    cmd = [
        'ffmpeg', '-i', input_path,
        '-ar', '44100',  # Sample rate
        '-ac', '1',      # Mono
        '-sample_fmt', 's16',  # 16-bit
        '-y',            # Overwrite output
        output_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg transcoding failed: {result.stderr}")
    
    return output_path

def analyze_audio(wav_path: str) -> AudioFeatures:
    """Comprehensive audio analysis using librosa, madmom, and aubio"""
    
    # Load audio
    y, sr = librosa.load(wav_path, sr=44100, mono=True)
    duration = len(y) / sr
    
    # Extract beats and tempo
    beats_data = extract_beats_and_tempo(y, sr)
    
    # Extract key and harmony
    key_data = extract_key_and_harmony(y, sr)
    
    # Segment structure
    sections = segment_structure(y, sr, beats_data['bars'])
    
    # Extract spectral features per beat
    spectral_features = extract_spectral_features(y, sr, beats_data['beat_times'])
    
    # Build AudioFeatures object
    features = AudioFeatures(
        duration=duration,
        sample_rate=sr,
        channels=1,
        bpm=beats_data['bpm'],
        tempo_confidence=beats_data['tempo_confidence'],
        time_signature=beats_data.get('time_signature'),
        key=key_data.get('key'),
        key_confidence=key_data.get('confidence'),
        beats=[Beat(timestamp=t, confidence=c) for t, c in zip(beats_data['beat_times'], beats_data['beat_confidences'])],
        downbeats=[Downbeat(timestamp=t, confidence=c) for t, c in zip(beats_data['downbeat_times'], beats_data['downbeat_confidences'])],
        bars=beats_data['bars'],
        sections=sections,
        spectral_features=spectral_features,
        analysis_version="1.0.0",
        processing_time=0.0  # Will be calculated
    )
    
    return features

def download_audio_from_url(url: str) -> str:
    """Download audio from any URL using universal processor"""
    return url_processor.download_audio(url)

def extract_url_metadata(url: str) -> Dict[str, Any]:
    """Extract metadata from any URL using universal processor"""
    return url_processor.get_metadata(url)

def update_job_status(job_id: str, status: JobStatus, progress: float, message: str):
    """Update job status in database"""
    
    with get_db() as db:
        job = db.query(AudioJob).filter(AudioJob.id == job_id).first()
        if job:
            job.status = status
            job.progress = progress
            job.status_message = message
            db.commit()

def save_features_to_db(job_id: str, features: AudioFeatures, processed_url: str):
    """Save extracted features to database"""
    
    with get_db() as db:
        job = db.query(AudioJob).filter(AudioJob.id == job_id).first()
        if job:
            job.features = features.dict()
            job.processed_file_url = processed_url
            db.commit()

def save_metadata_to_db(job_id: str, metadata: Dict[str, Any]):
    """Save metadata to database"""
    
    with get_db() as db:
        job = db.query(AudioJob).filter(AudioJob.id == job_id).first()
        if job:
            job.features = {'metadata': metadata}
            db.commit()
