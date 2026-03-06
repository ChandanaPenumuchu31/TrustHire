"""
Indeed Scraper - Using JSearch API for reliable job data
"""

from typing import List, Dict
from .base_scraper import BaseScraper
import requests
import logging
import urllib.parse
import time

logger = logging.getLogger(__name__)

class IndeedScraper(BaseScraper):
    """Indeed scraper - fetches real job listings using JSearch API"""
    
    BASE_URL = "https://www.indeed.com"
    
    def __init__(self):
        super().__init__()
        # Using public job search APIs
        self.session = requests.Session()
        
    def get_platform_name(self) -> str:
        return "indeed"
    
    def search_jobs(self, query: str, location: str = '', experience: str = '', max_results: int = 50) -> List[Dict]:
        """Search real jobs from Indeed using multiple methods"""
        jobs = []
        
        try:
            logger.info(f"Scraping Indeed for: '{query}' in '{location or 'US'}'")
            
            # Method 1: Try Indeed RSS feed (public, no auth required)
            jobs = self._scrape_indeed_rss(query, location, max_results)
            
            # Method 2: If RSS fails, try direct scraping with better headers
            if len(jobs) == 0:
                logger.info("RSS failed, trying direct scraping...")
                jobs = self._scrape_indeed_direct(query, location, max_results)
            
            logger.info(f"Successfully retrieved {len(jobs)} jobs from Indeed")
            
        except Exception as e:
            logger.error(f"Error scraping Indeed: {e}")
        
        return jobs
    
    def _scrape_indeed_rss(self, query: str, location: str, max_results: int = 50) -> List[Dict]:
        """Scrape Indeed RSS feed (public API)"""
        jobs = []
        try:
            logger.info("Fetching Indeed RSS feed...")
            
            params = {
                'q': query,
                'l': location or '',
                'sort': 'date',
                'limit': min(max_results, 50)
            }
            rss_url = f"{self.BASE_URL}/rss?{urllib.parse.urlencode(params)}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = self.session.get(rss_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'xml')
                items = soup.find_all('item')
                
                logger.info(f"Found {len(items)} jobs from Indeed RSS")
                
                for item in items[:max_results]:
                    try:
                        title = item.find('title').text if item.find('title') else None
                        link = item.find('link').text if item.find('link') else None
                        description = item.find('description').text if item.find('description') else ''
                        pub_date = item.find('pubDate').text if item.find('pubDate') else 'Recently'
                        
                        # Parse description HTML
                        desc_soup = BeautifulSoup(description, 'html.parser')
                        desc_text = desc_soup.get_text(strip=True)
                        
                        # Extract company from description or title
                        company = 'Company'
                        if ' - ' in title:
                            parts = title.split(' - ')
                            if len(parts) >= 2:
                                company = parts[-1]
                                title = ' - '.join(parts[:-1])
                        
                        # Try to find company in description
                        company_elem = desc_soup.find('span', {'class': 'company'})
                        if company_elem:
                            company = company_elem.text.strip()
                        
                        # Extract location from description
                        location_elem = desc_soup.find('span', {'class': 'location'})
                        job_location = location_elem.text.strip() if location_elem else (location or 'Remote')
                        
                        if title and link:
                            job_data = {
                                'title': title.strip(),
                                'company': company.strip(),
                                'location': job_location,
                                'description': desc_text[:500] if desc_text else f'{title} at {company}',
                                'url': link,
                                'posted_date': pub_date,
                                'platform': 'indeed',
                                'salary': self._extract_salary(desc_text),
                                'job_type': self._extract_job_type(desc_text),
                                'experience_level': experience or self._extract_experience_level(desc_text),
                                'verified_source': True
                            }
                            
                            if self._validate_job(job_data):
                                jobs.append(job_data)
                    except Exception as e:
                        logger.error(f"Error parsing RSS item: {e}")
                        continue
                
                logger.info(f"Successfully scraped {len(jobs)} jobs from Indeed RSS")
            else:
                logger.warning(f"Indeed RSS returned status {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error scraping Indeed RSS: {e}")
        
        return jobs
    
    def _scrape_indeed_direct(self, query: str, location: str, max_results: int = 50) -> List[Dict]:
        """Direct scraping with improved headers"""
        jobs = []
        try:
            from bs4 import BeautifulSoup
            
            params = {
                'q': query,
                'l': location or '',
                'fromage': '7',
                'sort': 'date'
            }
            search_url = f"{self.BASE_URL}/jobs?{urllib.parse.urlencode(params)}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://www.google.com/',
                'DNT': '1'
            }
            
            time.sleep(2)  # Rate limiting
            response = self.session.get(search_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Try multiple selectors
                job_cards = soup.find_all('div', {'class': lambda x: x and 'job_seen_beacon' in str(x)})
                if not job_cards:
                    job_cards = soup.find_all('td', {'class': 'resultContent'})
                if not job_cards:
                    job_cards = soup.find_all('div', {'data-jk': True})
                
                logger.info(f"Found {len(job_cards)} job cards")
                
                for card in job_cards[:max_results]:
                    try:
                        job_data = self._parse_job_card(card)
                        if job_data and self._validate_job(job_data):
                            jobs.append(job_data)
                    except Exception as e:
                        logger.error(f"Error parsing card: {e}")
                        
        except Exception as e:
            logger.error(f"Direct scraping error: {e}")
        
        return jobs
    
    def _parse_job_card(self, card) -> Dict:
        """Parse job card from HTML"""
        try:
            # Extract title
            title_elem = card.find('h2', {'class': lambda x: x and 'jobTitle' in str(x)})
            if not title_elem:
                title_elem = card.find('a', {'class': lambda x: x and 'jcs-JobTitle' in str(x)})
            
            title = title_elem.get_text(strip=True) if title_elem else None
            
            # Extract company
            company_elem = card.find('span', {'data-testid': 'company-name'})
            if not company_elem:
                company_elem = card.find('span', {'class': lambda x: x and 'companyName' in str(x)})
            
            company = company_elem.get_text(strip=True) if company_elem else 'Company'
            
            # Extract location
            location_elem = card.find('div', {'data-testid': 'text-location'})
            if not location_elem:
                location_elem = card.find('div', {'class': lambda x: x and 'companyLocation' in str(x)})
            
            location = location_elem.get_text(strip=True) if location_elem else 'Remote'
            
            # Extract URL
            link_elem = card.find('a', href=True)
            job_url = link_elem['href'] if link_elem else None
            if job_url and not job_url.startswith('http'):
                job_url = f"{self.BASE_URL}{job_url}"
            
            # Extract description
            desc_elem = card.find('div', {'class': lambda x: x and 'snippet' in str(x).lower()})
            description = desc_elem.get_text(strip=True) if desc_elem else f'{title} at {company}'
            
            if not title:
                return None
            
            return {
                'title': title,
                'company': company,
                'location': location,
                'description': description[:500],
                'url': job_url or f"{self.BASE_URL}/jobs",
                'posted_date': 'Recently',
                'platform': 'indeed',
                'salary': self._extract_salary(description),
                'job_type': self._extract_job_type(description),
                'experience_level': self._extract_experience_level(description),
                'verified_source': True
            }
            
        except Exception as e:
            logger.error(f"Error parsing job card: {e}")
            return None
    
    def _extract_salary(self, text: str) -> str:
        """Extract salary from text"""
        import re
        salary_patterns = [
            r'\$[\d,]+\s*-\s*\$[\d,]+',
            r'\$[\d,]+(?:\.\d{2})?(?:\s*(?:per|/)\s*(?:hour|year|month))?',
            r'[\d,]+\s*-\s*[\d,]+\s*(?:USD|INR|EUR)'
        ]
        for pattern in salary_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        return None
