# detection/anomaly.py
from collections import defaultdict
from datetime import datetime, timedelta
import threading
from config import *

class AnomalyDetector:
    def __init__(self):
        self.history = defaultdict(list)
        self.lock = threading.Lock()

    def record(self, src_ip, size):
        now = datetime.utcnow()
        with self.lock:
            self.history[src_ip].append((now, size))
            cutoff = now - timedelta(minutes=10)
            self.history[src_ip] = [x for x in self.history[src_ip] if x[0] >= cutoff]

    def detect(self, src_ip):
        now = datetime.utcnow()
        window = now - timedelta(seconds=BASE_WINDOW_SECONDS)

        with self.lock:
            events = self.history.get(src_ip, [])
            recent = [e for e in events if e[0] >= window]

        pkts = len(recent)
        bytes_ = sum(e[1] for e in recent)

        rate = pkts / (BASE_WINDOW_SECONDS / 60)

        if rate >= HARDCODED_PACKET_RATE_THRESHOLD:
            return "high", f"High packet rate: {rate:.1f}/min", pkts, bytes_

        return None, None, pkts, bytes_
