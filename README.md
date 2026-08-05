# 🛡️ NetSentinel - Advanced Network Intrusion Detection System

**NetSentinel** is a production-ready, ML-capable Intrusion Detection System (IDS) with multi-channel alerting, SIEM integration, and comprehensive attack detection capabilities.

![Version](https://img.shields.io/badge/version-2.0-blue)
![Python](https://img.shields.io/badge/python-3.11+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

---

## 🚀 Features

### ✅ **Multi-Attack Detection**
- **DoS/DDoS Attacks** - High packet volume detection
- **Port Scanning** - Detects reconnaissance activities
- **SYN Flood** - Incomplete TCP handshake detection
- **Brute Force** - Authentication attack detection
- **Beaconing** - C2 communication patterns
- **ICMP Flood** - ICMP-based attacks
- **Suspicious Port Access** - Monitoring sensitive ports

### 📧 **Multi-Channel Alerting**
- **Email** (SMTP) - Gmail, Outlook, custom SMTP
- **Telegram** - Real-time bot notifications
- **Slack** - Webhook integration
- **Unified Notification Manager** - Send to all channels simultaneously

### 🗄️ **Database Integration**
- **SQLite** (default) - Lightweight, embedded
- **PostgreSQL** (optional) - Production-ready
- **MongoDB** (optional) - NoSQL support
- Persistent alert storage
- Historical analysis capabilities

### 📊 **Web Dashboard**
- Real-time monitoring
- Alert statistics
- Attack visualization
- IP filtering and search
- Dark theme UI
- Mobile responsive

### 🔌 **SIEM Integration**
- **CEF Format** - Common Event Format
- **Syslog** (RFC 5424) - UDP/TCP support
- Compatible with:
  - Splunk
  - ELK Stack
  - QRadar
  - ArcSight
  - LogRhythm

### 🤖 **Machine Learning Ready**
- Feature extraction framework
- Anomaly detection models
- Adaptive threat detection
- Zero-day attack identification

### 🐳 **Production Deployment**
- **Docker** - Containerized deployment
- **Linux Daemon** - systemd service
- **Windows Service** - NSSM integration
- Auto-restart and health checks

---

## 📦 Installation

### Prerequisites
- Python 3.11+
- libpcap (Linux) or Npcap (Windows)
- Administrator/root privileges (for packet capture)

### Quick Start

```bash
# Clone repository
git clone https://github.com/yourusername/netsentinel.git
cd netsentinel

# Install dependencies
pip install -r requirements.txt

# Configure settings
nano config.py  # Edit email, Telegram, Slack settings

# Run NetSentinel
python main.py
```

### Dashboard Access
Open browser: **http://localhost:5000**

---

## ⚙️ Configuration

Edit `config.py` to customize:

```python
# Network Interface
INTERFACE = None  # None = all interfaces

# Detection Thresholds
PORT_SCAN_THRESHOLD = 15
HARDCODED_PACKET_RATE_THRESHOLD = 100

# Email Alerts
SMTP_SERVER = "smtp.gmail.com"
SMTP_USER = "your-email@gmail.com"
SMTP_PASSWORD = "your-app-password"
ALERT_TO = "recipient@gmail.com"

# Telegram (Optional)
TELEGRAM_BOT_TOKEN = "123456789:ABCdefGHI..."
TELEGRAM_CHAT_ID = "123456789"

# Slack (Optional)
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/..."

# SIEM (Optional)
SYSLOG_HOST = "siem.company.com"
SYSLOG_PORT = 514
SYSLOG_PROTOCOL = "udp"
```

---

## 🐳 Docker Deployment

### Build and Run

```bash
# Build image
docker build -t netsentinel .

# Run container
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Docker Compose Features
- Automatic restart
- Volume persistence
- Resource limits
- Log rotation

---

## 🐧 Linux Service Installation

```bash
cd deployment
sudo chmod +x install_service.sh
sudo ./install_service.sh
```

### Service Management

```bash
# Start
sudo systemctl start netsentinel

# Stop
sudo systemctl stop netsentinel

# Status
sudo systemctl status netsentinel

# Logs
sudo journalctl -u netsentinel -f
```

---

## 🪟 Windows Service Installation

```powershell
# Run PowerShell as Administrator
cd deployment
.\install_service.ps1 -Action install
```

### Service Management

```powershell
# Start
net start NetSentinel

# Stop
net stop NetSentinel

# Status
sc query NetSentinel
```

---

## 📊 Attack Detection Details

### 1. **DoS/Flood Detection**
- **Trigger**: >20 packets in single flow
- **Severity**: High
- **Action**: Alert + Block (optional)

### 2. **Port Scan Detection**
- **Trigger**: >15 unique ports in 30 seconds
- **Severity**: Medium
- **Pattern**: Reconnaissance activity

### 3. **SYN Flood Detection**
- **Trigger**: >50 SYN packets, <30% ACK ratio
- **Severity**: High
- **Pattern**: DDoS attack

### 4. **Brute Force Detection**
- **Trigger**: >10 auth attempts in 60 seconds
- **Severity**: Medium-High
- **Ports**: SSH(22), RDP(3389), FTP(21), etc.

### 5. **Beaconing Detection**
- **Trigger**: Long connection (>60s) with low data (<1KB)
- **Severity**: Medium
- **Pattern**: C2 communication

---

## 🔔 Notification Setup

### Email (Gmail)
1. Enable 2FA on Gmail
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Add to `config.py`:
   ```python
   SMTP_USER = "your-email@gmail.com"
   SMTP_PASSWORD = "your-app-password"
   ```

### Telegram
1. Create bot: Message @BotFather on Telegram
2. Get bot token
3. Get chat ID: Message bot, visit `https://api.telegram.org/bot<TOKEN>/getUpdates`
4. Add to `config.py`:
   ```python
   TELEGRAM_BOT_TOKEN = "your-token"
   TELEGRAM_CHAT_ID = "your-chat-id"
   ```

### Slack
1. Create Incoming Webhook: https://api.slack.com/messaging/webhooks
2. Add to `config.py`:
   ```python
   SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/..."
   ```

---

## 🧪 Testing

### Test Email Alerts
```bash
python test_email.py
```

### Test All Notifications
```python
from alerts.notification_manager import get_notification_manager

nm = get_notification_manager()
results = nm.test_all_channels()
print(results)
```

---

## 📁 Project Structure

```
NetSentinel/
├── alerts/                 # Notification modules
│   ├── emailer.py         # Email alerts
│   ├── notification_manager.py  # Unified notification manager
│   ├── slack_notifier.py  # Slack integration
│   └── telegram_bot.py    # Telegram integration
├── capture/               # Packet capture
│   └── sniffer.py        # Scapy-based sniffer
├── dashboard/             # Web interface
│   └── app.py            # Flask web dashboard
├── deployment/            # Service installers & documentation
│   ├── DEPLOYMENT_GUIDE.md # Service deployment guide
│   ├── install_service.ps1  # Windows service installer script
│   ├── install_service.sh   # Linux systemd service installer script
│   └── netsentinel.service  # systemd configuration unit
├── detection/             # Attack detection modules
│   ├── ai_anomaly.py     # AI Isolation Forest anomaly detector
│   ├── anomaly.py        # Rule/statistical anomaly detector
│   ├── brute_force.py    # Brute force detector
│   ├── engine.py         # Main detection engine manager
│   ├── portscan.py       # Port scan detector
│   └── syn_flood.py      # SYN flood detector
├── flow/                  # Flow tracking
│   └── flow_manager.py   # Flow state manager
├── models/                # Machine learning models
│   └── iforest.joblib    # Trained Isolation Forest model
├── siem/                  # SIEM integration
│   ├── cef_formatter.py  # Common Event Format (CEF) formatter
│   └── syslog_exporter.py # Syslog (UDP/TCP) exporter
├── storage/               # Database operations
│   └── database.py       # SQLite storage & alert logging
├── config.py              # Configuration settings
├── main.py                # Main application entry point
├── logger_setup.py        # Central logging setup
├── train_ai.py            # Script to train ML anomaly model
├── test_email.py          # Email test script
├── test_notifications.py  # Notification channels test script
├── quick_test.py          # Comprehensive quick test suite
├── check_db.py            # Database inspection utility
├── Dockerfile             # Docker container definition
├── docker-compose.yml     # Docker Compose multi-container setup
├── requirements.txt       # Python dependency list
├── ARCHITECTURE.md        # Architecture overview & documentation
├── COMPLETE.md            # Detailed implementation completion doc
├── EMAIL_ALERTS.md        # Email notification setup guide
├── FEATURES.md            # Feature breakdown & reference
├── IMPLEMENTATION_PLAN.md # Technical implementation plan
├── INDEX.md               # Documentation index
├── QUICK_REFERENCE.md     # System quick reference guide
├── SUMMARY.md             # Project summary report
├── TEST_RESULTS.md        # Test suite execution results
└── TESTING_GUIDE.md       # Comprehensive testing guide
```

---

## 🔧 Troubleshooting

### Permission Denied (Packet Capture)
```bash
# Linux
sudo setcap cap_net_raw,cap_net_admin=eip $(which python3)

# Or run as root
sudo python main.py
```

### Email Not Sending
- Check Gmail App Password (not regular password)
- Verify SMTP settings
- Check firewall (port 587)

### Dashboard Not Loading
- Check if Flask is running: `http://localhost:5000`
- Verify firewall allows port 5000
- Check logs: `logs/netsentinel.log`

---

## 🛣️ Roadmap

- [ ] Machine Learning models (Isolation Forest, One-Class SVM)
- [ ] Real-time dashboard charts (WebSocket)
- [ ] Geographic IP mapping
- [ ] Automatic IP blocking (iptables/Windows Firewall)
- [ ] Mobile app (iOS/Android)
- [ ] API for external integrations
- [ ] Threat intelligence feeds




