#!/usr/bin/env python3
"""
Test script to place an order via API
"""

import requests
import json

def test_place_order():
    """Test placing an order"""
    
    base_url = "http://127.0.0.1:8000"
    
    print("🧪 Testing Order Placement...")
    print("-" * 50)
    
    # First, let's login to get a token
    print("1️⃣ Logging in...")
    login_data = {
        "email": "shuklahitesh1821@gmail.com",
        "password": "hitu117@"  # You'll need to provide the actual password
    }
    
    try:
        login_response = requests.post(f"{base_url}/login", json=login_data)
        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data['access_token']
            print(f"   ✅ Login successful! Token: {access_token[:20]}...")
        else:
            print(f"   ❌ Login failed: {login_response.status_code} - {login_response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Login error: {str(e)}")
        return False
    
    # Get available products
    print("2️⃣ Getting available products...")
    try:
        products_response = requests.get(f"{base_url}/products/")
        if products_response.status_code == 200:
            products = products_response.json()
            if products:
                print(f"   ✅ Found {len(products)} products")
                # Use the first product for testing
                test_product = products[0]
                print(f"   📦 Using product: {test_product['title']} (ID: {test_product['id']}, Price: ${test_product['price']})")
            else:
                print("   ❌ No products found")
                return False
        else:
            print(f"   ❌ Failed to get products: {products_response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Products error: {str(e)}")
        return False
    
    # Place an order
    print("3️⃣ Placing order...")
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    order_data = {
        "customer_id": 1,  # This will be overridden by the backend
        "shipping_address_id": 1,  # This will be overridden by the backend
        "items": [
            {
                "product_id": test_product['id'],
                "quantity": 2,
                "price": test_product['price']
            }
        ],
        "total_amount": test_product['price'] * 2,
        "status": "pending"
    }
    
    try:
        order_response = requests.post(f"{base_url}/place-order/", json=order_data, headers=headers)
        if order_response.status_code == 200:
            order_result = order_response.json()
            print(f"   ✅ Order placed successfully!")
            print(f"   📋 Order ID: {order_result['id']}")
            print(f"   💰 Total Amount: ${order_result['total_amount']}")
            print(f"   📅 Order Date: {order_result['order_date']}")
            print(f"   📊 Status: {order_result['status']}")
        else:
            print(f"   ❌ Order placement failed: {order_response.status_code}")
            print(f"   📄 Response: {order_response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Order placement error: {str(e)}")
        return False
    
    # Check orders
    print("4️⃣ Checking order history...")
    try:
        orders_response = requests.get(f"{base_url}/my-orders", headers=headers)
        if orders_response.status_code == 200:
            orders_data = orders_response.json()
            if orders_data['orders']:
                print(f"   ✅ Found {orders_data['total_orders']} orders in history")
                for order in orders_data['orders']:
                    print(f"   📦 Order {order['id']}: ${order['total_amount']} - {order['status']}")
            else:
                print("   ❌ No orders found in history")
                return False
        else:
            print(f"   ❌ Failed to get order history: {orders_response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Order history error: {str(e)}")
        return False
    
    print("\n🎉 Order placement test completed successfully!")
    return True

if __name__ == "__main__":
    print("⚠️  Make sure the server is running on http://127.0.0.1:8000")
    print("⚠️  Update the password in the script before running")
    print()
    
    # Uncomment the line below and update the password in the script to run the test
    # test_place_order()
