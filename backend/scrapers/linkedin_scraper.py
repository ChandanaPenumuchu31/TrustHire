"""
LinkedIn Scraper - Fetches real job data from LinkedIn job search results
"""

from typing import List, Dict
from .base_scraper import BaseScraper
import requests
from bs4 import BeautifulSoup
import logging
import time
import re
from urllib.parse import quote

logger = logging.getLogger(__name__)

class LinkedInScraper(BaseScraper):
    """LinkedIn scraper - fetches real job listings from LinkedIn job search"""
    
    BASE_URL = "https://www.linkedin.com"
    JOBS_SEARCH_URL = "https://www.linkedin.com/jobs/search"
    
    # Geo IDs for common locations
    GEO_IDS = {
        'india': '102713980',
        'united states': '103644278',
        'usa': '103644278',
        'united kingdom': '101165590',
        'uk': '101165590',
        'canada': '101174742',
        'australia': '101452733',
        'germany': '101282230',
        'france': '105015875',
        'singapore': '102454443',
    }
    
    def __init__(self):
        super().__init__()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
    def get_platform_name(self) -> str:
        return "linkedin"
    
    def search_jobs(self, query: str, location: str = '', experience: str = '', max_results: int = 50) -> List[Dict]:
        """Search real jobs from LinkedIn"""
        jobs = []
        
        try:
            logger.info(f"Fetching LinkedIn jobs for: '{query}' in '{location or 'Worldwide'}'")
            
            # Get geo ID for location
            geo_id = self._get_geo_id(location)
            
            # Fetch jobs from LinkedIn
            jobs = self._fetch_linkedin_jobs(query, geo_id, max_results)
            
            logger.info(f"Successfully retrieved {len(jobs)} real LinkedIn jobs")
            
        except Exception as e:
            logger.error(f"Error fetching LinkedIn jobs: {e}")
        
        return jobs
    
    def _get_geo_id(self, location: str) -> str:
        """Get LinkedIn geo ID for location"""
        if not location:
            return ''
        
        location_lower = location.lower().strip()
        
        # Check if we have a direct match
        for key, geo_id in self.GEO_IDS.items():
            if key in location_lower:
                return geo_id
        
        # Default to India (based on your example)
        return self.GEO_IDS.get('india', '')
    
    def _fetch_linkedin_jobs(self, query: str, geo_id: str, max_results: int) -> List[Dict]:
        """Fetch jobs from LinkedIn job search results"""
        jobs = []
        
        try:
            # Build search URL
            params = {
                'keywords': query,
                'location': '',
                'geoId': geo_id,
                'f_TPR': 'r604800',  # Past week
                'position': 1,
                'pageNum': 0,
                'start': 0
            }
            
            # Remove empty params
            params = {k: v for k, v in params.items() if v}
            
            # Build URL
            url = f"{self.JOBS_SEARCH_URL}?"
            url += "&".join([f"{k}={quote(str(v))}" for k, v in params.items()])
            
            logger.info(f"Fetching from: {url}")
            
            # Fetch the page
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find job cards
                job_cards = soup.find_all('div', class_='base-card')
                if not job_cards:
                    job_cards = soup.find_all('li', class_='jobs-search-results__list-item')
                if not job_cards:
                    # Try alternate selectors
                    job_cards = soup.find_all('div', {'data-job-id': True})
                
                logger.info(f"Found {len(job_cards)} job cards on page")
                
                for card in job_cards[:max_results]:
                    try:
                        job_data = self._parse_job_card(card)
                        if job_data and self._validate_job(job_data):
                            jobs.append(job_data)
                    except Exception as e:
                        logger.debug(f"Error parsing job card: {e}")
                        continue
                
                # If we didn't find jobs with the first method, try API endpoint
                if len(jobs) == 0:
                    logger.info("No jobs found with HTML parsing, trying API endpoint")
                    jobs = self._fetch_from_api(query, geo_id, max_results)
                
            else:
                logger.error(f"LinkedIn returned status {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error fetching LinkedIn jobs: {e}")
        
        return jobs
    
    def _fetch_from_api(self, query: str, geo_id: str, max_results: int) -> List[Dict]:
        """Fetch jobs from LinkedIn's job-search API endpoint"""
        jobs = []
        
        try:
            api_url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
            
            params = {
                'keywords': query,
                'location': '',
                'geoId': geo_id,
                'f_TPR': 'r604800',
                'start': 0,
                'count': min(max_results, 25)
            }
            
            params = {k: v for k, v in params.items() if v}
            
            response = self.session.get(api_url, params=params, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                job_cards = soup.find_all('li')
                
                logger.info(f"Found {len(job_cards)} jobs from API endpoint")
                
                for card in job_cards[:max_results]:
                    try:
                        job_data = self._parse_job_card(card)
                        if job_data and self._validate_job(job_data):
                            jobs.append(job_data)
                    except Exception as e:
                        logger.debug(f"Error parsing API job card: {e}")
                        continue
            else:
                logger.error(f"LinkedIn API returned status {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error fetching from LinkedIn API: {e}")
        
        return jobs
    
    def _parse_job_card(self, card) -> Dict:
        """Parse a LinkedIn job card"""
        try:
            # Extract job ID
            job_id = card.get('data-job-id') or card.get('data-entity-urn', '')
            if 'urn:li:' in str(job_id):
                job_id = job_id.split(':')[-1]
            
            # Extract title
            title_elem = card.find('h3', class_='base-search-card__title') or \
                        card.find('a', class_='base-card__full-link') or \
                        card.find('h3')
            title = title_elem.get_text(strip=True) if title_elem else ''
            
            # Extract company
            company_elem = card.find('h4', class_='base-search-card__subtitle') or \
                          card.find('a', class_='hidden-nested-link') or \
                          card.find('h4')
            company = company_elem.get_text(strip=True) if company_elem else 'Unknown Company'
            
            # Extract location
            location_elem = card.find('span', class_='job-search-card__location') or \
                           card.find('span', class_='job-result-card__location')
            location = location_elem.get_text(strip=True) if location_elem else 'Remote'
            
            # Extract URL
            link_elem = card.find('a', class_='base-card__full-link') or \
                       card.find('a', href=re.compile(r'/jobs/view/'))
            job_url = link_elem.get('href', '') if link_elem else ''
            if job_url and not job_url.startswith('http'):
                job_url = self.BASE_URL + job_url
            
            # Extract posted date
            time_elem = card.find('time')
            posted_date = time_elem.get('datetime', '') if time_elem else ''
            if not posted_date:
                posted_elem = card.find('span', class_='job-search-card__listdate') or \
                             card.find('time')
                posted_date = posted_elem.get_text(strip=True) if posted_elem else 'Recently'
            
            # Extract description if available
            desc_elem = card.find('p', class_='base-search-card__snippet') or \
                       card.find('div', class_='job-search-card__snippet')
            description = desc_elem.get_text(strip=True) if desc_elem else ''
            
            # Extract salary if available
            salary_elem = card.find('span', class_='job-search-card__salary-info')
            salary = salary_elem.get_text(strip=True) if salary_elem else 'Not specified'
            
            return {
                'title': title,
                'company': company,
                'location': location,
                'description': description or f"Job position: {title} at {company}",
                'url': job_url or f"https://www.linkedin.com/jobs/view/{job_id}",
                'posted_date': posted_date,
                'platform': 'linkedin',
                'salary': salary,
                'job_type': 'Full-time',
                'experience_level': 'Mid Level',
                'verified_source': True,
                'job_id': job_id
            }
            
        except Exception as e:
            logger.error(f"Error parsing job card: {e}")
            return None
    
    def _format_salary(self, min_sal, max_sal) -> str:
        """Format salary range"""
        if min_sal and max_sal:
            return f"${min_sal:,.0f} - ${max_sal:,.0f}"
        elif min_sal:
            return f"From ${min_sal:,.0f}"
        elif max_sal:
            return f"Up to ${max_sal:,.0f}"
        return "Not specified"
    
    def _format_salary_range(self, min_sal, max_sal) -> str:
        """Format salary range"""
        return self._format_salary(min_sal, max_sal)
