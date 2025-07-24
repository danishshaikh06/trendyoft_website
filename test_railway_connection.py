#!/usr/bin/env python3
"""
Test script to verify Railway cloud database connection
"""

import pymysql
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def test_railway_connection():
    """Test the Railway database connection"""
    
    # Database configuration from .env
    config = {
        'host': os.getenv('host_name'),
        'port': int(os.getenv('db_port', 3306)),
        'user': os.getenv('db_username'),
        'password': os.getenv('db_password'),
        'database': os.getenv('database_name'),
        'charset': 'utf8mb4',
        'cursorclass': pymysql.cursors.DictCursor
    }
    
    print("🚀 Testing Railway Database Connection...")
    print(f"📍 Host: {config['host']}")
    print(f"🔌 Port: {config['port']}")
    print(f"👤 User: {config['user']}")
    print(f"🗄️  Database: {config['database']}")
    print("-" * 50)
    
    try:
        # Establish connection
        connection = pymysql.connect(**config)
        print("✅ Connection established successfully!")
        
        # Test basic query
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION() as version")
            result = cursor.fetchone()
            print(f"📊 MySQL Version: {result['version']}")
            
            # Show existing tables
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            if tables:
                print(f"📋 Existing tables ({len(tables)}):")
                for table in tables:
                    table_name = list(table.values())[0]
                    print(f"   - {table_name}")
            else:
                print("📋 No tables found (fresh database)")
                
            # Test create/drop table permissions
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS connection_test (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    test_message VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("✅ CREATE TABLE permission: OK")
            
            cursor.execute("DROP TABLE IF EXISTS connection_test")
            print("✅ DROP TABLE permission: OK")
            
        connection.close()
        print("✅ Connection closed successfully!")
        print("\n🎉 Railway database is ready for use!")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_railway_connection()
    if success:
        print("\n✨ You can now run your application with the Railway database!")
    else:
        print("\n⚠️  Please check your database credentials and try again.")
