#!/usr/bin/env python3
"""
Debug script to check orders and customers in the database
"""

import pymysql
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def debug_orders():
    """Debug orders and customers in the database"""
    
    # Database configuration from .env
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
            # Check customers
            cursor.execute("SELECT COUNT(*) as count FROM customers")
            customer_count = cursor.fetchone()
            print(f"👥 Total customers: {customer_count['count']}")
            
            if customer_count['count'] > 0:
                cursor.execute("SELECT id, email, first_name, last_name FROM customers LIMIT 5")
                customers = cursor.fetchall()
                print("📋 Sample customers:")
                for customer in customers:
                    print(f"   - ID: {customer['id']}, Email: {customer['email']}, Name: {customer['first_name']} {customer['last_name']}")
            
            # Check orders
            cursor.execute("SELECT COUNT(*) as count FROM orders")
            order_count = cursor.fetchone()
            print(f"📦 Total orders: {order_count['count']}")
            
            if order_count['count'] > 0:
                cursor.execute("""
                    SELECT o.id, o.customer_id, o.status, o.total_amount, o.order_date,
                           c.email, c.first_name, c.last_name
                    FROM orders o
                    JOIN customers c ON o.customer_id = c.id
                    ORDER BY o.order_date DESC
                    LIMIT 5
                """)
                orders = cursor.fetchall()
                print("📋 Sample orders:")
                for order in orders:
                    print(f"   - Order ID: {order['id']}, Customer: {order['email']}, Status: {order['status']}, Amount: ${order['total_amount']}")
            
            # Check order items
            cursor.execute("SELECT COUNT(*) as count FROM order_items")
            item_count = cursor.fetchone()
            print(f"📋 Total order items: {item_count['count']}")
            
            if item_count['count'] > 0:
                cursor.execute("""
                    SELECT oi.id, oi.order_id, oi.product_id, oi.quantity, oi.price,
                           p.title
                    FROM order_items oi
                    LEFT JOIN products p ON oi.product_id = p.id
                    LIMIT 5
                """)
                items = cursor.fetchall()
                print("📋 Sample order items:")
                for item in items:
                    print(f"   - Item ID: {item['id']}, Order: {item['order_id']}, Product: {item['title']}, Qty: {item['quantity']}")
            
            # Check users
            cursor.execute("SELECT COUNT(*) as count FROM users")
            user_count = cursor.fetchone()
            print(f"👤 Total users: {user_count['count']}")
            
            if user_count['count'] > 0:
                cursor.execute("SELECT id, email, username FROM users LIMIT 5")
                users = cursor.fetchall()
                print("📋 Sample users:")
                for user in users:
                    print(f"   - ID: {user['id']}, Email: {user['email']}, Username: {user['username']}")
        
        connection.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    debug_orders()
