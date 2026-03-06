"""
Job Scrapers Package
"""

from .base_scraper import BaseScraper
from .jooble_scraper import JoobleScraper
from .indeed_scraper import IndeedScraper
from .naukri_scraper import NaukriScraper
from .careerjet_scraper import CareerjetScraper
from .remoteok_scraper import RemoteOKScraper
from .weworkremotely_scraper import WeWorkRemotelyScraper
from .remotive_scraper import RemotiveScraper

__all__ = [
    'BaseScraper',
    'JoobleScraper',
    'IndeedScraper',
    'NaukriScraper',
    'CareerjetScraper',
    'RemoteOKScraper',
    'WeWorkRemotelyScraper',
    'RemotiveScraper'
]

scrapers = {
    'jooble': JoobleScraper,
    'indeed': IndeedScraper,
    'naukri': NaukriScraper,
    'careerjet': CareerjetScraper,
    'remoteok': RemoteOKScraper,
    'weworkremotely': WeWorkRemotelyScraper,
    'remotive': RemotiveScraper
}
