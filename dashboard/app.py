import os
import threading
import time
import logging
import sqlite3
from datetime import datetime, timedelta
from collections import defaultdict
from flask import Flask, render_template_string, request
from scapy.all import sniff, IP, TCP, UDP

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ============================
# CONFIGURATION
# ============================

# Network interface to sniff on (e.g. "eth0", "wlan0", or None for all)
INTERFACE = None  # None = default / all

# Alert thresholds (very simple baseline logic)
BASE_WINDOW_SECONDS = 60
BASE_MIN_PACKETS_FOR_BASELINE = 20
ANOMALY_MULTIPLIER = 3  # if current rate > baseline * this => anomaly
HARDCODED_PACKET_RATE_THRESHOLD = 100  # packets/min above this => anomaly anyway

# SQLite DB file
DB_PATH = "netsentinel.db"

# Email alert configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "vamshijoshi25@gmail.com"       # TODO: change this
SMTP_PASSWORD = "tbpv edzc jmmc cpvp"         # TODO: app password, not real password
ALERT_TO = "vamshijoshi450@gmail.com"     # TODO: change this

# Flask configuration
FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5000
FLASK_DEBUG = False

# ============================
# LOGGING
# ============================

if not os.path.exists("logs"):
    os.makedirs("logs")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/netsentinel.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("NetSentinel")

# ============================
# DATABASE SETUP (SQLite)
# ============================

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
      SELECT timestamp,
      src_ip, src_port,
      dst_ip, dst_port,
      protocol, attack_type,
      severity,packet_count, byte_count, duration, reason
