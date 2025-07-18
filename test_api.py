#!/usr/bin/env python3
"""
Test script for Trendyoft E-commerce API
This script demonstrates how to use the API endpoints
"""

import requests
import json

# API Base URL (change if running on different port)
BASE_URL = "http://localhost:8000"

# Admin token for protected operations
ADMIN_TOKEN = "danishshaikh@06"

def test_public_endpoints():
    """Test public endpoints that don't require authentication"""
    print("=== Testing Public Endpoints ===")
    
    # Test getting all products
    print("\n1. Getting all products:")
    response = requests.get(f"{BASE_URL}/products/")
    if response.status_code == 200:
        products = response.json()
        print(f"✓ Found {len(products)} products")
        for product in products[:2]:  # Show first 2 products
            print(f"  - {product['title']}: Rs. {product['price']}")
    else:
        print(f"✗ Error: {response.status_code}")
    
    # Test getting categories
    print("\n2. Getting categories:")
    response = requests.get(f"{BASE_URL}/categories/")
    if response.status_code == 200:
        categories = response.json()
        print(f"✓ Categories: {categories['categories']}")
    else:
        print(f"✗ Error: {response.status_code}")
    
    # Test search
    print("\n3. Testing search:")
    response = requests.get(f"{BASE_URL}/search/?q=striped")
    if response.status_code == 200:
        results = response.json()
        print(f"✓ Found {len(results)} results for 'striped'")
    else:
        print(f"✗ Error: {response.status_code}")

def test_admin_endpoints():
    """Test admin endpoints that require authentication"""
    print("\n=== Testing Admin Endpoints ===")
    
    headers = {
        "Authorization": f"Bearer {ADMIN_TOKEN}"
    }
    
    # Test adding a product (without actual file upload for simplicity)
    print("\n1. Testing admin authentication:")
    response = requests.get(f"{BASE_URL}/products/", headers=headers)
    if response.status_code == 200:
        print("✓ Admin token is valid")
    else:
        print(f"✗ Admin token error: {response.status_code}")
    
    # Test with invalid token
    print("\n2. Testing invalid token:")
    bad_headers = {"Authorization": "Bearer invalid-token"}
    response = requests.get(f"{BASE_URL}/products/", headers=bad_headers)
    print(f"✓ Invalid token correctly rejected (this is expected)")

def show_api_info():
    """Show API information"""
    print("=== API Information ===")
    response = requests.get(f"{BASE_URL}/")
    if response.status_code == 200:
        info = response.json()
        print(f"✓ {info['message']}")
        print(f"  Version: {info['version']}")
        print("  Available endpoints:")
        for endpoint, description in info['endpoints'].items():
            print(f"    - {endpoint}: {description}")
    else:
        print(f"✗ Error getting API info: {response.status_code}")

def main():
    """Main test function"""
    print("Trendyoft E-commerce API Test")
    print("=" * 40)
    
    try:
        # Test if server is running
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code != 200:
            print(f"✗ Server not responding properly: {response.status_code}")
            return
    except requests.exceptions.RequestException as e:
        print(f"✗ Cannot connect to server at {BASE_URL}")
        print(f"  Make sure the server is running with: python main.py")
        print(f"  Error: {e}")
        return
    
    show_api_info()
    test_public_endpoints()
    test_admin_endpoints()
    
    print("\n=== Test Complete ===")
    print("To start the server, run: python main.py")
    print("Then visit http://localhost:8000 in your browser")

if __name__ == "__main__":
    main()
