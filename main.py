from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional
import os
import uuid
import json
from datetime import datetime
from PIL import Image
import shutil
import pymysql
from pymysql import Error
from dotenv import load_dotenv
import logging
from contextlib import contextmanager

# Load environment variables from .env file
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

# Initialize FastAPI app
app = FastAPI(title="Trendyoft E-commerce Backend", version="1.0.0")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection management
@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    connection = None
    try:
        connection = pymysql.connect(**DB_CONFIG)
        logger.info("Database connection established")
        yield connection
    except Error as e:
        logger.error(f"Database connection error: {e}")
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if connection and connection.open:
            connection.close()
            logger.info("Database connection closed")

# Database initialization
def init_database():
    """Initialize database tables with proper schema and foreign keys"""
    try:
        with get_db_connection() as conn:
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
            
            # Drop and recreate order_items table to fix foreign key constraint issues
            drop_order_items_table = "DROP TABLE IF EXISTS order_items;"
            
            # Create order_items table (junction table for orders and products)
            create_order_items_table = """
            CREATE TABLE order_items (
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
            
            # Execute table creation queries in correct order for foreign keys
            tables = [
                ("customers", create_customers_table),
                ("products", create_products_table),
                ("shipping_addresses", create_shipping_addresses_table),
                ("orders", create_orders_table),
                ("payment_details", create_payment_details_table)
            ]
            
            for table_name, query in tables:
                cursor.execute(query)
                logger.info(f"Table {table_name} created/verified successfully")
            
            # TODO: Fix order_items table foreign key constraint issue later
            # cursor.execute(drop_order_items_table)
            # cursor.execute(create_order_items_table)
            # logger.info("Table order_items created/verified successfully")
            
            conn.commit()
            logger.info("Database initialization completed successfully")
            
    except Error as e:
        logger.error(f"Error initializing database: {e}")
        raise

# Initialize database on startup
try:
    init_database()
except Exception as e:
    logger.error(f"Failed to initialize database: {e}")

# CORS middleware to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],  # Allow your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create images directory structure if it doesn't exist
IMAGES_DIR = "images"
THUMBNAIL_DIR = os.path.join(IMAGES_DIR, "thumbnails")
MAIN_DIR = os.path.join(IMAGES_DIR, "main")
ORIGINAL_DIR = os.path.join(IMAGES_DIR, "original")

# Create directories
for directory in [IMAGES_DIR, THUMBNAIL_DIR, MAIN_DIR, ORIGINAL_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory)

# Mount static files for serving images
app.mount("/images", StaticFiles(directory=IMAGES_DIR), name="images")

# Admin token for protected operations
ADMIN_TOKEN = "danishshaikh@06"  # Change this to your actual admin token

# Security scheme
security = HTTPBearer()

# Database helper functions
def get_products_from_db():
    """Fetch all products from database"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, description, price, quantity, category, 
                   image_full_url, image_main_url, image_thumb_url, 
                   created_at, updated_at, is_active 
            FROM products 
            WHERE is_active = TRUE 
            ORDER BY created_at DESC
        """)
        return cursor.fetchall()

def get_product_by_id(product_id: int):
    """Fetch a single product by ID from database"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, description, price, quantity, category, 
                   image_full_url, image_main_url, image_thumb_url, 
                   created_at, updated_at, is_active 
            FROM products 
            WHERE id = %s AND is_active = TRUE
        """, (product_id,))
        return cursor.fetchone()

def insert_product_to_db(product_data):
    """Insert a new product into database"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        insert_query = """
            INSERT INTO products (title, description, price, quantity, category, 
                                image_full_url, image_main_url, image_thumb_url) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (
            product_data['title'],
            product_data['description'],
            product_data['price'],
            product_data['quantity'],
            product_data['category'],
            product_data['image_full_url'],
            product_data['image_main_url'],
            product_data['image_thumb_url']
        ))
        conn.commit()
        return cursor.lastrowid

def update_product_in_db(product_id: int, product_data):
    """Update a product in database"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Build dynamic update query based on provided data
        update_fields = []
        values = []
        
        for field, value in product_data.items():
            if value is not None:
                update_fields.append(f"{field} = %s")
                values.append(value)
        
        if update_fields:
            values.append(product_id)
            update_query = f"UPDATE products SET {', '.join(update_fields)} WHERE id = %s"
            cursor.execute(update_query, values)
            conn.commit()
            return cursor.rowcount > 0
        return False

def delete_product_from_db(product_id: int):
    """Soft delete a product (set is_active = FALSE)"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE products SET is_active = FALSE WHERE id = %s", (product_id,))
        conn.commit()
        return cursor.rowcount > 0

