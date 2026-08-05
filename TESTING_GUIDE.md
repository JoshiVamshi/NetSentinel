# 🧪 NetSentinel v2.0 - Complete Testing Guide

This guide will help you verify that all NetSentinel v2.0 features are working correctly.

---

## 📋 **Testing Checklist**

### ✅ **Quick Status Check**
- [ ] NetSentinel is running
- [ ] Dashboard is accessible
- [ ] Database is being populated
- [ ] Notifications are configured
- [ ] Logs are being generated

---

## 🔍 **1. System Status Verification**

### **Check if NetSentinel is Running**

**Windows:**
```powershell
# Check if main.py is running
Get-Process python | Where-Object {$_.CommandLine -like "*main.py*"}

# Or check the terminal where you ran it
# You should see: "NetSentinel IDS started..."
```

**Expected Output:**
```
NetSentinel IDS started...
Dashboard running on http://0.0.0.0:5000
```

---

## 🌐 **2. Web Dashboard Testing**

### **Test Steps:**

1. **Open Browser**
   - Navigate to: **http://localhost:5000**
   - Alternative: **http://127.0.0.1:5000**

2. **Verify Dashboard Elements:**
   - [ ] Page loads successfully
   - [ ] Statistics cards are visible (Total Alerts, High Severity, etc.)
   - [ ] Alert table is displayed
   - [ ] Search/filter functionality works
   - [ ] Dark theme is applied

3. **Test Dashboard Functionality:**
   ```powershell
   # Generate some test traffic to populate dashboard
   # Open another terminal and run:
   ping google.com -n 100
   ```

4. **Refresh Dashboard:**
   - Click "Refresh" button or reload page
   - Check if new alerts appear

### **Expected Results:**
✅ Dashboard loads without errors  
✅ Statistics update in real-time  
✅ Alerts are displayed in the table  
✅ UI is responsive and functional  

---

## 💾 **3. Database Testing**

### **Check Database File:**

```powershell
# Verify database exists
Test-Path "c:\Users\USER\OneDrive\Desktop\NetSentinel\netsentinel.db"

# Check database size (should be > 0 if alerts are stored)
(Get-Item "c:\Users\USER\OneDrive\Desktop\NetSentinel\netsentinel.db").Length
```

### **Query Database (Optional):**

```powershell
# Run the check_db.py script
python check_db.py
```

### **Expected Results:**
✅ Database file exists  
✅ Database size increases as alerts are generated  
✅ Alerts are being stored persistently  

---

## 🔔 **4. Notification System Testing**

### **A. Test All Channels at Once:**

```powershell
# Run the comprehensive test script
python test_notifications.py
```

### **Expected Output:**
```
============================================================
NetSentinel Notification System Test
============================================================

📡 Initializing notification manager...

✅ Active channels: email

🧪 Testing all notification channels...
------------------------------------------------------------
  Email        : ✅ Test email sent successfully
  Telegram     : ⚠️ Not configured
  Slack        : ⚠️ Not configured

📊 Test Results:
------------------------------------------------------------
============================================================
```

### **B. Test Individual Channels:**

#### **Email Testing:**
```powershell
# Test email alerts
python test_email.py
```

**What to Check:**
- [ ] Script runs without errors
- [ ] Check your email inbox (vamshijoshi450@gmail.com)
- [ ] Look for email with subject: "NetSentinel Test Alert"
- [ ] Verify email contains attack details

#### **Telegram Testing (if configured):**
1. Configure in `config.py`:
   ```python
   TELEGRAM_BOT_TOKEN = "your-token-here"
   TELEGRAM_CHAT_ID = "your-chat-id-here"
   ```
2. Run: `python test_notifications.py`
3. Check your Telegram for test message

#### **Slack Testing (if configured):**
1. Configure in `config.py`:
   ```python
   SLACK_WEBHOOK_URL = "your-webhook-url-here"
   ```
2. Run: `python test_notifications.py`
3. Check your Slack channel for test message

### **Expected Results:**
✅ Email alerts are received  
✅ Configured channels send test messages  
✅ No Python errors in terminal  

---

## 🎯 **5. Attack Detection Testing**

### **Test Each Detection Type:**

#### **A. Port Scan Detection**
```powershell
# Simulate port scan (requires nmap or similar)
# WARNING: Only test on your own machine!

# Simple test: Connect to multiple ports quickly
1..20 | ForEach-Object {
    Test-NetConnection -ComputerName localhost -Port $_ -WarningAction SilentlyContinue
}
```

**Expected:** Port scan alert triggered after 15+ unique ports

---

#### **B. DoS/Flood Detection**
```powershell
# Generate high packet volume
ping localhost -n 200 -l 1000
```

**Expected:** Flood alert triggered after threshold exceeded

---

#### **C. ICMP Flood Detection**
```powershell
# Generate ICMP traffic
ping google.com -n 50
```

**Expected:** ICMP flood alert if threshold exceeded

---

#### **D. SYN Flood Detection**
This requires specialized tools. For basic testing:
```powershell
# Generate TCP connections
1..10 | ForEach-Object {
    Test-NetConnection -ComputerName google.com -Port 80
}
```

**Expected:** SYN flood detection if pattern matches

---

#### **E. Brute Force Detection**
```powershell
# Simulate multiple connection attempts to SSH/RDP ports
# This is automatically detected if you have services running
```

**Expected:** Brute force alert after 10+ attempts in 60 seconds

---

### **Verify Detection:**

1. **Check Terminal Output:**
   - Look for alert messages in the terminal where `main.py` is running

