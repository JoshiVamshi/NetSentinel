# alerts/telegram_bot.py
"""
Telegram Bot Integration for NetSentinel Alerts

Sends real-time alerts to Telegram channel/group.
"""

import requests
from logger_setup import logger

class TelegramNotifier:
    """Send alerts via Telegram Bot API"""
    
    def __init__(self, bot_token=None, chat_id=None):
        """
        Initialize Telegram notifier
        
        Args:
            bot_token: Telegram Bot API token (get from @BotFather)
            chat_id: Telegram chat ID to send messages to
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.enabled = bool(bot_token and chat_id)
        
        if not self.enabled:
            logger.warning("Telegram notifications disabled: missing bot_token or chat_id")
    
    def send_alert(self, subject, message):
        """
        Send alert message to Telegram
        
        Args:
            subject: Alert subject/title
            message: Alert message body
        """
        if not self.enabled:
            logger.debug("Telegram notification skipped (not configured)")
            return False
        
        # Format message with Markdown
        formatted_message = f"🚨 *{subject}*\n\n{message}"
        
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": formatted_message,
                "parse_mode": "Markdown"
            }
            
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            logger.info("Telegram alert sent successfully")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send Telegram alert: {e}")
            return False
    
    def send_threat_alert(self, detection, flow):
        """
        Send formatted threat alert
        
        Args:
            detection: Detection result dict with attack_type, severity, reason
            flow: Flow object with connection details
        """
        severity_emoji = {
            "high": "🔴",
            "medium": "🟡",
            "low": "🟢"
        }
        
        emoji = severity_emoji.get(detection["severity"], "⚠️")
        
        subject = f"{emoji} NetSentinel Alert - {detection['attack_type']}"
        
        message = f"""*Attack Type:* {detection['attack_type']}
*Severity:* {detection['severity'].upper()}
*Source:* `{flow.src_ip}:{flow.src_port}`
*Destination:* `{flow.dst_ip}:{flow.dst_port}`
*Protocol:* {flow.protocol}
*Packets:* {flow.packet_count}
*Bytes:* {flow.byte_count}
*Duration:* {flow.duration():.1f}s

*Reason:* {detection['reason']}

⚡ Immediate investigation recommended!
"""
        
        return self.send_alert(subject, message)
    
    def send_status(self, stats):
        """
        Send system status update
        
        Args:
            stats: Dictionary with system statistics
        """
        message = f"""📊 *NetSentinel Status*

*Total Alerts:* {stats.get('total_alerts', 0)}
*High Severity:* {stats.get('high', 0)}
*Medium Severity:* {stats.get('medium', 0)}
*Unique Sources:* {stats.get('unique_sources', 0)}

✅ System is monitoring traffic
"""
        
        return self.send_alert("Status Update", message)


# Configuration helper
def get_telegram_config():
    """
    Get Telegram configuration from config.py
    
    Returns:
        TelegramNotifier instance
    """
    try:
        from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
        return TelegramNotifier(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
    except ImportError:
        logger.warning("Telegram config not found in config.py")
        return TelegramNotifier()  # Disabled instance
