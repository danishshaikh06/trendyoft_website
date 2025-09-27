#!/usr/bin/env python3
"""
Debug table structures to identify data type issues
"""

import pymysql
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def debug_table_structures():
    """Debug table structures"""
    
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
        
        with connection.cursor() as cursor:
            # Check each table structure in detail
            tables = ['customers', 'orders', 'order_items', 'products', 'users', 'shipping_addresses']
            
            for table in tables:
                print(f"\n📋 {table.upper()} TABLE STRUCTURE:")
                print("-" * 50)
                cursor.execute(f"DESCRIBE {table}")
                columns = cursor.fetchall()
                
                for col in columns:
                    key_info = f" [{col['Key']}]" if col['Key'] else ""
                    null_info = "NULL" if col['Null'] == 'YES' else "NOT NULL"
                    default_info = f" DEFAULT {col['Default']}" if col['Default'] else ""
                    extra_info = f" {col['Extra']}" if col['Extra'] else ""
                    
                    print(f"  {col['Field']:20} {col['Type']:15} {null_info:8}{key_info}{default_info}{extra_info}")
            
            # Check foreign key relationships
            print(f"\n🔗 FOREIGN KEY CONSTRAINTS:")
            print("-" * 50)
            cursor.execute("""
                SELECT 
                    TABLE_NAME,
                    COLUMN_NAME,
                    CONSTRAINT_NAME,
                    REFERENCED_TABLE_NAME,
                    REFERENCED_COLUMN_NAME
                FROM information_schema.KEY_COLUMN_USAGE 
                WHERE REFERENCED_TABLE_SCHEMA = %s
                AND REFERENCED_TABLE_NAME IS NOT NULL
            """, (os.getenv('database_name'),))
            
            fks = cursor.fetchall()
            if fks:
                for fk in fks:
                    print(f"  {fk['TABLE_NAME']}.{fk['COLUMN_NAME']} -> {fk['REFERENCED_TABLE_NAME']}.{fk['REFERENCED_COLUMN_NAME']}")
            else:
                print("  No foreign key constraints found")
        
        connection.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    debug_table_structures()
