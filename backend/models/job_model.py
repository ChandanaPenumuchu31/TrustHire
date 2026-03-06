"""
Job Model - Job aggregation and processing
"""

from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

from scrapers.remoteok_scraper import RemoteOKScraper
from scrapers.remotive_scraper import RemotiveScraper
from models.fraud_detector import get_fraud_detector
from database import db, Job, SearchHistory
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class JobAggregator:
    """Aggregate jobs from multiple platforms - using only working, API-based scrapers"""
    
    def __init__(self):
        """Initialize scrapers - RemoteOK and Remotive both have working APIs"""
        self.scrapers = {
            'remoteok': RemoteOKScraper(),
            'remotive': RemotiveScraper()
        }
        self.fraud_detector = get_fraud_detector()
    
    def search_all_platforms(self, query: str, location: str = '', 
                            experience: str = '', platforms: List[str] = None,
                            max_results_per_platform: int = 50) -> List[Dict]:
        """
        Search all platforms and aggregate results
        """
        if platforms is None or 'all' in platforms:
            platforms = list(self.scrapers.keys())
        
        all_jobs = []
        
        # Use ThreadPoolExecutor for parallel scraping
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_platform = {}
            
            for platform in platforms:
                if platform in self.scrapers:
                    scraper = self.scrapers[platform]
                    future = executor.submit(
                        scraper.search_jobs, 
                        query, location, experience, max_results_per_platform
                    )
                    future_to_platform[future] = platform
            
            # Collect results as they complete
            for future in as_completed(future_to_platform):
                platform = future_to_platform[future]
                try:
                    jobs = future.result()
                    logger.info(f"Retrieved {len(jobs)} jobs from {platform}")
                    all_jobs.extend(jobs)
                except Exception as e:
                    logger.error(f"Error scraping {platform}: {e}")
        
        # Run fraud detection on all jobs
        logger.info(f"Running fraud detection on {len(all_jobs)} jobs")
        all_jobs = self._apply_fraud_detection(all_jobs)
        
        # Sort by trust score
        all_jobs.sort(key=lambda x: x.get('trust_score', 0), reverse=True)
        
        return all_jobs
    
    def _apply_fraud_detection(self, jobs: List[Dict]) -> List[Dict]:
        """Apply fraud detection to job listings with detailed reasons"""
        for job in jobs:
            try:
                fraud_result = self.fraud_detector.predict(job)
                job['trust_score'] = fraud_result['trust_score']
                job['is_fraudulent'] = fraud_result['is_fraudulent']
                job['fraud_confidence'] = fraud_result['fraud_confidence']
                job['fraud_signals'] = fraud_result['fraud_signals']
                job['detailed_reasons'] = fraud_result.get('detailed_reasons', [])
                job['mca_verification'] = fraud_result.get('mca_verification', {})
                job['company_reviews'] = fraud_result.get('company_reviews', {})
            except Exception as e:
                logger.error(f"Error in fraud detection: {e}")
                job['trust_score'] = 0.5
                job['is_fraudulent'] = False
                job['fraud_confidence'] = 0.0
                job['fraud_signals'] = []
                job['detailed_reasons'] = []
        
        return jobs
    
    def save_jobs_to_db(self, jobs: List[Dict]) -> int:
        """Save jobs to database"""
        saved_count = 0
        
        for job_data in jobs:
            try:
                # Check if job already exists
                existing = Job.query.filter_by(
                    platform=job_data['platform'],
                    external_id=job_data.get('external_id', '')
                ).first()
                
                if existing:
                    # Update existing job
                    existing.trust_score = job_data.get('trust_score', 0.5)
                    existing.is_fraudulent = job_data.get('is_fraudulent', False)
                    existing.fraud_confidence = job_data.get('fraud_confidence', 0.0)
                    existing.fraud_signals = json.dumps(job_data.get('fraud_signals', []))
                    existing.updated_at = datetime.utcnow()
                else:
                    # Create new job
                    new_job = Job(
                        title=job_data.get('title', ''),
                        company=job_data.get('company', ''),
                        location=job_data.get('location', ''),
                        description=job_data.get('description', ''),
                        requirements=job_data.get('requirements', ''),
                        salary=job_data.get('salary', ''),
                        experience_required=job_data.get('experience_required', ''),
                        job_type=job_data.get('job_type', ''),
                        platform=job_data.get('platform', ''),
                        external_id=job_data.get('external_id', ''),
                        url=job_data.get('url', ''),
                        trust_score=job_data.get('trust_score', 0.5),
                        is_fraudulent=job_data.get('is_fraudulent', False),
                        fraud_confidence=job_data.get('fraud_confidence', 0.0),
                        fraud_signals=json.dumps(job_data.get('fraud_signals', [])),
                        posted_date=job_data.get('posted_date')
                    )
                    db.session.add(new_job)
                    saved_count += 1
                
                db.session.commit()
            except Exception as e:
                logger.error(f"Error saving job to database: {e}")
                db.session.rollback()
        
        return saved_count
    
    def track_search(self, query: str, location: str = '', experience: str = ''):
        """Track search history for analytics"""
        try:
            search = SearchHistory.query.filter_by(
                query=query,
                location=location,
                experience=experience
            ).first()
            
            if search:
                search.count += 1
                search.last_searched = datetime.utcnow()
            else:
                search = SearchHistory(
                    query=query,
                    location=location,
                    experience=experience
                )
                db.session.add(search)
            
            db.session.commit()
        except Exception as e:
            logger.error(f"Error tracking search: {e}")
            db.session.rollback()
