#!/usr/bin/env python3
"""
Comprehensive Test script for Trendyoft E-commerce API with Database Integration
This script tests all API endpoints including database operations
"""

import requests
import json
import io
from PIL import Image
import os
import time

# API Base URL (change if running on different port)
BASE_URL = "http://localhost:8000"

# Admin token for protected operations
ADMIN_TOKEN = "danishshaikh@06"

class APITester:
    def __init__(self):
        self.headers = {"Authorization": f"Bearer {ADMIN_TOKEN}"}
        self.created_product_id = None
        self.test_results = []
    
    def create_test_image(self):
        """Create a test image for upload"""
        img = Image.new('RGB', (200, 200), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        return img_bytes
    
    def log_test(self, test_name, passed, message=""):
        """Log test results"""
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name} {message}")
        self.test_results.append({"test": test_name, "passed": passed, "message": message})
    
    def test_server_connection(self):
        """Test if server is running"""
        print("=== Testing Server Connection ===")
        try:
            response = requests.get(f"{BASE_URL}/", timeout=5)
            if response.status_code == 200:
                info = response.json()
                self.log_test("Server Connection", True, f"- {info.get('message', 'Server running')}")
                return True
            else:
                self.log_test("Server Connection", False, f"- Status code: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            self.log_test("Server Connection", False, f"- Error: {e}")
            return False
    
    def test_get_products(self):
        """Test getting all products from database"""
        print("\n=== Testing Product Retrieval ===")
        try:
            response = requests.get(f"{BASE_URL}/products/")
            if response.status_code == 200:
                products = response.json()
                self.log_test("GET /products/", True, f"- Found {len(products)} products")
                
                # Test product structure
                if products:
                    product = products[0]
                    required_fields = ['id', 'title', 'price', 'description', 'quantity', 'category']
                    missing_fields = [field for field in required_fields if field not in product]
                    if not missing_fields:
                        self.log_test("Product Data Structure", True, "- All required fields present")
                    else:
                        self.log_test("Product Data Structure", False, f"- Missing fields: {missing_fields}")
                return True
            else:
                self.log_test("GET /products/", False, f"- Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("GET /products/", False, f"- Error: {e}")
            return False
    
    def test_add_product(self):
        """Test adding a new product to database"""
        print("\n=== Testing Product Creation ===")
        try:
            # Create test data
            product_data = {
                "title": "Test Product - Database Integration",
                "price": 29.99,
                "description": "A test product for database integration testing",
                "quantity": 15,
                "category": "test-category"
            }
            
            # Create test image
            test_image = self.create_test_image()
            files = {"image": ("test.jpg", test_image, "image/jpeg")}
            
            response = requests.post(
                f"{BASE_URL}/add-product/", 
                data=product_data, 
                files=files, 
                headers=self.headers
            )
            
            if response.status_code == 200:
                created_product = response.json()
                self.created_product_id = created_product['id']
                self.log_test("POST /add-product/", True, f"- Created product ID: {self.created_product_id}")
                
                # Verify product data
                if created_product['title'] == product_data['title']:
                    self.log_test("Product Data Integrity", True, "- Data saved correctly")
                else:
                    self.log_test("Product Data Integrity", False, "- Data mismatch")
                
                return True
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.headers.get('content-type') == 'application/json' else response.text
                self.log_test("POST /add-product/", False, f"- Status: {response.status_code}, Error: {error_detail}")
                return False
        except Exception as e:
            self.log_test("POST /add-product/", False, f"- Error: {e}")
            return False
    
    def test_get_product_by_id(self):
        """Test getting a specific product by ID"""
        print("\n=== Testing Product Retrieval by ID ===")
        if not self.created_product_id:
            self.log_test("GET /products/{id}", False, "- No product ID available")
            return False
        
        try:
            response = requests.get(f"{BASE_URL}/products/{self.created_product_id}")
            if response.status_code == 200:
                product = response.json()
                if product['id'] == self.created_product_id:
                    self.log_test("GET /products/{id}", True, f"- Retrieved product: {product['title']}")
                    return True
                else:
                    self.log_test("GET /products/{id}", False, "- ID mismatch")
                    return False
            else:
                self.log_test("GET /products/{id}", False, f"- Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("GET /products/{id}", False, f"- Error: {e}")
            return False
    
    def test_update_product(self):
        """Test updating a product in database"""
        print("\n=== Testing Product Update ===")
        if not self.created_product_id:
            self.log_test("PUT /update-product/{id}", False, "- No product ID available")
            return False
        
        try:
            update_data = {
                "title": "Updated Test Product - Database Integration",
                "price": 39.99,
                "quantity": 20
            }
            
            response = requests.put(
                f"{BASE_URL}/update-product/{self.created_product_id}",
                data=update_data,
                headers=self.headers
            )
            
            if response.status_code == 200:
                updated_product = response.json()
                if updated_product['title'] == update_data['title'] and updated_product['price'] == update_data['price']:
                    self.log_test("PUT /update-product/{id}", True, "- Product updated successfully")
                    return True
                else:
                    self.log_test("PUT /update-product/{id}", False, "- Update data mismatch")
                    return False
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.headers.get('content-type') == 'application/json' else response.text
                self.log_test("PUT /update-product/{id}", False, f"- Status: {response.status_code}, Error: {error_detail}")
                return False
        except Exception as e:
            self.log_test("PUT /update-product/{id}", False, f"- Error: {e}")
            return False
    
    def test_get_categories(self):
        """Test getting categories from database"""
        print("\n=== Testing Categories Retrieval ===")
        try:
            response = requests.get(f"{BASE_URL}/categories/")
            if response.status_code == 200:
                categories_data = response.json()
                categories = categories_data.get('categories', [])
                self.log_test("GET /categories/", True, f"- Found {len(categories)} categories")
                
                # Check if our test category is there
                test_category_found = any(cat['name'] == 'test-category' for cat in categories)
                if test_category_found:
                    self.log_test("Category Data Integrity", True, "- Test category found in database")
                else:
                    self.log_test("Category Data Integrity", False, "- Test category not found")
                
                return True
            else:
                self.log_test("GET /categories/", False, f"- Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("GET /categories/", False, f"- Error: {e}")
            return False
    
    def test_delete_product(self):
        """Test deleting a product from database (soft delete)"""
        print("\n=== Testing Product Deletion ===")
        if not self.created_product_id:
            self.log_test("DELETE /delete-product/{id}", False, "- No product ID available")
            return False
        
        try:
            response = requests.delete(
                f"{BASE_URL}/delete-product/{self.created_product_id}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                self.log_test("DELETE /delete-product/{id}", True, "- Product deleted successfully")
                
                # Verify product is no longer accessible
                time.sleep(1)  # Give database a moment to process
                get_response = requests.get(f"{BASE_URL}/products/{self.created_product_id}")
                if get_response.status_code == 404:
                    self.log_test("Soft Delete Verification", True, "- Product no longer accessible")
                else:
                    self.log_test("Soft Delete Verification", False, "- Product still accessible after deletion")
                
                return True
            else:
                error_detail = response.json().get('detail', 'Unknown error') if response.headers.get('content-type') == 'application/json' else response.text
                self.log_test("DELETE /delete-product/{id}", False, f"- Status: {response.status_code}, Error: {error_detail}")
                return False
        except Exception as e:
            self.log_test("DELETE /delete-product/{id}", False, f"- Error: {e}")
            return False
    
    def test_database_error_handling(self):
        """Test error handling for database operations"""
        print("\n=== Testing Error Handling ===")
        
        # Test getting non-existent product
        try:
            response = requests.get(f"{BASE_URL}/products/99999")
            if response.status_code == 404:
                self.log_test("Non-existent Product Handling", True, "- 404 returned for non-existent product")
            else:
                self.log_test("Non-existent Product Handling", False, f"- Unexpected status: {response.status_code}")
        except Exception as e:
            self.log_test("Non-existent Product Handling", False, f"- Error: {e}")
        
        # Test invalid admin token
        try:
            bad_headers = {"Authorization": "Bearer invalid-token"}
            response = requests.post(
                f"{BASE_URL}/add-product/",
                data={"title": "test", "price": 10, "description": "test", "quantity": 1, "category": "test"},
                headers=bad_headers
            )
            if response.status_code == 401:
                self.log_test("Invalid Token Handling", True, "- 401 returned for invalid token")
            else:
                self.log_test("Invalid Token Handling", False, f"- Unexpected status: {response.status_code}")
        except Exception as e:
            self.log_test("Invalid Token Handling", False, f"- Error: {e}")
    
    def run_all_tests(self):
        """Run all tests"""
        print("Trendyoft E-commerce API Database Integration Test")
        print("=" * 60)
        
        # Check server connection first
        if not self.test_server_connection():
            print("\n❌ Server is not running. Please start the server with: python main.py")
            return
        
        # Run all tests
        self.test_get_products()
        self.test_add_product()
        self.test_get_product_by_id()
        self.test_update_product()
        self.test_get_categories()
        self.test_delete_product()
        self.test_database_error_handling()
        
        # Print summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['passed'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\nFailed Tests:")
            for result in self.test_results:
                if not result['passed']:
                    print(f"  ❌ {result['test']}: {result['message']}")
        
        print("\n" + "=" * 60)
        if failed_tests == 0:
            print("🎉 All tests passed! Your database integration is working correctly.")
        else:
            print("⚠️  Some tests failed. Please check the database connection and API implementation.")
        
        print("\nTo start the server: python main.py")
        print("API Documentation: http://localhost:8000/docs")

def main():
    """Main function"""
    tester = APITester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()
