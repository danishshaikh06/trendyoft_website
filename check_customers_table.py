#!/usr/bin/env python3
"""
Script to investigate the customers table structure and data
"""

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
    
    # Check current customers table structure and data
    print('=== CUSTOMERS TABLE INFO ===')
    cursor.execute('DESCRIBE customers')
    columns = cursor.fetchall()
    for col in columns:
        field = col.get('Field', '')
        type_info = col.get('Type', '')
        key_info = col.get('Key', '')
        extra_info = col.get('Extra', '')
        print(f'{field}: {type_info} {key_info} {extra_info}')
    
    print('\n=== CUSTOMERS TABLE DATA ===')
    cursor.execute('SELECT * FROM customers ORDER BY id')
    customers = cursor.fetchall()
    print(f'Total customers: {len(customers)}')
    for customer in customers:
        customer_id = customer.get('id', 'N/A')
        first_name = customer.get('first_name', '')
        last_name = customer.get('last_name', '')
        email = customer.get('email', '')
        phone = customer.get('phone_number', 'None')
        created = customer.get('created_at', 'N/A')
        print(f'ID: {customer_id}, Name: {first_name} {last_name}, Email: {email}, Phone: {phone}, Created: {created}')
    
    print('\n=== CHECKING TABLE CONSTRAINTS ===')
    cursor.execute('SHOW CREATE TABLE customers')
    result = cursor.fetchone()
    create_table_sql = result.get('Create Table', '')
    print(create_table_sql)
    
    print('\n=== CHECKING FOR AUTO_INCREMENT ISSUES ===')
    cursor.execute('SHOW TABLE STATUS LIKE "customers"')
    status = cursor.fetchone()
    if status:
        auto_increment = status.get('Auto_increment', 'N/A')
        max_rows = status.get('Max_data_length', 'N/A')  
        engine = status.get('Engine', 'N/A')
        print(f'Engine: {engine}')
        print(f'Next Auto_increment: {auto_increment}')
        print(f'Max_data_length: {max_rows}')
    
    print('\n=== CHECKING DATABASE SIZE LIMITS ===')
    cursor.execute('SELECT COUNT(*) as total FROM customers')
    count_result = cursor.fetchone()
    total_count = count_result.get('total', 0)
    print(f'Total customer records: {total_count}')
    
    conn.close()
    print('\n=== Database check completed ===')
    
except Exception as e:
    print(f'Error: {e}')
