"""
Text processing utilities
"""

import re
from typing import List
import string

class TextProcessor:
    """Text processing and normalization utilities"""
    
    @staticmethod
    def clean_html(text: str) -> str:
        """Remove HTML tags from text"""
        clean = re.compile('<.*?>')
        return re.sub(clean, '', text)
    
    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """Normalize whitespace in text"""
        return ' '.join(text.split())
    
    @staticmethod
    def extract_email(text: str) -> List[str]:
        """Extract email addresses from text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.findall(email_pattern, text)
    
    @staticmethod
    def extract_phone(text: str) -> List[str]:
        """Extract phone numbers from text"""
        phone_pattern = r'\b\d{10,12}\b'
        return re.findall(phone_pattern, text)
    
    @staticmethod
    def extract_salary(text: str) -> str:
        """Extract salary information from text"""
        # Common salary patterns
        patterns = [
            r'\$\d+[,\d]*\s*-?\s*\$?\d*[,\d]*\s*(?:per\s+)?(?:year|annum|month|hour)?',
            r'₹\d+[,\d]*\s*-?\s*₹?\d*[,\d]*\s*(?:per\s+)?(?:year|annum|month|lpa)?',
            r'\d+[,\d]*\s*-\s*\d+[,\d]*\s*(?:LPA|lpa|USD|INR)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return ''
    
    @staticmethod
    def remove_punctuation(text: str) -> str:
        """Remove punctuation from text"""
        return text.translate(str.maketrans('', '', string.punctuation))
    
    @staticmethod
    def extract_keywords(text: str, top_n: int = 10) -> List[str]:
        """Extract top keywords from text"""
        # Remove common words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'should', 'could', 'may', 'might', 'must', 'can', 'this',
            'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
        }
        
        # Tokenize and clean
        words = text.lower().split()
        words = [w.strip(string.punctuation) for w in words]
        words = [w for w in words if w and w not in stop_words and len(w) > 2]
        
        # Count frequency
        freq = {}
        for word in words:
            freq[word] = freq.get(word, 0) + 1
        
        # Sort by frequency
        sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, count in sorted_words[:top_n]]
