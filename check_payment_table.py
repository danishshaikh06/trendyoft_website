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
    
    print("=== PAYMENT_DETAILS TABLE STRUCTURE ===")
    cursor.execute("DESCRIBE payment_details")
    columns = cursor.fetchall()
    for col in columns:
        print(f"{col['Field']}: {col['Type']} - {col['Null']} - {col['Key']} - {col['Default']}")
    
    print("\n=== SAMPLE PAYMENT_DETAILS RECORDS ===")
    cursor.execute("SELECT * FROM payment_details LIMIT 5")
    payments = cursor.fetchall()
    for payment in payments:
        print(payment)
        
    print("\n=== CUSTOMERS TABLE - RECENT RECORDS ===")
    cursor.execute("SELECT * FROM customers ORDER BY created_at DESC LIMIT 5")
    customers = cursor.fetchall()
    for customer in customers:
        print(customer)
        
    print("\n=== ORDERS TABLE - RECENT RECORDS ===")
    cursor.execute("SELECT * FROM orders ORDER BY order_date DESC LIMIT 5")
    orders = cursor.fetchall()
    for order in orders:
        print(order)
    
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
