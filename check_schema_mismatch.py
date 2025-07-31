#!/usr/bin/env python3
import pymysql
from dotenv import load_dotenv
import os

load_dotenv()

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
    cursor = connection.cursor()
    
    # Check if there are data type mismatches
    cursor.execute('DESCRIBE orders')
    orders_schema = cursor.fetchall()
    
    cursor.execute('DESCRIBE order_items')
    items_schema = cursor.fetchall()
    
    print('🔍 CHECKING DATA TYPE MISMATCHES:')
    print('=' * 50)
    print('ORDERS TABLE ID COLUMNS:')
    for col in orders_schema:
        if 'id' in col['Field']:
            print(f"  {col['Field']}: {col['Type']}")
    
    print('\nORDER_ITEMS TABLE ID COLUMNS:')
    for col in items_schema:
        if 'id' in col['Field']:
            print(f"  {col['Field']}: {col['Type']}")
    
    print('\n📊 LATEST RECORDS:')
    cursor.execute('SELECT id, customer_id, shipping_address_id FROM orders ORDER BY id DESC LIMIT 3')
    orders = cursor.fetchall()
    print('Recent orders:')
    for order in orders:
        print(f"  Order {order['id']}: customer_id={order['customer_id']}, shipping_address_id={order['shipping_address_id']}")
    
    connection.close()
    
except Exception as e:
    print(f'❌ Error: {e}')
