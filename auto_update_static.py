#!/usr/bin/env python3
"""
Auto-update static site whenever database products change
This runs in the background and automatically generates static files
"""

import time
import pymysql
import hashlib
import os
from datetime import datetime
from dotenv import load_dotenv
import subprocess

# Load environment variables
load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': os.getenv('host_name'),
    'port': 3306,
    'user': os.getenv('db_username'),
    'password': os.getenv('db_password'),
    'database': os.getenv('database_name'),
    'charset': 'utf8mb4',
    'autocommit': True,
    'cursorclass': pymysql.cursors.DictCursor
}

def get_products_hash():
    """Get a hash of all products to detect changes"""
    try:
        connection = pymysql.connect(**DB_CONFIG)
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, title, description, price, quantity, category, 
                       image_full_url, image_main_url, image_thumb_url, 
                       updated_at
                FROM products 
                WHERE is_active = TRUE 
                ORDER BY id
            """)
            products = cursor.fetchall()
        connection.close()
        
        # Create hash from product data
        products_str = str(products)
        return hashlib.md5(products_str.encode()).hexdigest()
        
    except Exception as e:
        print(f"Error getting products hash: {e}")
        return None

def run_static_generator():
    """Run the static site generator"""
    try:
        print(f"🔄 {datetime.now().strftime('%H:%M:%S')} - Products changed, updating static site...")
        result = subprocess.run(['python', 'generate_static_site.py'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {datetime.now().strftime('%H:%M:%S')} - Static site updated successfully!")
        else:
            print(f"❌ {datetime.now().strftime('%H:%M:%S')} - Error updating static site:")
            print(result.stderr)
    except Exception as e:
        print(f"❌ Error running static generator: {e}")

def monitor_products():
    """Monitor products table for changes"""
    print("🔍 Starting product monitor...")
    print("📝 This will automatically update static files when products change")
    print("⏹️  Press Ctrl+C to stop monitoring")
    print("-" * 60)
    
    last_hash = None
    check_interval = 30  # Check every 30 seconds
    
    try:
        while True:
            current_hash = get_products_hash()
            
            if current_hash is None:
                print(f"⚠️  {datetime.now().strftime('%H:%M:%S')} - Could not connect to database")
                time.sleep(check_interval)
                continue
            
            if last_hash is None:
                # First run
                last_hash = current_hash
                print(f"🎯 {datetime.now().strftime('%H:%M:%S')} - Initial product state captured")
                run_static_generator()
            elif current_hash != last_hash:
                # Products changed
                last_hash = current_hash
                run_static_generator()
            else:
                # No changes
                print(f"✅ {datetime.now().strftime('%H:%M:%S')} - No product changes detected", end='\r')
            
            time.sleep(check_interval)
            
    except KeyboardInterrupt:
        print(f"\n🛑 {datetime.now().strftime('%H:%M:%S')} - Product monitoring stopped")
    except Exception as e:
        print(f"\n❌ {datetime.now().strftime('%H:%M:%S')} - Error: {e}")

if __name__ == "__main__":
    monitor_products()
