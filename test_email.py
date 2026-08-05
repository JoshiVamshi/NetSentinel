# test_email.py
"""
Test script to verify email alert configuration is working properly.
Run this to test if email alerts can be sent successfully.
"""

from alerts.emailer import send_email
from logger_setup import logger

def test_email_alert():
    """Send a test email to verify configuration."""
    subject = "[NetSentinel] Test Email Alert"
    body = """This is a test email from NetSentinel.

If you receive this email, your email alert configuration is working correctly!

Test Details:
- SMTP Server: smtp.gmail.com
- SMTP Port: 587
- Email sent successfully at: {timestamp}

NetSentinel Email Alert System is ACTIVE.
"""
    
    try:
        send_email(subject, body)
        logger.info("Test email sent successfully!")
        print("✓ Test email sent successfully!")
        print("✓ Check your inbox at the configured ALERT_TO address")
        return True
    except Exception as e:
        logger.error(f"Test email failed: {e}")
        print(f"✗ Test email failed: {e}")
        print("\nPlease check:")
        print("1. SMTP credentials in config.py are correct")
        print("2. Gmail app password is valid (not regular password)")
        print("3. ALERT_TO email address is correct")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("NetSentinel Email Alert Test")
    print("=" * 50)
    test_email_alert()
