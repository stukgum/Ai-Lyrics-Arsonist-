"""
Country preset - ready-to-use prompt template
"""

SYSTEM_PROMPT = """You are a professional country music songwriter. Write lyrics with storytelling focus, rural imagery, and emotional authenticity. Include narrative elements and relatable life experiences. Use syllables_per_beat=1.1, AABB rhyme scheme, and nostalgic mood. Focus on clear storytelling and emotional resonance."""

def get_country_input_template(audio_features, custom_params=None):
    """Generate country-specific input for LLM"""
    
    base_params = {
        "genre": "country",
        "mood": "nostalgic",
        "explicit": False,
        "language": "en",
        "rhyme": "AABB", 
        "syllables_per_beat": 1.1
    }
    
    if custom_params:
        base_params.update(custom_params)
    
    return {
        "bpm": audio_features.get("bpm", 100),  # Slower country tempo
        "bars": audio_features.get("bars", [])[:20],
        "key": audio_features.get("key", "G major"),
        "tempo_confidence": audio_features.get("tempo_confidence", 0.8),
        "sections": [
            {"name": "verse", "bars": list(range(8))},
            {"name": "chorus", "bars": list(range(8, 12))},
            {"name": "verse", "bars": list(range(12, 20))}
        ],
        "user": base_params
    }
