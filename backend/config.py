import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'True') == 'True'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL', 
        'sqlite:///trusthire.db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Scraping Configuration
    SCRAPE_TIMEOUT = 30  # seconds
    MAX_RESULTS_PER_PLATFORM = 50
    REQUEST_DELAY = 2  # seconds between requests
    
    # Fraud Detection Thresholds
    FRAUD_THRESHOLD = 0.6  # 60% confidence to flag as fraud
    MIN_TRUST_SCORE = 0.4  # Minimum trust score to display
    
    # Supported Job Platforms
    PLATFORMS = ['linkedin', 'indeed', 'naukri']
    
    # CORS Settings
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
    
    # Rate Limiting
    RATE_LIMIT = "100 per hour"
    
    # Cache Settings
    CACHE_EXPIRY = 3600  # 1 hour
