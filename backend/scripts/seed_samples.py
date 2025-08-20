#!/usr/bin/env python3
"""
Seed sample audio files and data for development
"""

import os
import sys
import json
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))

from database import get_db, create_tables
from models.audio import AudioJob, JobStatus
from models.user import User
from utils.storage import upload_file_to_s3

def create_sample_user():
    """Create a sample user for testing"""
    
    with get_db() as db:
        # Check if sample user exists
        user = db.query(User).filter(User.email == "demo@beatlyrics.com").first()
        if user:
            print("Sample user already exists")
            return user.id
        
        # Create sample user
        user = User(
            email="demo@beatlyrics.com",
            username="demo_user",
            full_name="Demo User",
            role="user",
            is_active=True,
            credits_remaining=10
        )
        
        db.add(user)
        db.commit()
        
        print(f"Created sample user: {user.id}")
        return user.id

def create_sample_audio_job(user_id: str):
    """Create a sample audio job with mock features"""
    
    # Mock audio features for a 4/4 hip-hop beat at 120 BPM
    mock_features = {
        "duration": 60.0,
        "sample_rate": 44100,
        "channels": 1,
        "bpm": 120.0,
        "tempo_confidence": 0.95,
        "time_signature": "4/4",
        "key": "C minor",
        "key_confidence": 0.8,
        "beats": [
            {"timestamp": i * 0.5, "confidence": 0.9} 
            for i in range(120)  # 120 beats in 60 seconds at 120 BPM
        ],
        "downbeats": [
            {"timestamp": i * 2.0, "confidence": 0.85} 
            for i in range(30)  # 30 downbeats (bars)
        ],
        "bars": [
            {
                "start": i * 2.0,
                "end": (i + 1) * 2.0,
                "beat_count": 4,
                "downbeat_timestamp": i * 2.0
            }
            for i in range(30)
        ],
        "sections": [
            {"name": "intro", "start": 0.0, "end": 8.0, "bars": [0, 1, 2, 3], "confidence": 0.8},
            {"name": "verse", "start": 8.0, "end": 24.0, "bars": [4, 5, 6, 7, 8, 9, 10, 11], "confidence": 0.9},
            {"name": "chorus", "start": 24.0, "end": 40.0, "bars": [12, 13, 14, 15, 16, 17, 18, 19], "confidence": 0.9},
            {"name": "verse", "start": 40.0, "end": 56.0, "bars": [20, 21, 22, 23, 24, 25, 26, 27], "confidence": 0.9},
            {"name": "outro", "start": 56.0, "end": 60.0, "bars": [28, 29], "confidence": 0.7}
        ],
        "spectral_features": [
            {
                "timestamp": i * 0.5,
                "energy": 0.7 + (i % 4) * 0.1,
                "spectral_centroid": 2000.0 + (i % 8) * 100,
                "spectral_rolloff": 4000.0,
                "zero_crossing_rate": 0.1,
                "mfcc": [1.0, 0.5, 0.3, 0.2, 0.1, 0.05, 0.02, 0.01, 0.005, 0.002, 0.001, 0.0005, 0.0002]
            }
            for i in range(120)
        ],
        "analysis_version": "1.0.0",
        "processing_time": 15.2
    }
    
    with get_db() as db:
        # Check if sample job exists
        job = db.query(AudioJob).filter(AudioJob.filename == "sample_beat_120bpm.mp3").first()
        if job:
            print("Sample audio job already exists")
            return job.id
        
        # Create sample job
        job = AudioJob(
            user_id=user_id,
            filename="sample_beat_120bpm.mp3",
            file_size=5242880,  # 5MB
            file_url="http://minio:9000/beatlyrics/samples/sample_beat_120bpm.mp3",
            processed_file_url="http://minio:9000/beatlyrics/processed/sample/audio.wav",
            status=JobStatus.COMPLETED,
            progress=1.0,
            status_message="Sample audio processing completed",
            features=mock_features
        )
        
        db.add(job)
        db.commit()
        
        print(f"Created sample audio job: {job.id}")
        return job.id

def main():
    """Main seeding function"""
    
    print("Seeding sample data...")
    
    # Create tables
    create_tables()
    
    # Create sample user
    user_id = create_sample_user()
    
    # Create sample audio job
    job_id = create_sample_audio_job(user_id)
    
    print("Sample data seeding completed!")
    print(f"Sample user ID: {user_id}")
    print(f"Sample job ID: {job_id}")
    print("\nYou can now:")
    print("1. Use the sample job ID to test lyric generation")
    print("2. Upload your own audio files")
    print("3. Test the complete pipeline")

if __name__ == "__main__":
    main()
