import librosa
import madmom
import aubio
import numpy as np
from typing import Dict, List, Tuple, Any
from models.audio import Bar, Section, SpectralFeatures

def extract_beats_and_tempo(y: np.ndarray, sr: int) -> Dict[str, Any]:
    """Extract beats, tempo, and bar structure using librosa and madmom"""
    
    # Use madmom for more accurate beat tracking
    proc = madmom.features.beats.DBNBeatTrackingProcessor(fps=100)
    act = madmom.features.beats.RNNBeatProcessor()(y)
    beat_times = proc(act)
    
    # Estimate tempo
    tempo, beats_librosa = librosa.beat.beat_track(y=y, sr=sr, units='time')
    
    # Use madmom beats but librosa tempo as fallback
    if len(beat_times) == 0:
        beat_times = beats_librosa
        tempo_confidence = 0.5
    else:
        # Calculate tempo from madmom beats
        if len(beat_times) > 1:
            intervals = np.diff(beat_times)
            tempo = 60.0 / np.median(intervals)
            tempo_confidence = 1.0 - np.std(intervals) / np.mean(intervals)
        else:
            tempo_confidence = 0.3
    
    # Detect downbeats using madmom
    downbeat_proc = madmom.features.downbeats.DBNDownBeatTrackingProcessor(beats_per_bar=[4], fps=100)
    downbeat_act = madmom.features.downbeats.RNNDownBeatProcessor()(y)
    downbeats = downbeat_proc(downbeat_act)
    
    # Extract downbeat times and beat positions
    downbeat_times = downbeats[:, 0] if len(downbeats) > 0 else []
    beat_positions = downbeats[:, 1] if len(downbeats) > 0 else []
    
    # Estimate time signature from beat positions
    if len(beat_positions) > 0:
        unique_positions = np.unique(beat_positions)
        beats_per_bar = len(unique_positions)
        time_signature = f"{beats_per_bar}/4"
    else:
        time_signature = "4/4"  # Default
        beats_per_bar = 4
    
    # Create bar structure
    bars = create_bar_structure(beat_times, downbeat_times, beats_per_bar)
    
    # Generate confidence scores (simplified)
    beat_confidences = np.ones(len(beat_times)) * 0.8
    downbeat_confidences = np.ones(len(downbeat_times)) * 0.7
    
    return {
        'bpm': float(tempo),
        'tempo_confidence': float(tempo_confidence),
        'time_signature': time_signature,
        'beat_times': beat_times.tolist(),
        'beat_confidences': beat_confidences.tolist(),
        'downbeat_times': downbeat_times.tolist(),
        'downbeat_confidences': downbeat_confidences.tolist(),
        'bars': bars
    }

def extract_key_and_harmony(y: np.ndarray, sr: int) -> Dict[str, Any]:
    """Extract key and harmonic information using librosa"""
    
    # Chromagram for key detection
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    
    # Key detection using template matching
    key_templates = librosa.key_to_notes(['C:maj', 'C:min', 'C#:maj', 'C#:min', 
                                         'D:maj', 'D:min', 'D#:maj', 'D#:min',
                                         'E:maj', 'E:min', 'F:maj', 'F:min',
                                         'F#:maj', 'F#:min', 'G:maj', 'G:min',
                                         'G#:maj', 'G#:min', 'A:maj', 'A:min',
                                         'A#:maj', 'A#:min', 'B:maj', 'B:min'])
    
    # Simple key detection (can be improved with more sophisticated methods)
    chroma_mean = np.mean(chroma, axis=1)
    
    # Find the most prominent pitch class
    key_idx = np.argmax(chroma_mean)
    key_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    # Determine major/minor (simplified heuristic)
    # This is a basic implementation - real key detection is more complex
    major_profile = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
    minor_profile = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
    
    # Rotate profiles to match detected key
    major_rotated = np.roll(major_profile, key_idx)
    minor_rotated = np.roll(minor_profile, key_idx)
    
    major_correlation = np.corrcoef(chroma_mean, major_rotated)[0, 1]
    minor_correlation = np.corrcoef(chroma_mean, minor_rotated)[0, 1]
    
    if major_correlation > minor_correlation:
        key = f"{key_names[key_idx]} major"
        confidence = float(major_correlation)
    else:
        key = f"{key_names[key_idx]} minor"
        confidence = float(minor_correlation)
    
    return {
        'key': key,
        'confidence': max(0.0, min(1.0, confidence))  # Clamp to [0, 1]
    }

