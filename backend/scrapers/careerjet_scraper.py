"""
Careerjet Scraper - Fetches job data from Careerjet job search engine
Careerjet is a job search engine that aggregates job listings from various sources
"""

from typing import List, Dict, Optional
from .base_scraper import BaseScraper
import requests
import logging
import time
from urllib.parse import quote, urlencode

logger = logging.getLogger(__name__)

class CareerjetScraper(BaseScraper):
    """Careerjet scraper - fetches job listings via Careerjet API and web scraping"""
    
    BASE_URL = "https://public.api.careerjet.net/search"
    WEB_BASE_URL = "https://www.careerjet.com"
    
    # Locale codes for different countries
    LOCALE_CODES = {
        'india': 'en_IN',
        'united states': 'en_US',
        'usa': 'en_US',
        'united kingdom': 'en_GB',
        'uk': 'en_GB',
        'canada': 'en_CA',
        'australia': 'en_AU',
        'germany': 'de_DE',
        'france': 'fr_FR',
        'singapore': 'en_SG',
        'netherlands': 'nl_NL',
        'italy': 'it_IT',
        'spain': 'es_ES',
        'brazil': 'pt_BR',
        'mexico': 'es_MX',
        'japan': 'ja_JP',
        'ireland': 'en_IE',
        'new zealand': 'en_NZ'
    }
    
    def __init__(self, api_key: str = None):
        super().__init__()
        self.api_key = api_key or "your_careerjet_api_key"
        
    def get_platform_name(self) -> str:
        return "careerjet"
    
    def search_jobs(self, query: str, location: str = '', experience: str = '', max_results: int = 50) -> List[Dict]:
        """Search jobs from Careerjet"""
        jobs = []
        
        try:
            logger.info(f"Fetching Careerjet jobs for: '{query}' in '{location or 'Worldwide'}'")
            
            locale = self._get_locale(location)
            
            # Try API first if key is available
            if self.api_key and self.api_key != "your_careerjet_api_key":
                jobs = self._fetch_via_api(query, location, locale, experience, max_results)
            
            # Fallback to web scraping if API fails or no API key
            if not jobs:
                jobs = self._fetch_via_web(query, location, experience, max_results)
            
            logger.info(f"Successfully retrieved {len(jobs)} Careerjet jobs")
            
        except Exception as e:
            logger.error(f"Error fetching Careerjet jobs: {e}")
        
        return jobs
    
    def _get_locale(self, location: str) -> str:
        """Get locale code for location"""
        if not location:
            return 'en_US'  # Default to US
        
        location_lower = location.lower().strip()
        
        for country, locale in self.LOCALE_CODES.items():
            if country in location_lower:
                return locale
        
        return 'en_US'
    
    def _fetch_via_api(self, query: str, location: str, locale: str, experience: str, max_results: int) -> List[Dict]:
        """Fetch jobs using Careerjet API"""
        jobs = []
        
        try:
            params = {
                'keywords': query,
                'location': location,
                'affid': self.api_key,
                'locale_code': locale,
                'pagesize': min(max_results, 99),
                'page': 1,
                'user_ip': '8.8.8.8',
                'user_agent': self.session.headers['User-Agent']
            }
            
            response = self.session.get(self.BASE_URL, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('type') == 'JOBS':
                    job_listings = data.get('jobs', [])
                    
                    for job in job_listings[:max_results]:
                        try:
                            job_data = self._parse_api_job(job, experience)
                            if job_data and self._validate_job(job_data):
                                jobs.append(job_data)
                        except Exception as e:
                            logger.debug(f"Error parsing API job: {e}")
                            continue
                else:
                    logger.warning(f"Careerjet API returned type: {data.get('type')}")
                    
        except Exception as e:
            logger.error(f"Error with Careerjet API: {e}")
        
        return jobs
    
    def _fetch_via_web(self, query: str, location: str, experience: str, max_results: int) -> List[Dict]:
        """Fallback web scraping method"""
        jobs = []
        
        try:
            params = {
                's': query,
                'l': location,
                'sort': 'date'
            }
            
            # Remove empty params
            params = {k: v for k, v in params.items() if v}
            
            url = f"{self.WEB_BASE_URL}/search/jobs?{urlencode(params)}"
            
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find job listings
                job_elements = soup.find_all('article', class_='job') or \
                              soup.find_all('div', class_='job') or \
                              soup.find_all('li', class_='job')
                
                logger.info(f"Found {len(job_elements)} job listings on Careerjet")
                
                for element in job_elements[:max_results]:
                    try:
                        job_data = self._parse_web_job(element, experience)
                        if job_data and self._validate_job(job_data):
                            jobs.append(job_data)
                    except Exception as e:
                        logger.debug(f"Error parsing web job: {e}")
                        continue
                        
        except Exception as e:
            logger.error(f"Error with web scraping: {e}")
        
        return jobs
    
    def _parse_api_job(self, job: Dict, experience: str = '') -> Dict:
        """Parse job from API response"""
        job_data = {
            'title': job.get('title', ''),
            'company': job.get('company', ''),
            'location': job.get('locations', ''),
            'description': job.get('description', ''),
            'salary': job.get('salary', ''),
            'url': job.get('url', ''),
            'posted_date': self._parse_date(job.get('date', '')),
            'external_id': str(job.get('url', '').split('/')[-1] if job.get('url') else '')
        }
        
        # Filter by experience if provided
        if experience and not self._matches_experience(job_data, experience):
            return {}
        
        return self.normalize_job_data(job_data)
    
    def _parse_web_job(self, element, experience: str = '') -> Dict:
        """Parse job from web scraping"""
        try:
            from bs4 import BeautifulSoup
            
            # Extract job details
            title_elem = element.find('h2') or element.find('a', class_='job-title')
            title = title_elem.get_text(strip=True) if title_elem else ''
            
            url_elem = element.find('a', href=True)
            url = url_elem['href'] if url_elem else ''
            if url and not url.startswith('http'):
                url = f"{self.WEB_BASE_URL}{url}"
            
            company_elem = element.find('p', class_='company') or \
                          element.find('span', class_='company') or \
                          element.find(class_='company')
            company = company_elem.get_text(strip=True) if company_elem else ''
            
            location_elem = element.find('span', class_='location') or \
                           element.find('p', class_='location') or \
                           element.find(class_='location')
            location = location_elem.get_text(strip=True) if location_elem else ''
            
            desc_elem = element.find('div', class_='desc') or \
                       element.find('p', class_='description') or \
                       element.find(class_='description')
            description = desc_elem.get_text(strip=True) if desc_elem else ''
            
            salary_elem = element.find('span', class_='salary') or \
                         element.find('p', class_='salary')
            salary = salary_elem.get_text(strip=True) if salary_elem else ''
            
            date_elem = element.find('time') or element.find('span', class_='date')
            posted_date = date_elem.get_text(strip=True) if date_elem else ''
            
            job_data = {
                'title': title,
                'company': company,
                'location': location,
                'description': description,
                'salary': salary,
                'url': url,
                'posted_date': self._parse_date(posted_date),
                'external_id': ''
            }
            
            # Filter by experience if provided
            if experience and not self._matches_experience(job_data, experience):
                return {}
            
            return self.normalize_job_data(job_data)
            
        except Exception as e:
            logger.debug(f"Error parsing job element: {e}")
            return {}
    
    def _matches_experience(self, job_data: Dict, experience: str) -> bool:
        """Check if job matches the experience filter"""
        if not experience:
            return True
        
        experience_lower = experience.lower()
        text_to_search = f"{job_data.get('title', '')} {job_data.get('description', '')}".lower()
        
        # Experience level mappings
        if 'entry' in experience_lower or 'fresher' in experience_lower or '0' in experience_lower:
            return any(term in text_to_search for term in ['entry', 'fresher', 'junior', 'graduate', '0-1 year', '0-2 year'])
        elif 'junior' in experience_lower or '1' in experience_lower or '2' in experience_lower:
            return any(term in text_to_search for term in ['junior', '1-2', '1-3', '2-3', 'entry'])
        elif 'mid' in experience_lower or 'intermediate' in experience_lower or '3' in experience_lower or '4' in experience_lower or '5' in experience_lower:
            return any(term in text_to_search for term in ['mid', 'intermediate', '3-5', '4-6', '2-4', '3-6'])
        elif 'senior' in experience_lower or '6' in experience_lower or '7' in experience_lower or '8' in experience_lower:
            return any(term in text_to_search for term in ['senior', 'lead', '5+', '6+', '7+', '8+', '5-10'])
        
        return True
    
    def _validate_job(self, job_data: Dict) -> bool:
        """Validate that job data has required fields"""
        return bool(job_data.get('title') and job_data.get('company'))
