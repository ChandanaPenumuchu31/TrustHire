"""
Remotive Scraper - Fetches remote job data from Remotive
Remotive is a curated remote jobs platform for tech and startup positions
"""

from typing import List, Dict, Optional
from .base_scraper import BaseScraper
import requests
import logging
from bs4 import BeautifulSoup
from datetime import datetime

logger = logging.getLogger(__name__)

class RemotiveScraper(BaseScraper):
    """Remotive scraper - fetches remote job listings"""
    
    BASE_URL = "https://remotive.com"
    API_URL = "https://remotive.com/api/remote-jobs"
    
    def __init__(self):
        super().__init__()
        
    def get_platform_name(self) -> str:
        return "remotive"
    
    def search_jobs(self, query: str, location: str = '', experience: str = '', max_results: int = 50) -> List[Dict]:
        """Search remote jobs from Remotive"""
        jobs = []
        
        try:
            logger.info(f"Fetching Remotive jobs for: '{query}'")
            
            # Try API first
            jobs = self._fetch_via_api(query, experience, max_results)
            
            # Fallback to web scraping if API fails
            if not jobs:
                jobs = self._fetch_via_web(query, experience, max_results)
            
            logger.info(f"Successfully retrieved {len(jobs)} Remotive jobs")
            
        except Exception as e:
            logger.error(f"Error fetching Remotive jobs: {e}")
        
        return jobs
    
    def _fetch_via_api(self, query: str, experience: str, max_results: int) -> List[Dict]:
        """Fetch jobs via Remotive API"""
        jobs = []
        
        try:
            response = self.session.get(self.API_URL, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                job_listings = data.get('jobs', [])
                
                logger.info(f"Received {len(job_listings)} jobs from Remotive API")
                
                for job in job_listings:
                    if len(jobs) >= max_results:
                        break
                    
                    try:
                        job_data = self._parse_api_job(job, query, experience)
                        if job_data and self._validate_job(job_data):
                            jobs.append(job_data)
                    except Exception as e:
                        logger.debug(f"Error parsing API job: {e}")
                        continue
                        
        except Exception as e:
            logger.debug(f"Error with Remotive API: {e}")
        
        return jobs
    
    def _fetch_via_web(self, query: str, experience: str, max_results: int) -> List[Dict]:
        """Fetch jobs via web scraping"""
        jobs = []
        
        try:
            url = f"{self.BASE_URL}/remote-jobs"
            soup = self._fetch_page(url)
            
            if not soup:
                return jobs
            
            # Find job listings
            job_elements = soup.find_all('li', class_='job-tile')
            
            logger.info(f"Found {len(job_elements)} jobs on Remotive website")
            
            for element in job_elements:
                if len(jobs) >= max_results:
                    break
                
                try:
                    job_data = self._parse_web_job(element, query, experience)
                    if job_data and self._validate_job(job_data):
                        jobs.append(job_data)
                except Exception as e:
                    logger.debug(f"Error parsing job: {e}")
                    continue
                    
        except Exception as e:
            logger.debug(f"Error with web scraping: {e}")
        
        return jobs
    
    def _parse_api_job(self, job: Dict, query: str, experience: str) -> Dict:
        """Parse job from API response"""
        try:
            title = job.get('title', '')
            company = job.get('company_name', '')
            tags = job.get('tags', [])
            category = job.get('category', '')
            
            # Filter by query
            if query and not self._matches_query_text(title, company, ' '.join(tags), query):
                return {}
            
            # Extract salary
            salary = ''
            salary_min = job.get('salary_min')
            salary_max = job.get('salary_max')
            if salary_min or salary_max:
                if salary_min and salary_max:
                    salary = f"${salary_min:,} - ${salary_max:,}"
                elif salary_min:
                    salary = f"${salary_min:,}+"
            
            job_data = {
                'title': title,
                'company': company,
                'location': 'Remote',
                'description': job.get('description', ''),  # Full description, will be cleaned by normalize_job_data
                'salary': salary,
                'job_type': category or 'Remote',
                'url': job.get('url', ''),
                'posted_date': self._parse_date(job.get('publication_date', '')),
                'external_id': str(job.get('id', '')),
                'requirements': ', '.join(tags) if tags else ''
            }
            
            # Filter by experience
            if experience and not self._matches_experience(job_data, experience):
                return {}
            
            return self.normalize_job_data(job_data)
            
        except Exception as e:
            logger.debug(f"Error parsing API job: {e}")
            return {}
    
    def _parse_web_job(self, element, query: str, experience: str) -> Dict:
        """Parse job from web scraping"""
        try:
            # Get title
            title_elem = element.find('h3') or element.find('a', class_='job-title')
            title = title_elem.get_text(strip=True) if title_elem else ''
            
            # Get company
            company_elem = element.find('span', class_='company') or element.find('p', class_='company')
            company = company_elem.get_text(strip=True) if company_elem else ''
            
            # Get URL
            link_elem = element.find('a', href=True)
            url = link_elem['href'] if link_elem else ''
            if url and not url.startswith('http'):
                url = f"{self.BASE_URL}{url}"
            
            # Get tags/category
            tags_elem = element.find_all('span', class_='tag')
            tags = [tag.get_text(strip=True) for tag in tags_elem]
            
            # Filter by query
            if query and not self._matches_query_text(title, company, ' '.join(tags), query):
                return {}
            
            job_data = {
                'title': title,
                'company': company,
                'location': 'Remote',
                'description': f"Remote {' '.join(tags)} position",
                'job_type': ', '.join(tags) if tags else 'Remote',
                'url': url,
                'posted_date': datetime.now(),
                'external_id': url.split('/')[-1] if url else '',
                'requirements': ', '.join(tags)
            }
            
            # Filter by experience
            if experience and not self._matches_experience(job_data, experience):
                return {}
            
            return self.normalize_job_data(job_data)
            
        except Exception as e:
            logger.debug(f"Error parsing web job: {e}")
            return {}
    
    def _matches_query_text(self, title: str, company: str, tags: str, query: str) -> bool:
        """Check if job matches query"""
        if not query:
            return True
        
        query_lower = query.lower()
        search_text = f"{title} {company} {tags}".lower()
        
        query_words = query_lower.split()
        
        # Match if at least 50% of words are present
        matches = sum(1 for word in query_words if word in search_text)
        threshold = max(1, len(query_words) / 2)
        
        return matches >= threshold
    
    def _matches_experience(self, job_data: Dict, experience: str) -> bool:
        """Check if job matches experience filter"""
        if not experience:
            return True
        
        experience_lower = experience.lower()
        text_to_search = f"{job_data.get('title', '')} {job_data.get('description', '')} {job_data.get('requirements', '')}".lower()
        
        if 'entry' in experience_lower or 'fresher' in experience_lower:
            return any(term in text_to_search for term in ['entry', 'junior', 'graduate', 'beginner'])
        elif 'mid' in experience_lower or 'intermediate' in experience_lower:
            return any(term in text_to_search for term in ['mid', 'intermediate', 'experienced'])
        elif 'senior' in experience_lower:
            return any(term in text_to_search for term in ['senior', 'lead', 'principal', 'staff'])
        
        return True
    
    def _validate_job(self, job_data: Dict) -> bool:
        """Validate job data"""
        return bool(job_data.get('title') and job_data.get('company'))
