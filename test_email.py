import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_email_functionality():
    """Test email sending functionality"""
    from_email = os.getenv('EMAIL_USER')
    email_password = os.getenv('EMAIL_PASS')
    
    print(f"Email User: {from_email}")
    print(f"Email Password: {'*' * len(email_password) if email_password else 'Not set'}")
    
    if not from_email or not email_password:
        print("❌ EMAIL_USER or EMAIL_PASS not set in .env file")
        return False
    
    # Test email content
    subject = "TrendyOft Email Test"
    body = "This is a test email from TrendyOft system."
    to_email = from_email  # Send test email to self
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        print("🔄 Connecting to Gmail SMTP server...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        print("🔄 Starting TLS encryption...")
        
        print("🔄 Attempting login...")
        server.login(from_email, email_password)
        print("✅ Login successful!")
        
        print("🔄 Sending test email...")
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        
        print("✅ Test email sent successfully!")
        print(f"📧 Check {to_email} for the test email")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
        print("💡 Make sure you're using an App Password, not your regular Gmail password")
        print("💡 Enable 2-Factor Authentication and generate an App Password at: https://myaccount.google.com/apppasswords")
        return False
    except Exception as e:
        print(f"❌ Email sending failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing TrendyOft Email Functionality")
    print("=" * 50)
    test_email_functionality()
