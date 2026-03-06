"""
Web dashboard for PARIVESH monitor - open from your phone or browser.
Shows status and runs the monitor in the background.
"""
from __future__ import annotations

import os
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path

from flask import Flask, render_template_string

# Load .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

app = Flask(__name__)

# Status stored in memory (and optional file for persistence across restarts)
STATUS_FILE = Path(__file__).resolve().parent / "monitor_status.txt"
last_check_time = None
last_alert = None
last_error = None
is_running = False
check_interval = int(os.getenv("CHECK_INTERVAL_SECONDS", "60"))  # 60 when 24/7; use 1 for fastest

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>PARIVESH Monitor</title>
  <style>
    * { box-sizing: border-box; }
    body { font-family: system-ui, sans-serif; margin: 0; padding: 16px; background: #0f172a; color: #e2e8f0; min-height: 100vh; }
    .card { background: #1e293b; border-radius: 12px; padding: 20px; margin-bottom: 16px; }
    h1 { margin: 0 0 8px; font-size: 1.5rem; color: #38bdf8; }
    .badge { display: inline-block; padding: 4px 10px; border-radius: 20px; font-size: 0.85rem; font-weight: 600; }
    .badge-running { background: #22c55e; color: #fff; }
    .badge-stopped { background: #64748b; color: #fff; }
    .meta { color: #94a3b8; font-size: 0.9rem; margin-top: 12px; }
    a { color: #38bdf8; }
    .alert { background: #422006; border-left: 4px solid #f59e0b; padding: 12px; border-radius: 8px; margin-top: 12px; }
  </style>
</head>
<body>
  <div class="card">
    <h1>PARIVESH EC Monitor</h1>
    <p>TN, Karnataka, Telangana — Agenda & MoM → SMS to 9940944929</p>
    <p class="meta" style="margin-bottom: 12px;">
      <strong>24×7 monitoring.</strong> You receive an automated SMS from Twilio <strong>only when</strong> a new agenda or minutes (MoM) is uploaded on PARIVESH for these states.
    </p>
    <p>
      <span class="badge badge-{{ badge }}">{{ status_label }}</span>
    </p>
    <p class="meta">Last check: {{ last_check }}</p>
    {% if last_alert %}
    <div class="alert"><strong>Last alert:</strong> {{ last_alert }}</div>
    {% endif %}
    {% if last_error %}
    <div class="alert" style="border-color: #ef4444;"><strong>Error:</strong> {{ last_error }}</div>
    {% endif %}
    <p class="meta" style="margin-top: 16px;">
      <a href="https://parivesh.nic.in/#/ec-agenda-list" target="_blank">EC Agenda (PARIVESH 2.0)</a><br>
      <a href="https://parivesh.nic.in/#/ec-mom-list" target="_blank">EC MoM (PARIVESH 2.0)</a>
    </p>
  </div>
</body>
</html>
"""


def monitor_loop():
    global last_check_time, last_alert, last_error, is_running
    from parivesh_monitor import run_check
    is_running = True
    while True:
        try:
            run_check()
            last_check_time = datetime.utcnow()
            last_error = None
        except Exception as e:
            last_error = str(e)
        time.sleep(check_interval)


def load_last_alert():
    global last_alert
    if STATUS_FILE.exists():
        try:
            last_alert = STATUS_FILE.read_text(encoding="utf-8").strip() or None
        except Exception:
            pass


def save_last_alert(text: str):
    global last_alert
    last_alert = text
    try:
        STATUS_FILE.write_text(text, encoding="utf-8")
    except Exception:
        pass


@app.route("/")
def index():
    load_last_alert()
    if last_check_time:
        ist_time = last_check_time + timedelta(hours=5, minutes=30)
        last_str = ist_time.strftime("%Y-%m-%d %H:%M IST")
    else:
        last_str = "Never"
    return render_template_string(
        HTML_PAGE,
        status_label="Running" if is_running else "Starting…",
        badge="running" if is_running else "stopped",
        last_check=last_str,
        last_alert=last_alert,
        last_error=last_error,
    )


@app.route("/ping")
def ping():
    """Cron/health endpoint: also runs one monitor cycle so Last check updates even if threads sleep."""
    global last_check_time, last_error, is_running
    try:
        import parivesh_monitor as pm

        pm.run_check()
        last_check_time = datetime.utcnow()
        last_error = None
        is_running = True
        return "OK", 200
    except Exception as e:
        last_error = str(e)
        return f"ERROR: {e}", 500


def start_background_monitor():
    """Start monitor thread and patch SMS to record last alert. Called on import (gunicorn) or in main()."""
    global last_alert
    load_last_alert()
    import parivesh_monitor as pm
    _orig_send = pm.send_sms
    def _send(body):
        save_last_alert(body[:300] + "…" if len(body) > 300 else body)
        return _orig_send(body)
    pm.send_sms = _send
    t = threading.Thread(target=monitor_loop, daemon=True)
    t.start()


# Start monitor when module is loaded (for gunicorn on Render)
start_background_monitor()


def main():
    port = int(os.getenv("PORT", "5000"))
    host = os.getenv("HOST", "0.0.0.0")
    print(f"PARIVESH monitor dashboard: http://localhost:{port}")
    print("On your phone (same WiFi): use your laptop IP and this port, e.g. http://192.168.1.x:5000")
    app.run(host=host, port=port, debug=False, use_reloader=False)


if __name__ == "__main__":
    main()