def get_categories_from_db():
    """Get category statistics from database"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT category, 
                   COUNT(*) as count,
                   COUNT(*) as total_products,
                   SUM(CASE WHEN quantity > 0 THEN 1 ELSE 0 END) as in_stock,
                   SUM(CASE WHEN quantity = 0 THEN 1 ELSE 0 END) as out_of_stock
            FROM products 
            WHERE is_active = TRUE 
            GROUP BY category 
            ORDER BY count DESC
        """)
        categories = cursor.fetchall()
        
        # Format for compatibility with existing API
        formatted_categories = []
        for cat in categories:
            formatted_categories.append({
                'name': cat['category'],
                'count': cat['count'],
                'total_products': cat['total_products'],
                'in_stock': cat['in_stock'],
                'out_of_stock': cat['out_of_stock']
            })
        
        return formatted_categories

# Customer management functions
def insert_customer_to_db(customer_data):
    """Insert a new customer into database"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        insert_query = """
            INSERT INTO customers (first_name, last_name, phone_number, email) 
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(insert_query, (
            customer_data['first_name'],
            customer_data['last_name'],
            customer_data.get('phone_number'),
            customer_data['email']
        ))
        conn.commit()
        return cursor.lastrowid

def get_customer_by_email(email: str):
    """Get customer by email"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM customers WHERE email = %s", (email,))
        return cursor.fetchone()

# Order management functions
def create_order_in_db(order_data):
    """Create a new order with order items"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Insert order
        insert_order_query = """
            INSERT INTO orders (customer_id, shipping_address_id, status, total_amount) 
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(insert_order_query, (
            order_data['customer_id'],
            order_data['shipping_address_id'],
            order_data.get('status', 'pending'),
            order_data['total_amount']
        ))
        order_id = cursor.lastrowid
        
        # Insert order items
        if 'items' in order_data:
            insert_item_query = """
                INSERT INTO order_items (order_id, product_id, quantity, price) 
                VALUES (%s, %s, %s, %s)
            """
            for item in order_data['items']:
                cursor.execute(insert_item_query, (
                    order_id,
                    item['product_id'],
                    item['quantity'],
                    item['price']
                ))
        
        conn.commit()
        return order_id

# Legacy support - keeping products_db for backward compatibility during transition
products_db = []

# Initialize with some sample products
sample_products = [
    {
        "id": str(uuid.uuid4()),
        "title": "Striped Adventure Tee",
        "price": 19.99,
        "description": "Perfect for outdoor adventures with its comfortable striped design. Made from premium cotton blend for all-day comfort.",
        "quantity": 15,
        "category": "t-shirts",
        "image_url": "/images/placeholder.jpg",
        "images": {
            "thumbnail": "/images/placeholder.jpg",
            "main": "/images/placeholder.jpg",
            "original": "/images/placeholder.jpg"
        },
        "created_at": datetime.now().isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Mountain Sunset Shirt",
        "price": 19.99,
        "description": "Inspired by beautiful mountain sunsets, this shirt combines style with functionality. Ideal for casual wear and outdoor activities.",
        "quantity": 8,
        "category": "shirts",
        "image_url": "/images/placeholder.jpg",
        "images": {
            "thumbnail": "/images/placeholder.jpg",
            "main": "/images/placeholder.jpg",
            "original": "/images/placeholder.jpg"
        },
        "created_at": datetime.now().isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Forest Green Classic",
        "price": 19.99,
        "description": "A timeless forest green design that never goes out of style. Crafted with eco-friendly materials for the environmentally conscious.",
        "quantity": 12,
        "category": "t-shirts",
        "image_url": "/images/placeholder.jpg",
        "images": {
            "thumbnail": "/images/placeholder.jpg",
            "main": "/images/placeholder.jpg",
            "original": "/images/placeholder.jpg"
        },
        "created_at": datetime.now().isoformat()
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Coral Comfort Tee",
        "price": 19.99,
        "description": "Vibrant coral color that brightens any wardrobe. Super soft fabric ensures maximum comfort throughout the day.",
        "quantity": 5,
        "category": "t-shirts",
        "image_url": "/images/placeholder.jpg",
        "images": {
            "thumbnail": "/images/placeholder.jpg",
            "main": "/images/placeholder.jpg",
            "original": "/images/placeholder.jpg"
        },
        "created_at": datetime.now().isoformat()
    }
]

# Load sample products on startup
if not products_db:
    products_db.extend(sample_products)

# Pydantic models
class ProductImages(BaseModel):
    thumbnail: str  # 200x200 square thumbnail
    main: str      # 600x400 main product image
    original: str  # 800x600 original/zoom image

class Product(BaseModel):
    id: int
    title: str
    price: float
    description: str
    quantity: int
    category: str
    image_url: str  # Keep for backward compatibility
    images: ProductImages  # New multi-size images
    created_at: str
    updated_at: Optional[str] = None
    is_active: bool = True

class ProductResponse(BaseModel):
    id: int
    title: str
    price: float
    description: str
    quantity: int
    category: str
    image_url: str  # Keep for backward compatibility
    images: ProductImages  # New multi-size images
    created_at: str
    updated_at: Optional[str] = None
    is_active: bool = True

# Additional models for database operations
class CustomerCreate(BaseModel):
    first_name: str
    last_name: str
    phone_number: Optional[str] = None
    email: str

class CustomerResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    phone_number: Optional[str]
    email: str
    created_at: str

class ShippingAddressCreate(BaseModel):
    customer_id: int
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    country: str
    zip_code: str

class OrderItem(BaseModel):
    product_id: int
    quantity: int
    price: float

class OrderCreate(BaseModel):
    customer_id: int
    shipping_address_id: int
    items: List[OrderItem]
    total_amount: float
    status: Optional[str] = "pending"

class OrderResponse(BaseModel):
    id: int
    customer_id: int
    shipping_address_id: int
    status: str
    total_amount: float
    order_date: str

# Admin authentication
def verify_admin_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify admin token for protected operations"""
    if credentials.credentials != ADMIN_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials

