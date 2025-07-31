#!/usr/bin/env python3
"""
Check if orders are being saved to the database
"""

import pymysql
from dotenv import load_dotenv
import os
import time

# Load environment variables
load_dotenv()

def check_orders_continuously():
    """Continuously check for new orders in the database"""
    
    config = {
        'host': os.getenv('host_name'),
        'port': int(os.getenv('db_port', 3306)),
        'user': os.getenv('db_username'),
        'password': os.getenv('db_password'),
        'database': os.getenv('database_name'),
        'charset': 'utf8mb4',
        'cursorclass': pymysql.cursors.DictCursor
    }
    
    print("🔍 Monitoring database for new orders...")
    print("📱 Go ahead and place an order through your application now!")
    print("⏹️  Press Ctrl+C to stop monitoring")
    print("-" * 60)
    
    last_customer_count = 0
    last_order_count = 0
    last_item_count = 0
    
    try:
        while True:
            try:
                connection = pymysql.connect(**config)
                
                with connection.cursor() as cursor:
                    # Check customers
                    cursor.execute("SELECT COUNT(*) as count FROM customers")
                    customer_count = cursor.fetchone()['count']
                    
                    # Check orders  
                    cursor.execute("SELECT COUNT(*) as count FROM orders")
                    order_count = cursor.fetchone()['count']
                    
                    # Check order items
                    cursor.execute("SELECT COUNT(*) as count FROM order_items")
                    item_count = cursor.fetchone()['count']
                    
                    # Check if anything changed
                    if (customer_count != last_customer_count or 
                        order_count != last_order_count or 
                        item_count != last_item_count):
                        
                        print(f"🔄 {time.strftime('%H:%M:%S')} - CHANGE DETECTED!")
                        print(f"   👥 Customers: {last_customer_count} → {customer_count}")
                        print(f"   📦 Orders: {last_order_count} → {order_count}")
                        print(f"   📋 Order Items: {last_item_count} → {item_count}")
                        
                        # Show latest orders if any exist
                        if order_count > 0:
                            cursor.execute("""
                                SELECT o.id, o.customer_id, o.status, o.total_amount, o.order_date,
                                       c.email, c.first_name, c.last_name
                                FROM orders o
                                LEFT JOIN customers c ON o.customer_id = c.id
                                ORDER BY o.order_date DESC
                                LIMIT 3
                            """)
                            orders = cursor.fetchall()
                            print("   📋 Latest orders:")
                            for order in orders:
                                customer_info = f"{order['email']}" if order['email'] else f"Customer ID: {order['customer_id']}"
                                print(f"     - Order {order['id']}: ${order['total_amount']} ({order['status']}) - {customer_info}")
                            
                            # Show order items for latest order
                            latest_order_id = orders[0]['id']
                            cursor.execute("""
                                SELECT oi.*, p.title, p.price as product_price
                                FROM order_items oi
                                LEFT JOIN products p ON oi.product_id = p.id
                                WHERE oi.order_id = %s
                            """, (latest_order_id,))
                            items = cursor.fetchall()
                            print(f"   📋 Items in Order {latest_order_id}:")
                            for item in items:
                                print(f"     - {item['title']}: Qty {item['quantity']} @ ${item['price']} each")
                        
                        print("-" * 60)
                        
                        last_customer_count = customer_count
                        last_order_count = order_count
                        last_item_count = item_count
                
                connection.close()
                time.sleep(2)  # Check every 2 seconds
                
            except KeyboardInterrupt:
                print("\n👋 Monitoring stopped by user")
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                time.sleep(5)  # Wait longer on error
                
    except KeyboardInterrupt:
        print("\n👋 Monitoring stopped")

if __name__ == "__main__":
    check_orders_continuously()
