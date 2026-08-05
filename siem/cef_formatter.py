# siem/cef_formatter.py
"""
CEF (Common Event Format) Formatter

Formats NetSentinel alerts in CEF format for SIEM platforms like:
- ArcSight
- QRadar
- Splunk
- LogRhythm
"""

from datetime import datetime

class CEFFormatter:
    """
    Format alerts in CEF (Common Event Format)
    
    CEF Format:
    CEF:Version|Device Vendor|Device Product|Device Version|Signature ID|Name|Severity|Extension
    """
    
    VERSION = "0"
    VENDOR = "NetSentinel"
    PRODUCT = "NetSentinel IDS"
    DEVICE_VERSION = "1.0"
    
    # Severity mapping: NetSentinel -> CEF (0-10 scale)
    SEVERITY_MAP = {
        "low": 3,
        "medium": 6,
        "high": 9
    }
    
    @classmethod
    def format_alert(cls, alert_data):
        """
        Format alert in CEF format
        
        Args:
            alert_data: Dict with alert information
        
        Returns:
            CEF formatted string
        """
        # Extract data
        attack_type = alert_data.get("attack_type", "Unknown")
        severity = alert_data.get("severity", "medium")
        src_ip = alert_data.get("src_ip", "0.0.0.0")
        src_port = alert_data.get("src_port", 0)
        dst_ip = alert_data.get("dst_ip", "0.0.0.0")
        dst_port = alert_data.get("dst_port", 0)
        protocol = alert_data.get("protocol", "IP")
        packet_count = alert_data.get("packet_count", 0)
        byte_count = alert_data.get("byte_count", 0)
        reason = alert_data.get("reason", "")
        timestamp = alert_data.get("timestamp", datetime.utcnow().isoformat())
        
        # Map severity
        cef_severity = cls.SEVERITY_MAP.get(severity, 5)
        
        # Signature ID (unique identifier for attack type)
        signature_id = cls._get_signature_id(attack_type)
        
        # Build CEF header
        header = f"CEF:{cls.VERSION}|{cls.VENDOR}|{cls.PRODUCT}|{cls.DEVICE_VERSION}|{signature_id}|{attack_type}|{cef_severity}"
        
        # Build CEF extension (key=value pairs)
        extensions = [
            f"src={src_ip}",
            f"spt={src_port}",
            f"dst={dst_ip}",
            f"dpt={dst_port}",
            f"proto={protocol}",
            f"cnt={packet_count}",
            f"in={byte_count}",
            f"msg={reason}",
            f"rt={timestamp}",
            f"act=detected",
            f"cat=IDS"
        ]
        
        extension = " ".join(extensions)
        
        return f"{header}|{extension}"
    
    @staticmethod
    def _get_signature_id(attack_type):
        """Generate signature ID from attack type"""
        signature_map = {
            "DoS / Flood": "1001",
            "Port Scan": "1002",
            "Beaconing": "1003",
            "Suspicious Port Access": "1004",
            "ICMP Flood": "1005",
            "SYN Flood": "1006",
            "Brute Force": "1007"
        }
        return signature_map.get(attack_type, "9999")


def format_to_cef(flow, detection):
    """
    Helper function to format flow and detection into CEF
    
    Args:
        flow: Flow object
        detection: Detection dict
    
    Returns:
        CEF formatted string
    """
    alert_data = {
        "attack_type": detection["attack_type"],
        "severity": detection["severity"],
        "src_ip": flow.src_ip,
        "src_port": flow.src_port,
        "dst_ip": flow.dst_ip,
        "dst_port": flow.dst_port,
        "protocol": flow.protocol,
        "packet_count": flow.packet_count,
        "byte_count": flow.byte_count,
        "reason": detection["reason"],
        "timestamp": datetime.utcnow().isoformat()
    }
    
    return CEFFormatter.format_alert(alert_data)
