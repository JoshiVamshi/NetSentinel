# config.py

INTERFACE = None  # sniff all interfaces (captures real network traffic)

BASE_WINDOW_SECONDS = 60
BASE_MIN_PACKETS_FOR_BASELINE = 20
ANOMALY_MULTIPLIER = 3
HARDCODED_PACKET_RATE_THRESHOLD = 100

PORT_SCAN_WINDOW = 30
PORT_SCAN_THRESHOLD = 15

DB_PATH = "netsentinel.db"

# Email Alert Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "vamshijoshi25@gmail.com"
SMTP_PASSWORD = "tbpv edzc jmmc cpvp"
ALERT_TO = "vamshijoshi450@gmail.com"

# Telegram Bot Configuration (Optional)
# Get bot token from @BotFather on Telegram
# Get chat_id by messaging your bot and visiting: https://api.telegram.org/bot<TOKEN>/getUpdates
TELEGRAM_BOT_TOKEN = None  # Example: "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
TELEGRAM_CHAT_ID = None    # Example: "123456789" or "@channel_name"

# Slack Webhook Configuration (Optional)
# Get webhook URL from: https://api.slack.com/messaging/webhooks
SLACK_WEBHOOK_URL = None   # Example: "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXX"

# SIEM Integration (Optional)
# Syslog server for SIEM platforms (Splunk, ELK, QRadar, etc.)
SYSLOG_HOST = None         # Example: "siem.company.com" or "192.168.1.100"
SYSLOG_PORT = 514          # Standard syslog port
SYSLOG_PROTOCOL = "udp"    # "udp" or "tcp"

FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5000
FLASK_DEBUG = False

