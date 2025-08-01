#!/usr/bin/env python3
"""
Test script to verify order email system with detailed order information
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv
import uuid

# Load environment variables
load_dotenv()

def test_order_confirmation_email():
    """Test detailed order confirmation email"""
    from_email = os.getenv('EMAIL_USER')
    email_password = os.getenv('EMAIL_PASS')
    
    print("🧪 Testing Order Confirmation Email System")
    print("=" * 50)
    
    if not from_email or not email_password:
        print("❌ EMAIL_USER or EMAIL_PASS not set in .env file")
        return False
    
    print(f"📧 Sending from: {from_email}")
    
    # Sample order data for testing
    order_id = 12345
    customer_name = "John Doe"
    customer_email = "shaikhdanish.sd06@gmail.com"  # Your email for testing
    total_amount = 59.97
    
    # Sample order items
    order_items = [
        {"title": "Striped Adventure Tee", "quantity": 2, "price": 19.99},
        {"title": "Mountain Sunset Shirt", "quantity": 1, "price": 19.99}
    ]
    
    # Create order items description
    order_items_description = ""
    for item in order_items:
        order_items_description += f"- {item['title']}: {item['quantity']} x ${item['price']:.2f} each\n"
    
    print("\n🔄 Testing Customer Order Confirmation Email...")
    
    # Customer email content
    customer_subject = "Your TrendyOft Order Confirmation"
    customer_body = f"Thank you for your order!\nYour order has been successfully placed with ID: {order_id}.\n\nHere are your order details:\n{order_items_description}\nTotal Amount: ${total_amount:.2f}\n\nWe will process your order promptly and send you updates."
    
    # Create customer message
    customer_msg = MIMEMultipart()
    customer_msg['From'] = f'TrendyOft <{from_email}>'
    customer_msg['To'] = customer_email
    customer_msg['Subject'] = customer_subject
    customer_msg['Reply-To'] = from_email
    customer_msg['X-Mailer'] = 'TrendyOft Order System'
    customer_msg['Message-ID'] = f'<{uuid.uuid4()}@trendyoft.com>'
    
    # Format customer body
    formatted_customer_body = f"Dear {customer_name},\n\n{customer_body}\n\nBest regards,\nTrendyOft Team\n\n---\nThis is an automated message from TrendyOft. Please check your spam folder if you don't see our emails."
    customer_msg.attach(MIMEText(formatted_customer_body, 'plain'))
    
    try:
        # Send customer email
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, email_password)
        text = customer_msg.as_string()
        server.sendmail(from_email, customer_email, text)
        server.quit()
        
        print(f"✅ Customer confirmation email sent successfully to {customer_email}")
        
    except Exception as e:
        print(f"❌ Failed to send customer email: {e}")
        return False
    
    print("\n🔄 Testing Admin Order Notification Email...")
    
    # Admin email content
    admin_subject = f"New Order Received - ID: {order_id}"
    admin_body = f"You have received a new order with ID: {order_id}.\n\nCustomer Name: {customer_name}\nEmail: {customer_email}\nTotal Amount: ${total_amount:.2f}\n\nOrder Details:\n{order_items_description}"
    
    # Create admin message
    admin_msg = MIMEMultipart()
    admin_msg['From'] = f'TrendyOft <{from_email}>'
    admin_msg['To'] = from_email  # Admin receives at same email
    admin_msg['Subject'] = admin_subject
    admin_msg['Reply-To'] = from_email
    admin_msg['X-Mailer'] = 'TrendyOft Order System'
    admin_msg['Message-ID'] = f'<{uuid.uuid4()}@trendyoft.com>'
    
    # Format admin body
    formatted_admin_body = f"{admin_body}\n\nBest regards,\nTrendyOft Team"
    admin_msg.attach(MIMEText(formatted_admin_body, 'plain'))
    
    try:
        # Send admin email
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, email_password)
        text = admin_msg.as_string()
        server.sendmail(from_email, from_email, text)
        server.quit()
        
        print(f"✅ Admin notification email sent successfully to {from_email}")
        
    except Exception as e:
        print(f"❌ Failed to send admin email: {e}")
        return False
    
    print("\n🎉 Order Email System Test Completed Successfully!")
    print("\n📋 Email Content Summary:")
    print("=" * 30)
    print("CUSTOMER EMAIL INCLUDES:")
    print("✓ Personalized greeting with customer name")
    print("✓ Order ID for tracking")
    print("✓ Detailed list of ordered items with quantities and prices")
    print("✓ Total order amount")
    print("✓ Professional footer with company branding")
    print("✓ Spam folder reminder")
    
    print("\nADMIN EMAIL INCLUDES:")
    print("✓ Order ID for easy reference")
    print("✓ Customer name and email")
    print("✓ Complete order details")
    print("✓ Total order amount")
    print("✓ Professional notification format")
    
    return True

if __name__ == "__main__":
    test_order_confirmation_email()
