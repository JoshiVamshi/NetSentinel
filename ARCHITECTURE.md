# NetSentinel Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         NetSentinel IDS Architecture                         │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                            1. PACKET CAPTURE LAYER                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐         ┌──────────────┐         ┌──────────────┐       │
│  │   Network    │────────▶│    Scapy     │────────▶│     Flow     │       │
│  │  Interface   │         │   Sniffer    │         │   Manager    │       │
│  └──────────────┘         └──────────────┘         └──────────────┘       │
│   (eth0/wlan0)            capture/sniffer.py       flow/flow_manager.py    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          2. DETECTION ENGINE LAYER                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │                      Detection Engine                               │    │
│  │                    detection/engine.py                              │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                      │                                       │
│         ┌────────────────────────────┼────────────────────────────┐        │
│         │            │               │               │            │        │
│         ▼            ▼               ▼               ▼            ▼        │
│  ┌──────────┐ ┌──────────┐   ┌──────────┐   ┌──────────┐ ┌──────────┐   │
│  │   Port   │ │   SYN    │   │  Brute   │   │   DoS/   │ │ Beaconing│   │
│  │   Scan   │ │  Flood   │   │  Force   │   │  Flood   │ │          │   │
│  └──────────┘ └──────────┘   └──────────┘   └──────────┘ └──────────┘   │
│  portscan.py  syn_flood.py   brute_force.py  engine.py    engine.py      │
│                                                                              │
│  ┌──────────┐ ┌──────────┐                                                 │
│  │   ICMP   │ │Suspicious│                                                 │
│  │  Flood   │ │   Port   │                                                 │
│  └──────────┘ └──────────┘                                                 │
│   engine.py    engine.py                                                    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         3. STORAGE & LOGGING LAYER                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐         ┌──────────────┐         ┌──────────────┐       │
│  │   SQLite     │         │  PostgreSQL  │         │   MongoDB    │       │
│  │  (Default)   │         │  (Optional)  │         │  (Optional)  │       │
│  └──────────────┘         └──────────────┘         └──────────────┘       │
│  storage/database.py                                                        │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────┐          │
│  │                    Application Logs                           │          │
│  │                  logs/netsentinel.log                         │          │
│  └──────────────────────────────────────────────────────────────┘          │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    │                 │                 │
                    ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        4. NOTIFICATION LAYER                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │              Notification Manager                                   │    │
│  │          alerts/notification_manager.py                             │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                      │                                       │
│         ┌────────────────────────────┼────────────────────────────┐        │
│         │                            │                            │        │
│         ▼                            ▼                            ▼        │
│  ┌──────────────┐           ┌──────────────┐           ┌──────────────┐   │
│  │    Email     │           │   Telegram   │           │    Slack     │   │
│  │    (SMTP)    │           │     Bot      │           │   Webhook    │   │
│  └──────────────┘           └──────────────┘           └──────────────┘   │
│  alerts/emailer.py      alerts/telegram_bot.py    alerts/slack_notifier.py │
│                                                                              │
│         │                            │                            │        │
│         ▼                            ▼                            ▼        │
│  ┌──────────────┐           ┌──────────────┐           ┌──────────────┐   │
│  │    Gmail     │           │   Telegram   │           │    Slack     │   │
│  │   Outlook    │           │   Channel    │           │   Channel    │   │
│  └──────────────┘           └──────────────┘           └──────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                          5. SIEM INTEGRATION LAYER                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐         ┌──────────────┐                                 │
│  │     CEF      │         │   Syslog     │                                 │
│  │   Formatter  │         │   Exporter   │                                 │
│  └──────────────┘         └──────────────┘                                 │
│  siem/cef_formatter.py   siem/syslog_exporter.py                           │
│                                                                              │
│         │                            │                                       │
│         ▼                            ▼                                       │
│  ┌──────────────────────────────────────────────────────────────┐          │
│  │              SIEM Platforms                                   │          │
│  │  Splunk │ ELK Stack │ QRadar │ ArcSight │ LogRhythm          │          │
│  └──────────────────────────────────────────────────────────────┘          │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                         6. WEB DASHBOARD LAYER                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │                      Flask Web Application                          │    │
│  │                      dashboard/app.py                               │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                      │                                       │
│         ┌────────────────────────────┼────────────────────────────┐        │
│         │                            │                            │        │
│         ▼                            ▼                            ▼        │
│  ┌──────────────┐           ┌──────────────┐           ┌──────────────┐   │
│  │  Statistics  │           │    Alerts    │           │   Search &   │   │
│  │   Overview   │           │    Table     │           │    Filter    │   │
│  └──────────────┘           └──────────────┘           └──────────────┘   │
│                                                                              │
│  Access: http://localhost:5000                                              │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                        7. DEPLOYMENT OPTIONS                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐         ┌──────────────┐         ┌──────────────┐       │
│  │    Docker    │         │    Linux     │         │   Windows    │       │
│  │  Container   │         │   Daemon     │         │   Service    │       │
│  └──────────────┘         └──────────────┘         └──────────────┘       │
│   Dockerfile              systemd service           NSSM service           │
│   docker-compose.yml      install_service.sh        install_service.ps1    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘


DATA FLOW:
═══════════

1. Network Traffic ──▶ Scapy Sniffer ──▶ Flow Manager
                                              │
2. Flow Manager ──▶ Detection Engine ──▶ Attack Analysis
                                              │
3. Attack Detected ──▶ Database Storage ──▶ SQLite/PostgreSQL
                  │
                  ├──▶ Notification Manager ──▶ Email/Telegram/Slack
                  │
                  ├──▶ SIEM Export ──▶ CEF/Syslog ──▶ SIEM Platform
                  │
                  └──▶ Web Dashboard ──▶ Real-time Display


CONFIGURATION:
═════════════

config.py
├── Network Interface (INTERFACE)
├── Detection Thresholds
│   ├── PORT_SCAN_THRESHOLD
│   ├── HARDCODED_PACKET_RATE_THRESHOLD
│   └── BASE_WINDOW_SECONDS
├── Email (SMTP_USER, SMTP_PASSWORD, ALERT_TO)
├── Telegram (TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
├── Slack (SLACK_WEBHOOK_URL)
├── SIEM (SYSLOG_HOST, SYSLOG_PORT, SYSLOG_PROTOCOL)
└── Dashboard (FLASK_HOST, FLASK_PORT, FLASK_DEBUG)


ATTACK DETECTION FLOW:
══════════════════════

Packet Capture
      │
      ▼
Flow Aggregation
      │
      ├──▶ Port Scan Detector ──▶ >15 unique ports in 30s?
      │
      ├──▶ SYN Flood Detector ──▶ >50 SYN, <70% ACK ratio?
      │
      ├──▶ Brute Force Detector ──▶ >10 auth attempts in 60s?
      │
      ├──▶ DoS/Flood Detector ──▶ >20 packets in flow?
      │
      ├──▶ Beaconing Detector ──▶ >60s duration, <1KB data?
      │
      ├──▶ ICMP Flood Detector ──▶ >10 ICMP packets?
      │
      └──▶ Suspicious Port Detector ──▶ Traffic to 22/23/3389/445?
                │
                ▼
          Alert Generated
                │
                ├──▶ Store in Database
                ├──▶ Send Notifications
                ├──▶ Export to SIEM
                └──▶ Display on Dashboard
```
