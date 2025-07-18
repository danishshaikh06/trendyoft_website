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

# Initialize FastAPI app
app = FastAPI(title="Trendyoft E-commerce Backend", version="1.0.0")

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

# In-memory product storage (you can replace this with a JSON file if needed)
products_db = []

# Initialize with some sample products
'''sample_products = [
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
    products_db.extend(sample_products)'''

# Pydantic models
class ProductImages(BaseModel):
    thumbnail: str  # 200x200 square thumbnail
    main: str      # 600x400 main product image
    original: str  # 800x600 original/zoom image

class Product(BaseModel):
    id: str
    title: str
    price: float
    description: str
    quantity: int
    category: str
    image_url: str  # Keep for backward compatibility
    images: ProductImages  # New multi-size images
    created_at: str

class ProductResponse(BaseModel):
    id: str
    title: str
    price: float
    description: str
    quantity: int
    category: str
    image_url: str  # Keep for backward compatibility
    images: ProductImages  # New multi-size images
    created_at: str

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
    return products_db

@app.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str):
    """Get a specific product by ID - Public endpoint"""
    product = next((p for p in products_db if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

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
    
    # Create new product
    new_product = {
        "id": str(uuid.uuid4()),
        "title": title,
        "price": price,
        "description": description,
        "quantity": quantity,
        "category": category,
        "image_url": image_urls["main"],  # Keep for backward compatibility
        "images": image_urls,  # New field with multiple sizes
        "created_at": datetime.now().isoformat()
    }
    
    # Add to database
    products_db.append(new_product)
    
    return new_product

@app.put("/update-product/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: str,
    title: Optional[str] = Form(None),
    price: Optional[float] = Form(None),
    description: Optional[str] = Form(None),
    quantity: Optional[int] = Form(None),
    category: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    token: str = Depends(verify_admin_token)
):
    """Update an existing product - Admin only"""
    
    # Find product
    product = next((p for p in products_db if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Update fields if provided
    if title is not None:
        product["title"] = title
    if price is not None:
        if price <= 0:
            raise HTTPException(status_code=400, detail="Price must be positive")
        product["price"] = price
    if description is not None:
        product["description"] = description
    if quantity is not None:
        if quantity < 0:
            raise HTTPException(status_code=400, detail="Quantity cannot be negative")
        product["quantity"] = quantity
    if category is not None:
        product["category"] = category
    
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
    product_id: str,
    token: str = Depends(verify_admin_token)
):
    """Delete a product - Admin only"""
    
    # Find product
    product_index = next((i for i, p in enumerate(products_db) if p["id"] == product_id), None)
    if product_index is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get product data before deletion
    product = products_db[product_index]
    
    # Delete image files (all sizes)
    if "images" in product:
        delete_image_files(product["images"])
    else:
        # Legacy support for old single images
        delete_image_file(product["image_url"])
    
    # Remove from database
    products_db.pop(product_index)
    
    return {"message": f"Product '{product['title']}' deleted successfully"}

@app.get("/categories/")
async def get_categories():
    """Get all unique categories with metadata - Public endpoint"""
    if not products_db:
        return {"categories": []}
    
    category_stats = {}
    
    # Count products and calculate stats for each category
    for product in products_db:
        category = product["category"].lower()
        if category not in category_stats:
            category_stats[category] = {
                "name": product["category"],  # Keep original case
                "count": 0,
                "total_products": 0,
                "in_stock": 0,
                "out_of_stock": 0
            }
        
        category_stats[category]["count"] += 1
        category_stats[category]["total_products"] += 1
        
        if product["quantity"] > 0:
            category_stats[category]["in_stock"] += 1
        else:
            category_stats[category]["out_of_stock"] += 1
    
    # Convert to list and sort by product count (most popular first)
    categories_list = list(category_stats.values())
    categories_list.sort(key=lambda x: x["count"], reverse=True)
    
    return {
        "categories": categories_list,
        "total_categories": len(categories_list),
        "all_products_count": len(products_db)
    }

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
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
