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
    SCRAPE_TIMEOUT = 5  # Very fast
    MAX_RESULTS_PER_PLATFORM = 5  # Balanced limit
    REQUEST_DELAY = 0  # No delay for speed

    # Fraud Detection Thresholds
    FRAUD_THRESHOLD = 0.6  # 60% confidence to flag as fraud
    MIN_TRUST_SCORE = 0.4  # Minimum trust score to display
    
    # Fast Mode Configuration
    FAST_MODE = True  # Skip slow operations for instant results
    USE_FILE_REVIEWS = True  # Use company_reviews.json instead of web scraping
    
    # Supported Job Platforms (Updated with new platforms)
    PLATFORMS = ['remoteok', 'remotive']
    
    # CORS Settings
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
    
    # Rate Limiting
    RATE_LIMIT = "100 per hour"
    
    # Cache Settings
    CACHE_EXPIRY = 3600  # 1 hour
    
    # ============================================================================
    # LLM API KEYS - ENTER YOUR KEYS DIRECTLY HERE (OR USE .env FILE)
    # ============================================================================
    
    # Using Google Gemini (FREE API) - Disabled for speed (quota exhausted)
    GEMINI_API_KEY = None  # Set to your key when quota resets
    
    # Disabled providers (project uses Gemini only)
    OPENAI_API_KEY = None
    ANTHROPIC_API_KEY = None
    
    # ============================================================================
    
    # Use Gemini only
    LLM_PROVIDER = 'gemini'
    LLM_MODEL = 'gemini-2.0-flash'
    
    # Real-time Review Scraping (No API needed - works out of the box)
    ENABLE_REVIEW_SCRAPING = False  # Disabled for faster performance
    REVIEW_CACHE_HOURS = 24  # Cache company reviews for 24 hours
    
    # ============================================================================
    # INSTRUCTIONS:
    # ============================================================================
    # 1. Replace 'your_openai_key_here' with your actual OpenAI API key
    # 2. Set LLM_PROVIDER to 'openai' (or 'anthropic' if using Claude)
    # 3. Save this file
    # 4. The system will automatically use the LLM for advanced fraud detection
    #
    # To DISABLE LLM (use rule-based detection only):
    # - Set LLM_PROVIDER = 'none'
    # ============================================================================
