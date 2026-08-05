from detection.portscan import PortScanDetector
from detection.ai_anomaly import AIAnomalyDetector

class DetectionEngine:
    """
    Analyzes expired flows and decides
    whether they are suspicious.
    Supports multiple attack detection types.
    """
    
    def __init__(self):
        self.port_scan_detector = PortScanDetector()
        self.ai_detector = AIAnomalyDetector()

    def analyze_flow(self, flow):
        print(
        f"[DEBUG] analyze_flow called | "
        f"proto={flow.protocol} pkts={flow.packet_count} "
        f"bytes={flow.byte_count} duration={flow.duration():.1f}s"
        )
        """
        Returns:
        - None if flow is normal
        - dict with attack details if suspicious
        """

        signals = []

        # -------- Port Scan Detection --------
        if flow.protocol == "TCP":
            self.port_scan_detector.record(flow.src_ip, flow.dst_port)
            port_scan_result = self.port_scan_detector.detect(flow.src_ip)
            if port_scan_result[0]:  # severity
                signals.append({
                    "type": "Port Scan",
                    "severity": port_scan_result[0],
                    "reason": port_scan_result[1]
                })

        # -------- ICMP Flood Detection --------
        if flow.protocol == "IP" and flow.packet_count > 10:
            signals.append({
                "type": "ICMP Flood",
                "severity": "medium",
                "reason": f"ICMP packet burst detected ({flow.packet_count} packets)"
            })

        # -------- Rule 1: High packet volume (DoS-like behavior) --------
        if flow.packet_count > 20:
            signals.append({
                "type": "DoS / Flood",
                "severity": "high",
                "reason": f"High packet count ({flow.packet_count}) in single flow"
            })

        # -------- Rule 2: Long-lived connection with very low data (beaconing) --------
        if flow.duration() > 60 and flow.byte_count < 1000:
            signals.append({
                "type": "Beaconing",
                "severity": "medium",
                "reason": "Long-lived low-volume connection (possible C2 beacon)"
            })

        # -------- Rule 3: Suspicious destination ports --------
        suspicious_ports = {22, 23, 3389, 445}
        if flow.dst_port in suspicious_ports and flow.packet_count > 20:
            signals.append({
                "type": "Suspicious Port Access",
                "severity": "medium",
                "reason": f"Repeated traffic to sensitive port {flow.dst_port}"
            })

        # -------- AI / Anomaly Detection --------
        ai_signal = self.ai_detector.analyze(flow)
        if ai_signal:
            signals.append(ai_signal)

        if not signals:
            return None

        # Pick the highest severity signal
        severity_order = {"high": 3, "medium": 2, "low": 1}
        top_signal = max(signals, key=lambda s: severity_order[s["severity"]])

        return {
            "attack_type": top_signal["type"],
            "severity": top_signal["severity"],
            "reason": top_signal["reason"]
        }

