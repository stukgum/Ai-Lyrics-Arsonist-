import google.generativeai as genai
import json
import os
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class LLMOrchestrator:
    """Orchestrates LLM calls for lyric generation using Google Gemini"""
    
    def __init__(self):
        genai.configure(api_key=os.getenv("GOOGLE_AI_API_KEY"))
        self.model = genai.GenerativeModel('gemini-1.5-pro')
        self.system_prompt = self._get_system_prompt()
        self.json_schema = self._get_json_schema()
    
    def generate_lyrics(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate lyrics using Google Gemini with structured output"""
        
        try:
            full_prompt = f"{self.system_prompt}\n\nInput data:\n{json.dumps(input_data, indent=2)}\n\nGenerate lyrics in the exact JSON format specified above:"
            
            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.8,
                    max_output_tokens=2000,
                )
            )
            
            response_text = response.text.strip()
            
            # Clean up response text to extract JSON
            if response_text.startswith('\`\`\`json'):
                response_text = response_text[7:]
            if response_text.endswith('\`\`\`'):
                response_text = response_text[:-3]
            
            lyrics_json = json.loads(response_text.strip())
            
            # Validate response structure
            self._validate_response(lyrics_json)
            
            return lyrics_json
            
        except Exception as e:
            logger.error(f"LLM generation failed: {str(e)}")
            # Fallback to basic structure
            return self._generate_fallback_lyrics(input_data)
    
    def _get_system_prompt(self) -> str:
        """Get the exact system prompt from specification"""
        
        return """You are a professional lyricist and technical composer. You will receive an input JSON containing audio features (BPM, bars, beats, key, sections) and user parameters (genre, mood, explicit flag, syllables_per_beat). Produce ONLY a single valid JSON object that conforms exactly to the provided schema. Do not include any explanation, analysis, or additional text — only return the JSON schema. Ensure syllable_target fields are integers; rhyme_tag must be single uppercase letters. If you cannot meet exact syllable counts, include a best-effort syllable_target and we will post-process.

JSON Schema:
{
  "type": "object",
  "properties": {
    "title": {"type": "string"},
    "sections": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": {"type": "string", "enum": ["verse", "chorus", "bridge", "intro", "outro", "prechorus"]},
          "bars": {"type": "array", "items": {"type": "integer"}},
          "lines": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "line_index": {"type": "integer"},
                "text": {"type": "string"},
                "syllable_target": {"type": "integer"},
                "rhyme_tag": {"type": "string", "pattern": "^[A-Z]$"},
                "suggested_bar_start": {"type": "integer"}
              },
              "required": ["line_index", "text", "syllable_target", "rhyme_tag", "suggested_bar_start"]
            }
          }
        },
        "required": ["name", "bars", "lines"]
      }
    },
    "metadata": {
      "type": "object",
      "properties": {
        "estimated_total_syllables": {"type": "integer"}
      },
      "required": ["estimated_total_syllables"]
    }
  },
  "required": ["title", "sections", "metadata"]
}"""

    def _get_json_schema(self) -> Dict[str, Any]:
        """Get the exact JSON schema from specification"""
        
        return {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "sections": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "enum": ["verse", "chorus", "bridge", "intro", "outro", "prechorus"]
                            },
                            "bars": {
                                "type": "array",
                                "items": {"type": "integer"}
                            },
                            "lines": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "line_index": {"type": "integer"},
                                        "text": {"type": "string"},
                                        "syllable_target": {"type": "integer"},
                                        "rhyme_tag": {"type": "string", "pattern": "^[A-Z]$"},
                                        "suggested_bar_start": {"type": "integer"}
                                    },
                                    "required": ["line_index", "text", "syllable_target", "rhyme_tag", "suggested_bar_start"]
                                }
                            }
                        },
                        "required": ["name", "bars", "lines"]
                    }
                },
                "metadata": {
                    "type": "object",
                    "properties": {
                        "estimated_total_syllables": {"type": "integer"}
                    },
                    "required": ["estimated_total_syllables"]
                }
            },
            "required": ["title", "sections", "metadata"]
        }
    
    def _validate_response(self, response: Dict[str, Any]) -> None:
        """Validate LLM response structure"""
        
        required_keys = ["title", "sections", "metadata"]
        for key in required_keys:
            if key not in response:
                raise ValueError(f"Missing required key: {key}")
        
        if not isinstance(response["sections"], list):
            raise ValueError("Sections must be a list")
        
        for section in response["sections"]:
            if "lines" not in section:
                raise ValueError("Section missing lines")
            
            for line in section["lines"]:
                required_line_keys = ["line_index", "text", "syllable_target", "rhyme_tag", "suggested_bar_start"]
                for key in required_line_keys:
                    if key not in line:
                        raise ValueError(f"Line missing required key: {key}")
    
    def _generate_fallback_lyrics(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback lyrics if LLM fails"""
        
        user_params = input_data.get("user", {})
        genre = user_params.get("genre", "hip-hop")
        mood = user_params.get("mood", "energetic")
        
        # Simple fallback structure
        return {
            "title": f"{mood.title()} {genre.title()} Track",
            "sections": [
                {
                    "name": "verse",
                    "bars": [0, 1, 2, 3],
                    "lines": [
                        {
                            "line_index": 0,
                            "text": f"This is a {mood} {genre} verse line",
                            "syllable_target": 8,
                            "rhyme_tag": "A",
                            "suggested_bar_start": 0
                        },
                        {
                            "line_index": 1,
                            "text": f"Generated when the AI had to decline",
                            "syllable_target": 8,
                            "rhyme_tag": "A",
                            "suggested_bar_start": 1
                        }
                    ]
                }
            ],
            "metadata": {
                "estimated_total_syllables": 16
            }
        }

class PresetPrompts:
    """Ready-to-use LLM prompt presets as specified"""
    
    @staticmethod
    def get_rap_preset() -> Dict[str, Any]:
        """Rap (trap) preset - short system + user template"""
        return {
            "system_addition": "Focus on trap/hip-hop style with strong rhythm and wordplay. Use contemporary slang and confident delivery.",
            "user_params": {
                "genre": "trap",
                "mood": "introspective",
                "syllables_per_beat": 1.6,
                "rhyme": "AABB",
                "explicit": False
            }
        }
    
    @staticmethod
    def get_pop_preset() -> Dict[str, Any]:
        """Pop preset - syllables_per_beat=1.0, rhyme ABAB, mood uplifting"""
        return {
            "system_addition": "Create catchy, radio-friendly pop lyrics with universal themes and memorable hooks. Focus on emotional connection.",
            "user_params": {
                "genre": "pop",
                "mood": "uplifting",
                "syllables_per_beat": 1.0,
                "rhyme": "ABAB",
                "explicit": False,
                "target_structure": {"chorus": 8}
            }
        }
    
    @staticmethod
    def get_country_preset() -> Dict[str, Any]:
        """Country preset - syllables_per_beat=1.1, rhyme AABB, mood nostalgic"""
        return {
            "system_addition": "Write country music lyrics with storytelling focus, rural imagery, and emotional authenticity. Include narrative elements.",
            "user_params": {
                "genre": "country",
                "mood": "nostalgic",
                "syllables_per_beat": 1.1,
                "rhyme": "AABB",
                "explicit": False
            }
        }
