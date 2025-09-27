#!/usr/bin/env python3
"""
Test sending email to customer addresses to diagnose delivery issues
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_customer_email_delivery():
    """Test email delivery to customer addresses"""
    from_email = os.getenv('EMAIL_USER')
    email_password = os.getenv('EMAIL_PASS')
    
    print("🧪 Testing Customer Email Delivery")
    print("=" * 50)
    
    if not from_email or not email_password:
        print("❌ EMAIL_USER or EMAIL_PASS not set in .env file")
        return False
    
    print(f"📧 Sending from: {from_email}")
    
    # Test emails from recent orders
    test_customers = [
        {"name": "ben ten", "email": "shuklahitesh1821@gmail.com"},
        {"name": "hitesh shukla", "email": "shuklahitesh1821@gmail.com"},
        {"name": "Boss Sir", "email": "shaikhdanish.sd06@gmail.com"},
    ]
    
    success_count = 0
    
    for customer in test_customers:
        print(f"\n🔄 Testing delivery to {customer['name']} ({customer['email']})...")
        
        # Create test email
        subject = "TrendyOft Order Confirmation Test"
        body = f"""
Dear {customer['name']},

This is a test email from TrendyOft to verify email delivery.

If you receive this email, it means:
✅ Our email system can successfully deliver to your email address
✅ Your email is not being blocked by spam filters
✅ Email notifications should work for your orders

Thank you for testing our system!

Best regards,
TrendyOft Team
        """
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = customer['email']
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        try:
            # Send email
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(from_email, email_password)
            text = msg.as_string()
            server.sendmail(from_email, customer['email'], text)
            server.quit()
            
            print(f"✅ Test email sent successfully to {customer['email']}")
            success_count += 1
            
        except Exception as e:
            print(f"❌ Failed to send test email to {customer['email']}: {e}")
    
    print(f"\n📊 Summary: {success_count}/{len(test_customers)} emails sent successfully")
    
    if success_count == len(test_customers):
        print("\n🎉 All test emails sent successfully!")
        print("💡 If customers are not receiving emails, check:")
        print("   - Their spam/junk folders")
        print("   - Email address validity")
        print("   - Whether they regularly check that email")
    else:
        print(f"\n⚠️ {len(test_customers) - success_count} emails failed to send")
        print("💡 This indicates an email configuration issue")
    
    return success_count == len(test_customers)

def check_email_logs():
    """Check recent email sending attempts"""
    print("\n📋 Email Delivery Analysis")
    print("=" * 50)
    
    print("Recent customer orders that should have received emails:")
    print("- Order #36: ben ten (shuklahitesh1821@gmail.com)")
    print("- Order #35: hitesh shukla (shuklahitesh1821@gmail.com)")  
    print("- Order #34: Boss Sir (shaikhdanish.sd06@gmail.com)")
    
    print("\n🔍 Recommendations:")
    print("1. Contact customers directly to verify they're checking the right email")
    print("2. Ask them to check spam/junk folders")
    print("3. Consider adding email delivery confirmation/tracking")
    print("4. Test with different email providers (Gmail, Yahoo, Outlook)")

if __name__ == "__main__":
    test_customer_email_delivery()
    check_email_logs()
