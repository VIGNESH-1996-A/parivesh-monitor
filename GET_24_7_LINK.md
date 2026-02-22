# Get your 24/7 web link (≈10 minutes)

Follow these steps once. After that you’ll have a link like **https://parivesh-monitor-xxxx.onrender.com** to open on your phone anytime, and the monitor will run 24/7 even when your laptop is off.

---

## Step 1: Put the project on GitHub

1. Go to **https://github.com** and sign in (or create an account).
2. Click **+** → **New repository**.
3. Name: `parivesh-monitor`. Set to **Public**. Click **Create repository**.
4. On your PC, open PowerShell in `v:\PARIVESH` and run:

   ```powershell
   cd v:\PARIVESH
   git init
   git add .
   git commit -m "PARIVESH monitor 24/7"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/parivesh-monitor.git
   git push -u origin main
   ```
   Replace **YOUR_USERNAME** with your GitHub username. If Git asks for login, use a **Personal Access Token** (GitHub → Settings → Developer settings → Personal access tokens) instead of your password.

---

## Step 2: Deploy on Render

1. Go to **https://render.com** and sign up (or log in). Use **Sign up with GitHub**.
2. Click **Dashboard** → **New +** → **Web Service**.
3. **Connect a repository**: choose **parivesh-monitor** (or connect GitHub if needed and select the repo).
4. Use these settings:
   - **Name:** `parivesh-monitor` (or any name; this becomes part of your URL).
   - **Region:** choose closest to you.
   - **Branch:** `main`.
   - **Root Directory:** leave blank.
   - **Runtime:** Python 3.
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 2 web_monitor:app`
5. Click **Advanced** and add **Environment Variables** (same as your `.env`):

   | Key                 | Value              |
   |---------------------|--------------------|
   | PHONE_NUMBER        | 919940944929       |
   | TWILIO_ACCOUNT_SID  | (from your .env) |
   | TWILIO_AUTH_TOKEN   | (from your .env) |
   | TWILIO_FROM_NUMBER  | +19786164278       |
   | CHECK_INTERVAL_SECONDS | 60              |

6. Click **Create Web Service**. Wait until the first deploy finishes (status **Live**).
7. Your link is at the top, e.g. **https://parivesh-monitor-xxxx.onrender.com**. This is your 24/7 link.

---

## Step 3: Keep it awake 24/7 (free tier)

On Render’s free tier, the app sleeps after about 15 minutes with no visits. To keep it running 24/7:

1. Go to **https://cron-job.org** and create a free account.
2. Create a new cron job:
   - **URL:** `https://parivesh-monitor-xxxx.onrender.com/ping` (use your real Render URL + `/ping`).
   - **Interval:** every **10 minutes**.
3. Save. This will open your app every 10 minutes so it stays awake and the monitor keeps checking.

---

## Step 4: Use the link on your phone

1. On your phone, open the browser and go to your link: **https://parivesh-monitor-xxxx.onrender.com**.
2. Add it to your home screen: in the browser menu choose **Add to Home screen** or **Add shortcut**. You’ll get an icon that opens the dashboard anytime.

---

## Your link

After Step 2, your link will look like:

**https://parivesh-monitor-xxxx.onrender.com**

(You’ll see the exact URL in the Render dashboard after the first deploy.)

Only you can create the Render and GitHub accounts and add your Twilio token, so you need to do these steps yourself. Once done, the monitor runs 24/7 and you can use this link from your phone anytime.
