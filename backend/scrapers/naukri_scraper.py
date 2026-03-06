"""
Naukri Scraper - API-based scraping with fallback to HTML parsing
"""

from typing import List, Dict
from .base_scraper import BaseScraper
import requests
from bs4 import BeautifulSoup
import logging
import urllib.parse
import time
import random
import json

logger = logging.getLogger(__name__)

class NaukriScraper(BaseScraper):
    """Naukri scraper - fetches real job listings using API"""
    
    BASE_URL = "https://www.naukri.com"
    API_URL = "https://www.naukri.com/jobapi/v3/search"
    
    def __init__(self):
        super().__init__()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.naukri.com/',
            'Origin': 'https://www.naukri.com',
            'systemid': '109',
            'appid': '109',
            'clientid': 'd3skt0p'
        })
    
    def get_platform_name(self) -> str:
        return "naukri"
    
    def search_jobs(self, query: str, location: str = '', experience: str = '', max_results: int = 50) -> List[Dict]:
        """Search real jobs from Naukri using their API"""
        jobs = []
        
        try:
            logger.info(f"Scraping Naukri for: '{query}' in '{location or 'India'}'")
            
            # Try API approach first
            api_jobs = self._search_via_api(query, location, experience, max_results)
            if api_jobs:
                jobs.extend(api_jobs)
                logger.info(f"Got {len(api_jobs)} jobs from Naukri API")
            
            # If API fails or returns few jobs, try HTML scraping
            if len(jobs) < 10:
                html_jobs = self._search_via_html(query, location, experience, max_results)
                if html_jobs:
                    jobs.extend(html_jobs)
                    logger.info(f"Got {len(html_jobs)} additional jobs from Naukri HTML")
            
            # Remove duplicates based on URL
            seen_urls = set()
            unique_jobs = []
            for job in jobs:
                if job['url'] not in seen_urls:
                    seen_urls.add(job['url'])
                    unique_jobs.append(job)
            
            logger.info(f"Successfully scraped {len(unique_jobs)} unique jobs from Naukri")
            return unique_jobs[:max_results]
            
        except Exception as e:
            logger.error(f"Error scraping Naukri: {e}")
            return jobs
    
    def _search_via_api(self, query: str, location: str, experience: str, max_results: int) -> List[Dict]:
        """Search using Naukri's internal API"""
        jobs = []
        
        try:
            # Build API parameters
            params = {
                'noOfResults': min(max_results, 50),
                'urlType': 'search_by_keyword',
                'searchType': 'adv',
                'keyword': query,
                'pageNo': 1,
                'sort': 'date',
                'seoKey': query.replace(' ', '-').lower(),
                'src': 'jobsearchDesk',
                'latLong': ''
            }
            
            if location:
                params['location'] = location
                params['cityType'] = 'currentLocation'
            
            # Add experience filter
            if experience:
                exp_mapping = {
                    'entry': '0-2',
                    'junior': '2-5',
                    'mid': '5-10',
                    'senior': '10-15',
                    'lead': '15-20'
                }
                exp_value = exp_mapping.get(experience.lower(), '')
                if exp_value:
                    params['experience'] = exp_value
            
            response = self.session.get(self.API_URL, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'jobDetails' in data:
                    for job_item in data['jobDetails'][:max_results]:
                        try:
                            job_data = self._parse_api_job(job_item)
                            if job_data and self._validate_job(job_data):
                                jobs.append(job_data)
                        except Exception as e:
                            logger.error(f"Error parsing API job: {e}")
                            continue
                            
        except Exception as e:
            logger.error(f"Naukri API error: {e}")
        
        return jobs
    
    def _parse_api_job(self, job_item: Dict) -> Dict:
        """Parse job data from Naukri API response"""
        try:
            title = job_item.get('title', '').strip()
            company = job_item.get('companyName', 'Not specified').strip()
            
            if not title:
                return None
            
            # Build job URL
            job_id = job_item.get('jobId', '')
            job_url = f"{self.BASE_URL}/job-listings-{job_id}" if job_id else self.BASE_URL
            
            # Extract location
            placeholders = job_item.get('placeholders', [])
            location = ', '.join([p.get('label', '') for p in placeholders if p.get('type') == 'location'])
            if not location:
                location = 'India'
            
            # Extract experience
            experience = ''
            for p in placeholders:
                if p.get('type') == 'experience':
                    experience = p.get('label', '')
                    break
            
            # Extract salary
            salary = None
            for p in placeholders:
                if p.get('type') == 'salary':
                    salary = p.get('label', '')
                    break
            
            # Extract description
            description = job_item.get('jobDescription', '')
            if not description:
                description = f"{title} position at {company}"
            
            # Posted date
            posted_date = job_item.get('footerText', 'Recently posted')
            
            job_data = {
                'title': title,
                'company': company,
                'location': location,
                'description': description[:500],
                'url': job_url,
                'posted_date': posted_date,
                'platform': 'naukri',
                'experience_level': experience or 'Not specified',
                'salary': salary,
                'job_type': self._extract_job_type(description),
                'verified_source': True
            }
            
            return job_data
            
        except Exception as e:
            logger.error(f"Error parsing API job: {e}")
            return None
    
    def _search_via_html(self, query: str, location: str, experience: str, max_results: int) -> List[Dict]:
        """Fallback HTML scraping approach"""
        jobs = []
        
        try:
            # Build search URL
            query_encoded = urllib.parse.quote(query)
            location_encoded = urllib.parse.quote(location) if location else ''
            
            search_url = f"{self.BASE_URL}/{query.replace(' ', '-')}-jobs"
            if location:
                search_url += f"-in-{location.replace(' ', '-')}"
            
            # Add query parameters
            params = {
                'k': query,
                'sort': '1'  # Sort by date
            }
            if location:
                params['l'] = location
            
            response = self.session.get(search_url, params=params, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find job cards - try multiple selectors
                job_cards = soup.find_all('article', class_=lambda x: x and 'jobTuple' in str(x))
                
                if not job_cards:
                    job_cards = soup.find_all('div', class_=lambda x: x and 'jobTuple' in str(x))
                
                if not job_cards:
                    job_cards = soup.find_all('div', {'data-job-id': True})
                
                logger.info(f"Found {len(job_cards)} job cards via HTML")
                
                for card in job_cards[:max_results]:
                    try:
                        job_data = self._parse_html_job_card(card)
                        if job_data and self._validate_job(job_data):
                            jobs.append(job_data)
                    except Exception as e:
                        logger.error(f"Error parsing HTML job card: {e}")
                        continue
                        
        except Exception as e:
            logger.error(f"HTML scraping error: {e}")
        
        return jobs
    
    def _parse_html_job_card(self, card) -> Dict:
        """Parse a Naukri job card from HTML"""
        try:
            # Extract title
            title_elem = card.select_one('a.title, .jobTitle a, [class*="title"] a')
            title = title_elem.get_text(strip=True) if title_elem else None
            
            if not title:
                return None
            
            # Extract URL
            job_url = title_elem.get('href', '') if title_elem else ''
            if job_url and not job_url.startswith('http'):
                job_url = f"{self.BASE_URL}{job_url}"
            
            # Extract company
            company_elem = card.select_one('.companyInfo a, [class*="company"] a, .comp-name')
            company = company_elem.get_text(strip=True) if company_elem else 'Not specified'
            
            # Extract experience
            exp_elem = card.select_one('.expwdth, [class*="experience"], .exp')
            experience = exp_elem.get_text(strip=True) if exp_elem else 'Not specified'
            
            # Extract salary
            salary_elem = card.select_one('[class*="salary"], .sal')
            salary = salary_elem.get_text(strip=True) if salary_elem else None
            
            # Extract location
            location_elem = card.select_one('.locWdth, [class*="location"], .loc')
            location = location_elem.get_text(strip=True) if location_elem else 'India'
            
            # Extract description
            desc_elem = card.select_one('.job-description, .jobDesc, [class*="desc"]')
            description = desc_elem.get_text(strip=True) if desc_elem else f'{title} position at {company}'
            
            # Extract posted date
            date_elem = card.select_one('.jobAge, [class*="date"], .type')
            posted_date = date_elem.get_text(strip=True) if date_elem else 'Recently posted'
            
            job_data = {
                'title': title,
                'company': company,
                'location': location,
                'description': description[:500],
                'url': job_url or self.BASE_URL,
                'posted_date': posted_date,
                'platform': 'naukri',
                'experience_level': experience,
                'salary': salary,
                'job_type': self._extract_job_type(description)
            }
            
            return job_data
            
        except Exception as e:
            logger.error(f"Error parsing HTML job card: {e}")
            return None
