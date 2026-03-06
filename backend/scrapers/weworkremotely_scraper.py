"""
We Work Remotely Scraper - Fetches remote job data from We Work Remotely
We Work Remotely is one of the largest remote work communities
"""

from typing import List, Dict, Optional
from .base_scraper import BaseScraper
import requests
import logging
from bs4 import BeautifulSoup
from datetime import datetime

logger = logging.getLogger(__name__)

class WeWorkRemotelyScraper(BaseScraper):
    """We Work Remotely scraper - fetches remote job listings"""
    
    BASE_URL = "https://weworkremotely.com"
    
    def __init__(self):
        super().__init__()
        
    def get_platform_name(self) -> str:
        return "weworkremotely"
    
    def search_jobs(self, query: str, location: str = '', experience: str = '', max_results: int = 50) -> List[Dict]:
        """Search remote jobs from We Work Remotely"""
        jobs = []
        
        try:
            logger.info(f"Fetching We Work Remotely jobs for: '{query}'")
            
            # We Work Remotely has category-based listings
            categories = ['programming', 'design', 'marketing', 'customer-support', 'product', 'business']
            
            for category in categories:
                category_jobs = self._fetch_category_jobs(category, query, experience, max_results - len(jobs))
                jobs.extend(category_jobs)
                
                if len(jobs) >= max_results:
                    break
            
            logger.info(f"Successfully retrieved {len(jobs)} We Work Remotely jobs")
            
        except Exception as e:
            logger.error(f"Error fetching We Work Remotely jobs: {e}")
        
        return jobs[:max_results]
    
    def _fetch_category_jobs(self, category: str, query: str, experience: str, max_results: int) -> List[Dict]:
        """Fetch jobs from a specific category"""
        jobs = []
        
        try:
            url = f"{self.BASE_URL}/categories/remote-{category}-jobs"
            soup = self._fetch_page(url)
            
            if not soup:
                return jobs
            
            # Find job listings
            job_elements = soup.find_all('li', class_='feature')
            
            logger.debug(f"Found {len(job_elements)} jobs in {category} category")
            
            for element in job_elements:
                if len(jobs) >= max_results:
                    break
                    
                try:
                    job_data = self._parse_job(element, query, experience)
                    if job_data and self._validate_job(job_data):
                        jobs.append(job_data)
                except Exception as e:
                    logger.debug(f"Error parsing job: {e}")
                    continue
                    
        except Exception as e:
            logger.debug(f"Error fetching {category} jobs: {e}")
        
        return jobs
    
    def _parse_job(self, element, query: str, experience: str) -> Dict:
        """Parse job listing element"""
        try:
            # Get job title and URL
            title_elem = element.find('span', class_='title')
            title = title_elem.get_text(strip=True) if title_elem else ''
            
            link_elem = element.find('a', href=True)
            url = f"{self.BASE_URL}{link_elem['href']}" if link_elem else ''
            
            # Get company name
            company_elem = element.find('span', class_='company')
            company = company_elem.get_text(strip=True) if company_elem else ''
            
            # Get region/location info
            region_elem = element.find('span', class_='region')
            location = region_elem.get_text(strip=True) if region_elem else 'Remote'
            
            # Get job type/category
            tags_elem = element.find_all('span', class_='tag')
            tags = [tag.get_text(strip=True) for tag in tags_elem]
            job_type = ', '.join(tags) if tags else 'Remote'
            
            # Filter by query
            if query and not self._matches_query_text(title, company, ' '.join(tags), query):
                return {}
            
            job_data = {
                'title': title,
                'company': company,
                'location': location,
                'description': f"Remote {job_type} position",
                'job_type': job_type,
                'url': url,
                'posted_date': datetime.now(),
                'external_id': url.split('/')[-1] if url else '',
                'requirements': job_type
            }
            
            # Filter by experience if provided
            if experience and not self._matches_experience(job_data, experience):
                return {}
            
            return self.normalize_job_data(job_data)
            
        except Exception as e:
            logger.debug(f"Error parsing job element: {e}")
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
