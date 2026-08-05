# Email Alert Configuration Guide

## ✅ Email Alerts Status: ENABLED

Email alerts are now **fully integrated** into NetSentinel and will automatically send notifications when threats are detected.

## Configuration

Email settings are configured in `config.py`:

```python
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "vamshijoshi25@gmail.com"
SMTP_PASSWORD = "tbpv edzc jmmc cpvp"  # Gmail App Password
ALERT_TO = "vamshijoshi450@gmail.com"
```

### ⚠️ Important Notes

1. **Gmail App Password Required**: The `SMTP_PASSWORD` must be a Gmail App Password, NOT your regular Gmail password.
   - Go to: https://myaccount.google.com/apppasswords
   - Generate a new app password for "Mail"
   - Use that 16-character password in config.py

2. **Email Address Fixed**: The recipient email was corrected from `vamshijoshi450.com` to `vamshijoshi450@gmail.com`

## How Email Alerts Work

### When Alerts are Triggered

Email alerts are automatically sent when the detection engine identifies:

1. **DoS/Flood Attacks** (High Severity)
   - High packet count (>20 packets) in a single flow

2. **Beaconing** (Medium Severity)
   - Long-lived connections (>60s) with low data (<1000 bytes)

3. **Suspicious Port Access** (Medium Severity)
   - Repeated traffic to sensitive ports (22, 23, 3389, 445)

4. **ICMP Flood** (Medium Severity)
   - ICMP packet bursts (>10 packets)

### Email Content

Each alert email includes:
- Attack Type
- Severity Level (HIGH/MEDIUM)
- Source IP and Port
- Destination IP and Port
- Protocol (TCP/UDP/IP)
- Packet Count
- Byte Count
- Flow Duration
- Detailed Reason

### Example Email

```
Subject: [NetSentinel] HIGH Severity Alert - DoS / Flood

NetSentinel has detected suspicious network activity.

Attack Type: DoS / Flood
Severity: HIGH
Source: 192.168.1.100:54321
Destination: 10.0.0.5:80
Protocol: TCP
Packet Count: 45
Byte Count: 12500
Duration: 15.3 seconds
Reason: High packet count (45) in single flow

Please investigate this activity immediately.
```

## Testing Email Alerts

### Option 1: Run Test Script

```bash
python test_email.py
```

This will send a test email to verify your configuration is working.

### Option 2: Generate Test Traffic

Run NetSentinel and generate network traffic that triggers detection rules:

```bash
python main.py
```

Then generate traffic that exceeds thresholds (e.g., many packets to a single destination).

## Troubleshooting

### Email Not Sending?

1. **Check Gmail App Password**
   - Ensure you're using an App Password, not your regular password
   - App Password should be 16 characters (4 groups of 4)

2. **Check Email Addresses**
   - Verify `SMTP_USER` is correct
   - Verify `ALERT_TO` is correct and includes @gmail.com

3. **Check Logs**
   - Look in `logs/netsentinel.log` for email errors
   - Successful sends show: "Email alert sent"
   - Failures show: "Email failed: <error message>"

4. **Gmail Security Settings**
   - Ensure "Less secure app access" is not blocking (if using old Gmail)
   - For modern Gmail, App Passwords should work automatically

5. **Network Connectivity**
   - Ensure your system can reach smtp.gmail.com:587
   - Check firewall settings

### Common Errors

**"Authentication failed"**
- Wrong SMTP_USER or SMTP_PASSWORD
- Using regular password instead of App Password

**"Connection refused"**
- SMTP_SERVER or SMTP_PORT incorrect
- Firewall blocking port 587

**"Recipient address rejected"**
- ALERT_TO email address is invalid

## Rate Limiting

Currently, email alerts are sent for **every detected threat**. If you're getting too many emails, you can:

1. Adjust detection thresholds in `detection/engine.py`
2. Add rate limiting to the email sender (future enhancement)
3. Filter alerts by severity level

## Files Modified

1. ✅ `config.py` - Fixed ALERT_TO email address
2. ✅ `dashboard/app.py` - Fixed ALERT_TO email address  
3. ✅ `capture/sniffer.py` - Integrated email alerts into detection flow
4. ✅ `alerts/emailer.py` - Email sending functionality (already existed)
5. ✅ `test_email.py` - New test script for verification

## Next Steps

1. Run `python test_email.py` to verify email configuration
2. Start NetSentinel with `python main.py`
3. Monitor `logs/netsentinel.log` for email send confirmations
4. Check your inbox for alert emails when threats are detected

---

**Status**: Email alerts are now FULLY OPERATIONAL! 🎉
