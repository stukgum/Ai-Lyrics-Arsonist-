"""
Rap (trap) preset - ready-to-use prompt template
"""

SYSTEM_PROMPT = """You are a professional trap/hip-hop lyricist. Focus on strong rhythm, wordplay, and contemporary urban themes. Create lyrics with confident delivery and introspective depth. Use syllables_per_beat=1.6, AABB rhyme scheme, and introspective mood. Ensure tight rhymes and rhythmic flow that matches the beat structure."""

def get_rap_input_template(audio_features, custom_params=None):
    """Generate rap-specific input for LLM"""
    
    base_params = {
        "genre": "trap",
        "mood": "introspective", 
        "explicit": False,
        "language": "en",
        "rhyme": "AABB",
        "syllables_per_beat": 1.6
    }
    
    if custom_params:
        base_params.update(custom_params)
    
    return {
        "bpm": audio_features.get("bpm", 120),
        "bars": audio_features.get("bars", [])[:16],  # Focus on first 16 bars
        "key": audio_features.get("key", "C minor"),
        "tempo_confidence": audio_features.get("tempo_confidence", 0.8),
        "sections": [
            {"name": "verse", "bars": list(range(8))},
            {"name": "chorus", "bars": list(range(8, 16))}
        ],
        "user": base_params
    }
