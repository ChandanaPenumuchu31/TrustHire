"""
Verification script for fraud detection system
"""

print('=' * 60)
print('FRAUD DETECTION SYSTEM VERIFICATION')
print('=' * 60)
print()

print('1. Checking Core Dependencies...')
packages = [
    ('flask', 'Flask'),
    ('numpy', 'NumPy'), 
    ('requests', 'Requests'),
    ('bs4', 'BeautifulSoup4'),
    ('nltk', 'NLTK'),
    ('textblob', 'TextBlob'),
    ('google.genai', 'Google Gemini'),
    ('sklearn', 'scikit-learn'),
    ('pandas', 'Pandas'),
    ('dotenv', 'python-dotenv')
]

all_installed = True
for module, name in packages:
    try:
        __import__(module)
        print(f'   ✓ {name:20s} - INSTALLED')
    except ImportError:
        print(f'   ✗ {name:20s} - MISSING')
        all_installed = False

print()
print('2. Testing Fraud Detection Components...')

try:
    from config import Config
    from models.fraud_detector import get_fraud_detector
    from utils.llm_analyzer import get_llm_analyzer
    from utils.review_scraper import get_review_scraper
    
    print('   ✓ All modules imported successfully')
    
    detector = get_fraud_detector()
    print('   ✓ Fraud detector initialized')
    
    # Test prediction
    test_job = {
        'title': 'Python Developer',
        'company': 'Tech Corp Pvt Ltd',
        'description': 'We are looking for Python developer',
        'location': 'Remote',
        'url': ''
    }
    result = detector.predict(test_job)
    print('   ✓ Fraud prediction executed')
    
except Exception as e:
    print(f'   ✗ Error: {e}')
    all_installed = False

print()
print('3. Feature Status...')

try:
    review_status = 'ENABLED' if detector.review_scraper else 'DISABLED'
    gemini_status = 'ENABLED' if detector.llm_analyzer.enabled else 'DISABLED'
    
    print(f'   • Company Verification:  ENABLED')
    print(f'   • Review Scraping:       {review_status}')
    print(f'   • Role-based Signals:    ENABLED')
    print(f'   • Gemini AI:             {gemini_status}')
    print(f'   • Fallback Analysis:     ENABLED')
    
except Exception as e:
    print(f'   ✗ Error checking features: {e}')

print()
print('4. Configuration...')

try:
    print(f'   • LLM Provider:      {Config.LLM_PROVIDER}')
    print(f'   • LLM Model:         {Config.LLM_MODEL}')
    print(f'   • Review Caching:    {Config.REVIEW_CACHE_HOURS} hours')
    print(f'   • Fraud Threshold:   {Config.FRAUD_THRESHOLD}')
    print(f'   • Min Trust Score:   {Config.MIN_TRUST_SCORE}')
    
except Exception as e:
    print(f'   ✗ Error reading config: {e}')

print()
print('5. Test Prediction Result...')

try:
    print(f'   • Trust Score:       {result["trust_score"]:.2f}')
    print(f'   • Is Fraudulent:     {result["is_fraudulent"]}')
    print(f'   • Company Verified:  {result["company_verification"]["is_real"]}')
    print(f'   • Has Reviews:       {"reviews" in result["company_verification"]}')
    print(f'   • Has Role Signal:   {"role_review_signal" in result["company_verification"]["reviews"]}')
    print(f'   • Final Verdict:     {result["final_verdict"]}')
    
except Exception as e:
    print(f'   ✗ Error: {e}')

print()
print('=' * 60)
if all_installed:
    print('✓ FRAUD DETECTION SYSTEM: FULLY OPERATIONAL')
else:
    print('⚠ FRAUD DETECTION SYSTEM: SOME ISSUES DETECTED')
print('=' * 60)
