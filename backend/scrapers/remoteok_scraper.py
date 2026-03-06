"""
RemoteOK Scraper - Fetches remote job data from RemoteOK
RemoteOK is a job board for remote positions across the world
"""

from typing import List, Dict, Optional
from .base_scraper import BaseScraper
import requests
import logging
import time
from datetime import datetime

logger = logging.getLogger(__name__)

class RemoteOKScraper(BaseScraper):
    """RemoteOK scraper - fetches remote job listings via RemoteOK API"""
    
    API_URL = "https://remoteok.com/api"
    WEB_BASE_URL = "https://remoteok.com"
    
    def __init__(self):
        super().__init__()
        # RemoteOK has a public API that doesn't require authentication
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json'
        })
        
    def get_platform_name(self) -> str:
        return "remoteok"
    
    def search_jobs(self, query: str, location: str = '', experience: str = '', max_results: int = 50) -> List[Dict]:
        """Search remote jobs from RemoteOK"""
        jobs = []
        
        try:
            logger.info(f"Fetching RemoteOK jobs for: '{query}' in '{location or 'Remote'}'")
            
            # RemoteOK focuses on remote jobs, so location is less relevant
            jobs = self._fetch_jobs(query, location, experience, max_results)
            
            logger.info(f"Successfully retrieved {len(jobs)} RemoteOK jobs")
            
        except Exception as e:
            logger.error(f"Error fetching RemoteOK jobs: {e}")
        
        return jobs
    
    def _fetch_jobs(self, query: str, location: str, experience: str, max_results: int) -> List[Dict]:
        """Fetch jobs from RemoteOK API"""
        jobs = []
        
        try:
            # RemoteOK API returns all jobs, we need to filter
            response = self.session.get(self.API_URL, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                # First item is metadata, skip it
                job_listings = data[1:] if len(data) > 1 else []
                
                logger.info(f"Received {len(job_listings)} jobs from RemoteOK API")
                
                for job in job_listings:
                    try:
                        # Filter by query
                        if not self._matches_query(job, query):
                            continue
                        
                        # Filter by location if provided
                        if location and not self._matches_location(job, location):
                            continue
                        
                        # Parse job data
                        job_data = self._parse_job(job, experience)
                        
                        if job_data and self._validate_job(job_data):
                            jobs.append(job_data)
                            
                        if len(jobs) >= max_results:
                            break
                            
                    except Exception as e:
                        logger.debug(f"Error parsing RemoteOK job: {e}")
                        continue
                        
            else:
                logger.error(f"RemoteOK API returned status {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error fetching from RemoteOK API: {e}")
        
        return jobs
    
    def _matches_query(self, job: Dict, query: str) -> bool:
        """Check if job matches the search query - more flexible matching"""
        if not query:
            return True
        
        query_lower = query.lower()
        
        # Search in title, position, and tags
        title = job.get('position', '').lower()
        company = job.get('company', '').lower()
        tags = ' '.join(job.get('tags', [])).lower() if job.get('tags') else ''
        description = job.get('description', '').lower() if job.get('description') else ''
        
        search_text = f"{title} {company} {tags} {description}"
        
        # More flexible matching: match if ANY word appears (OR logic)
        query_words = query_lower.split()
        
        # If it's a single word, just check if it's in the text
        if len(query_words) == 1:
            return query_lower in search_text
        
        # For multiple words, match if at least 50% of words are present
        matches = sum(1 for word in query_words if word in search_text)
        threshold = max(1, len(query_words) / 2)  # At least half the words should match
        
        return matches >= threshold
    
    def _matches_location(self, job: Dict, location: str) -> bool:
        """Check if job matches the location filter"""
        if not location:
            return True
        
        location_lower = location.lower()
        
        # Check company location and allowed locations
        job_location = job.get('location', '').lower()
        company_location = job.get('company_location', '').lower()
        
        # RemoteOK jobs are remote, but some have geographic restrictions
        if 'anywhere' in job_location or 'worldwide' in job_location:
            return True
        
        # Check if location matches
        search_text = f"{job_location} {company_location}"
        return location_lower in search_text
    
    def _parse_job(self, job: Dict, experience: str = '') -> Dict:
        """Parse job from API response"""
        try:
            # Extract salary information
            salary = ''
            if job.get('salary_min') or job.get('salary_max'):
                salary_min = job.get('salary_min', 0)
                salary_max = job.get('salary_max', 0)
                if salary_min and salary_max:
                    salary = f"${salary_min:,} - ${salary_max:,}"
                elif salary_min:
                    salary = f"${salary_min:,}+"
                elif salary_max:
                    salary = f"Up to ${salary_max:,}"
            
            # Build job URL
            job_id = job.get('id', '')
            slug = job.get('slug', '')
            url = f"{self.WEB_BASE_URL}/remote-jobs/{slug}" if slug else f"{self.WEB_BASE_URL}/remote-jobs/{job_id}"
            
            # Get tags
            tags = job.get('tags', [])
            tags_str = ', '.join(tags) if tags else ''
            
            # Parse date
            posted_date = None
            if job.get('date'):
                try:
                    posted_date = datetime.fromtimestamp(int(job.get('date')))
                except:
                    posted_date = datetime.now()
            
            job_data = {
                'title': job.get('position', ''),
                'company': job.get('company', ''),
                'location': job.get('location', 'Remote'),
                'description': job.get('description', '') or f"Remote position: {tags_str}",
                'salary': salary,
                'job_type': 'Remote',
                'url': url,
                'posted_date': posted_date,
                'external_id': str(job_id),
                'requirements': tags_str
            }
            
            # Filter by experience if provided
            if experience and not self._matches_experience(job_data, experience):
                return {}
            
            return self.normalize_job_data(job_data)
            
        except Exception as e:
            logger.debug(f"Error parsing job: {e}")
            return {}
    
    def _matches_experience(self, job_data: Dict, experience: str) -> bool:
        """Check if job matches the experience filter"""
        if not experience:
            return True
        
        experience_lower = experience.lower()
        text_to_search = f"{job_data.get('title', '')} {job_data.get('description', '')} {job_data.get('requirements', '')}".lower()
        
        # Experience level mappings
        if 'entry' in experience_lower or 'fresher' in experience_lower or '0' in experience_lower:
            return any(term in text_to_search for term in ['entry', 'fresher', 'junior', 'graduate', '0-1 year', '0-2 year', 'beginner'])
        elif 'junior' in experience_lower or '1' in experience_lower or '2' in experience_lower:
            return any(term in text_to_search for term in ['junior', '1-2', '1-3', '2-3', 'entry'])
        elif 'mid' in experience_lower or 'intermediate' in experience_lower or '3' in experience_lower or '4' in experience_lower or '5' in experience_lower:
            return any(term in text_to_search for term in ['mid', 'intermediate', '3-5', '4-6', '2-4', '3-6', 'experienced'])
        elif 'senior' in experience_lower or '6' in experience_lower or '7' in experience_lower or '8' in experience_lower:
            return any(term in text_to_search for term in ['senior', 'lead', '5+', '6+', '7+', '8+', '5-10', 'principal', 'staff'])
        
        return True
    
    def _validate_job(self, job_data: Dict) -> bool:
        """Validate that job data has required fields"""
        return bool(job_data.get('title') and job_data.get('company'))
