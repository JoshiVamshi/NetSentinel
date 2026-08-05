# detection/syn_flood.py
"""
SYN Flood Detection Module

Detects SYN flood attacks by tracking incomplete TCP handshakes.
A SYN flood occurs when an attacker sends many SYN packets without
completing the three-way handshake (SYN -> SYN-ACK -> ACK).
"""

from collections import defaultdict
from datetime import datetime, timedelta
import threading

class SYNFloodDetector:
    """
    Detects SYN flood attacks by monitoring:
    1. High ratio of SYN packets without corresponding ACK
    2. Many incomplete connections from same source
    """
    
    def __init__(self, window_seconds=30, syn_threshold=50, ratio_threshold=0.7):
        """
        Args:
            window_seconds: Time window to analyze (default 30s)
            syn_threshold: Minimum SYN count to trigger detection
            ratio_threshold: SYN/(SYN+ACK) ratio threshold (0.7 = 70% incomplete)
        """
        self.window_seconds = window_seconds
        self.syn_threshold = syn_threshold
        self.ratio_threshold = ratio_threshold
        
        # Track SYN and ACK packets per source IP
        self.syn_packets = defaultdict(list)  # {src_ip: [(timestamp, dst_ip, dst_port), ...]}
        self.ack_packets = defaultdict(list)  # {src_ip: [(timestamp, dst_ip, dst_port), ...]}
        
        self.lock = threading.Lock()
    
    def record_syn(self, src_ip, dst_ip, dst_port):
        """Record a SYN packet"""
        now = datetime.utcnow()
        with self.lock:
            self.syn_packets[src_ip].append((now, dst_ip, dst_port))
            self._cleanup_old(src_ip, now)
    
    def record_ack(self, src_ip, dst_ip, dst_port):
        """Record an ACK packet"""
        now = datetime.utcnow()
        with self.lock:
            self.ack_packets[src_ip].append((now, dst_ip, dst_port))
            self._cleanup_old(src_ip, now)
    
    def _cleanup_old(self, src_ip, now):
        """Remove packets older than the time window"""
        cutoff = now - timedelta(seconds=self.window_seconds)
        
        self.syn_packets[src_ip] = [
            p for p in self.syn_packets[src_ip] if p[0] >= cutoff
        ]
        self.ack_packets[src_ip] = [
            p for p in self.ack_packets[src_ip] if p[0] >= cutoff
        ]
        
        # Clean up empty entries
        if not self.syn_packets[src_ip]:
            del self.syn_packets[src_ip]
        if not self.ack_packets[src_ip]:
            del self.ack_packets[src_ip]
    
    def detect(self, src_ip):
        """
        Detect SYN flood from a source IP
        
        Returns:
            (severity, reason) if attack detected, else (None, None)
        """
        with self.lock:
            syn_count = len(self.syn_packets.get(src_ip, []))
            ack_count = len(self.ack_packets.get(src_ip, []))
        
        # Need minimum SYN packets to trigger
        if syn_count < self.syn_threshold:
            return None, None
        
        # Calculate ratio of incomplete handshakes
        total = syn_count + ack_count
        if total == 0:
            return None, None
        
        syn_ratio = syn_count / total
        
        # Detect if ratio exceeds threshold
        if syn_ratio >= self.ratio_threshold:
            severity = "high" if syn_count > 100 else "medium"
            reason = (
                f"SYN flood detected: {syn_count} SYN packets, "
                f"{ack_count} ACK packets in {self.window_seconds}s "
                f"(incomplete ratio: {syn_ratio:.1%})"
            )
            return severity, reason
        
        return None, None
    
    def get_stats(self, src_ip):
        """Get statistics for a source IP"""
        with self.lock:
            syn_count = len(self.syn_packets.get(src_ip, []))
            ack_count = len(self.ack_packets.get(src_ip, []))
        
        return {
            "syn_count": syn_count,
            "ack_count": ack_count,
            "total": syn_count + ack_count,
            "syn_ratio": syn_count / (syn_count + ack_count) if (syn_count + ack_count) > 0 else 0
        }
