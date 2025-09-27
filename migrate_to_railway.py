#!/usr/bin/env python3
"""
Migration script to set up Railway database with all required tables
"""

import pymysql
from dotenv import load_dotenv
import os
import logging

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_railway_connection():
    """Get Railway database connection"""
    config = {
        'host': os.getenv('host_name'),
        'port': int(os.getenv('db_port', 3306)),
        'user': os.getenv('db_username'),
        'password': os.getenv('db_password'),
        'database': os.getenv('database_name'),
        'charset': 'utf8mb4',
        'autocommit': True,
        'cursorclass': pymysql.cursors.DictCursor
    }
    return pymysql.connect(**config)

def migrate_database():
    """Migrate database to Railway with all required tables"""
    
    print("🚀 Starting Railway Database Migration...")
    
    try:
        with get_railway_connection() as conn:
            cursor = conn.cursor()
            
            # Create customers table
            create_customers_table = """
            CREATE TABLE IF NOT EXISTS customers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                first_name VARCHAR(100) NOT NULL,
                last_name VARCHAR(100) NOT NULL,
                phone_number VARCHAR(20) UNIQUE,
                email VARCHAR(255) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_email (email),
                INDEX idx_phone (phone_number)
            ) ENGINE=InnoDB;
            """
            
            # Create products table
            create_products_table = """
            CREATE TABLE IF NOT EXISTS products (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                price DECIMAL(10, 2) NOT NULL,
                quantity INT NOT NULL DEFAULT 0,
                category VARCHAR(100) NOT NULL,
                image_full_url VARCHAR(500),
                image_main_url VARCHAR(500),
                image_thumb_url VARCHAR(500),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                INDEX idx_category (category),
                INDEX idx_title (title),
                INDEX idx_is_active (is_active)
            ) ENGINE=InnoDB;
            """
            
            # Create shipping_addresses table
            create_shipping_addresses_table = """
            CREATE TABLE IF NOT EXISTS shipping_addresses (
                id INT AUTO_INCREMENT PRIMARY KEY,
                customer_id INT NOT NULL,
                address_line1 VARCHAR(255) NOT NULL,
                address_line2 VARCHAR(255),
                city VARCHAR(100) NOT NULL,
                country VARCHAR(100) NOT NULL,
                zip_code VARCHAR(20) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
                INDEX idx_customer_id (customer_id)
            ) ENGINE=InnoDB;
            """
            
            # Create orders table
            create_orders_table = """
            CREATE TABLE IF NOT EXISTS orders (
                id INT AUTO_INCREMENT PRIMARY KEY,
                customer_id INT NOT NULL,
                shipping_address_id INT NOT NULL,
                status ENUM('pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled') DEFAULT 'pending',
                total_amount DECIMAL(10, 2) NOT NULL,
                order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
                FOREIGN KEY (shipping_address_id) REFERENCES shipping_addresses(id) ON DELETE RESTRICT,
                INDEX idx_customer_id (customer_id),
                INDEX idx_status (status),
                INDEX idx_order_date (order_date)
            ) ENGINE=InnoDB;
            """
            
            # Create payment_details table
            create_payment_details_table = """
            CREATE TABLE IF NOT EXISTS payment_details (
                id INT AUTO_INCREMENT PRIMARY KEY,
                order_id INT NOT NULL,
                payment_provider VARCHAR(50) NOT NULL,
                payment_id VARCHAR(255) NOT NULL,
                status ENUM('pending', 'completed', 'failed', 'refunded') DEFAULT 'pending',
                currency VARCHAR(3) DEFAULT 'USD',
                amount DECIMAL(10, 2) NOT NULL,
                payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
                INDEX idx_order_id (order_id),
                INDEX idx_payment_id (payment_id),
                INDEX idx_status (status)
            ) ENGINE=InnoDB;
            """
            
            # Create order_items table
            create_order_items_table = """
            CREATE TABLE IF NOT EXISTS order_items (
                id INT AUTO_INCREMENT PRIMARY KEY,
                order_id INT NOT NULL,
                product_id INT NOT NULL,
                quantity INT NOT NULL,
                price DECIMAL(10, 2) NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT,
                INDEX idx_order_id (order_id),
                INDEX idx_product_id (product_id)
            ) ENGINE=InnoDB;
            """
            
            # Execute table creation queries
            tables = [
                ("customers", create_customers_table),
                ("products", create_products_table),
                ("shipping_addresses", create_shipping_addresses_table),
                ("orders", create_orders_table),
                ("payment_details", create_payment_details_table),
                ("order_items", create_order_items_table)
            ]
            
            for table_name, query in tables:
                try:
                    cursor.execute(query)
                    print(f"✅ Table '{table_name}' created/verified successfully")
                except Exception as e:
                    print(f"⚠️  Warning for table '{table_name}': {e}")
            
            # Insert sample products if products table is empty
            cursor.execute("SELECT COUNT(*) as count FROM products")
            result = cursor.fetchone()
            
            if result['count'] == 0:
                print("📦 Adding sample products...")
                sample_products = [
                    ("Striped Adventure Tee", "Perfect for outdoor adventures", 19.99, 50, "clothing"),
                    ("Mountain Sunset Shirt", "Inspired by mountain sunsets", 19.99, 30, "clothing"),
                    ("Forest Green Classic", "Timeless eco-friendly design", 19.99, 40, "clothing"),
                    ("Coral Comfort Tee", "Vibrant comfort all day long", 19.99, 25, "clothing")
                ]
                
                insert_query = """
                INSERT INTO products (title, description, price, quantity, category)
                VALUES (%s, %s, %s, %s, %s)
                """
                
                for product in sample_products:
                    cursor.execute(insert_query, product)
                    
                print(f"✅ Added {len(sample_products)} sample products")
            
            conn.commit()
            print("\\n🎉 Railway Database Migration Completed Successfully!")
            
            # Show final status
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"\\n📋 Final Database Status - {len(tables)} tables:")
            for table in tables:
                table_name = list(table.values())[0]
                cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
                count = cursor.fetchone()['count']
                print(f"   - {table_name}: {count} records")
                
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        print(f"❌ Migration failed: {e}")
        return False
        
    return True

if __name__ == "__main__":
    success = migrate_database()
    if success:
        print("\\n✨ Your Railway database is ready! You can now start your application.")
    else:
        print("\\n⚠️  Migration failed. Please check the error messages above.")
