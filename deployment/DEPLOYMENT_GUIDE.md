# 🚀 NetSentinel Deployment Guide

Complete guide for deploying NetSentinel in production environments.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Docker Deployment](#docker-deployment)
3. [Linux Daemon](#linux-daemon)
4. [Windows Service](#windows-service)
5. [Configuration](#configuration)
6. [Testing](#testing)
7. [Monitoring](#monitoring)
8. [Troubleshooting](#troubleshooting)

---

## 🔧 Prerequisites

### System Requirements
- **OS**: Linux (Ubuntu 20.04+, CentOS 8+) or Windows 10/11/Server
- **RAM**: Minimum 512MB, Recommended 1GB+
- **CPU**: 1+ cores
- **Disk**: 1GB+ free space
- **Network**: Administrator/root access for packet capture

### Software Requirements
- **Python**: 3.11 or higher
- **libpcap** (Linux) or **Npcap** (Windows)
- **Docker** (optional, for containerized deployment)
- **systemd** (Linux, for daemon)
- **NSSM** (Windows, for service)

---

## 🐳 Docker Deployment

### Advantages
- ✅ Isolated environment
- ✅ Easy updates
- ✅ Consistent across platforms
- ✅ Resource limits
- ✅ Auto-restart

### Installation Steps

#### 1. Install Docker

**Linux:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

**Windows:**
Download and install Docker Desktop from https://www.docker.com/products/docker-desktop

#### 2. Clone Repository
```bash
git clone https://github.com/yourusername/netsentinel.git
cd netsentinel
```

#### 3. Configure Settings
Edit `config.py` with your settings (email, Telegram, etc.)

#### 4. Build and Run
```bash
# Build image
docker build -t netsentinel .

# Run with Docker Compose (recommended)
docker-compose up -d

# Or run directly
docker run -d \
  --name netsentinel \
  --network host \
  --privileged \
  -v $(pwd)/netsentinel.db:/app/netsentinel.db \
  -v $(pwd)/logs:/app/logs \
  netsentinel
```

#### 5. Verify Deployment
```bash
# Check container status
docker ps

# View logs
docker logs -f netsentinel

# Access dashboard
curl http://localhost:5000
```

### Docker Management

```bash
# Start
docker-compose start

# Stop
docker-compose stop

# Restart
docker-compose restart

# View logs
docker-compose logs -f

# Update
docker-compose pull
docker-compose up -d

# Remove
docker-compose down
```

---

## 🐧 Linux Daemon (systemd)

### Advantages
- ✅ Native Linux integration
- ✅ Auto-start on boot
- ✅ systemd logging
- ✅ Resource management
- ✅ Security hardening

### Installation Steps

#### 1. Install Dependencies
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip libpcap-dev

# CentOS/RHEL
sudo yum install python3 python3-pip libpcap-devel
```

#### 2. Clone Repository
```bash
cd /opt
sudo git clone https://github.com/yourusername/netsentinel.git
cd netsentinel
```

#### 3. Install Python Dependencies
```bash
sudo pip3 install -r requirements.txt
```

#### 4. Configure Settings
```bash
sudo nano config.py
# Edit email, Telegram, Slack settings
```

#### 5. Run Installer
```bash
cd deployment
sudo chmod +x install_service.sh
sudo ./install_service.sh
```

#### 6. Start Service
```bash
sudo systemctl start netsentinel
sudo systemctl enable netsentinel  # Auto-start on boot
```

#### 7. Verify
```bash
# Check status
sudo systemctl status netsentinel

# View logs
sudo journalctl -u netsentinel -f

# Access dashboard
curl http://localhost:5000
```

### Service Management

```bash
# Start
sudo systemctl start netsentinel

# Stop
sudo systemctl stop netsentinel

# Restart
sudo systemctl restart netsentinel

# Status
sudo systemctl status netsentinel

# Enable auto-start
sudo systemctl enable netsentinel

# Disable auto-start
sudo systemctl disable netsentinel

# View logs
sudo journalctl -u netsentinel -f

# View recent logs
sudo journalctl -u netsentinel -n 100
```

### Manual Installation (Alternative)

If the installer doesn't work:

```bash
# 1. Create user
sudo useradd -r -s /bin/false netsentinel

# 2. Copy files
sudo mkdir -p /opt/netsentinel
sudo cp -r * /opt/netsentinel/
sudo chown -R netsentinel:netsentinel /opt/netsentinel

# 3. Install service file
sudo cp deployment/netsentinel.service /etc/systemd/system/
sudo systemctl daemon-reload

# 4. Start service
sudo systemctl start netsentinel
sudo systemctl enable netsentinel
```

---

## 🪟 Windows Service

### Advantages
- ✅ Native Windows integration
- ✅ Auto-start on boot
- ✅ Event log integration
- ✅ Service management console

### Prerequisites

Install **NSSM** (Non-Sucking Service Manager):

**Option 1: Chocolatey**
```powershell
choco install nssm
```

**Option 2: Manual**
1. Download from https://nssm.cc/download
2. Extract to `C:\Program Files\NSSM`
3. Add to PATH

### Installation Steps

#### 1. Install Python
Download and install Python 3.11+ from https://www.python.org/downloads/

#### 2. Install Npcap
Download and install from https://npcap.com/#download

#### 3. Clone Repository
```powershell
cd C:\
git clone https://github.com/yourusername/netsentinel.git
cd netsentinel
```

#### 4. Install Dependencies
```powershell
pip install -r requirements.txt
```

#### 5. Configure Settings
Edit `config.py` with your settings

#### 6. Run Installer (as Administrator)
```powershell
cd deployment
.\install_service.ps1 -Action install
```

#### 7. Start Service
```powershell
net start NetSentinel
```

#### 8. Verify
```powershell
# Check status
sc query NetSentinel

# Access dashboard
Start-Process http://localhost:5000
```

### Service Management

```powershell
# Start
net start NetSentinel

# Stop
net stop NetSentinel

# Restart
net stop NetSentinel
net start NetSentinel

# Status
sc query NetSentinel

# View logs
Get-Content "C:\Program Files\NetSentinel\logs\service-stdout.log" -Tail 50 -Wait

# Uninstall
.\install_service.ps1 -Action uninstall
```

---

## ⚙️ Configuration

### Essential Settings

Edit `config.py`:

```python
# Network Interface
INTERFACE = None  # None = all interfaces, or "eth0", "wlan0", etc.

# Detection Thresholds
PORT_SCAN_THRESHOLD = 15
HARDCODED_PACKET_RATE_THRESHOLD = 100

# Email Alerts (Required)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "your-email@gmail.com"
SMTP_PASSWORD = "your-app-password"  # Gmail App Password
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

# Dashboard
FLASK_HOST = "0.0.0.0"  # 0.0.0.0 = all interfaces
FLASK_PORT = 5000
FLASK_DEBUG = False  # Set to True for development only
```

### Security Recommendations

1. **Use App Passwords** for email (not regular passwords)
2. **Restrict Dashboard Access** - Use firewall rules
3. **Enable HTTPS** - Use reverse proxy (nginx/Apache)
4. **Limit Interface** - Specify specific network interface
5. **Regular Updates** - Keep dependencies updated

---

## 🧪 Testing

### 1. Test Notifications
```bash
# Test email only
python test_email.py

# Test all channels
python test_notifications.py
```

### 2. Test Packet Capture
```bash
# Run NetSentinel
python main.py

# Generate traffic (another terminal)
ping google.com
curl http://example.com
```

### 3. Test Dashboard
```bash
# Access in browser
http://localhost:5000

# Or via curl
curl http://localhost:5000
```

### 4. Test Attack Detection
```bash
# Port scan simulation (use nmap)
nmap -p 1-100 localhost

# HTTP flood simulation
for i in {1..100}; do curl http://localhost & done
```

---

## 📊 Monitoring

### Dashboard Metrics
- Total alerts
- High/Medium severity counts
- Unique source IPs
- Recent alerts (last 200)

### Log Files

**Linux:**
```bash
# Application logs
tail -f /opt/netsentinel/logs/netsentinel.log

# System logs
sudo journalctl -u netsentinel -f
```

**Windows:**
```powershell
# Application logs
Get-Content "C:\Program Files\NetSentinel\logs\netsentinel.log" -Tail 50 -Wait

# Service logs
Get-Content "C:\Program Files\NetSentinel\logs\service-stdout.log" -Tail 50 -Wait
```

**Docker:**
```bash
docker logs -f netsentinel
```

### Database Queries

```bash
# Connect to SQLite
sqlite3 netsentinel.db

# View recent alerts
SELECT * FROM alerts ORDER BY id DESC LIMIT 10;

# Count by severity
SELECT severity, COUNT(*) FROM alerts GROUP BY severity;

# Top attacking IPs
SELECT src_ip, COUNT(*) as count FROM alerts GROUP BY src_ip ORDER BY count DESC LIMIT 10;
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Permission Denied (Packet Capture)

**Linux:**
```bash
# Option 1: Run as root
sudo python main.py

# Option 2: Grant capabilities
sudo setcap cap_net_raw,cap_net_admin=eip $(which python3)

# Option 3: Add user to group
sudo usermod -aG wireshark $USER
```

**Windows:**
- Run as Administrator
- Ensure Npcap is installed

#### 2. Email Not Sending

- ✅ Check Gmail App Password (not regular password)
- ✅ Verify SMTP settings
- ✅ Check firewall (port 587)
- ✅ Check logs for errors

#### 3. Dashboard Not Loading

- ✅ Check if Flask is running
- ✅ Verify port 5000 is not in use: `netstat -an | grep 5000`
- ✅ Check firewall rules
- ✅ Try accessing via 127.0.0.1 instead of localhost

#### 4. Service Won't Start

**Linux:**
```bash
# Check service status
sudo systemctl status netsentinel

# View detailed logs
sudo journalctl -u netsentinel -xe

# Check permissions
ls -la /opt/netsentinel
```

**Windows:**
```powershell
# Check service status
sc query NetSentinel

# View event logs
Get-EventLog -LogName Application -Source NetSentinel -Newest 10
```

#### 5. High CPU/Memory Usage

- Reduce packet capture rate
- Limit network interface
- Adjust detection thresholds
- Enable resource limits (Docker/systemd)

---

## 🔒 Security Best Practices

### 1. Network Segmentation
- Deploy on dedicated monitoring network
- Use SPAN/mirror ports for traffic capture

### 2. Access Control
- Restrict dashboard access (firewall rules)
- Use strong passwords
- Enable HTTPS (reverse proxy)

### 3. Log Management
- Rotate logs regularly
- Archive old alerts
- Monitor disk space

### 4. Updates
```bash
# Update dependencies
pip install -r requirements.txt --upgrade

# Update NetSentinel
git pull origin main
```

### 5. Backup
```bash
# Backup database
cp netsentinel.db netsentinel.db.backup

# Backup configuration
cp config.py config.py.backup
```

---

## 📞 Support

- **Issues**: https://github.com/yourusername/netsentinel/issues
- **Documentation**: README.md, FEATURES.md
- **Email**: support@netsentinel.com

---

**🎉 Happy Deploying!**
