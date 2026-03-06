"""
Test HTML cleaning in job descriptions
"""
from scrapers import RemoteOKScraper, RemotiveScraper

print("=" * 70)
print("TESTING HTML CLEANING IN JOB DESCRIPTIONS")
print("=" * 70)

# Test RemoteOK
print("\n1. Testing RemoteOK scraper...")
print("-" * 70)
remoteok = RemoteOKScraper()
jobs = remoteok.search_jobs('developer', '', '', 3)

print(f"Found {len(jobs)} jobs from RemoteOK\n")

for i, job in enumerate(jobs[:2], 1):
    print(f"Job {i}:")
    print(f"  Title: {job['title']}")
    print(f"  Company: {job['company']}")
    print(f"  Description: {job['description']}")
    print()

# Test Remotive
print("\n2. Testing Remotive scraper...")
print("-" * 70)
remotive = RemotiveScraper()
jobs = remotive.search_jobs('python', '', '', 3)

print(f"Found {len(jobs)} jobs from Remotive\n")

for i, job in enumerate(jobs[:2], 1):
    print(f"Job {i}:")
    print(f"  Title: {job['title']}")
    print(f"  Company: {job['company']}")
    print(f"  Description: {job['description']}")
    print()

print("=" * 70)
print("✅ HTML cleaning test complete!")
print("=" * 70)
