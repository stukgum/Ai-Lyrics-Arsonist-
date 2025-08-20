import pyphen
import pronouncing
import nltk
import re
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class SyllableCounter:
    """Accurate syllable counting using multiple methods"""
    
    def __init__(self):
        self.pyphen_dic = pyphen.Pyphen(lang='en')
        self._ensure_nltk_data()
    
    def _ensure_nltk_data(self):
        """Ensure required NLTK data is downloaded"""
        try:
            nltk.data.find('corpora/cmudict')
        except LookupError:
            nltk.download('cmudict', quiet=True)
    
    def count_syllables(self, text: str) -> int:
        """Count syllables in text using multiple methods for accuracy"""
        
        # Clean text
        text = re.sub(r'[^\w\s]', '', text.lower())
        words = text.split()
        
        total_syllables = 0
        
        for word in words:
            if not word:
                continue
            
            # Try pronouncing library (CMU dict) first
            syllables = self._count_with_pronouncing(word)
            
            # Fallback to pyphen
            if syllables is None:
                syllables = self._count_with_pyphen(word)
            
            # Final fallback to heuristic method
            if syllables is None:
                syllables = self._count_heuristic(word)
            
            total_syllables += syllables
        
        return max(1, total_syllables)  # Ensure at least 1 syllable
    
    def _count_with_pronouncing(self, word: str) -> Optional[int]:
        """Count syllables using CMU Pronouncing Dictionary"""
        
        try:
            phones = pronouncing.phones_for_word(word)
            if phones:
                # Count vowel sounds (syllables) in first pronunciation
                return pronouncing.syllable_count(phones[0])
        except:
            pass
        
        return None
    
    def _count_with_pyphen(self, word: str) -> Optional[int]:
        """Count syllables using pyphen hyphenation"""
        
        try:
            hyphenated = self.pyphen_dic.inserted(word)
            return len(hyphenated.split('-'))
        except:
            pass
        
        return None
    
    def _count_heuristic(self, word: str) -> int:
        """Heuristic syllable counting as final fallback"""
        
        word = word.lower()
        
        # Count vowel groups
        vowels = 'aeiouy'
        syllables = 0
        prev_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_was_vowel:
                syllables += 1
            prev_was_vowel = is_vowel
        
        # Handle silent 'e'
        if word.endswith('e') and syllables > 1:
            syllables -= 1
        
        # Handle 'le' ending
        if word.endswith('le') and len(word) > 2 and word[-3] not in vowels:
            syllables += 1
        
        return max(1, syllables)
    
    def get_syllable_breakdown(self, text: str) -> List[Dict[str, Any]]:
        """Get detailed syllable breakdown for each word"""
        
        words = re.sub(r'[^\w\s]', '', text.lower()).split()
        breakdown = []
        
        for word in words:
            if not word:
                continue
            
            syllables = self.count_syllables(word)
            breakdown.append({
                'word': word,
                'syllables': syllables,
                'hyphenated': self.pyphen_dic.inserted(word)
            })
        
        return breakdown
