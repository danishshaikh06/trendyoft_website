#!/usr/bin/env python3
"""
Debug script to test order placement with detailed error tracking
"""

import requests
import json
import pymysql
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def check_database_constraints():
    """Check database constraints that might be causing order failures"""
    
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
        print("✅ Database connection established")
        
        with connection.cursor() as cursor:
            print("\n🔍 CHECKING DATABASE CONSTRAINTS:")
            print("-" * 50)
            
            # Check foreign key constraints
            cursor.execute("SHOW CREATE TABLE orders")
            orders_table = cursor.fetchone()
            print("📋 Orders table constraints:")
            print(orders_table['Create Table'])
            
            print("\n📋 Order items table constraints:")
            cursor.execute("SHOW CREATE TABLE order_items")
            items_table = cursor.fetchone()
            print(items_table['Create Table'])
            
            # Check if there are any constraint violations
            print("\n🔍 CHECKING FOR CONSTRAINT ISSUES:")
            print("-" * 50)
            
            # Check customers
            cursor.execute("SELECT id, email FROM customers")
            customers = cursor.fetchall()
            print(f"👥 Available customers: {len(customers)}")
            for customer in customers:
                print(f"   - Customer ID: {customer['id']}, Email: {customer['email']}")
            
            # Check shipping addresses
            cursor.execute("SELECT id, customer_id, address_line1, city FROM shipping_addresses")
            addresses = cursor.fetchall()
            print(f"📬 Available shipping addresses: {len(addresses)}")
            for addr in addresses:
                print(f"   - Address ID: {addr['id']}, Customer: {addr['customer_id']}, Address: {addr['address_line1']}, {addr['city']}")
            
            # Check products with stock
            cursor.execute("SELECT id, title, quantity, price FROM products WHERE quantity > 0 LIMIT 5")
            products = cursor.fetchall()
            print(f"📦 Products with stock: {len(products)}")
            for product in products:
                print(f"   - Product ID: {product['id']}, Title: {product['title']}, Stock: {product['quantity']}, Price: ${product['price']}")
            
            # Check recent orders
            cursor.execute("""
                SELECT o.id, o.customer_id, o.shipping_address_id, o.status, o.total_amount, o.order_date
                FROM orders o 
                ORDER BY o.id DESC 
                LIMIT 3
            """)
            recent_orders = cursor.fetchall()
            print(f"\n📦 Recent orders: {len(recent_orders)}")
            for order in recent_orders:
                print(f"   - Order ID: {order['id']}, Customer: {order['customer_id']}, Address: {order['shipping_address_id']}, Status: {order['status']}")
            
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ Database error: {str(e)}")
        return False

def test_order_placement_directly():
    """Test order placement directly through the API with detailed error tracking"""
    
    base_url = "http://127.0.0.1:8000"
    
    print("\n🧪 TESTING ORDER PLACEMENT:")
    print("-" * 50)
    
    # Get a valid user token (you'll need to provide correct credentials)
    print("1️⃣ Attempting to get user token...")
    login_data = {
        "email": "shuklahitesh1821@gmail.com",
        "password": "hitu117@"  # Update this with the correct password
    }
    
    try:
        login_response = requests.post(f"{base_url}/login", json=login_data)
        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data['access_token']
            print(f"   ✅ Login successful!")
        else:
            print(f"   ❌ Login failed: {login_response.status_code} - {login_response.text}")
            print("   💡 Please update the password in this script to test order placement")
            return False
    except Exception as e:
        print(f"   ❌ Login error: {str(e)}")
        return False
    
    # Get products
    print("2️⃣ Getting products...")
    try:
        products_response = requests.get(f"{base_url}/products/")
        if products_response.status_code == 200:
            products = products_response.json()
            if products:
                test_product = products[0]
                print(f"   ✅ Using product: {test_product['title']} (ID: {test_product['id']}, Price: ${test_product['price']}, Stock: {test_product['quantity']})")
            else:
                print("   ❌ No products available")
                return False
        else:
            print(f"   ❌ Failed to get products: {products_response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Products error: {str(e)}")
        return False
    
    # Test order placement
    print("3️⃣ Placing test order...")
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    order_data = {
        "customer_id": 1,  # This gets overridden by backend
        "shipping_address_id": 1,  # This gets overridden by backend
        "items": [
            {
                "product_id": test_product['id'],
                "quantity": 1,
                "price": test_product['price']
            }
        ],
        "total_amount": test_product['price'],
        "status": "pending",
        # Add shipping details
        "shipping_address_line1": "123 Test Street",
        "shipping_address_line2": "",
        "city": "Test City",
        "country": "Test Country",
        "zip_code": "12345",
        # Add payment details
        "payment_provider": "credit_card",
        "card_number": "1234567890123456",
        "expiry_date": "12/25",
        "cvv": "123"
    }
    
    try:
        order_response = requests.post(f"{base_url}/place-order/", json=order_data, headers=headers, timeout=30)
        print(f"   📡 Response status: {order_response.status_code}")
        print(f"   📄 Response body: {order_response.text}")
        
        if order_response.status_code == 200:
            order_result = order_response.json()
            print(f"   ✅ Order placed successfully!")
            print(f"   📋 Order ID: {order_result.get('id')}")
            print(f"   💰 Total Amount: ${order_result.get('total_amount')}")
        else:
            print(f"   ❌ Order placement failed!")
            # Try to parse error details
            try:
                error_data = order_response.json()
                print(f"   🔍 Error details: {error_data}")
            except:
                print(f"   🔍 Raw error response: {order_response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Order placement exception: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    print("🔧 ORDER PLACEMENT DEBUGGING TOOL")
    print("=" * 60)
    
    # Check database first
    if check_database_constraints():
        print("\n" + "=" * 60)
        test_order_placement_directly()
    
    print("\n" + "=" * 60)
    print("💡 TROUBLESHOOTING TIPS:")
    print("1. Check server console for detailed error messages")
    print("2. Ensure all required fields are provided in the order")
    print("3. Verify product stock levels")
    print("4. Check foreign key constraints in database")
    print("5. Update the password in this script for full testing")