FROM alerts
ORDER BY id DESC
LIMIT 200
""")
    conn.commit()
    conn.close()
    logger.info("SQLite database initialized at %s", DB_PATH)


def insert_alert(src_ip, dst_ip, protocol, packet_count, bytes_count, severity, reason):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO alerts (timestamp, src_ip, dst_ip, protocol, packet_count, bytes_count, severity, reason)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            datetime.utcnow().isoformat(),
            src_ip,
            dst_ip,
            protocol,
            packet_count,
            bytes_count,
            severity,
            reason
        )
    )
    conn.commit()
    conn.close()
    logger.warning("Alert stored in DB: %s | %s", severity, reason)

# ============================
# EMAIL ALERTING
# ============================

def send_email_alert(subject: str, message: str):
    """Send email alert using SMTP."""
    msg = MIMEMultipart()
    msg["From"] = SMTP_USER
    msg["To"] = ALERT_TO
    msg["Subject"] = subject
    msg.attach(MIMEText(message, "plain"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        logger.info("Alert email sent to %s", ALERT_TO)
    except Exception as e:
        logger.error("Failed to send email alert: %s", e)

# ============================
# ANOMALY DETECTION LOGIC
# ============================

class AnomalyDetector:
    """
    Very lightweight "statistical baseline":
    - Keeps track of packet counts per source IP in time windows.
    - Computes simple average packets/min for each IP.
    - Flags if current rate >> baseline or exceeds fixed thresholds.
    """

    def __init__(self):
        # For each src_ip: list of (timestamp, packet_len)
        self.history = defaultdict(list)
        self.lock = threading.Lock()

    def _cleanup_old(self, now):
        """Remove very old entries to avoid memory growth."""
        cutoff = now - timedelta(minutes=10)  # keep last 10 minutes
        for src_ip in list(self.history.keys()):
            self.history[src_ip] = [
                (ts, size) for (ts, size) in self.history[src_ip] if ts >= cutoff
            ]
            if not self.history[src_ip]:
                del self.history[src_ip]

    def record_packet(self, src_ip, packet_len):
        now = datetime.utcnow()
        with self.lock:
            self.history[src_ip].append((now, packet_len))
            self._cleanup_old(now)

    def check_anomaly(self, src_ip):
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=BASE_WINDOW_SECONDS)

        with self.lock:
            events = self.history.get(src_ip, [])
            # Current window packets and bytes
            window_packets = [e for e in events if e[0] >= window_start]
            packet_count = len(window_packets)
            bytes_count = sum(size for (_, size) in window_packets)

            # Historical baseline: use all except current window
            baseline_events = [e for e in events if e[0] < window_start]
            baseline_packet_count = len(baseline_events)

        if packet_count == 0:
            return None, packet_count, bytes_count

        # Compute packets/min in current window
        window_minutes = BASE_WINDOW_SECONDS / 60.0
        current_rate = packet_count / window_minutes

        # Compute baseline packets/min
        if baseline_packet_count >= BASE_MIN_PACKETS_FOR_BASELINE:
            oldest_ts = baseline_events[0][0]
            newest_ts = baseline_events[-1][0]
            total_minutes = max((newest_ts - oldest_ts).total_seconds() / 60.0, 1/60)
            baseline_rate = baseline_packet_count / total_minutes
        else:
            baseline_rate = None

        severity = None
        reason_parts = []

        # Hard limit rule: very high rate
        if current_rate >= HARDCODED_PACKET_RATE_THRESHOLD:
            severity = "high"
            reason_parts.append(
                f"Very high packet rate from {src_ip}: ~{current_rate:.1f} pkts/min"
            )

        # Baseline anomaly rule
        if baseline_rate is not None:
            if current_rate > baseline_rate * ANOMALY_MULTIPLIER:
                sev = "medium" if severity is None else severity
                severity = sev
                reason_parts.append(
                    f"Current rate {current_rate:.1f} > {ANOMALY_MULTIPLIER}x baseline {baseline_rate:.1f}"
                )

        if severity is None:
            return None, packet_count, bytes_count

        reason = "; ".join(reason_parts)
        return {"severity": severity, "reason": reason}, packet_count, bytes_count


detector = AnomalyDetector()

# ============================
# PACKET SNIFFER
# ============================

def process_packet(pkt):
    if not pkt.haslayer(IP):
        return

    ip_layer = pkt[IP]
    src_ip = ip_layer.src
    dst_ip = ip_layer.dst
    length = len(pkt)

    if pkt.haslayer(TCP):
        protocol = "TCP"
    elif pkt.haslayer(UDP):
        protocol = "UDP"
    else:
        protocol = "IP"

    # Record into detector
    detector.record_packet(src_ip, length)
    anomaly, packet_count, bytes_count = detector.check_anomaly(src_ip)

    if anomaly:
        severity = anomaly["severity"]
        reason = anomaly["reason"]
        logger.warning(
            "Anomaly detected from %s -> %s | proto=%s | pkts=%d, bytes=%d | %s",
            src_ip, dst_ip, protocol, packet_count, bytes_count, reason
        )

        # Store in DB
        insert_alert(src_ip, dst_ip, protocol, packet_count, bytes_count, severity, reason)

        # Send email alert (can be rate-limited if needed)
        alert_msg = (
            f"NetSentinel detected suspicious activity.\n\n"
            f"Source IP: {src_ip}\n"
            f"Destination IP: {dst_ip}\n"
            f"Protocol: {protocol}\n"
            f"Packets (last {BASE_WINDOW_SECONDS}s): {packet_count}\n"
            f"Bytes (last {BASE_WINDOW_SECONDS}s): {bytes_count}\n"
            f"Severity: {severity}\n"
            f"Reason: {reason}\n"
            f"Time (UTC): {datetime.utcnow().isoformat()}\n"
        )
        send_email_alert(
            subject="[NetSentinel] Suspicious network activity detected",
            message=alert_msg
        )
def start_sniffer():
    logger.info("Starting packet sniffer on interface: %s", INTERFACE or "(default)")
    sniff(
        iface=INTERFACE,
        prn=process_packet,
        store=False
    )

# ============================
# FLASK DASHBOARD
# ============================

app = Flask(__name__)

DASHBOARD_TEMPLATE = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>NetSentinel Dashboard</title>
    <style>
      body {
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        background: #020617;
        color: #e5e7eb;
        margin: 0;
      }
      .nav {
        background: #020617;
        border-bottom: 1px solid #1f2937;
        padding: 0.8rem 1.6rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.6);
        position: sticky;
        top: 0;
        z-index: 10;
      }
      .nav h1 {
        margin: 0;
        font-size: 1.3rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
      }
      .nav span {
        font-size: 0.8rem;
        color: #9ca3af;
      }
      .container {
        max-width: 1100px;
        margin: 1.5rem auto;
        padding: 0 1.5rem 2rem;
      }
      .cards {
        display: grid;
        gap: 1rem;
        grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
        margin-bottom: 1.2rem;
      }
      .card {
        background: #020617;
        border: 1px solid #1f2937;
        border-radius: 0.9rem;
        padding: 0.9rem 1rem;
        box-shadow: 0 15px 30px rgba(15,23,42,0.8);
      }
      .card h2 {
        margin: 0;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.09em;
        color: #9ca3af;
      }
      .card .value {
        font-size: 1.4rem;
        font-weight: 700;
        margin-top: 0.3rem;
      }
      .badge {
        display: inline-block;
        padding: 0.15rem 0.5rem;
        border-radius: 999px;
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
      }
      .badge-high {
        background: rgba(220,38,38,0.3);
        color: #fecaca;
      }
      .badge-medium {
        background: rgba(234,179,8,0.25);
        color: #facc15;
      }
      .badge-low {
        background: rgba(22,163,74,0.25);
        color: #bbf7d0;
      }
      .table-wrapper {
        overflow-x: auto;
        border-radius: 0.9rem;
        border: 1px solid #1f2937;
        box-shadow: 0 15px 30px rgba(15,23,42,0.85);
      }
      table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.78rem;
      }
      thead {
        background: #020617;
      }
      th, td {
        padding: 0.5rem 0.7rem;
        border-bottom: 1px solid #111827;
        text-align: left;
      }
      tbody tr:last-child td {
        border-bottom: none;
      }
      tbody tr:hover {
        background: #020617;
      }
      .timestamp {
        color: #9ca3af;
        font-size: 0.72rem;
      }
      .filter-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.8rem;
        gap: 0.5rem;
      }
      .filter-bar form {
        display: flex;
        gap: 0.4rem;
        align-items: center;
        flex-wrap: wrap;
      }
      input[type="text"] {
        padding: 0.35rem 0.55rem;
        border-radius: 0.4rem;
        border: 1px solid #374151;
        background: #020617;
        color: #e5e7eb;
        font-size: 0.78rem;
      }
      button {
        padding: 0.35rem 0.9rem;
        border-radius: 999px;
        border: none;
        cursor: pointer;
        background: #22d3ee;
        color: #020617;
        font-weight: 600;
        font-size: 0.78rem;
        letter-spacing: 0.05em;
        text-transform: uppercase;
      }
      @media (max-width: 768px) {
        .container { padding: 0 1rem 2rem; }
      }
    </style>
  </head>
  <body>
    <div class="nav">
      <h1>NetSentinel</h1>
      <span>Network Threat Detection & Alerting Dashboard</span>
    </div>
    <div class="container">
      <div class="cards">
        <div class="card">
          <h2>Total Alerts</h2>
          <div class="value">{{ stats.total_alerts }}</div>
        </div>
        <div class="card">
          <h2>High Severity</h2>
          <div class="value">{{ stats.high }}</div>
        </div>
        <div class="card">
          <h2>Medium Severity</h2>
          <div class="value">{{ stats.medium }}</div>
        </div>
        <div class="card">
          <h2>Unique Source IPs</h2>
          <div class="value">{{ stats.unique_sources }}</div>
        </div>
      </div>

      <div class="filter-bar">
        <h2 style="font-size:0.95rem; margin:0;">Recent Alerts</h2>
        <form method="get">
          <input type="text" name="q" value="{{ q }}" placeholder="Filter by IP or reason..." />
          <button type="submit">Filter</button>
        </form>
      </div>

      <div class="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>Time</th>
              <th>Source</th>
              <th>Destination</th>
              <th>Protocol</th>
              <th>Attack</th>
              <th>Severity</th>
              <th>Packets</th>
              <th>Bytes</th>
              <th>Duration</th>
              <th>Reason</th>
            </tr>
          </thead>
          <tbody>
            {% if alerts %}
              {% for a in alerts %}
              <tr>
                <td>{{ a.src_ip }}:{{ a.src_port }}</td>
<td>{{ a.dst_ip }}:{{ a.dst_port }}</td>
<td>{{ a.attack_type }}</td>
<td>{{ a.severity }}</td>
<td>{{ a.packet_count }}</td>
<td>{{ a.byte_count }}</td>
<td>{{ "%.1f"|format(a.duration) }}s</td>
<td>{{ a.reason }}</td>

                <td>
                  {% if a.severity == "high" %}
                    <span class="badge badge-high">High</span>
                  {% elif a.severity == "medium" %}
                    <span class="badge badge-medium">Medium</span>
                  {% else %}
                    <span class="badge badge-low">Low</span>
                  {% endif %}
                </td>
                <td>{{ a.reason }}</td>
              </tr>
              {% endfor %}
            {% else %}
              <tr>
                <td colspan="8" style="text-align:center; padding:0.8rem; color:#9ca3af;">
                  No alerts yet. System is monitoring traffic...
                </td>
              </tr>
            {% endif %}
          </tbody>
        </table>
      </div>
    </div>
  </body>
</html>
"""


