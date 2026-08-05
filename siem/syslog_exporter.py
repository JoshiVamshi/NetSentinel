# siem/syslog_exporter.py
"""
Syslog Exporter for SIEM Integration

Sends NetSentinel alerts to remote syslog servers (RFC 5424).
Compatible with most SIEM platforms.
"""

import socket
import logging
from datetime import datetime
from siem.cef_formatter import format_to_cef

class SyslogExporter:
    """
    Export alerts to remote syslog server
    
    Supports:
    - UDP (default, port 514)
    - TCP (port 514 or 601)
    - RFC 5424 format
    """
    
    # Syslog severity levels
    SEVERITY_MAP = {
        "low": 5,      # Notice
        "medium": 4,   # Warning
        "high": 2      # Critical
    }
    
    # Syslog facility (16 = local use 0)
    FACILITY = 16
    
    def __init__(self, host, port=514, protocol="udp"):
        """
        Initialize syslog exporter
        
        Args:
            host: Syslog server hostname/IP
            port: Syslog server port (default 514)
            protocol: 'udp' or 'tcp'
        """
        self.host = host
        self.port = port
        self.protocol = protocol.lower()
        self.logger = logging.getLogger("SyslogExporter")
    
    def send_alert(self, flow, detection):
        """
        Send alert to syslog server
        
        Args:
            flow: Flow object
            detection: Detection dict
        """
        try:
            # Format message in CEF
            cef_message = format_to_cef(flow, detection)
            
            # Build syslog message (RFC 5424)
            syslog_message = self._build_syslog_message(detection["severity"], cef_message)
            
            # Send via UDP or TCP
            if self.protocol == "udp":
                self._send_udp(syslog_message)
            else:
                self._send_tcp(syslog_message)
            
            self.logger.info(f"Alert sent to syslog server {self.host}:{self.port}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send syslog: {e}")
            return False
    
    def _build_syslog_message(self, severity, message):
        """
        Build RFC 5424 syslog message
        
        Format: <PRI>VERSION TIMESTAMP HOSTNAME APP-NAME PROCID MSGID SD MSG
        """
        # Calculate priority: (Facility * 8) + Severity
        syslog_severity = self.SEVERITY_MAP.get(severity, 5)
        priority = (self.FACILITY * 8) + syslog_severity
        
        # RFC 5424 format
        version = 1
        timestamp = datetime.utcnow().isoformat() + "Z"
        hostname = socket.gethostname()
        app_name = "NetSentinel"
        procid = "-"
        msgid = "-"
        structured_data = "-"
        
        syslog_msg = (
            f"<{priority}>{version} {timestamp} {hostname} "
            f"{app_name} {procid} {msgid} {structured_data} {message}"
        )
        
        return syslog_msg
    
    def _send_udp(self, message):
        """Send message via UDP"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.sendto(message.encode('utf-8'), (self.host, self.port))
        finally:
            sock.close()
    
    def _send_tcp(self, message):
        """Send message via TCP"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((self.host, self.port))
            # Add newline for TCP framing
            sock.sendall((message + "\n").encode('utf-8'))
        finally:
            sock.close()


# Configuration helper
def get_syslog_exporter():
    """Get syslog exporter from config"""
    try:
        from config import SYSLOG_HOST, SYSLOG_PORT, SYSLOG_PROTOCOL
        if SYSLOG_HOST:
            return SyslogExporter(SYSLOG_HOST, SYSLOG_PORT, SYSLOG_PROTOCOL)
    except ImportError:
        pass
    return None
