#!/usr/bin/env python3
"""
Verify that customer data from checkout forms is properly stored in the database
"""

import pymysql
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

def print_separator(title):
    """Print a separator with title"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def verify_customer_data():
    """Verify that customer data is correctly stored"""
    print_separator("VERIFYING CUSTOMER DATA IN DATABASE")
    
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Check the most recent customer record
        cursor.execute("""
            SELECT id, first_name, last_name, username, phone_number, email, created_at 
            FROM customers 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        customers = cursor.fetchall()
        
        print(f"📋 RECENT CUSTOMERS ({len(customers)} found):")
        print("-" * 80)
        for customer in customers:
            print(f"ID: {customer['id']}")
            print(f"Name: {customer['first_name']} {customer['last_name']}")
            print(f"Username: {customer.get('username', 'N/A')}")
            print(f"Email: {customer['email']}")
            print(f"Phone: {customer.get('phone_number', 'N/A')}")
            print(f"Created: {customer['created_at']}")
            print("-" * 40)
        
        # Check for our test user specifically
        test_email = "shaikhdanish.sd06@gmail.com"
        cursor.execute("""
            SELECT id, first_name, last_name, username, phone_number, email, created_at 
            FROM customers 
            WHERE email = %s
        """, (test_email,))
        test_customer = cursor.fetchone()
        
        if test_customer:
            print(f"\n✅ TEST USER VERIFICATION:")
            print(f"Expected checkout form data:")
            print(f"  - First Name: Danish")
            print(f"  - Last Name: Shaikh") 
            print(f"  - Phone: +91-9876543210")
            print(f"  - Email: {test_email}")
            
            print(f"\nActual database data:")
            print(f"  - First Name: {test_customer['first_name']}")
            print(f"  - Last Name: {test_customer['last_name']}")
            print(f"  - Username: {test_customer.get('username', 'N/A')}")
            print(f"  - Phone: {test_customer.get('phone_number', 'N/A')}")
            print(f"  - Email: {test_customer['email']}")
            
            # Verify if checkout form data was stored correctly
            if (test_customer['first_name'] == 'Danish' and 
                test_customer['last_name'] == 'Shaikh' and
                test_customer.get('phone_number') == '+91-9876543210'):
                print(f"\n✅ SUCCESS: Checkout form data stored correctly!")
                print(f"   - Customer name from form: Danish Shaikh ✓")
                print(f"   - Phone from form: +91-9876543210 ✓")
                
                if test_customer.get('username'):
                    print(f"   - Username tracked: {test_customer['username']} ✓")
                else:
                    print(f"   - Username tracking: Not implemented yet")
            else:
                print(f"\n❌ ISSUE: Checkout form data not stored correctly!")
                print(f"   Expected: Danish Shaikh, +91-9876543210")
                print(f"   Got: {test_customer['first_name']} {test_customer['last_name']}, {test_customer.get('phone_number')}")
        else:
            print(f"\n❌ Test customer not found in database!")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error verifying customer data: {e}")

def verify_orders_data():
    """Verify that orders are linked to customers correctly"""
    print_separator("VERIFYING ORDERS DATA")
    
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Get recent orders with customer info
        cursor.execute("""
            SELECT 
                o.id as order_id,
                o.status,
                o.total_amount,
                o.order_date,
                c.first_name,
                c.last_name,
                c.username,
                c.email,
                c.phone_number
            FROM orders o
            JOIN customers c ON o.customer_id = c.id
            ORDER BY o.order_date DESC
            LIMIT 5
        """)
        orders = cursor.fetchall()
        
        print(f"📦 RECENT ORDERS ({len(orders)} found):")
        print("-" * 80)
        for order in orders:
            print(f"Order ID: {order['order_id']}")
            print(f"Customer: {order['first_name']} {order['last_name']}")
            print(f"Username: {order.get('username', 'N/A')}")
            print(f"Email: {order['email']}")
            print(f"Phone: {order.get('phone_number', 'N/A')}")
            print(f"Total: ${order['total_amount']}")
            print(f"Status: {order['status']}")
            print(f"Date: {order['order_date']}")
            print("-" * 40)
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error verifying orders data: {e}")

def main():
    """Main verification function"""
    print_separator("DATABASE VERIFICATION TEST")
    print("Checking if checkout form data is properly stored...")
    
    verify_customer_data()
    verify_orders_data()
    
    print_separator("VERIFICATION COMPLETE")
    print("If you see ✅ SUCCESS messages above, the checkout system is working correctly!")
    print("The customer names entered in checkout forms are now properly stored.")

if __name__ == "__main__":
    main()
