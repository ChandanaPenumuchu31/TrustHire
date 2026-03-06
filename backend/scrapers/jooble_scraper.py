"""
Jooble Scraper - Fetches job data from Jooble job search API
Jooble is a job aggregator that provides an API for job searching
"""

from typing import List, Dict, Optional
from .base_scraper import BaseScraper
import requests
import logging
import time
from urllib.parse import quote, urlencode

logger = logging.getLogger(__name__)

class JoobleAPIScraper(BaseScraper):
    """Jooble API scraper - fetches job listings via Jooble API"""
    
    BASE_URL = "https://jooble.org/api"
    
    # Country codes for different locations
    COUNTRY_CODES = {
        'india': 'in',
        'united states': 'us',
        'usa': 'us',
        'united kingdom': 'uk',
        'uk': 'uk',
        'canada': 'ca',
        'australia': 'au',
        'germany': 'de',
        'france': 'fr',
        'singapore': 'sg',
        'netherlands': 'nl',
        'italy': 'it',
        'spain': 'es',
        'brazil': 'br',
        'mexico': 'mx',
        'japan': 'jp',
        'south korea': 'kr',
        'china': 'cn'
    }
    
    def __init__(self, api_key: str = None):
        super().__init__()
        # Jooble provides free API access, but you can get an API key for higher limits
        self.api_key = api_key or "your_jooble_api_key_here"
        self.use_selenium = True  # Enable Selenium for Cloudflare bypass
        
    def get_platform_name(self) -> str:
        return "jooble"
    
    def search_jobs(self, query: str, location: str = '', experience: str = '', max_results: int = 50) -> List[Dict]:
        """Search jobs from Jooble API"""
        jobs = []
        
        try:
            logger.info(f"Fetching Jooble jobs for: '{query}' in '{location or 'Worldwide'}'")
            
            # Get country code for location
            country = self._get_country_code(location)
            
            # If API key is available, use API endpoint
            if self.api_key and self.api_key != "your_jooble_api_key_here":
                jobs = self._fetch_via_api(query, location, country, max_results)
            
            # Fallback to web scraping with Selenium (bypasses Cloudflare)
            if not jobs:
                jobs = self._fetch_via_selenium(query, location, max_results)
            
            logger.info(f"Successfully retrieved {len(jobs)} Jooble jobs")
            
        except Exception as e:
            logger.error(f"Error fetching Jooble jobs: {e}")
        
        return jobs
    
    def _get_country_code(self, location: str) -> str:
        """Get country code for location"""
        if not location:
            return 'us'  # Default to US
        
        location_lower = location.lower().strip()
        
        # Check if we have a direct match
        for country, code in self.COUNTRY_CODES.items():
            if country in location_lower:
                return code
        
        # Default to US
        return 'us'
    
    def _fetch_via_api(self, query: str, location: str, country: str, max_results: int) -> List[Dict]:
        """Fetch jobs using Jooble API"""
        jobs = []
        
        try:
            api_url = f"{self.BASE_URL}/{self.api_key}"
            
            payload = {
                "keywords": query,
                "location": location,
                "radius": "25",
                "page": "1"
            }
            
            headers = {
                'Content-Type': 'application/json'
            }
            
            response = self.session.post(api_url, json=payload, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                job_listings = data.get('jobs', [])
                
                for job in job_listings[:max_results]:
                    try:
                        job_data = self._parse_api_job(job)
                        if job_data and self._validate_job(job_data):
                            jobs.append(job_data)
                    except Exception as e:
                        logger.debug(f"Error parsing API job: {e}")
                        continue
            else:
                logger.error(f"Jooble API returned status {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error with Jooble API: {e}")
        
        return jobs
    
    def _fetch_via_selenium(self, query: str, location: str, max_results: int) -> List[Dict]:
        """Fetch jobs using Selenium to bypass Cloudflare"""
        jobs = []
        
        try:
            # Import Selenium here (lazy import)
            try:
                from selenium import webdriver
                from selenium.webdriver.chrome.service import Service
                from selenium.webdriver.chrome.options import Options
                from selenium.webdriver.common.by import By
                from selenium.webdriver.support.ui import WebDriverWait
                from selenium.webdriver.support import expected_conditions as EC
                from webdriver_manager.chrome import ChromeDriverManager
                import undetected_chromedriver as uc
            except ImportError:
                logger.warning("Selenium not available, skipping browser-based scraping")
                return jobs
            
            logger.info("Using Selenium to bypass Cloudflare protection...")
            
            # Build URL with correct parameters
            params = {'ukw': query}
            if location:
                params['rgns'] = location
            
            url = f"https://jooble.org/SearchResult?{urlencode(params)}"
            logger.info(f"Fetching: {url}")
            
            # Use undetected-chromedriver to bypass bot detection
            options = uc.ChromeOptions()
            options.add_argument('--headless=new')  # Run in background
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            
            driver = uc.Chrome(options=options)
            
            try:
                driver.get(url)
                
                # Wait for Cloudflare check to complete
                logger.info("Waiting for Cloudflare challenge...")
                time.sleep(5)  # Give Cloudflare time to verify
                
                # Wait for job listings to load
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, "article"))
                    )
                except:
                    logger.warning("No articles found, trying alternative selectors...")
                
                # Get page source after JavaScript execution
                page_source = driver.page_source
                
                # Parse with BeautifulSoup
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(page_source, 'html.parser')
                
                # Find job listings - try multiple selectors
                job_elements = (
                    soup.find_all('article', limit=max_results) or
                    soup.find_all('div', class_='job-item', limit=max_results) or
                    soup.find_all('div', class_='vacancy', limit=max_results) or
                    soup.select('.serp-item__content', limit=max_results)
                )
                
                logger.info(f"Found {len(job_elements)} job elements with Selenium")
                
                for element in job_elements[:max_results]:
                    try:
                        job_data = self._parse_web_job(element)
                        if job_data and self._validate_job(job_data):
                            jobs.append(job_data)
                            logger.info(f"✓ Parsed: {job_data.get('title')} at {job_data.get('company')}")
                    except Exception as e:
                        logger.debug(f"Error parsing job: {e}")
                        continue
                
            finally:
                driver.quit()
                
        except Exception as e:
            logger.error(f"Error with Selenium scraping: {e}", exc_info=True)
        
        return jobs
    
    def _parse_api_job(self, job: Dict) -> Dict:
        """Parse job from API response"""
        return self.normalize_job_data({
            'title': job.get('title', ''),
            'company': job.get('company', ''),
            'location': job.get('location', ''),
            'description': job.get('snippet', ''),
            'salary': job.get('salary', ''),
            'job_type': job.get('type', ''),
            'url': job.get('link', ''),
            'posted_date': self._parse_date(job.get('updated', '')),
            'external_id': str(job.get('id', ''))
        })
    
    def _parse_web_job(self, element) -> Dict:
        """Parse job from web scraping"""
        try:
            # Extract job details - updated selectors for Jooble's structure
            title_elem = (
                element.find('h2') or
                element.find('a', class_='job-title') or
                element.find('a', href=True)
            )
            
            title = title_elem.get_text(strip=True) if title_elem else ''
            url = title_elem.get('href', '') if title_elem else ''
            
            # Make URL absolute
            if url and not url.startswith('http'):
                url = f"https://jooble.org{url}"
            
            company_elem = (
                element.find('span', class_='company') or
                element.find('div', class_='company') or
                element.find(class_='company-name')
            )
            company = company_elem.get_text(strip=True) if company_elem else ''
            
            location_elem = (
                element.find('span', class_='location') or
                element.find('div', class_='location') or
                element.find(class_='job-location')
            )
            location = location_elem.get_text(strip=True) if location_elem else ''
            
            # Get description/snippet
            desc_elem = (
                element.find('div', class_='description') or
                element.find('p', class_='snippet') or
                element.find('div', class_='job-snippet')
            )
            description = desc_elem.get_text(strip=True) if desc_elem else ''
            
            # Get salary if available
            salary_elem = element.find('span', class_='salary') or element.find('div', class_='salary')
            salary = salary_elem.get_text(strip=True) if salary_elem else ''
            
            # Get posted date
            date_elem = element.find('time') or element.find('span', class_='date')
            posted_date = date_elem.get_text(strip=True) if date_elem else ''
            
            return self.normalize_job_data({
                'title': title,
                'company': company,
                'location': location,
                'description': description,
                'salary': salary,
                'url': url,
                'posted_date': self._parse_date(posted_date),
                'external_id': ''
            })
            
        except Exception as e:
            logger.debug(f"Error parsing job element: {e}")
            return {}
    
    def _validate_job(self, job_data: Dict) -> bool:
        """Validate that job data has required fields"""
        required_fields = ['title', 'company']
        return all(job_data.get(field) for field in required_fields)

# Backward-compatible alias
JoobleScraper = JoobleAPIScraper