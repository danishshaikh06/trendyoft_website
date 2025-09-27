#!/usr/bin/env python3
"""
Fix database schema and foreign key constraints
"""

import pymysql
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def fix_database_schema():
    """Fix database schema issues"""
    
    config = {
        'host': os.getenv('host_name'),
        'port': int(os.getenv('db_port', 3306)),
        'user': os.getenv('db_username'),
        'password': os.getenv('db_password'),
        'database': os.getenv('database_name'),
        'charset': 'utf8mb4',
        'cursorclass': pymysql.cursors.DictCursor
    }
    
    print("🔧 Fixing database schema...")
    
    try:
        connection = pymysql.connect(**config)
        
        with connection.cursor() as cursor:
            # Drop existing foreign key constraints if they exist
            print("🗑️ Removing existing foreign key constraints...")
            
            try:
                cursor.execute("ALTER TABLE order_items DROP FOREIGN KEY fk_order_items_order_id")
                print("   - Dropped fk_order_items_order_id")
            except:
                print("   - fk_order_items_order_id doesn't exist")
            
            try:
                cursor.execute("ALTER TABLE order_items DROP FOREIGN KEY fk_order_items_product_id")
                print("   - Dropped fk_order_items_product_id")
            except:
                print("   - fk_order_items_product_id doesn't exist")
            
            # Drop and recreate order_items table with proper structure
            print("🔄 Recreating order_items table...")
            cursor.execute("DROP TABLE IF EXISTS order_items")
            
            cursor.execute("""
                CREATE TABLE order_items (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    order_id INT NOT NULL,
                    product_id INT NOT NULL,
                    quantity INT NOT NULL,
                    price DECIMAL(10, 2) NOT NULL,
                    INDEX idx_order_id (order_id),
                    INDEX idx_product_id (product_id)
                ) ENGINE=InnoDB
            """)
            
            # Add foreign key constraints with proper references
            print("🔗 Adding foreign key constraints...")
            
            cursor.execute("""
                ALTER TABLE order_items 
                ADD CONSTRAINT fk_order_items_order_id 
                FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
            """)
            print("   - Added order_id foreign key")
            
            cursor.execute("""
                ALTER TABLE order_items 
                ADD CONSTRAINT fk_order_items_product_id 
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT
            """)
            print("   - Added product_id foreign key")
            
            # Check table structures
            print("📋 Checking table structures...")
            
            for table in ['customers', 'orders', 'order_items', 'products', 'users', 'shipping_addresses']:
                cursor.execute(f"DESCRIBE {table}")
                columns = cursor.fetchall()
                print(f"   - {table}: {len(columns)} columns")
                for col in columns:
                    if col['Key'] in ['PRI', 'MUL', 'UNI']:
                        print(f"     * {col['Field']} ({col['Type']}) - {col['Key']}")
            
            connection.commit()
            print("✅ Database schema fixed successfully!")
        
        connection.close()
        
    except Exception as e:
        print(f"❌ Error fixing database schema: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    if fix_database_schema():
        print("\n🎉 Database schema is now properly configured!")
    else:
        print("\n⚠️ Failed to fix database schema.")