@app.route("/")
def dashboard():
    q = request.args.get("q", "").strip()

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    if q:
        like = f"%{q}%"
        cur.execute(
            """
            SELECT * FROM alerts
            WHERE src_ip LIKE ? OR dst_ip LIKE ? OR reason LIKE ?
            ORDER BY id DESC
            LIMIT 200
            """,
            (like, like, like)
        )
    else:
        cur.execute(
            "SELECT * FROM alerts ORDER BY id DESC LIMIT 200"
        )

    rows = cur.fetchall()

    # Stats
    cur.execute("SELECT COUNT(*) FROM alerts")
    total_alerts = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM alerts WHERE severity='high'")
    high = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM alerts WHERE severity='medium'")
    medium = cur.fetchone()[0]

    cur.execute("SELECT COUNT(DISTINCT src_ip) FROM alerts")
    unique_sources = cur.fetchone()[0]

    conn.close()

    stats = {
        "total_alerts": total_alerts,
        "high": high,
        "medium": medium,
        "unique_sources": unique_sources
    }

    return render_template_string(
        DASHBOARD_TEMPLATE,
        alerts=rows,
        stats=stats,
        q=q
    )


def start_flask():
    logger.info("Starting Flask dashboard at http://%s:%s", FLASK_HOST, FLASK_PORT)
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG, use_reloader=False)

# ============================
# MAIN
# ============================

if __name__ == "__main__":
    logger.info("Initializing NetSentinel...")
    init_db()

    # Start sniffer thread
    sniffer_thread = threading.Thread(target=start_sniffer, daemon=True)
    sniffer_thread.start()

    # Start Flask (main thread)
    start_flask()
