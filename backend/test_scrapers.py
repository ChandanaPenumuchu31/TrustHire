"""
Test script to debug job scrapers
"""
import sys
import logging
from scrapers import JoobleScraper, CareerjetScraper, RemoteOKScraper

# Set up detailed logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(name)s - %(message)s')

def test_jooble():
    print("\n" + "="*60)
    print("TESTING JOOBLE SCRAPER")
    print("="*60)
    
    scraper = JoobleScraper()
    
    # Test 1: Simple query without location
    print("\n[TEST 1] Search: 'java' | Location: None")
    jobs = scraper.search_jobs("java", "", "", max_results=5)
    print(f"✓ Found {len(jobs)} jobs")
    if jobs:
        print(f"Sample job: {jobs[0].get('title')} at {jobs[0].get('company')}")
    
    # Test 2: Query with location
    print("\n[TEST 2] Search: 'python' | Location: 'India'")
    jobs = scraper.search_jobs("python", "India", "", max_results=5)
    print(f"✓ Found {len(jobs)} jobs")
    if jobs:
        print(f"Sample job: {jobs[0].get('title')} at {jobs[0].get('company')}")

def test_careerjet():
    print("\n" + "="*60)
    print("TESTING CAREERJET SCRAPER")
    print("="*60)
    
    scraper = CareerjetScraper()
    
    print("\n[TEST] Search: 'developer' | Location: 'Remote'")
    jobs = scraper.search_jobs("developer", "Remote", "", max_results=5)
    print(f"✓ Found {len(jobs)} jobs")
    if jobs:
        print(f"Sample job: {jobs[0].get('title')} at {jobs[0].get('company')}")

def test_remoteok():
    print("\n" + "="*60)
    print("TESTING REMOTEOK SCRAPER")
    print("="*60)
    
    scraper = RemoteOKScraper()
    
    print("\n[TEST] Search: 'developer' | Location: ''")
    jobs = scraper.search_jobs("developer", "", "", max_results=5)
    print(f"✓ Found {len(jobs)} jobs")
    if jobs:
        print(f"Sample job: {jobs[0].get('title')} at {jobs[0].get('company')}")

if __name__ == "__main__":
    try:
        test_jooble()
        test_careerjet()
        test_remoteok()
        print("\n" + "="*60)
        print("ALL TESTS COMPLETED")
        print("="*60)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