def segment_structure(y: np.ndarray, sr: int, bars: List[Bar]) -> List[Section]:
    """Segment audio into structural sections using spectral features"""
    
    # Extract features for segmentation
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
    
    # Combine features
    features = np.vstack([mfcc, chroma, spectral_contrast])
    
    # Use librosa's segment boundaries
    boundaries = librosa.segment.agglomerative(features, k=None)
    boundary_times = librosa.frames_to_time(boundaries, sr=sr)
    
    # Map boundaries to bars
    sections = []
    section_names = ['intro', 'verse', 'chorus', 'verse', 'chorus', 'bridge', 'chorus', 'outro']
    
    for i, (start_time, end_time) in enumerate(zip(boundary_times[:-1], boundary_times[1:])):
        # Find bars that overlap with this section
        section_bars = []
        for j, bar in enumerate(bars):
            if bar.start >= start_time and bar.end <= end_time:
                section_bars.append(j)
        
        if section_bars:  # Only add sections with bars
            section_name = section_names[i % len(section_names)]
            sections.append(Section(
                name=section_name,
                start=start_time,
                end=end_time,
                bars=section_bars,
                confidence=0.7  # Simplified confidence
            ))
    
    return sections

def extract_spectral_features(y: np.ndarray, sr: int, beat_times: List[float]) -> List[SpectralFeatures]:
    """Extract spectral features aligned to beats"""
    
    features = []
    
    # Convert beat times to sample indices
    beat_samples = librosa.time_to_samples(beat_times, sr=sr)
    
    # Extract features for each beat segment
    for i, beat_sample in enumerate(beat_samples[:-1]):
        start_sample = beat_sample
        end_sample = beat_samples[i + 1] if i + 1 < len(beat_samples) else len(y)
        
        # Extract segment
        segment = y[start_sample:end_sample]
        
        if len(segment) > 0:
            # Spectral features
            energy = float(np.sum(segment ** 2))
            spectral_centroids = librosa.feature.spectral_centroid(y=segment, sr=sr)
            spectral_rolloff = librosa.feature.spectral_rolloff(y=segment, sr=sr)
            zero_crossing_rate = librosa.feature.zero_crossing_rate(segment)
            mfcc = librosa.feature.mfcc(y=segment, sr=sr, n_mfcc=13)
            
            features.append(SpectralFeatures(
                timestamp=beat_times[i],
                energy=energy,
                spectral_centroid=float(np.mean(spectral_centroids)),
                spectral_rolloff=float(np.mean(spectral_rolloff)),
                zero_crossing_rate=float(np.mean(zero_crossing_rate)),
                mfcc=np.mean(mfcc, axis=1).tolist()
            ))
    
    return features

def create_bar_structure(beat_times: np.ndarray, downbeat_times: np.ndarray, beats_per_bar: int) -> List[Bar]:
    """Create bar structure from beat and downbeat information"""
    
    bars = []
    
    if len(downbeat_times) == 0:
        # Fallback: create bars from beats assuming 4/4 time
        for i in range(0, len(beat_times), beats_per_bar):
            if i + beats_per_bar <= len(beat_times):
                start_time = beat_times[i]
                end_time = beat_times[i + beats_per_bar - 1]
                bars.append(Bar(
                    start=float(start_time),
                    end=float(end_time),
                    beat_count=beats_per_bar,
                    downbeat_timestamp=float(start_time)
                ))
    else:
        # Use detected downbeats
        for i, downbeat_time in enumerate(downbeat_times[:-1]):
            next_downbeat = downbeat_times[i + 1]
            
            # Count beats in this bar
            beats_in_bar = np.sum((beat_times >= downbeat_time) & (beat_times < next_downbeat))
            
            bars.append(Bar(
                start=float(downbeat_time),
                end=float(next_downbeat),
                beat_count=int(beats_in_bar),
                downbeat_timestamp=float(downbeat_time)
            ))
    
    return bars
