import requests
import smtplib
import json
import time
import os
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# =========================================================
# CONFIGURATION
# =========================================================

APP_URL = os.getenv("APP_URL", "http://localhost:8000")
CHECK_INTERVAL_SECONDS = 60   # check every 60 seconds
ALERT_EMAIL = os.getenv("ALERT_EMAIL", "your@email.com")
SMTP_EMAIL = os.getenv("SMTP_EMAIL", "your@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "your_app_password")

# Thresholds — if any of these are exceeded, send an alert
THRESHOLDS = {
    "response_time_ms": 5000,   # alert if response takes > 5 seconds
    "error_rate_pct": 10,       # alert if > 10% of checks fail
    "consecutive_failures": 3,  # alert immediately after 3 failures in a row
}

# =========================================================
# STATE TRACKING
# =========================================================

stats = {
    "total_checks": 0,
    "total_failures": 0,
    "consecutive_failures": 0,
    "last_alert_time": None,
    "history": []
}

# =========================================================
# HEALTH CHECK
# =========================================================

def check_health():
    start = time.time()
    try:
        response = requests.get(f"{APP_URL}/health", timeout=10)
        elapsed_ms = round((time.time() - start) * 1000)

        if response.status_code == 200:
            return {
                "status": "healthy",
                "response_time_ms": elapsed_ms,
                "status_code": 200,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "status": "unhealthy",
                "response_time_ms": elapsed_ms,
                "status_code": response.status_code,
                "error": f"Unexpected status code: {response.status_code}",
                "timestamp": datetime.now().isoformat()
            }

    except requests.exceptions.Timeout:
        return {
            "status": "unhealthy",
            "response_time_ms": 10000,
            "error": "Request timed out after 10 seconds",
            "timestamp": datetime.now().isoformat()
        }
    except requests.exceptions.ConnectionError:
        return {
            "status": "unhealthy",
            "response_time_ms": 0,
            "error": "Could not connect to app — is it running?",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "response_time_ms": 0,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# =========================================================
# ALERTING
# =========================================================

def send_alert(subject, body):
    # Don't spam alerts — wait 30 minutes between them
    if stats["last_alert_time"]:
        minutes_since_last = (time.time() - stats["last_alert_time"]) / 60
        if minutes_since_last < 30:
            print(f"  [Alert suppressed — sent {round(minutes_since_last)}min ago]")
            return

    try:
        msg = MIMEMultipart()
        msg["From"] = SMTP_EMAIL
        msg["To"] = ALERT_EMAIL
        msg["Subject"] = f"🚨 AI Meal Coach Alert: {subject}"

        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.send_message(msg)

        stats["last_alert_time"] = time.time()
        print(f"  [Alert sent to {ALERT_EMAIL}]")

    except Exception as e:
        print(f"  [Failed to send alert: {e}]")

def build_alert_body(check_result, reason):
    recent = stats["history"][-5:] if stats["history"] else []
    history_text = "\n".join([
        f"  {h['timestamp']}: {h['status']} ({h.get('response_time_ms', 0)}ms)"
        for h in recent
    ])

    return f"""
AI Meal Coach — Automated Health Alert
=======================================
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Reason: {reason}

Latest check result:
  Status: {check_result['status']}
  Response time: {check_result.get('response_time_ms', 'N/A')}ms
  Error: {check_result.get('error', 'None')}

Recent history (last 5 checks):
{history_text}

Stats:
  Total checks: {stats['total_checks']}
  Total failures: {stats['total_failures']}
  Consecutive failures: {stats['consecutive_failures']}
  Error rate: {round(stats['total_failures']/max(stats['total_checks'],1)*100, 1)}%

Action needed:
  1. Check if the app is still running
  2. Check Google Cloud Run logs for errors
  3. Check if USDA API or BLIP-2 is causing timeouts

— AI Meal Coach Monitor
"""

# =========================================================
# ANALYSIS — this is the "predict before users notice" part
# =========================================================

def analyze_trends():
    if len(stats["history"]) < 5:
        return None   # not enough data yet

    recent = stats["history"][-5:]

    # Check if response times are trending upward (early warning sign)
    times = [h.get("response_time_ms", 0) for h in recent if h["status"] == "healthy"]
    if len(times) >= 3:
        # Simple trend: is each reading higher than the last?
        trending_up = all(times[i] < times[i+1] for i in range(len(times)-1))
        if trending_up and times[-1] > 2000:
            return f"Response time trending upward: {' → '.join(str(t)+'ms' for t in times)} — may become slow for users soon"

    # Check if we're seeing intermittent failures (not consecutive, but frequent)
    recent_failures = sum(1 for h in recent if h["status"] == "unhealthy")
    if recent_failures >= 2:
        return f"{recent_failures}/5 recent checks failed — intermittent instability detected"

    return None

# =========================================================
# MAIN LOOP
# =========================================================

def run_monitor():
    print(f"Starting AI Meal Coach health monitor")
    print(f"Checking: {APP_URL}")
    print(f"Interval: every {CHECK_INTERVAL_SECONDS} seconds")
    print(f"Alerts → {ALERT_EMAIL}")
    print("=" * 50)

    while True:
        result = check_health()
        stats["total_checks"] += 1
        stats["history"].append(result)

        # Keep only last 100 checks in memory
        if len(stats["history"]) > 100:
            stats["history"].pop(0)

        # Print status
        status_icon = "✅" if result["status"] == "healthy" else "❌"
        print(f"{status_icon} [{result['timestamp'][:19]}] "
              f"{result['status'].upper()} — "
              f"{result.get('response_time_ms', 0)}ms"
              + (f" — {result.get('error', '')}" if result["status"] == "unhealthy" else ""))

        # Track failures
        if result["status"] == "unhealthy":
            stats["total_failures"] += 1
            stats["consecutive_failures"] += 1

            # Alert immediately after N consecutive failures
            if stats["consecutive_failures"] >= THRESHOLDS["consecutive_failures"]:
                send_alert(
                    "App is down",
                    build_alert_body(result,
                        f"{stats['consecutive_failures']} consecutive failures detected")
                )
        else:
            stats["consecutive_failures"] = 0

            # Alert if response time too high
            if result["response_time_ms"] > THRESHOLDS["response_time_ms"]:
                send_alert(
                    "Slow response time",
                    build_alert_body(result,
                        f"Response took {result['response_time_ms']}ms "
                        f"(threshold: {THRESHOLDS['response_time_ms']}ms)")
                )

        # Check error rate
        error_rate = stats["total_failures"] / stats["total_checks"] * 100
        if error_rate > THRESHOLDS["error_rate_pct"] and stats["total_checks"] > 10:
            send_alert(
                "High error rate",
                build_alert_body(result,
                    f"Error rate is {round(error_rate, 1)}% "
                    f"(threshold: {THRESHOLDS['error_rate_pct']}%)")
            )

        # Trend analysis — predict problems before users notice
        trend_warning = analyze_trends()
        if trend_warning:
            print(f"  ⚠ TREND WARNING: {trend_warning}")
            send_alert("Early warning — potential issue developing",
                      build_alert_body(result, trend_warning))

        # Save stats to file so you can check them anytime
        with open("monitoring/stats.json", "w") as f:
            json.dump({
                "last_check": result,
                "total_checks": stats["total_checks"],
                "total_failures": stats["total_failures"],
                "error_rate_pct": round(error_rate, 1),
                "consecutive_failures": stats["consecutive_failures"],
            }, f, indent=2)

        time.sleep(CHECK_INTERVAL_SECONDS)

if __name__ == "__main__":
    os.makedirs("monitoring", exist_ok=True)
    run_monitor()