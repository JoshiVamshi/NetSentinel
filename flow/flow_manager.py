# flow/flow_manager.py

from collections import defaultdict
from datetime import datetime, timedelta
import threading

FLOW_TIMEOUT_SECONDS = 10
  # inactivity timeout


class Flow:
    def __init__(self, src, dst, sport, dport, proto):
        self.src_ip = src
        self.dst_ip = dst
        self.src_port = sport
        self.dst_port = dport
        self.protocol = proto

        self.packet_count = 0
        self.byte_count = 0

        self.start_time = datetime.utcnow()
        self.last_seen = self.start_time

    def update(self, pkt_size):
        self.packet_count += 1
        self.byte_count += pkt_size
        self.last_seen = datetime.utcnow()

    def duration(self):
        return (self.last_seen - self.start_time).total_seconds()

    def to_dict(self):
        return {
            "src_ip": self.src_ip,
            "dst_ip": self.dst_ip,
            "src_port": self.src_port,
            "dst_port": self.dst_port,
            "protocol": self.protocol,
            "packets": self.packet_count,
            "bytes": self.byte_count,
            "duration": self.duration(),
            "first_seen": self.start_time,
            "last_seen": self.last_seen,
        }


class FlowManager:
    """
    Maintains active network flows and expires them
    after inactivity.
    """

    def __init__(self):
        self.flows = {}
        self.lock = threading.Lock()

    def _flow_key(self, src, dst, sport, dport, proto):
        return (src, dst, sport, dport, proto)

    def process_packet(self, src, dst, sport, dport, proto, pkt_size):
        now = datetime.utcnow()
        key = self._flow_key(src, dst, sport, dport, proto)

        with self.lock:
            if key not in self.flows:
                self.flows[key] = Flow(src, dst, sport, dport, proto)

            self.flows[key].update(pkt_size)

        return None

    def expire_flows(self):
        """
        Returns expired flows for analysis.
        """
        expired = []
        now = datetime.utcnow()

        with self.lock:
            for key in list(self.flows.keys()):
                flow = self.flows[key]
                if (now - flow.last_seen).total_seconds() > FLOW_TIMEOUT_SECONDS:
                    expired.append(flow)
                    del self.flows[key]

        return expired