# Helper function to create square thumbnail with proper centering
def create_square_thumbnail(image: Image.Image, size: int) -> Image.Image:
    """Create a square thumbnail by cropping the center of the image"""
    # Calculate the crop box to get the center square
    width, height = image.size
    if width > height:
        # Landscape: crop width
        left = (width - height) // 2
        top = 0
        right = left + height
        bottom = height
    else:
        # Portrait: crop height
        left = 0
        top = (height - width) // 2
        right = width
        bottom = top + width
    
    # Crop to square
    square_image = image.crop((left, top, right, bottom))
    
    # Resize to target size
    square_image = square_image.resize((size, size), Image.Resampling.LANCZOS)
    
    return square_image

# Helper function to resize image maintaining aspect ratio
def resize_with_aspect_ratio(image: Image.Image, target_width: int, target_height: int) -> Image.Image:
    """Resize image to fit within target dimensions while maintaining aspect ratio"""
    # Calculate scaling factor to fit within target dimensions
    scale_w = target_width / image.width
    scale_h = target_height / image.height
    scale = min(scale_w, scale_h)
    
    # Calculate new dimensions
    new_width = int(image.width * scale)
    new_height = int(image.height * scale)
    
    # Resize the image
    resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    return resized_image

# Enhanced function to save uploaded image with multiple sizes
def save_uploaded_image_with_sizes(file: UploadFile) -> dict:
    """Save uploaded image in multiple sizes and return URLs"""
    # Generate unique filename base
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in ["jpg", "jpeg", "png", "gif", "webp"]:
        raise HTTPException(status_code=400, detail="Invalid image format. Supported formats: JPG, JPEG, PNG, GIF, WEBP")
    
    # Use consistent extension
    if file_extension in ["jpg", "jpeg"]:
        file_extension = "jpg"
    
    unique_id = str(uuid.uuid4())
    filename_base = f"{unique_id}.{file_extension}"
    
    # Save original uploaded file temporarily
    temp_path = os.path.join(IMAGES_DIR, f"temp_{filename_base}")
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # Open the image
        with Image.open(temp_path) as img:
            # Convert to RGB if necessary (for JPEG compatibility)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            
            # 1. Create thumbnail (200x200 square)
            thumbnail = create_square_thumbnail(img, 200)
            thumbnail_path = os.path.join(THUMBNAIL_DIR, filename_base)
            thumbnail.save(thumbnail_path, optimize=True, quality=85)
            
            # 2. Create main product image (600x400 max, maintaining aspect ratio)
            main_image = resize_with_aspect_ratio(img, 600, 400)
            main_path = os.path.join(MAIN_DIR, filename_base)
            main_image.save(main_path, optimize=True, quality=90)
            
            # 3. Create original size (800x600 max, maintaining aspect ratio)
            original_image = resize_with_aspect_ratio(img, 800, 600)
            original_path = os.path.join(ORIGINAL_DIR, filename_base)
            original_image.save(original_path, optimize=True, quality=95)
            
            # Return URLs for all sizes
            return {
                "thumbnail": f"/images/thumbnails/{filename_base}",
                "main": f"/images/main/{filename_base}",
                "original": f"/images/original/{filename_base}"
            }
            
    except Exception as e:
        # Clean up any created files on error
        for path in [thumbnail_path, main_path, original_path]:
            if 'path' in locals() and os.path.exists(path):
                os.remove(path)
        raise HTTPException(status_code=400, detail=f"Error processing image: {str(e)}")
    
    finally:
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)

