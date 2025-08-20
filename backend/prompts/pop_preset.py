"""
Pop preset - ready-to-use prompt template
"""

SYSTEM_PROMPT = """You are a professional pop songwriter. Create catchy, radio-friendly lyrics with universal themes and memorable hooks. Focus on emotional connection and sing-along potential. Use syllables_per_beat=1.0, ABAB rhyme scheme, and uplifting mood. Ensure chorus has 8 bars and is highly memorable."""

def get_pop_input_template(audio_features, custom_params=None):
    """Generate pop-specific input for LLM"""
    
    base_params = {
        "genre": "pop",
        "mood": "uplifting",
        "explicit": False,
        "language": "en", 
        "rhyme": "ABAB",
        "syllables_per_beat": 1.0
    }
    
    if custom_params:
        base_params.update(custom_params)
    
    return {
        "bpm": audio_features.get("bpm", 120),
        "bars": audio_features.get("bars", [])[:24],  # Longer structure for pop
        "key": audio_features.get("key", "C major"),
        "tempo_confidence": audio_features.get("tempo_confidence", 0.8),
        "sections": [
            {"name": "verse", "bars": list(range(8))},
            {"name": "chorus", "bars": list(range(8, 16))},
            {"name": "verse", "bars": list(range(16, 24))}
        ],
        "user": base_params
    }
