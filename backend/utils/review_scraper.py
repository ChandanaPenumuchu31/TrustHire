"""
Real-Time Company Review Scraper
Scrapes company reviews from Glassdoor, Indeed, Google, and AmbitionBox
"""

import requests
from bs4 import BeautifulSoup
import logging
import time
from typing import Dict, Optional
import json
import re
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CompanyReviewScraper:
    """Scrapes real company reviews from multiple platforms"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        })
        self.cache = {}  # Simple in-memory cache
        self.cache_duration = timedelta(hours=24)
    
    def get_company_reviews(self, company_name: str, role: str = '') -> Dict:
        """
        Get comprehensive company reviews from multiple sources
        Returns: {
            'glassdoor': {'rating': float, 'reviews': int, 'recommend': float},
            'indeed': {'rating': float, 'reviews': int},
            'google': {'rating': float, 'reviews': int},
            'ambitionbox': {'rating': float, 'reviews': int},
            'average_rating': float,
            'total_reviews': int,
            'sources_found': int
        }
        """
        # Check cache first
        cache_key = f"{company_name.lower().strip()}::{role.lower().strip()}"
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if datetime.now() - cached_time < self.cache_duration:
                logger.info(f"Using cached reviews for {company_name}")
                return cached_data
        
        logger.info(f"Scraping real-time reviews for: {company_name} (role: {role or 'n/a'})")
        
        reviews = {
            'glassdoor': self._scrape_glassdoor(company_name),
            'indeed': self._scrape_indeed(company_name),
            'google': self._scrape_google(company_name),
            'ambitionbox': self._scrape_ambitionbox(company_name)
        }

        role_review_signal = self._scrape_role_signals(company_name, role)
        
        # Calculate aggregate stats
        ratings = [r['rating'] for r in reviews.values() if r and r['rating'] > 0]
        total_reviews = sum([r['reviews'] for r in reviews.values() if r and r['reviews'] > 0])
        
        result = {
            **reviews,
            'average_rating': round(sum(ratings) / len(ratings), 1) if ratings else 0.0,
            'total_reviews': total_reviews,
            'sources_found': len(ratings),
            'role': role,
            'role_review_signal': role_review_signal,
            'scraped_at': datetime.now().isoformat()
        }
        
        # Cache the result
        self.cache[cache_key] = (result, datetime.now())
        
        return result

    def _scrape_role_signals(self, company_name: str, role: str) -> Dict:
        """Collect lightweight role-specific review signals from public search pages."""
        if not role:
            return {
                'query': '',
                'evidence_count': 0,
                'trusted_domain_hits': 0,
                'confidence_boost': 0.0
            }

        try:
            query = f"{company_name} {role} review"
            url = f"https://duckduckgo.com/html/?q={requests.utils.quote(query)}"
            response = self.session.get(url, timeout=5)
            if response.status_code != 200:
                return {
                    'query': query,
                    'evidence_count': 0,
                    'trusted_domain_hits': 0,
                    'confidence_boost': 0.0
                }

            soup = BeautifulSoup(response.text, 'html.parser')
            results = soup.select('.result')
            trusted_domains = ['glassdoor.com', 'indeed.com', 'ambitionbox.com', 'linkedin.com']

            evidence_count = 0
            trusted_hits = 0
            role_words = [w for w in role.lower().split() if w]

            for result in results[:10]:
                text = result.get_text(' ', strip=True).lower()
                if all(word in text for word in role_words[:2]):
                    evidence_count += 1
                if any(domain in text for domain in trusted_domains):
                    trusted_hits += 1

            confidence_boost = min((evidence_count * 0.03) + (trusted_hits * 0.04), 0.25)
            return {
                'query': query,
                'evidence_count': evidence_count,
                'trusted_domain_hits': trusted_hits,
                'confidence_boost': round(confidence_boost, 3)
            }
        except Exception as e:
            logger.debug(f"Role signal scraping error: {e}")
            return {
                'query': f"{company_name} {role} review",
                'evidence_count': 0,
                'trusted_domain_hits': 0,
                'confidence_boost': 0.0
            }
    
    def _scrape_glassdoor(self, company_name: str) -> Dict:
        """Scrape Glassdoor reviews"""
        try:
            # Clean company name for URL
            company_slug = company_name.lower().replace(' ', '-').replace('.', '')
            
            # Try multiple URL patterns
            urls = [
                f"https://www.glassdoor.com/Reviews/{company_slug}-reviews-SRCH_KE0,{len(company_name)}.htm",
                f"https://www.glassdoor.com/Overview/Working-at-{company_slug}-EI_IE.htm"
            ]
            
            for url in urls:
                try:
                    response = self.session.get(url, timeout=5)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # Try to find rating
                        rating_elem = (
                            soup.find('div', {'class': re.compile(r'.*rating.*', re.I)}) or
                            soup.find('span', {'class': re.compile(r'.*rating.*', re.I)})
                        )
                        
                        if rating_elem:
                            rating_text = rating_elem.get_text()
                            rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                            if rating_match:
                                rating = float(rating_match.group(1))
                                
                                # Try to find review count
                                review_count = 0
                                review_elem = soup.find(text=re.compile(r'\d+\s*reviews?', re.I))
                                if review_elem:
                                    count_match = re.search(r'(\d+)', review_elem)
                                    if count_match:
                                        review_count = int(count_match.group(1))
                                
                                logger.info(f"✓ Glassdoor: {rating}/5.0 ({review_count} reviews)")
                                return {'rating': rating, 'reviews': review_count, 'recommend': rating * 20}
                except Exception as e:
                    logger.debug(f"Glassdoor URL failed: {url} - {e}")
                    continue
            
            logger.debug(f"Could not scrape Glassdoor for {company_name}")
            return {'rating': 0.0, 'reviews': 0, 'recommend': 0}
            
        except Exception as e:
            logger.debug(f"Glassdoor scraping error: {e}")
            return {'rating': 0.0, 'reviews': 0, 'recommend': 0}
    
    def _scrape_indeed(self, company_name: str) -> Dict:
        """Scrape Indeed company reviews"""
        try:
            # Clean company name
            company_slug = company_name.lower().replace(' ', '-').replace('.', '')
            
            url = f"https://www.indeed.com/cmp/{company_slug}/reviews"
            
            response = self.session.get(url, timeout=5)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for rating
                rating_elem = soup.find('div', {'class': re.compile(r'.*rating.*', re.I)})
                if not rating_elem:
                    rating_elem = soup.find('span', {'itemprop': 'ratingValue'})
                
                if rating_elem:
                    rating_text = rating_elem.get_text()
                    rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                    if rating_match:
                        rating = float(rating_match.group(1))
                        
                        # Find review count
                        review_count = 0
                        count_elem = soup.find('span', {'itemprop': 'reviewCount'})
                        if count_elem:
                            count_match = re.search(r'(\d+)', count_elem.get_text())
                            if count_match:
                                review_count = int(count_match.group(1))
                        
                        logger.info(f"✓ Indeed: {rating}/5.0 ({review_count} reviews)")
                        return {'rating': rating, 'reviews': review_count}
            
            logger.debug(f"Could not scrape Indeed for {company_name}")
            return {'rating': 0.0, 'reviews': 0}
            
        except Exception as e:
            logger.debug(f"Indeed scraping error: {e}")
            return {'rating': 0.0, 'reviews': 0}
    
    def _scrape_google(self, company_name: str) -> Dict:
        """Scrape Google Reviews (from Google search results)"""
        try:
            # Search Google for company reviews
            query = f"{company_name} reviews rating"
            url = f"https://www.google.com/search?q={requests.utils.quote(query)}"
            
            response = self.session.get(url, timeout=5)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for rating in knowledge panel
                rating_elem = soup.find('span', {'class': re.compile(r'.*rating.*', re.I)})
                if not rating_elem:
                    # Try finding in text
                    rating_text = soup.find(text=re.compile(r'\d+\.?\d*\s*(?:stars?|★)', re.I))
                    if rating_text:
                        rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                        if rating_match:
                            rating = float(rating_match.group(1))
                            logger.info(f"✓ Google: {rating}/5.0")
                            return {'rating': rating, 'reviews': 0}
                
            logger.debug(f"Could not scrape Google for {company_name}")
            return {'rating': 0.0, 'reviews': 0}
            
        except Exception as e:
            logger.debug(f"Google scraping error: {e}")
            return {'rating': 0.0, 'reviews': 0}
    
    def _scrape_ambitionbox(self, company_name: str) -> Dict:
        """Scrape AmbitionBox reviews (India-specific)"""
        try:
            company_slug = company_name.lower().replace(' ', '-').replace('.', '')
            url = f"https://www.ambitionbox.com/reviews/{company_slug}-reviews"
            
            response = self.session.get(url, timeout=5)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for rating
                rating_elem = soup.find('span', {'class': re.compile(r'.*rating.*', re.I)})
                if rating_elem:
                    rating_text = rating_elem.get_text()
                    rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                    if rating_match:
                        rating = float(rating_match.group(1))
                        
                        # Find review count
                        review_count = 0
                        count_elem = soup.find(text=re.compile(r'\d+\s*reviews?', re.I))
                        if count_elem:
                            count_match = re.search(r'(\d+)', count_elem)
                            if count_match:
                                review_count = int(count_match.group(1))
                        
                        logger.info(f"✓ AmbitionBox: {rating}/5.0 ({review_count} reviews)")
                        return {'rating': rating, 'reviews': review_count}
            
            logger.debug(f"Could not scrape AmbitionBox for {company_name}")
            return {'rating': 0.0, 'reviews': 0}
            
        except Exception as e:
            logger.debug(f"AmbitionBox scraping error: {e}")
            return {'rating': 0.0, 'reviews': 0}

# Singleton instance
_review_scraper = None

def get_review_scraper():
    """Get or create review scraper instance"""
    global _review_scraper
    if _review_scraper is None:
        _review_scraper = CompanyReviewScraper()
    return _review_scraper
