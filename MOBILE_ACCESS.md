# Access PARIVESH monitor from your phone

## Does it run only when my laptop is on?

**Yes.** If you run the monitor on your laptop (e.g. `python run_every_second.py` or the scheduled task), it runs **only when the laptop is on** and the script is running.

To have it run **24/7** and still use a phone shortcut, use the **web monitor** and either keep it on your laptop when you’re home, or deploy it to a free cloud server (see below).

---

## Option 1: Web dashboard on your laptop (phone on same Wi‑Fi)

1. Install Flask (once):
   ```powershell
   cd v:\PARIVESH
   pip install flask
   ```
2. Start the web monitor:
   ```powershell
   python web_monitor.py
   ```
3. On your **laptop**: open **http://localhost:5000**
4. On your **phone** (same Wi‑Fi):
   - Find your laptop’s IP: on the laptop run `ipconfig` and note **IPv4 Address** (e.g. `192.168.1.5`)
   - On the phone browser open: **http://192.168.1.5:5000** (use your laptop’s IP)
5. **Add to home screen:** On the phone, in the browser menu choose **Add to Home screen** or **Add shortcut**. You’ll get an icon that opens the dashboard.

The page shows:
- Whether the monitor is running
- Last check time
- Last SMS alert (if any)
- Link to the PARIVESH portal

**Note:** This works only when the laptop is on and `python web_monitor.py` is running.

---

## Option 2: 24/7 + phone shortcut (deploy to cloud)

To have the monitor run **all the time** and open the same dashboard from your phone **anywhere**:

1. Deploy the app to a free “always on” host, for example:
   - **Render** (render.com): free Web Service, set root to `v:\PARIVESH`, start command: `python web_monitor.py`, add env vars (see below).
   - **PythonAnywhere** (pythonanywhere.com): free account, upload project, set env vars, run `web_monitor.py` as a always-on task or web app.
2. In the cloud dashboard, set these **environment variables** (same as `.env`):
   - `PHONE_NUMBER=919940944929`
   - `TWILIO_ACCOUNT_SID=...`
   - `TWILIO_AUTH_TOKEN=...`
   - `TWILIO_FROM_NUMBER=+19786164278`
   - Optional: `CHECK_INTERVAL_SECONDS=60` (checks every 60 seconds when running 24/7)
3. The host will give you a URL, e.g. `https://your-app.onrender.com`
4. On your **phone**, open that URL and use **Add to Home screen** so you have a shortcut that works anytime.

Then the monitor runs 24/7 on the cloud and you can open the same status page from your phone at any time.

---

## Quick summary

| Setup | When it runs | Phone shortcut |
|--------|----------------|-----------------|
| Laptop: `python run_every_second.py` | Only when laptop is on | No web page |
| Laptop: `python web_monitor.py` | Only when laptop is on | Yes: http://&lt;laptop-IP&gt;:5000 (same Wi‑Fi) |
| Cloud (e.g. Render): `web_monitor.py` | 24/7 | Yes: https://your-app.onrender.com (anywhere) |
