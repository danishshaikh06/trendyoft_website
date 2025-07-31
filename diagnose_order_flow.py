#!/usr/bin/env python3
"""
Diagnose the order placement flow step by step
"""

import pymysql
from dotenv import load_dotenv
import os
import requests
import json

# Load environment variables
load_dotenv()

def test_api_endpoints():
    """Test each API endpoint step by step"""
    
    base_url = "http://127.0.0.1:8000"
    
    print("🔍 DIAGNOSING ORDER PLACEMENT FLOW")
    print("=" * 60)
    
    # Test 1: Check API is running
    print("1️⃣ Testing API connectivity...")
    try:
        response = requests.get(f"{base_url}/api", timeout=5)
        if response.status_code == 200:
            print("   ✅ API is running and accessible")
        else:
            print(f"   ❌ API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Cannot connect to API: {str(e)}")
        return False
    
    # Test 2: Check products
    print("2️⃣ Testing products endpoint...")
    try:
        response = requests.get(f"{base_url}/products/", timeout=5)
        if response.status_code == 200:
            products = response.json()
            print(f"   ✅ Found {len(products)} products")
            if products:
                test_product = products[0]
                print(f"   📦 Test product: {test_product['title']} (ID: {test_product['id']})")
            else:
                print("   ⚠️ No products available for testing")
                return False
        else:
            print(f"   ❌ Products endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Products endpoint error: {str(e)}")
        return False
    
    # Test 3: Check login endpoint with existing user
    print("3️⃣ Testing login endpoint...")
    login_data = {
        "email": "shuklahitesh1821@gmail.com",
        "password": "test123"  # This is likely wrong, but let's see the error
    }
    try:
        response = requests.post(f"{base_url}/login", json=login_data, timeout=5)
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data['access_token']
            print(f"   ✅ Login successful")
            
            # Test 4: Try to place an order
            print("4️⃣ Testing order placement...")
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            order_data = {
                "customer_id": 1,
                "shipping_address_id": 1,
                "items": [
                    {
                        "product_id": test_product['id'],
                        "quantity": 1,
                        "price": test_product['price']
                    }
                ],
                "total_amount": test_product['price'],
                "status": "pending"
            }
            
            try:
                response = requests.post(f"{base_url}/place-order/", json=order_data, headers=headers, timeout=10)
                if response.status_code == 200:
                    order_result = response.json()
                    print(f"   ✅ Order placed successfully!")
                    print(f"   📋 Order ID: {order_result.get('id')}")
                else:
                    print(f"   ❌ Order placement failed: {response.status_code}")
                    print(f"   📄 Response: {response.text}")
            except Exception as e:
                print(f"   ❌ Order placement error: {str(e)}")
            
        else:
            print(f"   ❌ Login failed: {response.status_code}")
            print(f"   📄 Response: {response.text}")
            print("   💡 This is expected - we don't know the actual password")
            print("   💡 You can manually login through the web interface")
    except Exception as e:
        print(f"   ❌ Login endpoint error: {str(e)}")
    
    return True

def check_database_directly():
    """Check database directly"""
    
    print("\n5️⃣ Checking database directly...")
    
    config = {
        'host': os.getenv('host_name'),
        'port': int(os.getenv('db_port', 3306)),
        'user': os.getenv('db_username'),
        'password': os.getenv('db_password'),
        'database': os.getenv('database_name'),
        'charset': 'utf8mb4',
        'cursorclass': pymysql.cursors.DictCursor
    }
    
    try:
        connection = pymysql.connect(**config)
        
        with connection.cursor() as cursor:
            # Check all tables
            tables = ['customers', 'orders', 'order_items', 'products', 'users', 'shipping_addresses']
            
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                count = cursor.fetchone()['count']
                print(f"   📊 {table}: {count} records")
            
            # Check if there are any products with stock
            cursor.execute("SELECT COUNT(*) as count FROM products WHERE quantity > 0")
            in_stock_count = cursor.fetchone()['count']
            print(f"   📦 Products in stock: {in_stock_count}")
        
        connection.close()
        print("   ✅ Database connectivity OK")
        
    except Exception as e:
        print(f"   ❌ Database error: {str(e)}")

if __name__ == "__main__":
    test_api_endpoints()
    check_database_directly()
    
    print("\n" + "=" * 60)
    print("🎯 NEXT STEPS:")
    print("1. If API tests pass, try placing an order through the web interface")
    print("2. Watch the server console for error messages")
    print("3. Run 'python debug_orders.py' after placing an order")
    print("4. If login fails, use the correct password for the user")
