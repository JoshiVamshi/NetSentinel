# alerts/notification_manager.py
"""
Unified Notification Manager

Manages all notification channels (Email, Telegram, Slack) from a single interface.
"""

from logger_setup import logger

class NotificationManager:
    """
    Centralized notification system that sends alerts through multiple channels.
    """
    
    def __init__(self):
        """Initialize all notification channels"""
        self.channels = []
        
        # Initialize Email
        try:
            from alerts.emailer import send_email
            self.email_sender = send_email
            self.channels.append("email")
            logger.info("Email notifications enabled")
        except Exception as e:
            logger.warning(f"Email notifications disabled: {e}")
            self.email_sender = None
        
        # Initialize Telegram
        try:
            from alerts.telegram_bot import get_telegram_config
            self.telegram = get_telegram_config()
            if self.telegram.enabled:
                self.channels.append("telegram")
                logger.info("Telegram notifications enabled")
        except Exception as e:
            logger.warning(f"Telegram notifications disabled: {e}")
            self.telegram = None
        
        # Initialize Slack
        try:
            from alerts.slack_notifier import get_slack_config
            self.slack = get_slack_config()
            if self.slack.enabled:
                self.channels.append("slack")
                logger.info("Slack notifications enabled")
        except Exception as e:
            logger.warning(f"Slack notifications disabled: {e}")
            self.slack = None
        
        if not self.channels:
            logger.warning("⚠️  No notification channels enabled!")
        else:
            logger.info(f"✅ Active notification channels: {', '.join(self.channels)}")
    
    def send_threat_alert(self, detection, flow):
        """
        Send threat alert through all enabled channels
        
        Args:
            detection: Detection result dict
            flow: Flow object with connection details
        """
        success_count = 0
        
        # Send via Email
        if self.email_sender:
            try:
                subject = f"[NetSentinel] {detection['severity'].upper()} - {detection['attack_type']}"
                body = self._format_email_body(detection, flow)
                self.email_sender(subject, body)
                success_count += 1
            except Exception as e:
                logger.error(f"Email notification failed: {e}")
        
        # Send via Telegram
        if self.telegram and self.telegram.enabled:
            try:
                self.telegram.send_threat_alert(detection, flow)
                success_count += 1
            except Exception as e:
                logger.error(f"Telegram notification failed: {e}")
        
        # Send via Slack
        if self.slack and self.slack.enabled:
            try:
                self.slack.send_threat_alert(detection, flow)
                success_count += 1
            except Exception as e:
                logger.error(f"Slack notification failed: {e}")
        
        logger.info(f"Alert sent through {success_count}/{len(self.channels)} channels")
        return success_count > 0
    
    def send_status_update(self, stats):
        """
        Send system status update through all channels
        
        Args:
            stats: Dictionary with system statistics
        """
        # Send via Telegram
        if self.telegram and self.telegram.enabled:
            try:
                self.telegram.send_status(stats)
            except Exception as e:
                logger.error(f"Telegram status update failed: {e}")
        
        # Send via Slack
        if self.slack and self.slack.enabled:
            try:
                self.slack.send_status(stats)
            except Exception as e:
                logger.error(f"Slack status update failed: {e}")
    
    def _format_email_body(self, detection, flow):
        """Format email body for threat alerts"""
        return f"""NetSentinel has detected suspicious network activity.

Attack Type: {detection['attack_type']}
Severity: {detection['severity'].upper()}
Source: {flow.src_ip}:{flow.src_port}
Destination: {flow.dst_ip}:{flow.dst_port}
Protocol: {flow.protocol}
Packet Count: {flow.packet_count}
Byte Count: {flow.byte_count}
Duration: {flow.duration():.1f} seconds
Reason: {detection['reason']}

Please investigate this activity immediately.

---
NetSentinel Intrusion Detection System
"""
    
    def test_all_channels(self):
        """
        Send test message to all channels
        
        Returns:
            dict with test results for each channel
        """
        results = {}
        
        # Test Email
        if self.email_sender:
            try:
                self.email_sender(
                    "[NetSentinel] Test Alert",
                    "This is a test message from NetSentinel notification system."
                )
                results["email"] = "✅ Success"
            except Exception as e:
                results["email"] = f"❌ Failed: {e}"
        else:
            results["email"] = "⚠️  Not configured"
        
        # Test Telegram
        if self.telegram and self.telegram.enabled:
            try:
                self.telegram.send_alert(
                    "Test Alert",
                    "This is a test message from NetSentinel."
                )
                results["telegram"] = "✅ Success"
            except Exception as e:
                results["telegram"] = f"❌ Failed: {e}"
        else:
            results["telegram"] = "⚠️  Not configured"
        
        # Test Slack
        if self.slack and self.slack.enabled:
            try:
                self.slack.send_alert(
                    "Test Alert",
                    "This is a test message from NetSentinel.",
                    severity="low"
                )
                results["slack"] = "✅ Success"
            except Exception as e:
                results["slack"] = f"❌ Failed: {e}"
        else:
            results["slack"] = "⚠️  Not configured"
        
        return results


# Global notification manager instance
_notification_manager = None

def get_notification_manager():
    """Get or create global notification manager instance"""
    global _notification_manager
    if _notification_manager is None:
        _notification_manager = NotificationManager()
    return _notification_manager
