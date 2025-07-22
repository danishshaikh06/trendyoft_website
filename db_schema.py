# Database Schema Configuration
# This file defines the database table structures for reference and validation

DATABASE_SCHEMA = {
    "customers": {
        "table_name": "customers",
        "columns": [
            "id",
            "first_name", 
            "last_name", 
            "phone_number",
            "email",
            "created_at"
        ]
    },
    
    "orders": {
        "table_name": "orders",
        "columns": [
            "id", 
            "customer_id", 
            "shipping_address_id", 
            "status",
            "total_amount",
            "order_date"
        ]
    },
    
    "payment_details": {
        "table_name": "payment_details",
        "columns": [
            "id", 
            "order_id", 
            "payment_provider", 
            "payment_id",
            "status",
            "currency",
            "amount",
            "payment_date"
        ]
    },
    
    "products": {
        "table_name": "products",
        "columns": [
            "id", 
            "title", 
            "description", 
            "price",
            "quantity",
            "category",
            "image_full_url",
            "image_main_url",
            "image_thumb_url",
            "created_at",
            "updated_at",
            "is_active"
        ]
    },
    
    "shipping_addresses": {
        "table_name": "shipping_addresses",
        "columns": [
            "id", 
            "customer_id", 
            "address_line1", 
            "address_line2",
            "city",
            "country",
            "zip_code",
            "created_at"
        ]
    },
    
    "order_items": {
        "table_name": "order_items",
        "columns": [
            "id",
            "order_id",
            "product_id",
            "quantity",
            "price"
        ]
    }
}

# Helper functions to get column names
def get_table_columns(table_name):
    """Get column names for a specific table"""
    return DATABASE_SCHEMA.get(table_name, {}).get("columns", [])

def validate_columns(table_name, columns):
    """Validate if columns exist for a table"""
    valid_columns = get_table_columns(table_name)
    invalid_columns = [col for col in columns if col not in valid_columns]
    return len(invalid_columns) == 0, invalid_columns

# SQL query builders using schema
def build_select_query(table_name, columns=None, where_clause=""):
    """Build SELECT query using schema validation"""
    if columns is None:
        columns = get_table_columns(table_name)
    
    valid, invalid = validate_columns(table_name, columns)
    if not valid:
        raise ValueError(f"Invalid columns for {table_name}: {invalid}")
    
    query = f"SELECT {', '.join(columns)} FROM {table_name}"
    if where_clause:
        query += f" WHERE {where_clause}"
    
    return query

def build_insert_query(table_name, data):
    """Build INSERT query using schema validation"""
    columns = list(data.keys())
    valid, invalid = validate_columns(table_name, columns)
    if not valid:
        raise ValueError(f"Invalid columns for {table_name}: {invalid}")
    
    placeholders = ", ".join(["%s"] * len(columns))
    query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
    
    return query, list(data.values())
