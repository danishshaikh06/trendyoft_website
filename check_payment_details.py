#!/usr/bin/env python3
"""
Script to check payment details for recent orders in the database.
"""

import pymysql
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def connect_to_database():
    """Connect to the MySQL database"""
    try:
        connection = pymysql.connect(
            host=os.getenv('host_name', 'localhost'),
            user=os.getenv('db_username', 'root'),
            password=os.getenv('db_password', ''),
            database=os.getenv('database_name', 'railway'),
            port=int(os.getenv('db_port', '3306')),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except Exception as e:
        print(f"Database connection failed: {e}")
        return None

def check_payment_details():
    """Check payment details table and recent orders"""
    conn = connect_to_database()
    if not conn:
        return
    
    try:
        with conn.cursor() as cursor:
            print("=== PAYMENT DETAILS TABLE STRUCTURE ===")
            cursor.execute("DESCRIBE payment_details")
            columns = cursor.fetchall()
            for col in columns:
                nullable = "" if col['Null'] == 'YES' else "NOT NULL"
                default = f"DEFAULT {col['Default']}" if col['Default'] else ""
                key = col['Key'] if col['Key'] else ""
                extra = col['Extra'] if col['Extra'] else ""
                print(f"{col['Field']}: {col['Type']} {key} {nullable} {default} {extra}")
            
            print("\n=== RECENT PAYMENT DETAILS ===")
            cursor.execute("""
                SELECT pd.*, o.id as order_id, o.total_amount, o.status, o.created_at as order_created
                FROM payment_details pd
                JOIN orders o ON pd.order_id = o.id
                ORDER BY pd.created_at DESC
                LIMIT 10
            """)
            payments = cursor.fetchall()
            
            if payments:
                print(f"Found {len(payments)} payment records:")
                for payment in payments:
                    print(f"Order {payment['order_id']}: ${payment['amount']:.2f} via {payment['provider']} ({payment['currency']}) - Status: {payment['status']} - Created: {payment['created_at']}")
            else:
                print("No payment details found!")
            
            print("\n=== CHECKING LATEST ORDER (ID: 21) ===")
            cursor.execute("""
                SELECT pd.*, o.total_amount, o.status as order_status
                FROM payment_details pd
                JOIN orders o ON pd.order_id = o.id
                WHERE o.id = 21
            """)
            latest_payment = cursor.fetchone()
            
            if latest_payment:
                print("✅ Payment details found for Order 21:")
                print(f"  Amount: ${latest_payment['amount']:.2f}")
                print(f"  Provider: {latest_payment['provider']}")
                print(f"  Currency: {latest_payment['currency']}")
                print(f"  Status: {latest_payment['status']}")
                print(f"  Created: {latest_payment['created_at']}")
                print(f"  Order Total: ${latest_payment['total_amount']:.2f}")
                print(f"  Order Status: {latest_payment['order_status']}")
            else:
                print("❌ No payment details found for Order 21!")
                
                # Check if order exists
                cursor.execute("SELECT * FROM orders WHERE id = 21")
                order = cursor.fetchone()
                if order:
                    print(f"Order 21 exists with total: ${order['total_amount']:.2f}")
                else:
                    print("Order 21 does not exist!")

    except Exception as e:
        print(f"Error checking payment details: {e}")
    
    finally:
        conn.close()

if __name__ == "__main__":
    check_payment_details()
