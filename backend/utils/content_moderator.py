import google.generativeai as genai
import os
from typing import Dict, Any, List
from dataclasses import dataclass
import logging
import json

logger = logging.getLogger(__name__)

@dataclass
class ModerationResult:
    is_safe: bool
    reason: str
    categories: Dict[str, bool]
    category_scores: Dict[str, float]

class ContentModerator:
    """Content moderation using Google Gemini and custom rules"""
    
    def __init__(self):
        genai.configure(api_key=os.getenv("GOOGLE_AI_API_KEY"))
        self.model = genai.GenerativeModel('gemini-1.5-pro')
        self.blocked_keywords = self._load_blocked_keywords()
    
    def moderate_lyrics(self, lyrics: Dict[str, Any]) -> ModerationResult:
        """Moderate generated lyrics for safety and compliance"""
        
        # Extract all text from lyrics
        full_text = self._extract_text_from_lyrics(lyrics)
        
        # Check with Gemini moderation
        gemini_result = self._check_gemini_moderation(full_text)
        
        # Check custom rules
        custom_result = self._check_custom_rules(full_text)
        
        # Combine results
        is_safe = gemini_result.is_safe and custom_result.is_safe
        reason = gemini_result.reason if not gemini_result.is_safe else custom_result.reason
        
        return ModerationResult(
            is_safe=is_safe,
            reason=reason,
            categories=gemini_result.categories,
            category_scores=gemini_result.category_scores
        )
    
    def _extract_text_from_lyrics(self, lyrics: Dict[str, Any]) -> str:
        """Extract all text content from lyrics JSON"""
        
        text_parts = []
        
        # Add title
        if 'title' in lyrics:
            text_parts.append(lyrics['title'])
        
        # Add all line text
        for section in lyrics.get('sections', []):
            for line in section.get('lines', []):
                if 'text' in line:
                    text_parts.append(line['text'])
        
        return ' '.join(text_parts)
    
    def _check_gemini_moderation(self, text: str) -> ModerationResult:
        """Check content using Google Gemini for safety analysis"""
        
        try:
            moderation_prompt = f"""Analyze the following text for harmful content. Respond with ONLY a JSON object in this format:
{{
  "is_safe": true/false,
  "reason": "explanation",
  "categories": {{"hate": false, "violence": false, "sexual": false, "harassment": false}},
  "category_scores": {{"hate": 0.1, "violence": 0.1, "sexual": 0.1, "harassment": 0.1}}
}}

Text to analyze: {text}"""
            
            response = self.model.generate_content(moderation_prompt)
            response_text = response.text.strip()
            
            # Clean up JSON response
            if response_text.startswith('\`\`\`json'):
                response_text = response_text[7:]
            if response_text.endswith('\`\`\`'):
                response_text = response_text[:-3]
            
            result_data = json.loads(response_text.strip())
            
            return ModerationResult(
                is_safe=result_data.get('is_safe', False),
                reason=result_data.get('reason', 'Gemini moderation check'),
                categories=result_data.get('categories', {}),
                category_scores=result_data.get('category_scores', {})
            )
            
        except Exception as e:
            logger.error(f"Gemini moderation failed: {str(e)}")
            # Fail safe - reject if we can't moderate
            return ModerationResult(
                is_safe=False,
                reason=f"Moderation service unavailable: {str(e)}",
                categories={},
                category_scores={}
            )
    
    def _check_custom_rules(self, text: str) -> ModerationResult:
        """Check content against custom rules"""
        
        text_lower = text.lower()
        
        # Check for blocked keywords
        for keyword in self.blocked_keywords:
            if keyword in text_lower:
                return ModerationResult(
                    is_safe=False,
                    reason=f"Contains blocked keyword: {keyword}",
                    categories={},
                    category_scores={}
                )
        
        # Check for potential weaponization content
        weaponization_keywords = [
            'how to make', 'bomb', 'weapon', 'kill', 'hurt', 'harm',
            'illegal', 'drugs', 'violence', 'threat'
        ]
        
        for keyword in weaponization_keywords:
            if keyword in text_lower:
                return ModerationResult(
                    is_safe=False,
                    reason=f"Potential weaponization content detected: {keyword}",
                    categories={},
                    category_scores={}
                )
        
        return ModerationResult(
            is_safe=True,
            reason="Passed custom moderation rules",
            categories={},
            category_scores={}
        )
    
    def _load_blocked_keywords(self) -> List[str]:
        """Load blocked keywords list"""
        
        # Basic blocked keywords - in production, load from file or database
        return [
            'hate', 'nazi', 'terrorist', 'suicide', 'self-harm',
            'doxx', 'harassment', 'stalking', 'revenge'
        ]
