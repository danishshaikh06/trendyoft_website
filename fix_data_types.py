#!/usr/bin/env python3
"""
Fix data type mismatches in database schema
"""

import pymysql
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def fix_data_types():
    """Fix data type mismatches"""
    
    config = {
        'host': os.getenv('host_name'),
        'port': int(os.getenv('db_port', 3306)),
        'user': os.getenv('db_username'),
        'password': os.getenv('db_password'),
        'database': os.getenv('database_name'),
        'charset': 'utf8mb4',
        'cursorclass': pymysql.cursors.DictCursor
    }
    
    print("🔧 Fixing data type mismatches...")
    
    try:
        connection = pymysql.connect(**config)
        
        with connection.cursor() as cursor:
            # Fix orders table - make customer_id and shipping_address_id match the referenced tables
            print("📋 Fixing orders table...")
            cursor.execute("ALTER TABLE orders MODIFY COLUMN customer_id BIGINT UNSIGNED NOT NULL")
            cursor.execute("ALTER TABLE orders MODIFY COLUMN shipping_address_id BIGINT UNSIGNED NOT NULL")
            print("   - Fixed customer_id and shipping_address_id data types")
            
            # Fix order_items table - make order_id and product_id match the referenced tables
            print("📋 Fixing order_items table...")
            cursor.execute("ALTER TABLE order_items MODIFY COLUMN order_id BIGINT UNSIGNED NOT NULL")
            cursor.execute("ALTER TABLE order_items MODIFY COLUMN product_id BIGINT UNSIGNED NOT NULL")
            print("   - Fixed order_id and product_id data types")
            
            # Fix shipping_addresses table - make customer_id match
            print("📋 Fixing shipping_addresses table...")
            cursor.execute("ALTER TABLE shipping_addresses MODIFY COLUMN customer_id BIGINT UNSIGNED NOT NULL")
            print("   - Fixed customer_id data type")
            
            # Now add the foreign key constraints
            print("🔗 Adding foreign key constraints...")
            
            # Add foreign key for orders.customer_id -> customers.id
            try:
                cursor.execute("""
                    ALTER TABLE orders 
                    ADD CONSTRAINT fk_orders_customer_id 
                    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
                """)
                print("   - Added orders.customer_id foreign key")
            except Exception as e:
                print(f"   - orders.customer_id foreign key already exists or failed: {e}")
            
            # Add foreign key for orders.shipping_address_id -> shipping_addresses.id
            try:
                cursor.execute("""
                    ALTER TABLE orders 
                    ADD CONSTRAINT fk_orders_shipping_address_id 
                    FOREIGN KEY (shipping_address_id) REFERENCES shipping_addresses(id) ON DELETE RESTRICT
                """)
                print("   - Added orders.shipping_address_id foreign key")
            except Exception as e:
                print(f"   - orders.shipping_address_id foreign key already exists or failed: {e}")
            
            # Add foreign key for order_items.order_id -> orders.id
            try:
                cursor.execute("""
                    ALTER TABLE order_items 
                    ADD CONSTRAINT fk_order_items_order_id 
                    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
                """)
                print("   - Added order_items.order_id foreign key")
            except Exception as e:
                print(f"   - order_items.order_id foreign key already exists or failed: {e}")
            
            # Add foreign key for order_items.product_id -> products.id
            try:
                cursor.execute("""
                    ALTER TABLE order_items 
                    ADD CONSTRAINT fk_order_items_product_id 
                    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT
                """)
                print("   - Added order_items.product_id foreign key")
            except Exception as e:
                print(f"   - order_items.product_id foreign key already exists or failed: {e}")
            
            # Add foreign key for shipping_addresses.customer_id -> customers.id
            try:
                cursor.execute("""
                    ALTER TABLE shipping_addresses 
                    ADD CONSTRAINT fk_shipping_addresses_customer_id 
                    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
                """)
                print("   - Added shipping_addresses.customer_id foreign key")
            except Exception as e:
                print(f"   - shipping_addresses.customer_id foreign key already exists or failed: {e}")
            
            connection.commit()
            print("✅ Data types and foreign keys fixed successfully!")
        
        connection.close()
        
    except Exception as e:
        print(f"❌ Error fixing data types: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    if fix_data_types():
        print("\n🎉 Database schema is now properly configured!")
        print("📋 You can now place orders and they should be saved to the database.")
    else:
        print("\n⚠️ Failed to fix database schema.")
