# capture/sniffer.py
from scapy.all import sniff, IP, TCP, UDP
import threading
import time
from detection.engine import DetectionEngine
from storage.database import insert_alert

from logger_setup import logger
from config import INTERFACE

from flow.flow_manager import FlowManager

# Initialize Flow Manager (Stage-2)
flow_manager = FlowManager()


def process_packet(pkt):
    if not pkt.haslayer(IP):
        return

    ip = pkt[IP]
    src_ip = ip.src
    dst_ip = ip.dst
    pkt_size = len(pkt)

    protocol = "IP"
    src_port = 0
    dst_port = 0

    if pkt.haslayer(TCP):
        protocol = "TCP"
        src_port = pkt[TCP].sport
        dst_port = pkt[TCP].dport
    elif pkt.haslayer(UDP):
        protocol = "UDP"
        src_port = pkt[UDP].sport
        dst_port = pkt[UDP].dport

    # Feed packet into Flow Manager
    flow_manager.process_packet(
        src=src_ip,
        dst=dst_ip,
        sport=src_port,
        dport=dst_port,
        proto=protocol,
        pkt_size=pkt_size
    )

    # Expire flows periodically
#expired_flows = flow_manager.expire_flows()

from detection.engine import DetectionEngine
from storage.database import insert_alert
from alerts.notification_manager import get_notification_manager

engine = DetectionEngine()
notification_manager = get_notification_manager()

def flow_expiry_worker():
    while True:
        time.sleep(2)  # check every 2 seconds
        expired_flows = flow_manager.expire_flows()

        for flow in expired_flows:
            detection = engine.analyze_flow(flow)
            if detection:
                insert_alert(flow, detection)
                logger.warning(
                    "ALERT | %s | %s:%s → %s:%s | %s | %s",
                    detection["attack_type"],
                    flow.src_ip,
                    flow.src_port,
                    flow.dst_ip,
                    flow.dst_port,
                    detection["severity"].upper(),
                    detection["reason"]
                )
                
                # Send alert through all configured channels (Email, Telegram, Slack)
                notification_manager.send_threat_alert(detection, flow)




def start_sniffer():
    threading.Thread(
        target=flow_expiry_worker,
        daemon=True
    ).start()
    logger.info("Starting packet sniffer (Stage-2 Flow Mode)")
    sniff(
        iface=INTERFACE,
        prn=process_packet,
        store=False
    )
