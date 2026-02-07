"""
Naukri.com job scraper
"""

from typing import List, Dict
from .base_scraper import BaseScraper
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class NaukriScraper(BaseScraper):
    """Scraper for Naukri.com (Indian job portal)"""
    
    BASE_URL = "https://www.naukri.com"
    
    def get_platform_name(self) -> str:
        return "naukri"
    
    def search_jobs(self, query: str, location: str = '', experience: str = '', max_results: int = 50) -> List[Dict]:
        """Search jobs on Naukri"""
        jobs = []
        
        try:
            # Build search URL
            query_formatted = query.replace(' ', '-')
            location_formatted = location.replace(' ', '-') if location else 'india'
            
            search_url = f"{self.BASE_URL}/{query_formatted}-jobs"
            
            if location:
                search_url += f"-in-{location_formatted}"
            
            # Add experience filter
            params = []
            if experience:
                exp_min, exp_max = self._map_experience(experience)
                if exp_min is not None:
                    params.append(f"experience={exp_min}")
            
            if params:
                search_url += "?" + "&".join(params)
            
            soup = self._fetch_page(search_url)
            if not soup:
                logger.warning(f"Failed to fetch Naukri jobs for query: {query}")
                return jobs
            
            # Parse job listings
            job_cards = soup.find_all(['article', 'div'], class_=lambda x: x and ('job' in x.lower() or 'tuple' in x.lower()))
            
            for card in job_cards[:max_results]:
                try:
                    job_data = self._parse_job_card(card)
                    if job_data and job_data.get('title'):
                        jobs.append(self.normalize_job_data(job_data))
                except Exception as e:
                    logger.debug(f"Error parsing Naukri job card: {e}")
                    continue
            
            logger.info(f"Scraped {len(jobs)} jobs from Naukri for '{query}'")
            
        except Exception as e:
            logger.error(f"Error scraping Naukri: {e}")
        
        return jobs
    
    def _parse_job_card(self, card) -> Dict:
        """Parse individual job card"""
        job_data = {}
        
        try:
            # Title
            title_elem = card.find(['a', 'h2', 'div'], class_=lambda x: x and 'title' in x.lower())
            if title_elem:
                job_data['title'] = title_elem.get_text(strip=True)
            
            # Company
            company_elem = card.find(['a', 'div', 'span'], class_=lambda x: x and ('company' in x.lower() or 'recruiter' in x.lower()))
            if company_elem:
                job_data['company'] = company_elem.get_text(strip=True)
            
            # Location
            location_elem = card.find(['span', 'div'], class_=lambda x: x and ('location' in x.lower() or 'loc' in x.lower()))
            if location_elem:
                job_data['location'] = location_elem.get_text(strip=True)
            
            # Experience
            exp_elem = card.find(['span', 'div'], class_=lambda x: x and ('exp' in x.lower() or 'experience' in x.lower()))
            if exp_elem:
                job_data['experience_required'] = exp_elem.get_text(strip=True)
            
            # Salary
            salary_elem = card.find(['span', 'div'], class_=lambda x: x and 'salary' in x.lower())
            if salary_elem:
                job_data['salary'] = salary_elem.get_text(strip=True)
            
            # Description
            desc_elem = card.find(['div', 'span'], class_=lambda x: x and ('desc' in x.lower() or 'snippet' in x.lower()))
            if desc_elem:
                job_data['description'] = desc_elem.get_text(strip=True)
            
            # URL
            link_elem = card.find('a', href=True)
            if link_elem:
                href = link_elem['href']
                job_data['url'] = href if href.startswith('http') else f"{self.BASE_URL}{href}"
                # Extract job ID
                if '/job-listings-' in href:
                    job_data['external_id'] = href.split('/job-listings-')[1].split('?')[0]
            
            # Posted date
            date_elem = card.find(['span', 'div'], class_=lambda x: x and ('date' in x.lower() or 'posted' in x.lower()))
            if date_elem:
                job_data['posted_date'] = self._parse_date(date_elem.get_text(strip=True))
            
            # Job type
            type_elem = card.find(['span'], text=lambda x: x and any(t in x.lower() for t in ['full time', 'part time', 'contract']))
            if type_elem:
                job_data['job_type'] = type_elem.get_text(strip=True)
            
        except Exception as e:
            logger.debug(f"Error parsing Naukri job element: {e}")
        
        return job_data
    
    def _map_experience(self, experience: str) -> tuple:
        """Map experience to Naukri format (min, max years)"""
        experience = experience.lower()
        if 'entry' in experience or '0-1' in experience or 'fresher' in experience:
            return (0, 2)
        elif 'mid' in experience or '2-5' in experience:
            return (2, 5)
        elif 'senior' in experience or '5+' in experience:
            return (5, 15)
        return (None, None)
