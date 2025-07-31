import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://127.0.0.1:8000"

def test_complete_order_flow():
    """Test the complete order flow with customer data"""
    
    print("🔍 Testing Complete Order Flow with Customer Data")
    print("=" * 60)
    
    # Step 1: Login to get token
    print("\n1. Logging in...")
    login_data = {
        "email": "shuklahitesh1821@gmail.com",
        "password": "test123"
    }
    
    login_response = requests.post(f"{BASE_URL}/login", json=login_data)
    print(f"Login Status: {login_response.status_code}")
    
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.text}")
        return
    
    token = login_response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 2: Get available products
    print("\n2. Getting available products...")
    products_response = requests.get(f"{BASE_URL}/products/")
    if products_response.status_code == 200:
        products = products_response.json()
        if products:
            test_product = products[0]
            print(f"Using product: {test_product['title']} (ID: {test_product['id']}, Price: ${test_product['price']})")
        else:
            print("No products available")
            return
    else:
        print(f"Failed to get products: {products_response.status_code}")
        return
    
    # Step 3: Check customer data before order
    print("\n3. Checking customer data before order...")
    check_customer_data()
    
    # Step 4: Place order with detailed customer info
    print("\n4. Placing order with customer details...")
    order_data = {
        "customer_id": 1,  # This will be overridden by the backend
        "shipping_address_id": 1,  # This will be overridden by the backend
        "items": [
            {
                "product_id": test_product['id'],
                "quantity": 1,
                "price": test_product['price']
            }
        ],
        "total_amount": test_product['price'],
        "status": "pending",
        # Customer details from checkout form
        "first_name": "Hitesh",
        "last_name": "Shukla",
        "email": "shuklahitesh1821@gmail.com",
        "phone_number": "+91-9876543210",
        # Shipping address fields
        "shipping_address_line1": "123 Test Street",
        "shipping_address_line2": "Apartment 4B",
        "city": "Mumbai",
        "country": "India",
        "zip_code": "400001",
        # Payment fields
        "payment_provider": "credit_card",
        "card_number": "1234-5678-9012-3456",
        "expiry_date": "12/25",
        "cvv": "123"
    }
    
    order_response = requests.post(f"{BASE_URL}/place-order/", json=order_data, headers=headers)
    print(f"Order Status: {order_response.status_code}")
    
    if order_response.status_code == 200:
        order_result = order_response.json()
        print(f"Order created successfully: Order ID {order_result['id']}")
        print(f"Order details: {json.dumps(order_result, indent=2)}")
    else:
        print(f"Order failed: {order_response.text}")
        return
    
    # Step 5: Check customer data after order
    print("\n5. Checking customer data after order...")
    check_customer_data()
    
    # Step 6: Check payment details
    print("\n6. Checking payment details...")
    check_payment_data()
    
    # Step 7: Check shipping addresses
    print("\n7. Checking shipping addresses...")
    check_shipping_data()
    
    print("\n✅ Test completed!")

def check_customer_data():
    """Check customer data in database"""
    import pymysql
    from dotenv import load_dotenv
    import os
    
    load_dotenv()
    
    DB_CONFIG = {
        'host': os.getenv('host_name'),
        'port': int(os.getenv('db_port', 3306)),
        'user': os.getenv('db_username'),
        'password': os.getenv('db_password'),
        'database': os.getenv('database_name'),
        'charset': 'utf8mb4',
        'cursorclass': pymysql.cursors.DictCursor
    }
    
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM customers ORDER BY created_at DESC LIMIT 3")
        customers = cursor.fetchall()
        
        print("📋 CUSTOMERS TABLE:")
        for customer in customers:
            print(f"  ID: {customer['id']}")
            print(f"  Name: {customer['first_name']} {customer['last_name']}")
            print(f"  Email: {customer['email']}")
            print(f"  Phone: {customer['phone_number']}")
            print(f"  Created: {customer['created_at']}")
            print("  ---")
        
        conn.close()
    except Exception as e:
        print(f"Error checking customer data: {e}")

def check_payment_data():
    """Check payment data in database"""
    import pymysql
    from dotenv import load_dotenv
    import os
    
    load_dotenv()
    
    DB_CONFIG = {
        'host': os.getenv('host_name'),
        'port': int(os.getenv('db_port', 3306)),
        'user': os.getenv('db_username'),
        'password': os.getenv('db_password'),
        'database': os.getenv('database_name'),
        'charset': 'utf8mb4',
        'cursorclass': pymysql.cursors.DictCursor
    }
    
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM payment_details ORDER BY payment_date DESC LIMIT 3")
        payments = cursor.fetchall()
        
        print("💳 PAYMENT_DETAILS TABLE:")
        if payments:
            for payment in payments:
                print(f"  Payment ID: {payment['id']}")
                print(f"  Order ID: {payment['order_id']}")
                print(f"  Provider: {payment['payment_provider']}")
                print(f"  Payment ID: {payment['payment_id']}")
                print(f"  Status: {payment['status']}")
                print(f"  Amount: {payment['amount']}")
                print(f"  Currency: {payment['currency']}")
                print(f"  Date: {payment['payment_date']}")
                print("  ---")
        else:
            print("  No payment records found")
        
        conn.close()
    except Exception as e:
        print(f"Error checking payment data: {e}")

def check_shipping_data():
    """Check shipping address data in database"""
    import pymysql
    from dotenv import load_dotenv
    import os
    
    load_dotenv()
    
    DB_CONFIG = {
        'host': os.getenv('host_name'),
        'port': int(os.getenv('db_port', 3306)),
        'user': os.getenv('db_username'),
        'password': os.getenv('db_password'),
        'database': os.getenv('database_name'),
        'charset': 'utf8mb4',
        'cursorclass': pymysql.cursors.DictCursor
    }
    
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM shipping_addresses ORDER BY created_at DESC LIMIT 3")
        addresses = cursor.fetchall()
        
        print("🏠 SHIPPING_ADDRESSES TABLE:")
        for address in addresses:
            print(f"  Address ID: {address['id']}")
            print(f"  Customer ID: {address['customer_id']}")
            print(f"  Address: {address['address_line1']}")
            if address['address_line2']:
                print(f"  Address Line 2: {address['address_line2']}")
            print(f"  City: {address['city']}")
            print(f"  Country: {address['country']}")
            print(f"  ZIP: {address['zip_code']}")
            print(f"  Created: {address['created_at']}")
            print("  ---")
        
        conn.close()
    except Exception as e:
        print(f"Error checking shipping data: {e}")

if __name__ == "__main__":
    test_complete_order_flow()
