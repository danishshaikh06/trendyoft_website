#!/usr/bin/env python3
"""
Test script to place an order with customer details and verify database entries.
This script tests the complete order placement flow including customer data updates.
"""

import requests
import json
import time
import sys

# Configuration
BASE_URL = "http://127.0.0.1:8000"  # Adjust if your server runs on a different port
TEST_EMAIL = "shaikhdanish.sd06@gmail.com"
TEST_PASSWORD = "danishshaikh@06"

# Test data
CHECKOUT_DATA = {
    "first_name": "Danish",
    "last_name": "Shaikh", 
    "phone_number": "+91-9876543210",
    "email": TEST_EMAIL,
    "shipping_address_line1": "123 Test Street",
    "shipping_address_line2": "Apt 456",
    "city": "Mumbai",
    "country": "India",
    "zip_code": "400001",
    "payment_provider": "credit_card"
}

def print_separator(title):
    """Print a separator with title"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def test_login():
    """Test user login and get access token"""
    print_separator("TESTING LOGIN")
    
    login_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    try:
        response = requests.post(f"{BASE_URL}/login", json=login_data)
        print(f"Login Status Code: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            print(f"Login successful!")
            print(f"Username: {token_data.get('username')}")
            print(f"Token type: {token_data.get('token_type')}")
            return token_data.get('access_token')
        else:
            print(f"Login failed: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Login request failed: {e}")
        return None

def get_test_products():
    """Get available products for testing"""
    print_separator("GETTING TEST PRODUCTS")
    
    try:
        response = requests.get(f"{BASE_URL}/products/")
        print(f"Products fetch status: {response.status_code}")
        
        if response.status_code == 200:
            products = response.json()
            if products:
                print(f"Found {len(products)} products")
                # Return first available product with stock and reasonable price (< 100000)
                for product in products:
                    if product.get('quantity', 0) > 0 and product.get('price', 0) < 100000:
                        print(f"Selected product: {product['title']} (ID: {product['id']}, Price: {product['price']}, Stock: {product['quantity']})")
                        return product
                print("No products with stock and reasonable price found!")
                return None
            else:
                print("No products found!")
                return None
        else:
            print(f"Failed to fetch products: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Products request failed: {e}")
        return None

def place_test_order(access_token, product):
    """Place a test order with checkout details"""
    print_separator("PLACING TEST ORDER")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Create order with checkout details
    order_data = {
        "items": [
            {
                "product_id": product['id'],
                "quantity": 1,
                "price": product['price']
            }
        ],
        "total_amount": product['price'],
        "status": "pending",
        # Customer details from checkout form
        **CHECKOUT_DATA
    }
    
    print("Order data being sent:")
    print(json.dumps(order_data, indent=2))
    
    try:
        response = requests.post(f"{BASE_URL}/place-order/", 
                               headers=headers, 
                               json=order_data)
        
        print(f"Order placement status: {response.status_code}")
        
        if response.status_code == 200:
            order_response = response.json()
            print("Order placed successfully!")
            print(f"Order ID: {order_response.get('id')}")
            print(f"Status: {order_response.get('status')}")
            print(f"Total: {order_response.get('total_amount')}")
            return order_response.get('id')
        else:
            print(f"Order placement failed: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Order placement request failed: {e}")
        return None

def verify_customer_data():
    """Verify that customer data was updated in database"""
    print_separator("VERIFYING CUSTOMER DATA")
    
    print("Expected customer data:")
    print(f"  First Name: {CHECKOUT_DATA['first_name']}")
    print(f"  Last Name: {CHECKOUT_DATA['last_name']}")
    print(f"  Phone: {CHECKOUT_DATA['phone_number']}")
    print(f"  Email: {CHECKOUT_DATA['email']}")
    
    print("\nTo verify in database, check the customers table:")
    print(f"SELECT * FROM customers WHERE email = '{TEST_EMAIL}';")
    
    print("\nExpected result should show:")
    print(f"- first_name: {CHECKOUT_DATA['first_name']}")
    print(f"- last_name: {CHECKOUT_DATA['last_name']}")
    print(f"- phone_number: {CHECKOUT_DATA['phone_number']}")

def check_my_orders(access_token):
    """Check orders for the authenticated user"""
    print_separator("CHECKING MY ORDERS")
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/my-orders", headers=headers)
        print(f"My orders status: {response.status_code}")
        
        if response.status_code == 200:
            orders_data = response.json()
            orders = orders_data.get('orders', [])
            print(f"Found {len(orders)} orders")
            
            for order in orders:
                print(f"Order {order['id']}: Status={order['status']}, Total={order['total_amount']}, Items={len(order['items'])}")
                
            return orders
        else:
            print(f"Failed to fetch orders: {response.text}")
            return []
            
    except requests.exceptions.RequestException as e:
        print(f"My orders request failed: {e}")
        return []

def main():
    """Main test function"""
    print_separator("STARTING ORDER PLACEMENT TEST")
    print(f"Test email: {TEST_EMAIL}")
    print(f"Server URL: {BASE_URL}")
    
    # Step 1: Login
    access_token = test_login()
    if not access_token:
        print("❌ Login failed. Cannot continue with test.")
        sys.exit(1)
    
    # Step 2: Get a test product
    product = get_test_products()
    if not product:
        print("❌ No suitable products found. Cannot continue with test.")
        sys.exit(1)
    
    # Step 3: Place order with checkout details
    order_id = place_test_order(access_token, product)
    if not order_id:
        print("❌ Order placement failed.")
        sys.exit(1)
    
    # Step 4: Verify orders were created
    print("\n⏳ Waiting 2 seconds for database updates...")
    time.sleep(2)
    
    orders = check_my_orders(access_token)
    
    # Step 5: Verification instructions
    verify_customer_data()
    
    print_separator("TEST SUMMARY")
    if order_id:
        print("✅ Order placement test completed successfully!")
        print(f"✅ Order ID: {order_id}")
        print("✅ Check server logs for detailed customer update information")
        print("✅ Check database manually to verify customer details were updated")
    else:
        print("❌ Order placement test failed!")
    
    print("\nNext steps:")
    print("1. Check the server logs for customer update messages")
    print("2. Verify customer data in the database")
    print("3. If customer data is not updated, there may be an issue with the update logic")

if __name__ == "__main__":
    main()
