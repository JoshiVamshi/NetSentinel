# test_notifications.py
"""
Test all notification channels (Email, Telegram, Slack)
"""

from alerts.notification_manager import get_notification_manager
from logger_setup import logger

def main():
    print("=" * 60)
    print("NetSentinel Notification System Test")
    print("=" * 60)
    print()
    
    # Initialize notification manager
    print("📡 Initializing notification manager...")
    nm = get_notification_manager()
    print()
    
    # Show active channels
    if nm.channels:
        print(f"✅ Active channels: {', '.join(nm.channels)}")
    else:
        print("⚠️  No notification channels configured!")
        print()
        print("To configure notifications, edit config.py:")
        print("  - Email: SMTP_USER, SMTP_PASSWORD, ALERT_TO")
        print("  - Telegram: TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID")
        print("  - Slack: SLACK_WEBHOOK_URL")
        return
    
    print()
    print("🧪 Testing all notification channels...")
    print("-" * 60)
    
    # Test all channels
    results = nm.test_all_channels()
    
    # Display results
    print()
    print("📊 Test Results:")
    print("-" * 60)
    for channel, result in results.items():
        print(f"  {channel.capitalize():12} : {result}")
    
    print()
    print("=" * 60)
    
    # Summary
    success_count = sum(1 for r in results.values() if "✅" in r)
    total_count = len(results)
    
    if success_count == total_count:
        print("🎉 All notification channels are working!")
    elif success_count > 0:
        print(f"⚠️  {success_count}/{total_count} channels working")
    else:
        print("❌ No channels are working - check configuration")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