# Legacy function for backward compatibility
def save_uploaded_image(file: UploadFile) -> str:
    """Legacy function - returns main image URL for backward compatibility"""
    image_urls = save_uploaded_image_with_sizes(file)
    return image_urls["main"]

# Helper function to delete image files (all sizes)
def delete_image_files(images: dict):
    """Delete all image files from disk"""
    for size, url in images.items():
        if url.startswith("/images/"):
            filename = url.split("/")[-1]
            # Determine the correct directory based on the URL path
            if "/thumbnails/" in url:
                file_path = os.path.join(THUMBNAIL_DIR, filename)
            elif "/main/" in url:
                file_path = os.path.join(MAIN_DIR, filename)
            elif "/original/" in url:
                file_path = os.path.join(ORIGINAL_DIR, filename)
            else:
                # Legacy support for old single images
                file_path = os.path.join(IMAGES_DIR, filename)
            
            if os.path.exists(file_path):
                os.remove(file_path)

# Legacy function for backward compatibility
def delete_image_file(image_url: str):
    """Legacy function - delete single image file from disk"""
    if image_url.startswith("/images/"):
        filename = image_url.split("/")[-1]
        file_path = os.path.join(IMAGES_DIR, filename)
        if os.path.exists(file_path):
            os.remove(file_path)

# API Endpoints

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Trendyoft E-commerce Backend API",
        "version": "1.0.0",
        "endpoints": {
            "products": "/products/",
            "add_product": "/add-product/ (POST, Admin only)",
            "delete_product": "/delete-product/{product_id} (DELETE, Admin only)"
        }
    }

@app.get("/products/", response_model=List[ProductResponse])
async def get_products():
    """Get all products - Public endpoint for frontend"""
    try:
        products = get_products_from_db()
        # Format products to match expected response
        formatted_products = []
        for product in products:
            formatted_product = {
                **product,
                'image_url': product.get('image_main_url', ''),  # Backward compatibility
                'images': {
                    'thumbnail': product.get('image_thumb_url', ''),
                    'main': product.get('image_main_url', ''),
                    'original': product.get('image_full_url', '')
                },
                'created_at': product['created_at'].isoformat() if product.get('created_at') else '',
                'updated_at': product['updated_at'].isoformat() if product.get('updated_at') else None
            }
            formatted_products.append(formatted_product)
        return formatted_products
    except Exception as e:
        logger.error(f"Error fetching products: {e}")
        raise HTTPException(status_code=500, detail="Error fetching products")

@app.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int):
    """Get a specific product by ID - Public endpoint"""
    try:
        product = get_product_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Format product to match expected response
        formatted_product = {
            **product,
            'image_url': product.get('image_main_url', ''),  # Backward compatibility
            'images': {
                'thumbnail': product.get('image_thumb_url', ''),
                'main': product.get('image_main_url', ''),
                'original': product.get('image_full_url', '')
            },
            'created_at': product['created_at'].isoformat() if product.get('created_at') else '',
            'updated_at': product['updated_at'].isoformat() if product.get('updated_at') else None
        }
        return formatted_product
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching product {product_id}: {e}")
        raise HTTPException(status_code=500, detail="Error fetching product")

