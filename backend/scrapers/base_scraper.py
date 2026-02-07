"""
Base scraper class for job platforms
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseScraper(ABC):
    """Base class for all job scrapers"""
    
    def __init__(self, timeout: int = 30, delay: int = 2):
        """Initialize scraper"""
        self.timeout = timeout
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
    
    @abstractmethod
    def search_jobs(self, query: str, location: str = '', experience: str = '', max_results: int = 50) -> List[Dict]:
        """
        Search for jobs on the platform
        Must be implemented by each scraper
        """
        pass
    
    @abstractmethod
    def get_platform_name(self) -> str:
        """Return platform name"""
        pass
    
    def _fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse a web page"""
        try:
            time.sleep(self.delay)  # Rate limiting
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ''
        return ' '.join(text.strip().split())
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string to datetime"""
        if not date_str:
            return None
        
        try:
            # Handle "Posted X days ago" format
            if 'day' in date_str.lower():
                days = int(''.join(filter(str.isdigit, date_str)))
                return datetime.now() - timedelta(days=days)
            elif 'hour' in date_str.lower():
                hours = int(''.join(filter(str.isdigit, date_str)))
                return datetime.now() - timedelta(hours=hours)
            elif 'today' in date_str.lower():
                return datetime.now()
            elif 'yesterday' in date_str.lower():
                return datetime.now() - timedelta(days=1)
        except:
            pass
        
        return datetime.now()
    
    def normalize_job_data(self, raw_data: Dict) -> Dict:
        """Normalize job data to standard format"""
        return {
            'title': self._clean_text(raw_data.get('title', '')),
            'company': self._clean_text(raw_data.get('company', '')),
            'location': self._clean_text(raw_data.get('location', '')),
            'description': self._clean_text(raw_data.get('description', '')),
            'requirements': self._clean_text(raw_data.get('requirements', '')),
            'salary': self._clean_text(raw_data.get('salary', '')),
            'experience_required': self._clean_text(raw_data.get('experience_required', '')),
            'job_type': self._clean_text(raw_data.get('job_type', '')),
            'url': raw_data.get('url', ''),
            'platform': self.get_platform_name(),
            'posted_date': raw_data.get('posted_date'),
            'external_id': raw_data.get('external_id', '')
        }
