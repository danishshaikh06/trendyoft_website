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
    
    print("Adding currency column to payment_details table...")
    
    # Check if currency column already exists
    cursor.execute("SHOW COLUMNS FROM payment_details LIKE 'currency'")
    if cursor.fetchone():
        print("Currency column already exists!")
    else:
        # Add currency column
        cursor.execute("ALTER TABLE payment_details ADD COLUMN currency VARCHAR(3) DEFAULT 'INR' AFTER amount")
        conn.commit()
        print("Currency column added successfully!")
    
    # Show updated table structure
    print("\n=== UPDATED PAYMENT_DETAILS TABLE STRUCTURE ===")
    cursor.execute("DESCRIBE payment_details")
    columns = cursor.fetchall()
    for col in columns:
        print(f"{col['Field']}: {col['Type']} - {col['Null']} - {col['Key']} - {col['Default']}")
    
    conn.close()
    print("\nDatabase update completed!")
    
except Exception as e:
    print(f"Error: {e}")
