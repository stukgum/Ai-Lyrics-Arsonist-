from typing import Dict, Any, List
import re
import logging

from utils.syllable_counter import SyllableCounter
from utils.rhyme_detector import RhymeDetector

logger = logging.getLogger(__name__)

class LyricPostProcessor:
    """Post-process generated lyrics to fix syllable counts and improve quality"""
    
    def __init__(self, syllable_counter: SyllableCounter, rhyme_detector: RhymeDetector):
        self.syllable_counter = syllable_counter
        self.rhyme_detector = rhyme_detector
    
    def process_lyrics(self, lyrics: Dict[str, Any], audio_features: Dict[str, Any]) -> Dict[str, Any]:
        """Post-process lyrics with syllable correction and timing assignment"""
        
        processed_lyrics = lyrics.copy()
        
        # Process each section
        for section in processed_lyrics.get('sections', []):
            self._process_section(section, audio_features)
        
        # Assign timestamps based on bar timing
        self._assign_timestamps(processed_lyrics, audio_features)
        
        # Validate and fix syllable counts
        self._fix_syllable_counts(processed_lyrics)
        
        # Update metadata
        self._update_metadata(processed_lyrics)
        
        return processed_lyrics
    
    def _process_section(self, section: Dict[str, Any], audio_features: Dict[str, Any]):
        """Process individual section"""
        
        lines = section.get('lines', [])
        
        for line in lines:
            # Verify syllable count
            actual_syllables = self.syllable_counter.count_syllables(line['text'])
            target_syllables = line['syllable_target']
            
            # If syllable count is off by more than 1, try to fix
            if abs(actual_syllables - target_syllables) > 1:
                fixed_text = self._fix_line_syllables(line['text'], target_syllables)
                if fixed_text:
                    line['text'] = fixed_text
                    logger.info(f"Fixed syllables: '{line['text']}' -> '{fixed_text}'")
    
    def _fix_line_syllables(self, text: str, target_syllables: int) -> str:
        """Attempt to fix syllable count in a line"""
        
        current_syllables = self.syllable_counter.count_syllables(text)
        
        if current_syllables == target_syllables:
            return text
        
        words = text.split()
        
        if current_syllables > target_syllables:
            # Too many syllables - try to shorten
            return self._shorten_line(words, current_syllables - target_syllables)
        else:
            # Too few syllables - try to lengthen
            return self._lengthen_line(words, target_syllables - current_syllables)
    
    def _shorten_line(self, words: List[str], syllables_to_remove: int) -> str:
        """Remove syllables from line by shortening words"""
        
        # Simple approach: remove articles and short words
        articles = ['a', 'an', 'the', 'and', 'or', 'but']
        
        filtered_words = []
        removed_syllables = 0
        
        for word in words:
            if (word.lower() in articles and 
                removed_syllables < syllables_to_remove):
                removed_syllables += 1
                continue
            filtered_words.append(word)
        
        return ' '.join(filtered_words)
    
    def _lengthen_line(self, words: List[str], syllables_to_add: int) -> str:
        """Add syllables to line by expanding words or adding words"""
        
        # Simple approach: add descriptive words
        if syllables_to_add == 1:
            # Add a one-syllable word
            descriptors = ['so', 'now', 'just', 'still', 'more', 'here']
            words.insert(len(words) // 2, descriptors[0])
        elif syllables_to_add == 2:
            # Add a two-syllable word
            descriptors = ['really', 'always', 'never', 'maybe']
            words.insert(len(words) // 2, descriptors[0])
        
        return ' '.join(words)
    
    def _assign_timestamps(self, lyrics: Dict[str, Any], audio_features: Dict[str, Any]):
        """Assign timestamps to lines based on bar timing"""
        
        bars = audio_features.get('bars', [])
        
        for section in lyrics.get('sections', []):
            section_bars = section.get('bars', [])
            lines = section.get('lines', [])
            
            for line in lines:
                suggested_bar = line.get('suggested_bar_start', 0)
                
                # Find the corresponding bar timing
                if suggested_bar < len(bars):
                    bar = bars[suggested_bar]
                    line['timestamp_start'] = bar.get('start', 0)
                    
                    # Estimate end time (assume line takes half a bar)
                    bar_duration = bar.get('end', 2) - bar.get('start', 0)
                    line['timestamp_end'] = line['timestamp_start'] + (bar_duration / 2)
    
    def _fix_syllable_counts(self, lyrics: Dict[str, Any]):
        """Final pass to fix any remaining syllable count issues"""
        
        for section in lyrics.get('sections', []):
            for line in section.get('lines', []):
                actual_syllables = self.syllable_counter.count_syllables(line['text'])
                line['actual_syllables'] = actual_syllables
                
                # Update syllable_target if it's way off
                if abs(actual_syllables - line['syllable_target']) > 2:
                    line['syllable_target'] = actual_syllables
    
    def _update_metadata(self, lyrics: Dict[str, Any]):
        """Update metadata with actual syllable counts"""
        
        total_syllables = 0
        total_lines = 0
        
        for section in lyrics.get('sections', []):
            for line in section.get('lines', []):
                total_syllables += line.get('actual_syllables', line.get('syllable_target', 0))
                total_lines += 1
        
        if 'metadata' not in lyrics:
            lyrics['metadata'] = {}
        
        lyrics['metadata'].update({
            'actual_total_syllables': total_syllables,
            'total_lines': total_lines,
            'average_syllables_per_line': total_syllables / max(total_lines, 1)
        })
