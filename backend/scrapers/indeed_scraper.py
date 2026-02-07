"""
Indeed job scraper
"""

from typing import List, Dict
from .base_scraper import BaseScraper
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class IndeedScraper(BaseScraper):
    """Scraper for Indeed.com"""
    
    BASE_URL = "https://www.indeed.com"
    
    def get_platform_name(self) -> str:
        return "indeed"
    
    def search_jobs(self, query: str, location: str = '', experience: str = '', max_results: int = 50) -> List[Dict]:
        """Search jobs on Indeed"""
        jobs = []
        
        try:
            # Build search URL
            search_url = f"{self.BASE_URL}/jobs"
            params = {
                'q': query,
                'l': location,
                'fromage': '14',  # Last 14 days
            }
            
            # Add experience filter if provided
            if experience:
                params['explvl'] = self._map_experience(experience)
            
            # Build URL with params
            url = f"{search_url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
            
            soup = self._fetch_page(url)
            if not soup:
                logger.warning(f"Failed to fetch Indeed jobs for query: {query}")
                return jobs
            
            # Parse job listings
            job_cards = soup.find_all(['div', 'a'], class_=lambda x: x and ('job' in x.lower() or 'card' in x.lower()))
            
            for card in job_cards[:max_results]:
                try:
                    job_data = self._parse_job_card(card)
                    if job_data and job_data.get('title'):
                        jobs.append(self.normalize_job_data(job_data))
                except Exception as e:
                    logger.debug(f"Error parsing Indeed job card: {e}")
                    continue
            
            logger.info(f"Scraped {len(jobs)} jobs from Indeed for '{query}'")
            
        except Exception as e:
            logger.error(f"Error scraping Indeed: {e}")
        
        return jobs
    
    def _parse_job_card(self, card) -> Dict:
        """Parse individual job card"""
        job_data = {}
        
        try:
            # Title
            title_elem = card.find(['h2', 'span', 'a'], class_=lambda x: x and 'title' in x.lower())
            if title_elem:
                job_data['title'] = title_elem.get_text(strip=True)
            
            # Company
            company_elem = card.find(['span', 'div'], class_=lambda x: x and 'company' in x.lower())
            if company_elem:
                job_data['company'] = company_elem.get_text(strip=True)
            
            # Location
            location_elem = card.find(['div', 'span'], class_=lambda x: x and 'location' in x.lower())
            if location_elem:
                job_data['location'] = location_elem.get_text(strip=True)
            
            # Salary
            salary_elem = card.find(['div', 'span'], class_=lambda x: x and 'salary' in x.lower())
            if salary_elem:
                job_data['salary'] = salary_elem.get_text(strip=True)
            
            # Description snippet
            desc_elem = card.find(['div', 'span'], class_=lambda x: x and ('snippet' in x.lower() or 'summary' in x.lower()))
            if desc_elem:
                job_data['description'] = desc_elem.get_text(strip=True)
            
            # URL
            link_elem = card.find('a', href=True)
            if link_elem:
                href = link_elem['href']
                job_data['url'] = f"{self.BASE_URL}{href}" if href.startswith('/') else href
                # Extract job ID from URL
                if '/viewjob?jk=' in href:
                    job_data['external_id'] = href.split('jk=')[1].split('&')[0]
            
            # Posted date
            date_elem = card.find(['span', 'div'], class_=lambda x: x and 'date' in x.lower())
            if date_elem:
                job_data['posted_date'] = self._parse_date(date_elem.get_text(strip=True))
            
            # Job type
            type_elem = card.find(['span', 'div'], text=lambda x: x and any(t in x.lower() for t in ['full-time', 'part-time', 'contract']))
            if type_elem:
                job_data['job_type'] = type_elem.get_text(strip=True)
            
        except Exception as e:
            logger.debug(f"Error parsing job card element: {e}")
        
        return job_data
    
    def _map_experience(self, experience: str) -> str:
        """Map experience level to Indeed format"""
        experience = experience.lower()
        if 'entry' in experience or '0-1' in experience:
            return 'entry_level'
        elif 'mid' in experience or '2-5' in experience:
            return 'mid_level'
        elif 'senior' in experience or '5+' in experience:
            return 'senior_level'
        return ''
