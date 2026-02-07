"""
LinkedIn job scraper
"""

from typing import List, Dict
from .base_scraper import BaseScraper
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class LinkedInScraper(BaseScraper):
    """Scraper for LinkedIn Jobs"""
    
    BASE_URL = "https://www.linkedin.com"
    
    def get_platform_name(self) -> str:
        return "linkedin"
    
    def search_jobs(self, query: str, location: str = '', experience: str = '', max_results: int = 50) -> List[Dict]:
        """Search jobs on LinkedIn"""
        jobs = []
        
        try:
            # Build search URL
            search_url = f"{self.BASE_URL}/jobs/search"
            params = {
                'keywords': query.replace(' ', '%20'),
                'location': location.replace(' ', '%20') if location else '',
                'f_TPR': 'r604800',  # Past week
            }
            
            # Add experience level if provided
            if experience:
                exp_code = self._map_experience(experience)
                if exp_code:
                    params['f_E'] = exp_code
            
            # Build URL
            url = f"{search_url}?{'&'.join([f'{k}={v}' for k, v in params.items() if v])}"
            
            soup = self._fetch_page(url)
            if not soup:
                logger.warning(f"Failed to fetch LinkedIn jobs for query: {query}")
                return jobs
            
            # Parse job cards
            job_cards = soup.find_all(['div', 'li'], class_=lambda x: x and ('job' in x.lower() or 'card' in x.lower()))
            
            for card in job_cards[:max_results]:
                try:
                    job_data = self._parse_job_card(card)
                    if job_data and job_data.get('title'):
                        jobs.append(self.normalize_job_data(job_data))
                except Exception as e:
                    logger.debug(f"Error parsing LinkedIn job card: {e}")
                    continue
            
            logger.info(f"Scraped {len(jobs)} jobs from LinkedIn for '{query}'")
            
        except Exception as e:
            logger.error(f"Error scraping LinkedIn: {e}")
        
        return jobs
    
    def _parse_job_card(self, card) -> Dict:
        """Parse individual job card"""
        job_data = {}
        
        try:
            # Title
            title_elem = card.find(['h3', 'a'], class_=lambda x: x and 'title' in x.lower())
            if title_elem:
                job_data['title'] = title_elem.get_text(strip=True)
            
            # Company
            company_elem = card.find(['h4', 'span', 'a'], class_=lambda x: x and 'company' in x.lower())
            if company_elem:
                job_data['company'] = company_elem.get_text(strip=True)
            
            # Location
            location_elem = card.find(['span', 'div'], class_=lambda x: x and 'location' in x.lower())
            if location_elem:
                job_data['location'] = location_elem.get_text(strip=True)
            
            # Description
            desc_elem = card.find(['p', 'div'], class_=lambda x: x and ('description' in x.lower() or 'snippet' in x.lower()))
            if desc_elem:
                job_data['description'] = desc_elem.get_text(strip=True)
            
            # URL
            link_elem = card.find('a', href=True)
            if link_elem:
                href = link_elem['href']
                job_data['url'] = href if href.startswith('http') else f"{self.BASE_URL}{href}"
                # Extract job ID
                if '/jobs/view/' in href:
                    job_data['external_id'] = href.split('/jobs/view/')[1].split('?')[0].split('/')[0]
            
            # Posted date
            date_elem = card.find(['time', 'span'], class_=lambda x: x and 'time' in x.lower())
            if date_elem:
                job_data['posted_date'] = self._parse_date(date_elem.get_text(strip=True))
            
            # Job type
            type_elem = card.find(['span'], class_=lambda x: x and 'type' in x.lower())
            if type_elem:
                job_data['job_type'] = type_elem.get_text(strip=True)
            
        except Exception as e:
            logger.debug(f"Error parsing LinkedIn job element: {e}")
        
        return job_data
    
    def _map_experience(self, experience: str) -> str:
        """Map experience level to LinkedIn format"""
        experience = experience.lower()
        if 'entry' in experience or '0-1' in experience:
            return '1,2'  # Internship, Entry level
        elif 'mid' in experience or '2-5' in experience:
            return '3'  # Associate
        elif 'senior' in experience or '5+' in experience:
            return '4,5'  # Mid-Senior, Director
        return ''
