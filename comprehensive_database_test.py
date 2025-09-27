#!/usr/bin/env python3
"""
Comprehensive database test to verify customer data updates during order placement
"""

import pymysql
import requests
import json
import time
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': os.getenv('host_name'),
    'port': int(os.getenv('db_port', 3306)),
    'user': os.getenv('db_username'),
    'password': os.getenv('db_password'),
    'database': os.getenv('database_name'),
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

# API configuration
BASE_URL = "http://127.0.0.1:8000"
TEST_EMAIL = "test_user_" + str(int(time.time())) + "@example.com"  # Unique email
TEST_PASSWORD = "testpassword123"

def print_separator(title):
    """Print a separator with title"""
    print("\n" + "="*80)
    print(f" {title}")
    print("="*80)

def check_database_connection():
    """Check if we can connect to the database"""
    print_separator("CHECKING DATABASE CONNECTION")
    
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("✅ Database connection successful!")
        print(f"Host: {DB_CONFIG['host']}")
        print(f"Port: {DB_CONFIG['port']}")
        print(f"Database: {DB_CONFIG['database']}")
        print(f"User: {DB_CONFIG['user']}")
        
        # Check if customers table exists
        cursor.execute("SHOW TABLES LIKE 'customers'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            print("✅ Customers table exists")
            
            # Get table structure
            cursor.execute("DESCRIBE customers")
            columns = cursor.fetchall()
            print("\nTable structure:")
            for col in columns:
                print(f"  - {col['Field']}: {col['Type']}")
                
        else:
            print("❌ Customers table does not exist!")
            return False
            
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("\nPlease check:")
        print("1. Database server is running")
        print("2. Environment variables are set correctly")
        print("3. Database credentials are correct")
        return False

def get_customers_before():
    """Get all customers before the test"""
    print_separator("CUSTOMERS BEFORE TEST")
    
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM customers ORDER BY id")
        customers = cursor.fetchall()
        
        print(f"Total customers before test: {len(customers)}")
        for customer in customers:
            print(f"ID: {customer['id']}, Name: {customer['first_name']} {customer['last_name']}, Email: {customer['email']}, Phone: {customer.get('phone_number', 'None')}")
        
        conn.close()
        return customers
        
    except Exception as e:
        print(f"❌ Error fetching customers: {e}")
        return []

def register_test_user():
    """Register a new test user"""
    print_separator("REGISTERING TEST USER")
    
    user_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "username": "Test User"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/register", json=user_data)
        print(f"Registration status: {response.status_code}")
        
        if response.status_code == 201:
            print(f"✅ User registered successfully: {TEST_EMAIL}")
            return True
        else:
            print(f"❌ Registration failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return False

def login_test_user():
    """Login with test user"""
    print_separator("LOGGING IN TEST USER")
    
    login_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    try:
        response = requests.post(f"{BASE_URL}/login", json=login_data)
        print(f"Login status: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            print(f"✅ Login successful")
            return token_data.get('access_token')
        else:
            print(f"❌ Login failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def place_test_order(access_token):
    """Place a test order with specific customer details"""
    print_separator("PLACING TEST ORDER")
    
    # First get a product with available stock
    try:
        products_response = requests.get(f"{BASE_URL}/products/")
        if products_response.status_code == 200:
            products = products_response.json()
            if products:
                # Find a product with stock > 0 and reasonable price (< 10000)
                product = None
                for p in products:
                    if p.get('quantity', 0) > 0 and p.get('price', 0) < 10000:
                        product = p
                        break
                
                if product:
                    print(f"Using product: {product['title']} (ID: {product['id']}, Price: {product['price']}, Stock: {product['quantity']})")
                else:
                    print("❌ No products with available stock")
                    return None
            else:
                print("❌ No products available")
                return None
        else:
            print("❌ Failed to get products")
            return None
    except Exception as e:
        print(f"❌ Error getting products: {e}")
        return None
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Order with detailed customer information
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
        "first_name": "John",
        "last_name": "Doe",
        "phone_number": "+1-555-123-4567",
        "email": TEST_EMAIL,
        "shipping_address_line1": "123 Main Street",
        "shipping_address_line2": "Apt 101",
        "city": "New York",
        "country": "USA",
        "zip_code": "10001",
        "payment_provider": "credit_card"
    }
    
    print("Order data:")
    print(json.dumps({k: v for k, v in order_data.items() if k not in ['items']}, indent=2))
    
    try:
        response = requests.post(f"{BASE_URL}/place-order/", 
                               headers=headers, 
                               json=order_data)
        
        print(f"Order placement status: {response.status_code}")
        
        if response.status_code == 200:
            order_response = response.json()
            print("✅ Order placed successfully!")
            print(f"Order ID: {order_response.get('id')}")
            return order_response.get('id')
        else:
            print(f"❌ Order placement failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Order placement error: {e}")
        return None

def get_customers_after():
    """Get all customers after the test"""
    print_separator("CUSTOMERS AFTER TEST")
    
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM customers ORDER BY id")
        customers = cursor.fetchall()
        
        print(f"Total customers after test: {len(customers)}")
        for customer in customers:
            print(f"ID: {customer['id']}, Name: {customer['first_name']} {customer['last_name']}, Email: {customer['email']}, Phone: {customer.get('phone_number', 'None')}")
        
        # Specifically check for our test user
        cursor.execute("SELECT * FROM customers WHERE email = %s", (TEST_EMAIL,))
        test_customer = cursor.fetchone()
        
        if test_customer:
            print(f"\n✅ Test customer found in database:")
            print(f"  ID: {test_customer['id']}")
            print(f"  Name: {test_customer['first_name']} {test_customer['last_name']}")
            print(f"  Email: {test_customer['email']}")
            print(f"  Phone: {test_customer.get('phone_number', 'None')}")
            print(f"  Created: {test_customer.get('created_at', 'N/A')}")
        else:
            print(f"❌ Test customer NOT found in database!")
        
        conn.close()
        return customers
        
    except Exception as e:
        print(f"❌ Error fetching customers: {e}")
        return []

def check_orders_table():
    """Check if orders were created"""
    print_separator("CHECKING ORDERS TABLE")
    
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Get recent orders
        cursor.execute("SELECT * FROM orders ORDER BY id DESC LIMIT 5")
        orders = cursor.fetchall()
        
        print(f"Recent orders: {len(orders)}")
        for order in orders:
            print(f"Order ID: {order['id']}, Customer ID: {order['customer_id']}, Total: {order['total_amount']}, Status: {order['status']}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking orders: {e}")

def main():
    """Main test function"""
    print_separator("COMPREHENSIVE DATABASE TEST")
    print(f"Test email: {TEST_EMAIL}")
    
    # Step 1: Check database connection
    if not check_database_connection():
        print("❌ Cannot proceed without database connection")
        return
    
    # Step 2: Get initial state
    customers_before = get_customers_before()
    
    # Step 3: Register test user
    if not register_test_user():
        print("❌ Cannot proceed without user registration")
        return
    
    # Step 4: Login
    access_token = login_test_user()
    if not access_token:
        print("❌ Cannot proceed without login")
        return
    
    # Step 5: Place order
    order_id = place_test_order(access_token)
    if not order_id:
        print("❌ Order placement failed")
        return
    
    # Step 6: Wait for database updates
    print("\n⏳ Waiting 3 seconds for database updates...")
    time.sleep(3)
    
    # Step 7: Check final state
    customers_after = get_customers_after()
    check_orders_table()
    
    # Step 8: Summary
    print_separator("TEST SUMMARY")
    
    if len(customers_after) > len(customers_before):
        print("✅ Customer was added to database")
    else:
        print("❌ No new customer was added to database")
    
    if order_id:
        print(f"✅ Order {order_id} was created")
    else:
        print("❌ No order was created")
    
    print("\n📝 If you still can't see the data in your database client:")
    print("1. Check if you're connected to the same database")
    print("2. Refresh your database client")
    print("3. Check if there are connection issues")
    print("4. Verify the database name and credentials")

if __name__ == "__main__":
    main()
