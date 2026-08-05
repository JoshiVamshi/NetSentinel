# detection/portscan.py
from collections import defaultdict
from datetime import datetime, timedelta
from config import PORT_SCAN_WINDOW, PORT_SCAN_THRESHOLD

class PortScanDetector:
    def __init__(self):
        self.ports = defaultdict(list)

    def record(self, src_ip, dst_port):
        self.ports[src_ip].append((datetime.utcnow(), dst_port))

    def detect(self, src_ip):
        now = datetime.utcnow()
        window = now - timedelta(seconds=PORT_SCAN_WINDOW)

        recent = [p for p in self.ports[src_ip] if p[0] >= window]
        unique_ports = {p[1] for p in recent}

        if len(unique_ports) >= PORT_SCAN_THRESHOLD:
            return "medium", f"Port scan: {len(unique_ports)} ports in {PORT_SCAN_WINDOW}s"

        return None, None
