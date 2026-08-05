# 🚀 NetSentinel Quick Reference Guide

## ⚡ Quick Commands

### Start NetSentinel
```bash
python main.py
```

### Test Notifications
```bash
python test_notifications.py
```

### Access Dashboard
```
http://localhost:5000
```

---

## 📋 Configuration Checklist

### ✅ Required
- [ ] `SMTP_USER` - Your email address
- [ ] `SMTP_PASSWORD` - Gmail app password
- [ ] `ALERT_TO` - Recipient email

### 🔧 Optional
- [ ] `TELEGRAM_BOT_TOKEN` - Telegram bot token
- [ ] `TELEGRAM_CHAT_ID` - Telegram chat ID
- [ ] `SLACK_WEBHOOK_URL` - Slack webhook URL
- [ ] `SYSLOG_HOST` - SIEM server address

---

## 🎯 Attack Detection Thresholds

| Attack Type | Threshold | Severity |
|-------------|-----------|----------|
| Port Scan | >15 ports in 30s | Medium |
| SYN Flood | >50 SYN, <70% ACK | High |
| Brute Force | >10 attempts in 60s | Medium-High |
| DoS/Flood | >20 packets in flow | High |
| Beaconing | >60s, <1KB data | Medium |
| ICMP Flood | >10 ICMP packets | Medium |
| Suspicious Port | Traffic to 22/23/3389/445 | Medium |

---

## 🐳 Docker Commands

```bash
# Build
docker build -t netsentinel .

# Run
docker-compose up -d

# Logs
docker-compose logs -f

# Stop
docker-compose down

# Restart
docker-compose restart
```

---

## 🐧 Linux Service Commands

```bash
# Start
sudo systemctl start netsentinel

# Stop
sudo systemctl stop netsentinel

# Status
sudo systemctl status netsentinel

# Logs
sudo journalctl -u netsentinel -f

# Enable auto-start
sudo systemctl enable netsentinel
```

---

## 🪟 Windows Service Commands

```powershell
# Install
.\deployment\install_service.ps1 -Action install

# Start
net start NetSentinel

# Stop
net stop NetSentinel

# Status
sc query NetSentinel

# Uninstall
.\deployment\install_service.ps1 -Action uninstall
```

---

## 📊 Database Queries

```sql
-- Recent alerts
SELECT * FROM alerts ORDER BY id DESC LIMIT 10;

-- Count by severity
SELECT severity, COUNT(*) FROM alerts GROUP BY severity;

-- Top attacking IPs
SELECT src_ip, COUNT(*) as count 
FROM alerts 
GROUP BY src_ip 
ORDER BY count DESC 
LIMIT 10;

-- Alerts in last hour
SELECT * FROM alerts 
WHERE timestamp > datetime('now', '-1 hour');
```

---

## 🔧 Troubleshooting

### Permission Denied
```bash
# Linux
sudo python main.py
# or
sudo setcap cap_net_raw,cap_net_admin=eip $(which python3)
```

### Email Not Sending
1. Check Gmail App Password
2. Verify SMTP settings
3. Check logs: `logs/netsentinel.log`

### Dashboard Not Loading
1. Check if port 5000 is available
2. Try: `http://127.0.0.1:5000`
3. Check firewall rules

---

## 📁 Important Files

| File | Purpose |
|------|---------|
| `config.py` | Configuration settings |
| `main.py` | Entry point |
| `logs/netsentinel.log` | Application logs |
| `netsentinel.db` | SQLite database |
| `requirements.txt` | Python dependencies |

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| `README.md` | Main documentation |
| `FEATURES.md` | Feature summary |
| `SUMMARY.md` | Complete implementation summary |
| `ARCHITECTURE.md` | System architecture |
| `deployment/DEPLOYMENT_GUIDE.md` | Deployment guide |
| `EMAIL_ALERTS.md` | Email setup |

---

## 🧪 Testing

```bash
# Test email
python test_email.py

# Test all notifications
python test_notifications.py

# Generate test traffic
ping google.com
curl http://example.com

# Port scan test (use with caution)
nmap -p 1-100 localhost
```

---

## 🔔 Notification Setup

### Gmail App Password
1. Go to: https://myaccount.google.com/apppasswords
2. Generate app password
3. Add to `config.py`

### Telegram Bot
1. Message @BotFather
2. Create new bot
3. Get token and chat ID
4. Add to `config.py`

### Slack Webhook
1. Go to: https://api.slack.com/messaging/webhooks
2. Create webhook
3. Add URL to `config.py`

---

## 🚨 Common Alerts

### Port Scan
**Meaning**: Someone is scanning your network for open ports  
**Action**: Investigate source IP, consider blocking

### SYN Flood
**Meaning**: DDoS attack attempt  
**Action**: Enable rate limiting, contact ISP if severe

### Brute Force
**Meaning**: Password guessing attack  
**Action**: Block source IP, review authentication logs

### Beaconing
**Meaning**: Possible malware C2 communication  
**Action**: Investigate destination IP, scan for malware

---

## 📞 Quick Support

- **Logs**: `logs/netsentinel.log`
- **Database**: `sqlite3 netsentinel.db`
- **Dashboard**: http://localhost:5000
- **Test**: `python test_notifications.py`

---

## 🎯 Performance Tips

1. **Limit Interface**: Set specific interface in `config.py`
2. **Adjust Thresholds**: Tune detection thresholds
3. **Resource Limits**: Use Docker resource limits
4. **Log Rotation**: Enable log rotation
5. **Database Cleanup**: Archive old alerts periodically

---

## 🔒 Security Best Practices

1. ✅ Use strong passwords
2. ✅ Restrict dashboard access
3. ✅ Enable HTTPS (reverse proxy)
4. ✅ Regular updates
5. ✅ Monitor logs
6. ✅ Backup database

---

**Quick Start**: `python main.py` → http://localhost:5000 🚀
