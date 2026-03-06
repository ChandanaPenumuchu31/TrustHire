"""
Test script to diagnose job search issues
"""

import requests
import json
import time

API_URL = "http://localhost:5000/api/search"

print("=" * 60)
print("JOB SEARCH DIAGNOSTIC TEST")
print("=" * 60)
print()

# Test 1: Basic connectivity
print("1. Testing API connectivity...")
try:
    response = requests.get("http://localhost:5000/")
    if response.status_code == 200:
        print("   ✓ Backend server is running")
        data = response.json()
        print(f"   Service: {data.get('service')}")
        print(f"   Version: {data.get('version')}")
    else:
        print(f"   ✗ Server returned status {response.status_code}")
except Exception as e:
    print(f"   ✗ Cannot connect to backend: {e}")
    exit(1)

print()

# Test 2: Simple job search
print("2. Testing job search endpoint...")
search_params = {
    "query": "python",
    "location": "remote",
    "experience": "",
    "platforms": ["all"],
    "save_to_db": False
}

print(f"   Search params: {json.dumps(search_params, indent=2)}")
print()

start_time = time.time()

try:
    response = requests.post(
        API_URL,
        json=search_params,
        headers={"Content-Type": "application/json"},
        timeout=120  # 2 minute timeout
    )
    
    elapsed = time.time() - start_time
    print(f"   Request completed in {elapsed:.2f} seconds")
    print(f"   Status code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Success: {data.get('success')}")
        print(f"   Jobs found: {data.get('count', 0)}")
        print()
        
        if data.get('count', 0) > 0:
            print("3. Sample job data:")
            first_job = data['jobs'][0]
            print(f"   Title: {first_job.get('title')}")
            print(f"   Company: {first_job.get('company')}")
            print(f"   Platform: {first_job.get('platform')}")
            print(f"   Trust Score: {first_job.get('trust_score', 0):.2f}")
            print(f"   Is Fraudulent: {first_job.get('is_fraudulent')}")
            print(f"   Company Verified: {first_job.get('company_verification', {}).get('is_real')}")
            
            print()
            print("4. Summary statistics:")
            summary = data.get('summary', {})
            print(f"   Total jobs: {summary.get('total_jobs', 0)}")
            print(f"   Trusted jobs: {summary.get('trusted_jobs', 0)}")
            print(f"   Verified companies: {summary.get('verified_companies', 0)}")
            print(f"   Active jobs: {summary.get('active_jobs', 0)}")
            print(f"   Fraud detected: {summary.get('fraud_detected', 0)}")
        else:
            print("   ⚠ No jobs returned (this might be why frontend shows error)")
            
    else:
        print(f"   ✗ Request failed with status {response.status_code}")
        try:
            error_data = response.json()
            print(f"   Error: {error_data.get('error')}")
            print(f"   Message: {error_data.get('message')}")
        except:
            print(f"   Response text: {response.text[:200]}")
            
except requests.exceptions.Timeout:
    print("   ✗ Request timed out after 120 seconds")
    print("   This might be due to slow fraud detection processing")
    
except requests.exceptions.ConnectionError as e:
    print(f"   ✗ Connection error: {e}")
    print("   Make sure backend is running on port 5000")
    
except Exception as e:
    print(f"   ✗ Unexpected error: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)
print("DIAGNOSTIC COMPLETE")
print("=" * 60)
