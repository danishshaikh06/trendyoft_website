#!/usr/bin/env python3
"""
Debug script for Trendyoft website
This script helps troubleshoot common issues with the website
"""

import requests
import json
import os

def test_api_endpoint(url, endpoint_name):
    """Test an API endpoint and return results"""
    try:
        print(f"\n🔍 Testing {endpoint_name}...")
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            print(f"✅ {endpoint_name} is working!")
            data = response.json()
            if isinstance(data, list):
                print(f"📊 Returned {len(data)} items")
                if len(data) > 0:
                    print(f"📝 Sample item: {data[0].get('title', 'N/A')}")
            elif isinstance(data, dict):
                print(f"📊 Response keys: {list(data.keys())}")
            return True
        else:
            print(f"❌ {endpoint_name} failed with status {response.status_code}")
            print(f"📝 Response: {response.text[:200]}...")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ {endpoint_name} - Connection failed! Is the server running?")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ {endpoint_name} - Request timed out!")
        return False
    except Exception as e:
        print(f"❌ {endpoint_name} - Error: {str(e)}")
        return False

def main():
    """Main debug function"""
    print("🚀 Trendyoft Website Debug Tool")
    print("=" * 40)
    
    base_url = os.getenv("BASE_URL", "http://127.0.0.1:8000")
    
    # Test server is running
    print(f"\n🏠 Testing server at {base_url}...")
    
    # Test API endpoints
    endpoints = [
        (f"{base_url}/products", "Products API"),
        (f"{base_url}/categories", "Categories API"),
        (f"{base_url}/api", "API Info"),
        (f"{base_url}/", "Website Root")
    ]
    
    results = []
    for url, name in endpoints:
        results.append(test_api_endpoint(url, name))
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 SUMMARY")
    print("=" * 40)
    
    if all(results[:2]):  # Products and Categories APIs
        print("✅ All critical APIs are working!")
        print(f"🌐 Your website should be accessible at: {base_url}")
        print("\n💡 If products still don't show:")
        print("   1. Open browser console (F12) and check for errors")
        print("   2. Make sure you're accessing http://127.0.0.1:8000 (not file://)")
        print("   3. Check if browser is blocking CORS requests")
    else:
        print("❌ Some APIs are not working!")
        print("🔧 Troubleshooting steps:")
        print("   1. Make sure the server is running:")
        print("      python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload")
        print("   2. Check if port 8000 is available")
        print("   3. Check your database connection in .env file")
        
    print(f"\n🔄 Re-run this script anytime with: python debug_website.py")

if __name__ == "__main__":
    main()
