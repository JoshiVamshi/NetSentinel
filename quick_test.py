# quick_test.py
"""
Quick system health check for NetSentinel v2.0
Run this to verify all components are working
"""

import os
import sqlite3
import requests
from datetime import datetime

def print_header(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def print_result(component, status, details=""):
    icon = "✅" if status else "❌"
    print(f"{icon} {component:30} {details}")

def main():
    print_header("🛡️ NetSentinel v2.0 - Quick Health Check")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    
    # 1. Check if database exists
    print_header("1. Database Check")
    db_exists = os.path.exists("netsentinel.db")
    print_result("Database File", db_exists)
    
    if db_exists:
        try:
            conn = sqlite3.connect("netsentinel.db")
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM alerts")
            alert_count = cursor.fetchone()[0]
            print_result("Alert Count", True, f"{alert_count} alerts stored")
            
            # Get recent alerts
            cursor.execute("SELECT attack_type, COUNT(*) FROM alerts GROUP BY attack_type")
            attack_types = cursor.fetchall()
            if attack_types:
                print("\n  Attack Types Detected:")
                for attack_type, count in attack_types:
                    print(f"    • {attack_type}: {count}")
            
            conn.close()
            results['database'] = True
        except Exception as e:
            print_result("Database Query", False, str(e))
            results['database'] = False
    else:
        results['database'] = False
    
    # 2. Check if dashboard is accessible
    print_header("2. Dashboard Check")
    try:
        response = requests.get("http://localhost:5000", timeout=3)
        dashboard_ok = response.status_code == 200
        print_result("Dashboard (Port 5000)", dashboard_ok, 
                    f"Status: {response.status_code}")
        results['dashboard'] = dashboard_ok
    except requests.exceptions.ConnectionError:
        print_result("Dashboard (Port 5000)", False, "Not accessible - Is main.py running?")
        results['dashboard'] = False
    except Exception as e:
        print_result("Dashboard (Port 5000)", False, str(e))
        results['dashboard'] = False
    
    # 3. Check log file
    print_header("3. Logging Check")
    log_exists = os.path.exists("logs/netsentinel.log")
    print_result("Log File", log_exists)
    
    if log_exists:
        try:
            with open("logs/netsentinel.log", "r") as f:
                lines = f.readlines()
                log_size = len(lines)
                print_result("Log Entries", True, f"{log_size} lines")
                
                # Show last 3 log entries
                print("\n  Recent Log Entries:")
                for line in lines[-3:]:
                    print(f"    {line.strip()[:80]}")
            results['logs'] = True
        except Exception as e:
            print_result("Log Read", False, str(e))
            results['logs'] = False
    else:
        results['logs'] = False
    
    # 4. Check configuration
    print_header("4. Configuration Check")
    try:
        import config
        
        # Email config
        email_configured = (
            config.SMTP_USER and 
            config.SMTP_PASSWORD and 
            config.ALERT_TO
        )
        print_result("Email Notifications", email_configured,
                    f"To: {config.ALERT_TO if email_configured else 'Not configured'}")
        
        # Telegram config
        telegram_configured = (
            config.TELEGRAM_BOT_TOKEN and 
            config.TELEGRAM_CHAT_ID
        )
        print_result("Telegram Notifications", telegram_configured,
                    "Configured" if telegram_configured else "Not configured")
        
        # Slack config
        slack_configured = bool(config.SLACK_WEBHOOK_URL)
        print_result("Slack Notifications", slack_configured,
                    "Configured" if slack_configured else "Not configured")
        
        # SIEM config
        siem_configured = bool(config.SYSLOG_HOST)
        print_result("SIEM Integration", siem_configured,
                    f"Host: {config.SYSLOG_HOST}" if siem_configured else "Not configured")
        
        results['config'] = True
    except Exception as e:
        print_result("Configuration", False, str(e))
        results['config'] = False
    
    # Summary
    print_header("📊 Summary")
    
    total_checks = len(results)
    passed_checks = sum(1 for v in results.values() if v)
    
    print(f"\n  Passed: {passed_checks}/{total_checks} checks")
    
    if passed_checks == total_checks:
        print("\n  🎉 All systems operational!")
        print("  ✅ NetSentinel v2.0 is working correctly")
    elif passed_checks > 0:
        print(f"\n  ⚠️  {passed_checks}/{total_checks} systems working")
        print("  Some components need attention")
    else:
        print("\n  ❌ System not operational")
        print("  Please check if NetSentinel is running (python main.py)")
    
    print_header("🔗 Quick Actions")
    print("\n  Dashboard:  http://localhost:5000")
    print("  Test Email: python test_email.py")
    print("  Test All:   python test_notifications.py")
    print("  View Logs:  Get-Content logs\\netsentinel.log -Tail 50")
    print("\n" + "=" * 60 + "\n")

if __name__ == "__main__":
    main()
