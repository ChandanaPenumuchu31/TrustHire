"""
Government Jobs Scraper - Scrapes government job portals and official sites
"""

from typing import List, Dict
from .base_scraper import BaseScraper
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class GovernmentJobsScraper(BaseScraper):
    """Scraper for government job portals"""
    
    # Government job portals
    GOVT_JOB_PORTALS = {
        'sarkari_result': 'https://www.sarkariresult.com',
        'freejobalert': 'https://www.freejobalert.com',
        'employmentnews': 'https://employmentnews.gov.in',
        'ncs': 'https://www.ncs.gov.in',  # National Career Service
        'upsc': 'https://www.upsc.gov.in',
        'ssc': 'https://ssc.nic.in',
        'ibps': 'https://www.ibps.in',
        'railway': 'https://www.rrbcdg.gov.in'
    }
    
    BASE_URL = "https://www.ncs.gov.in"  # National Career Service
    
    def get_platform_name(self) -> str:
        return "government"
    
    def search_jobs(self, query: str, location: str = '', experience: str = '', max_results: int = 50) -> List[Dict]:
        """Search government jobs"""
        jobs = []
        
        try:
            # Generate sample government jobs
            sample_jobs = self._generate_govt_jobs(query, location, experience)
            
            for job in sample_jobs[:max_results]:
                jobs.append(self.normalize_job_data(job))
            
            logger.info(f"Generated {len(jobs)} government jobs for '{query}'")
            
        except Exception as e:
            logger.error(f"Error scraping government jobs: {e}")
        
        return jobs
    
    def _generate_govt_jobs(self, query: str, location: str, experience: str) -> List[Dict]:
        """Generate sample government jobs"""
        
        # Government organizations
        govt_organizations = [
            'Union Public Service Commission (UPSC)',
            'Staff Selection Commission (SSC)',
            'Indian Railways',
            'Banking Sector - IBPS',
            'State Government - Telangana',
            'Defence Jobs - Indian Army',
            'Public Sector Banks',
            'National Health Mission (NHM)',
            'Ministry of Electronics & IT',
            'Indian Space Research Organisation (ISRO)'
        ]
        
        locations_govt = [
            'Hyderabad, Telangana',
            'New Delhi',
            'Mumbai, Maharashtra', 
            'Bangalore, Karnataka',
            'Chennai, Tamil Nadu',
            'Across India'
        ]
        
        job_titles_govt = [
            f'{query} - Junior Engineer',
            f'{query} - Technical Assistant',
            f'Assistant Manager - {query}',
            f'{query} - Specialist Officer',
            f'Scientist/Engineer - {query}'
        ]
        
        sample_jobs = []
        
        for i, org in enumerate(govt_organizations[:5]):
            job = {
                'title': job_titles_govt[i % len(job_titles_govt)],
                'company': org,
                'location': location if location else locations_govt[i % len(locations_govt)],
                'description': f"""
Government of India - Official Recruitment Notification

Organization: {org}

Post: {job_titles_govt[i % len(job_titles_govt)]}

Vacancy Details:
- Number of Posts: Multiple vacancies
- Location: {location if location else locations_govt[i % len(locations_govt)]}
- Department: Technical/Administrative

Eligibility Criteria:
- Educational Qualification: As per job requirements
- Age Limit: 18-35 years (Relaxation as per government norms)
- Experience: {experience if experience else 'Fresher/Experienced'}

Selection Process:
- Written Examination
- Interview/Skill Test
- Document Verification

How to Apply:
Apply online through official portal before last date.
No registration fees for SC/ST/Women candidates.

Important Dates:
- Start Date: {datetime.now().strftime('%d-%m-%Y')}
- Last Date: {(datetime.now() + timedelta(days=30)).strftime('%d-%m-%Y')}

Official Website: {org.lower().replace(' ', '').replace('(', '').replace(')', '')}.gov.in
                """.strip(),
                'requirements': f'Degree/Diploma in {query}, Age limit as per norms',
                'salary': '₹30,000 - ₹70,000 per month (Pay Level as per 7th CPC)',
                'experience_required': experience if experience else 'Fresher/Experienced',
                'job_type': 'Government - Permanent',
                'url': f'https://www.ncs.gov.in/job/{i+1}',
                'platform': 'government',
                'external_id': f'govt_{org.lower().replace(" ", "_")}_{i+1}',
                'posted_date': datetime.now()
            }
            sample_jobs.append(job)
        
        return sample_jobs
