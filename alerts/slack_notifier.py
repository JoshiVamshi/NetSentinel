# alerts/slack_notifier.py
"""
Slack Integration for NetSentinel Alerts

Sends real-time alerts to Slack channel via webhooks.
"""

import requests
import json
from logger_setup import logger

class SlackNotifier:
    """Send alerts to Slack via Incoming Webhooks"""
    
    def __init__(self, webhook_url=None):
        """
        Initialize Slack notifier
        
        Args:
            webhook_url: Slack Incoming Webhook URL
                        Get from: https://api.slack.com/messaging/webhooks
        """
        self.webhook_url = webhook_url
        self.enabled = bool(webhook_url)
        
        if not self.enabled:
            logger.warning("Slack notifications disabled: missing webhook_url")
    
    def send_alert(self, subject, message, severity="medium"):
        """
        Send alert message to Slack
        
        Args:
            subject: Alert subject/title
            message: Alert message body
            severity: Alert severity (high/medium/low)
        """
        if not self.enabled:
            logger.debug("Slack notification skipped (not configured)")
            return False
        
        # Color coding by severity
        colors = {
            "high": "#dc2626",      # Red
            "medium": "#f59e0b",    # Orange
            "low": "#10b981"        # Green
        }
        color = colors.get(severity, "#6b7280")  # Gray default
        
        # Slack message payload with rich formatting
        payload = {
            "attachments": [
                {
                    "color": color,
                    "title": f"🚨 {subject}",
                    "text": message,
                    "footer": "NetSentinel IDS",
                    "footer_icon": "https://platform.slack-edge.com/img/default_application_icon.png",
                    "ts": int(datetime.utcnow().timestamp())
                }
            ]
        }
        
        try:
            response = requests.post(
                self.webhook_url,
                data=json.dumps(payload),
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            response.raise_for_status()
            
            logger.info("Slack alert sent successfully")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send Slack alert: {e}")
            return False
    
    def send_threat_alert(self, detection, flow):
        """
        Send formatted threat alert
        
        Args:
            detection: Detection result dict with attack_type, severity, reason
            flow: Flow object with connection details
        """
        subject = f"Security Alert - {detection['attack_type']}"
        
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
        
        return self.send_alert(subject, message, detection['severity'])
    
    def send_status(self, stats):
        """
        Send system status update
        
        Args:
            stats: Dictionary with system statistics
        """
        subject = "NetSentinel Status Update"
        
        message = f"""*Total Alerts:* {stats.get('total_alerts', 0)}
*High Severity:* {stats.get('high', 0)}
*Medium Severity:* {stats.get('medium', 0)}
*Unique Sources:* {stats.get('unique_sources', 0)}

✅ System is monitoring traffic
"""
        
        return self.send_alert(subject, message, severity="low")
    
    def send_blocks_message(self, blocks):
        """
        Send advanced message using Slack Block Kit
        
        Args:
            blocks: List of Slack block elements
        """
        if not self.enabled:
            return False
        
        payload = {"blocks": blocks}
        
        try:
            response = requests.post(
                self.webhook_url,
                data=json.dumps(payload),
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send Slack blocks message: {e}")
            return False


# Configuration helper
def get_slack_config():
    """
    Get Slack configuration from config.py
    
    Returns:
        SlackNotifier instance
    """
    try:
        from config import SLACK_WEBHOOK_URL
        return SlackNotifier(SLACK_WEBHOOK_URL)
    except ImportError:
        logger.warning("Slack config not found in config.py")
        return SlackNotifier()  # Disabled instance


# Fix import
from datetime import datetime