@app.post("/add-product/", response_model=ProductResponse)
async def add_product(
    title: str = Form(...),
    price: float = Form(...),
    description: str = Form(...),
    quantity: int = Form(...),
    category: str = Form(...),
    image: UploadFile = File(...),
    token: str = Depends(verify_admin_token)
):
    """Add a new product - Admin only"""
    
    # Validate input
    if price <= 0:
        raise HTTPException(status_code=400, detail="Price must be positive")
    if quantity < 0:
        raise HTTPException(status_code=400, detail="Quantity cannot be negative")
    
    # Save image and generate multiple sizes
    try:
        image_urls = save_uploaded_image_with_sizes(image)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error saving image: {str(e)}")
    
    # Prepare product data for database
    product_data = {
        "title": title,
        "description": description,
        "price": price,
        "quantity": quantity,
        "category": category,
        "image_full_url": image_urls["original"],
        "image_main_url": image_urls["main"],
        "image_thumb_url": image_urls["thumbnail"]
    }
    
    try:
        # Insert product into database
        product_id = insert_product_to_db(product_data)
        
        # Fetch the created product to return
        created_product = get_product_by_id(product_id)
        if not created_product:
            raise HTTPException(status_code=500, detail="Failed to retrieve created product")
        
        # Format response
        formatted_product = {
            **created_product,
            'image_url': created_product.get('image_main_url', ''),  # Backward compatibility
            'images': {
                'thumbnail': created_product.get('image_thumb_url', ''),
                'main': created_product.get('image_main_url', ''),
                'original': created_product.get('image_full_url', '')
            },
            'created_at': created_product['created_at'].isoformat() if created_product.get('created_at') else '',
            'updated_at': created_product['updated_at'].isoformat() if created_product.get('updated_at') else None
        }
        
        return formatted_product
        
    except Exception as e:
        logger.error(f"Error creating product: {e}")
        # Clean up uploaded images on error
        try:
            delete_image_files(image_urls)
        except:
            pass
        raise HTTPException(status_code=500, detail="Error creating product")

@app.put("/update-product/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    title: Optional[str] = Form(None),
    price: Optional[float] = Form(None),
    description: Optional[str] = Form(None),
    quantity: Optional[int] = Form(None),
    category: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    token: str = Depends(verify_admin_token)
):
    """Update an existing product - Admin only"""
    
    # Fetch existing product
    existing_product = get_product_by_id(product_id)
    if not existing_product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Validate input
    if price is not None and price <= 0:
        raise HTTPException(status_code=400, detail="Price must be positive")
    if quantity is not None and quantity < 0:
        raise HTTPException(status_code=400, detail="Quantity cannot be negative")

    # Prepare update data
    update_data = {
        "title": title,
        "description": description,
        "price": price,
        "quantity": quantity,
        "category": category
    }

    # Update image if provided
    if image is not None:
        try:
            # Delete old images (all sizes)
            if "images" in existing_product:
                delete_image_files(existing_product["images"])
            else:
                # Legacy support for old single images
                delete_image_file(existing_product["image_url"])
            
            # Save new image in multiple sizes
            image_urls = save_uploaded_image_with_sizes(image)
            update_data.update({
                "image_full_url": image_urls["original"],
                "image_main_url": image_urls["main"],
                "image_thumb_url": image_urls["thumbnail"]
            })
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error updating image: {str(e)}")
    
    # Update product in database
    try:
        if not update_product_in_db(product_id, {k: v for k, v in update_data.items() if v is not None}):
            raise HTTPException(status_code=500, detail="Failed to update product")

        # Fetch updated product
        updated_product = get_product_by_id(product_id)
        if not updated_product:
            raise HTTPException(status_code=500, detail="Failed to retrieve updated product")

        # Format response
        formatted_product = {
            **updated_product,
            'image_url': updated_product.get('image_main_url', ''),  # Backward compatibility
            'images': {
                'thumbnail': updated_product.get('image_thumb_url', ''),
                'main': updated_product.get('image_main_url', ''),
                'original': updated_product.get('image_full_url', '')
            },
            'created_at': updated_product['created_at'].isoformat() if updated_product.get('created_at') else '',
            'updated_at': updated_product['updated_at'].isoformat() if updated_product.get('updated_at') else None
        }

        return formatted_product
    except Exception as e:
        logger.error(f"Error updating product {product_id}: {e}")
        raise HTTPException(status_code=500, detail="Error updating product")
    
    # Update image if provided
    if image is not None:
        try:
            # Delete old images (all sizes)
            if "images" in product:
                delete_image_files(product["images"])
            else:
                # Legacy support for old single images
                delete_image_file(product["image_url"])
            
            # Save new image in multiple sizes
            image_urls = save_uploaded_image_with_sizes(image)
            product["image_url"] = image_urls["main"]  # Keep for backward compatibility
            product["images"] = image_urls  # New field with multiple sizes
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error updating image: {str(e)}")
    
    return product

