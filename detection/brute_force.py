# detection/brute_force.py
"""
Brute Force Attack Detection Module

Detects brute force attacks by monitoring:
- Repeated connection attempts to authentication ports
- High frequency of connections from same source
- Pattern of failed authentication attempts
"""

from collections import defaultdict
from datetime import datetime, timedelta
import threading

class BruteForceDetector:
    """
    Detects brute force attacks on common authentication services.
    
    Monitors ports:
    - SSH (22)
    - Telnet (23)
    - FTP (21)
    - RDP (3389)
    - HTTP/HTTPS (80, 443) - web login forms
    - SMTP (25, 587)
    - MySQL (3306)
    - PostgreSQL (5432)
    - MongoDB (27017)
    """
    
    # Authentication service ports
    AUTH_PORTS = {
        21: "FTP",
        22: "SSH",
        23: "Telnet",
        25: "SMTP",
        80: "HTTP",
        443: "HTTPS",
        587: "SMTP",
        3306: "MySQL",
        3389: "RDP",
        5432: "PostgreSQL",
        27017: "MongoDB"
    }
    
    def __init__(self, window_seconds=60, attempt_threshold=10):
        """
        Args:
            window_seconds: Time window to analyze (default 60s)
            attempt_threshold: Number of attempts to trigger alert
        """
        self.window_seconds = window_seconds
        self.attempt_threshold = attempt_threshold
        
        # Track connection attempts: {(src_ip, dst_port): [(timestamp, dst_ip), ...]}
        self.attempts = defaultdict(list)
        self.lock = threading.Lock()
    
    def record_attempt(self, src_ip, dst_ip, dst_port):
        """Record a connection attempt to an authentication port"""
        # Only track known authentication ports
        if dst_port not in self.AUTH_PORTS:
            return
        
        now = datetime.utcnow()
        key = (src_ip, dst_port)
        
        with self.lock:
            self.attempts[key].append((now, dst_ip))
            self._cleanup_old(key, now)
    
    def _cleanup_old(self, key, now):
        """Remove attempts older than the time window"""
        cutoff = now - timedelta(seconds=self.window_seconds)
        
        self.attempts[key] = [
            attempt for attempt in self.attempts[key] if attempt[0] >= cutoff
        ]
        
        # Clean up empty entries
        if not self.attempts[key]:
            del self.attempts[key]
    
    def detect(self, src_ip, dst_port):
        """
        Detect brute force attack from a source IP to a specific port
        
        Returns:
            (severity, reason) if attack detected, else (None, None)
        """
        if dst_port not in self.AUTH_PORTS:
            return None, None
        
        key = (src_ip, dst_port)
        
        with self.lock:
            attempt_count = len(self.attempts.get(key, []))
        
        if attempt_count < self.attempt_threshold:
            return None, None
        
        service = self.AUTH_PORTS[dst_port]
        
        # Determine severity based on attempt count
        if attempt_count > 50:
            severity = "high"
        elif attempt_count > 20:
            severity = "medium"
        else:
            severity = "low"
        
        reason = (
            f"Brute force attack detected on {service} (port {dst_port}): "
            f"{attempt_count} connection attempts in {self.window_seconds}s"
        )
        
        return severity, reason
    
    def get_stats(self, src_ip=None):
        """
        Get statistics for brute force attempts
        
        Args:
            src_ip: If provided, get stats for specific IP, else all IPs
        
        Returns:
            dict with statistics
        """
        with self.lock:
            if src_ip:
                # Stats for specific IP across all ports
                total_attempts = 0
                ports_targeted = []
                
                for (ip, port), attempts in self.attempts.items():
                    if ip == src_ip:
                        total_attempts += len(attempts)
                        ports_targeted.append(port)
                
                return {
                    "src_ip": src_ip,
                    "total_attempts": total_attempts,
                    "ports_targeted": ports_targeted,
                    "services_targeted": [self.AUTH_PORTS[p] for p in ports_targeted]
                }
            else:
                # Overall stats
                total_attempts = sum(len(attempts) for attempts in self.attempts.values())
                unique_ips = len(set(ip for ip, _ in self.attempts.keys()))
                
                return {
                    "total_attempts": total_attempts,
                    "unique_attackers": unique_ips,
                    "active_attacks": len(self.attempts)
                }
    
    def get_top_attackers(self, limit=10):
        """Get top N attacking IPs by attempt count"""
        ip_counts = defaultdict(int)
        
        with self.lock:
            for (src_ip, _), attempts in self.attempts.items():
                ip_counts[src_ip] += len(attempts)
        
        # Sort by count descending
        sorted_ips = sorted(ip_counts.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_ips[:limit]
