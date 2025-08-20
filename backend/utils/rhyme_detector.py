import pronouncing
import nltk
from typing import List, Dict, Set, Optional
import re

class RhymeDetector:
    """Detect and validate rhyme schemes using phonetic analysis"""
    
    def __init__(self):
        self._ensure_nltk_data()
    
    def _ensure_nltk_data(self):
        """Ensure required NLTK data is downloaded"""
        try:
            nltk.data.find('corpora/cmudict')
        except LookupError:
            nltk.download('cmudict', quiet=True)
    
    def get_rhyming_part(self, word: str) -> Optional[str]:
        """Get the rhyming part of a word using CMU dictionary"""
        
        word = re.sub(r'[^\w]', '', word.lower())
        
        try:
            phones = pronouncing.phones_for_word(word)
            if phones:
                return pronouncing.rhyming_part(phones[0])
        except:
            pass
        
        return None
    
    def words_rhyme(self, word1: str, word2: str) -> bool:
        """Check if two words rhyme"""
        
        rhyme1 = self.get_rhyming_part(word1)
        rhyme2 = self.get_rhyming_part(word2)
        
        if rhyme1 and rhyme2:
            return rhyme1 == rhyme2
        
        # Fallback to simple ending comparison
        return self._simple_rhyme_check(word1, word2)
    
    def _simple_rhyme_check(self, word1: str, word2: str) -> bool:
        """Simple rhyme check based on word endings"""
        
        word1 = re.sub(r'[^\w]', '', word1.lower())
        word2 = re.sub(r'[^\w]', '', word2.lower())
        
        if len(word1) < 2 or len(word2) < 2:
            return False
        
        # Check if they end with the same 2-3 characters
        return (word1[-2:] == word2[-2:] or 
                (len(word1) >= 3 and len(word2) >= 3 and word1[-3:] == word2[-3:]))
    
    def validate_rhyme_scheme(self, lines: List[str], expected_scheme: str) -> Dict[str, Any]:
        """Validate if lines follow the expected rhyme scheme"""
        
        if len(lines) != len(expected_scheme):
            return {
                'valid': False,
                'reason': 'Line count does not match rhyme scheme length'
            }
        
        # Extract last word from each line
        last_words = []
        for line in lines:
            words = re.findall(r'\b\w+\b', line.lower())
            if words:
                last_words.append(words[-1])
            else:
                last_words.append('')
        
        # Group lines by rhyme tag
        rhyme_groups = {}
        for i, tag in enumerate(expected_scheme):
            if tag not in rhyme_groups:
                rhyme_groups[tag] = []
            rhyme_groups[tag].append((i, last_words[i]))
        
        # Check if words in each group rhyme
        violations = []
        for tag, group in rhyme_groups.items():
            if len(group) > 1:
                # Check all pairs in the group
                for i in range(len(group)):
                    for j in range(i + 1, len(group)):
                        word1 = group[i][1]
                        word2 = group[j][1]
                        if not self.words_rhyme(word1, word2):
                            violations.append({
                                'tag': tag,
                                'lines': [group[i][0], group[j][0]],
                                'words': [word1, word2]
                            })
        
        return {
            'valid': len(violations) == 0,
            'violations': violations,
            'rhyme_groups': rhyme_groups
        }
    
    def suggest_rhymes(self, word: str, limit: int = 10) -> List[str]:
        """Suggest rhyming words for a given word"""
        
        try:
            rhymes = pronouncing.rhymes(word.lower())
            return rhymes[:limit]
        except:
            return []
    
    def get_rhyme_tags(self, lines: List[str]) -> List[str]:
        """Automatically assign rhyme tags to lines"""
        
        last_words = []
        for line in lines:
            words = re.findall(r'\b\w+\b', line.lower())
            if words:
                last_words.append(words[-1])
            else:
                last_words.append('')
        
        # Assign tags based on rhyming
        tags = []
        used_tags = []
        tag_chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        
        for i, word in enumerate(last_words):
            # Check if this word rhymes with any previous word
            found_tag = None
            for j in range(i):
                if self.words_rhyme(word, last_words[j]):
                    found_tag = tags[j]
                    break
            
            if found_tag:
                tags.append(found_tag)
            else:
                # Assign new tag
                for tag in tag_chars:
                    if tag not in used_tags:
                        tags.append(tag)
                        used_tags.append(tag)
                        break
                else:
                    tags.append('X')  # Fallback
        
        return tags
