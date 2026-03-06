"""
Debug script to inspect Jooble HTML structure
"""
import requests
from bs4 import BeautifulSoup

def debug_jooble_html():
    print("=" * 70)
    print("DEBUGGING JOOBLE HTML STRUCTURE")
    print("=" * 70)
    
    # Test URLs based on your manual test
    urls = [
        ("https://jooble.org/SearchResult?ukw=python", "Python jobs (no location)"),
        ("https://jooble.org/SearchResult?rgns=india&ukw=python", "Python jobs in India")
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    for url, description in urls:
        print(f"\n\n{'=' * 70}")
        print(f"Testing: {description}")
        print(f"URL: {url}")
        print('=' * 70)
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            print(f"\n✓ Status Code: {response.status_code}")
            print(f"✓ Response Size: {len(response.text)} bytes")
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Check for various job listing elements
            print("\n--- Checking for job elements ---")
            
            # Try different selectors
            selectors = [
                ('article', None, 'article tags'),
                ('div', {'class': 'job'}, 'div.job'),
                ('div', {'class': 'vacancy'}, 'div.vacancy'),
                ('div', {'class': 'result'}, 'div.result'),
                ('div', {'class': 'serp-item'}, 'div.serp-item'),
                ('div', {'data-job': True}, 'div with data-job attribute'),
            ]
            
            for tag, attrs, desc in selectors:
                elements = soup.find_all(tag, attrs)
                print(f"  {desc}: {len(elements)} found")
                if elements and len(elements) > 0:
                    print(f"    First element classes: {elements[0].get('class', 'No class')}")
                    print(f"    First element id: {elements[0].get('id', 'No id')}")
            
            # Check for JavaScript-rendered content indicators
            print("\n--- Checking for dynamic content indicators ---")
            scripts = soup.find_all('script')
            print(f"  Script tags: {len(scripts)}")
            
            # Check if there's a root div for React/Vue apps
            root_div = soup.find('div', id='root') or soup.find('div', id='app')
            if root_div:
                print("  ⚠️ Found root div - likely a JavaScript SPA (Single Page App)")
            
            # Look for JSON data in script tags
            for script in scripts[:5]:  # Check first 5 scripts
                script_text = script.string or ''
                if 'window.__INITIAL_STATE__' in script_text or 'window.__DATA__' in script_text:
                    print("  ✓ Found initial state data in script tag!")
                    # Try to extract it
                    if len(script_text) < 1000:
                        print(f"    Content preview: {script_text[:200]}...")
            
            # Save a sample of HTML for inspection
            print(f"\n--- First 2000 characters of HTML ---")
            print(response.text[:2000])
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    debug_jooble_html()