@app.delete("/delete-product/{product_id}")
async def delete_product(
    product_id: int,
    token: str = Depends(verify_admin_token)
):
    """Delete a product - Admin only"""
    
    # Delete product from database
    try:
        if not delete_product_from_db(product_id):
            raise HTTPException(status_code=404, detail="Product not found")

        return {"message": f"Product with ID {product_id} deleted successfully"}

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Error deleting product {product_id}: {e}")
        raise HTTPException(status_code=500, detail="Error deleting product")

@app.get("/categories/")
async def get_categories():
    """Get all unique categories with metadata - Public endpoint"""
    try:
        categories = get_categories_from_db()
        
        if not categories:
            return {"categories": []}
        
        total_products = sum(cat['total_products'] for cat in categories)
        
        return {
            "categories": categories,
            "total_categories": len(categories),
            "all_products_count": total_products
        }
    except Exception as e:
        logger.error(f"Error fetching categories: {e}")
        raise HTTPException(status_code=500, detail="Error fetching categories")

@app.get("/products/category/{category}", response_model=List[ProductResponse])
async def get_products_by_category(category: str):
    """Get products by category - Public endpoint"""
    if category.lower() == "all":
        return products_db
    
    filtered_products = [p for p in products_db if p["category"].lower() == category.lower()]
    return filtered_products

@app.get("/filter/")
async def filter_products(
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    in_stock: Optional[bool] = None,
    sort_by: Optional[str] = "created_at",  # created_at, price, title, quantity
    sort_order: Optional[str] = "desc"  # asc, desc
):
    """Advanced product filtering - Public endpoint"""
    filtered_products = products_db.copy()
    
    # Filter by category
    if category and category.lower() != "all":
        filtered_products = [p for p in filtered_products if p["category"].lower() == category.lower()]
    
    # Filter by price range
    if min_price is not None:
        filtered_products = [p for p in filtered_products if p["price"] >= min_price]
    if max_price is not None:
        filtered_products = [p for p in filtered_products if p["price"] <= max_price]
    
    # Filter by stock status
    if in_stock is not None:
        if in_stock:
            filtered_products = [p for p in filtered_products if p["quantity"] > 0]
        else:
            filtered_products = [p for p in filtered_products if p["quantity"] == 0]
    
    # Sort results
    reverse_order = sort_order.lower() == "desc"
    
    if sort_by == "price":
        filtered_products.sort(key=lambda x: x["price"], reverse=reverse_order)
    elif sort_by == "title":
        filtered_products.sort(key=lambda x: x["title"].lower(), reverse=reverse_order)
    elif sort_by == "quantity":
        filtered_products.sort(key=lambda x: x["quantity"], reverse=reverse_order)
    else:  # created_at
        filtered_products.sort(key=lambda x: x["created_at"], reverse=reverse_order)
    
    return {
        "products": filtered_products,
        "total_found": len(filtered_products),
        "filters_applied": {
            "category": category,
            "min_price": min_price,
            "max_price": max_price,
            "in_stock": in_stock,
            "sort_by": sort_by,
            "sort_order": sort_order
        }
    }

@app.get("/search/")
async def search_products(q: str = ""):
    """Search products by title or description - Public endpoint"""
    if not q:
        return products_db
    
    query = q.lower()
    filtered_products = [
        p for p in products_db 
        if query in p["title"].lower() or query in p["description"].lower()
    ]
    return filtered_products

# Optional: Save products to JSON file
def save_products_to_file():
    """Save products to JSON file (optional backup)"""
    with open("products.json", "w") as f:
        json.dump(products_db, f, indent=2)

def load_products_from_file():
    """Load products from JSON file (optional)"""
    try:
        with open("products.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Run the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
