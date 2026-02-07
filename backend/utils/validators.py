"""
Input validation utilities
"""

import re
import validators as val

class Validators:
    """Input validation functions"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email address"""
        if not email:
            return False
        return val.email(email)
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL"""
        if not url:
            return False
        return val.url(url)
    
    @staticmethod
    def validate_query(query: str) -> bool:
        """Validate search query"""
        if not query or len(query.strip()) < 2:
            return False
        if len(query) > 200:
            return False
        return True
    
    @staticmethod
    def validate_location(location: str) -> bool:
        """Validate location string"""
        if not location:
            return True  # Optional field
        if len(location) > 200:
            return False
        # Check for SQL injection attempts
        dangerous_chars = ['<', '>', ';', '--', '/*', '*/', 'DROP', 'DELETE']
        return not any(char in location.upper() for char in dangerous_chars)
    
    @staticmethod
    def validate_experience(experience: str) -> bool:
        """Validate experience parameter"""
        if not experience:
            return True  # Optional field
        
        valid_experiences = [
            'entry', 'junior', 'mid', 'senior', 'lead', 'fresher',
            '0-1', '1-3', '2-5', '5+', '5-10', '10+'
        ]
        
        return any(exp in experience.lower() for exp in valid_experiences)
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """Sanitize user input"""
        if not text:
            return ''
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove special characters that could be harmful
        text = re.sub(r'[<>\"\'%;()&+]', '', text)
        
        return text.strip()
    
    @staticmethod
    def validate_platform(platform: str) -> bool:
        """Validate platform name"""
        valid_platforms = ['linkedin', 'indeed', 'naukri', 'all']
        return platform.lower() in valid_platforms