2. **Check Dashboard:**
   - Refresh http://localhost:5000
   - Look for new alerts in the table

3. **Check Email:**
   - Verify you received email notifications

4. **Check Logs:**
   ```powershell
   Get-Content "logs\netsentinel.log" -Tail 50
   ```

---

## 📊 **6. SIEM Integration Testing**

### **If SIEM is Configured:**

1. **Configure SIEM in config.py:**
   ```python
   SYSLOG_HOST = "your-siem-server.com"
   SYSLOG_PORT = 514
   SYSLOG_PROTOCOL = "udp"
   ```

2. **Generate Test Alert:**
   - Trigger any attack detection
   - Check SIEM platform for incoming events

3. **Verify Formats:**
   - CEF format should be visible in SIEM
   - Syslog messages should be properly formatted

### **Expected Results:**
✅ Events appear in SIEM platform  
✅ CEF format is correctly parsed  
✅ Severity levels are mapped correctly  

---

## 📝 **7. Log File Testing**

### **Check Log Files:**

```powershell
# View recent logs
Get-Content "logs\netsentinel.log" -Tail 100

# Check log file size
(Get-Item "logs\netsentinel.log").Length
```

### **What to Look For:**
- [ ] Log file exists
- [ ] Timestamps are current
- [ ] No critical errors
- [ ] Detection events are logged
- [ ] Notification events are logged

### **Expected Log Entries:**
```
2026-02-08 14:50:00 - INFO - NetSentinel started
2026-02-08 14:50:01 - INFO - Dashboard running on http://0.0.0.0:5000
2026-02-08 14:51:00 - WARNING - Port scan detected from 192.168.1.100
2026-02-08 14:51:01 - INFO - Email alert sent successfully
```

---

## 🐳 **8. Deployment Testing (Optional)**

### **Docker Testing:**

```powershell
# Build Docker image
docker build -t netsentinel .

# Run container
docker-compose up -d

# Check logs
docker-compose logs -f

# Access dashboard
# Navigate to: http://localhost:5000

# Stop container
docker-compose down
```

### **Expected Results:**
✅ Docker image builds successfully  
✅ Container starts without errors  
✅ Dashboard is accessible  
✅ Logs show normal operation  

---

## 🔧 **9. Troubleshooting Common Issues**

### **Issue: Dashboard Not Loading**

**Solution:**
```powershell
# Check if Flask is running
netstat -ano | findstr :5000

# Check firewall
# Windows Firewall might be blocking port 5000
```

---

### **Issue: No Alerts Being Generated**

**Solution:**
```powershell
# Check if packets are being captured
# Look for "Processing packet" messages in logs

# Verify network interface
# In config.py, try setting: INTERFACE = None
```

---

### **Issue: Email Not Sending**

**Solution:**
1. Verify Gmail App Password (not regular password)
2. Check SMTP settings in config.py
3. Check firewall (port 587)
4. Run: `python test_email.py` for detailed error

---

### **Issue: Database Not Updating**

**Solution:**
```powershell
# Check database permissions
# Verify DB_PATH in config.py

# Delete and recreate database
Remove-Item netsentinel.db
# Restart NetSentinel
```

---

## ✅ **10. Complete System Test**

### **Full Integration Test:**

1. **Start NetSentinel:**
   ```powershell
   python main.py
   ```

2. **Open Dashboard:**
   - Browser: http://localhost:5000

3. **Generate Test Traffic:**
   ```powershell
   # In another terminal
   ping google.com -n 100
   ```

4. **Verify All Components:**
   - [ ] Terminal shows packet processing
   - [ ] Dashboard shows new alerts
   - [ ] Database is updated
   - [ ] Email notification received
   - [ ] Logs are updated

5. **Check Statistics:**
   - Dashboard should show:
     - Total alerts count
     - Severity breakdown
     - Unique IP addresses
     - Recent alerts in table

---

## 📊 **Success Criteria**

### **✅ System is Working If:**

1. ✅ **NetSentinel runs without crashes**
2. ✅ **Dashboard is accessible at http://localhost:5000**
3. ✅ **Database file exists and grows**
4. ✅ **At least one notification channel works**
5. ✅ **Alerts are detected and logged**
6. ✅ **Logs show normal operation**
7. ✅ **No critical errors in terminal**

---

## 🎯 **Quick Test Commands**

```powershell
# 1. Test notifications
python test_notifications.py

# 2. Test email specifically
python test_email.py

# 3. Check database
python check_db.py

# 4. View logs
Get-Content logs\netsentinel.log -Tail 50

# 5. Generate test traffic
ping google.com -n 100

# 6. Check dashboard
Start-Process "http://localhost:5000"
```

---

## 📞 **Getting Help**

If tests fail, check:
1. **Logs**: `logs\netsentinel.log`
2. **Configuration**: `config.py`
3. **Documentation**: `README.md`, `FEATURES.md`
4. **Terminal Output**: Look for error messages

---

## 🎉 **Test Results Template**

Copy and fill this out:

```
NetSentinel v2.0 Test Results
=============================
Date: _______________
Tester: _______________

[ ] System Running
[ ] Dashboard Accessible
[ ] Database Working
[ ] Email Notifications
[ ] Telegram Notifications (if configured)
[ ] Slack Notifications (if configured)
[ ] Port Scan Detection
[ ] DoS/Flood Detection
[ ] ICMP Flood Detection
[ ] SYN Flood Detection
[ ] Brute Force Detection
[ ] Logs Generated
[ ] SIEM Integration (if configured)

Overall Status: _______________
Notes: _______________
```

---

**🛡️ NetSentinel v2.0 - Your Network Security Guardian**
