# Upload to GitHub without Git (if Git is not installed)

Your repo: **https://github.com/VIGNESH-1996-A/parivesh-monitor**

1. Open: https://github.com/VIGNESH-1996-A/parivesh-monitor  
2. If the repo is empty, click **“uploading an existing file”** (or **Add file** → **Upload files**).  
3. From **v:\PARIVESH** drag these files/folders (do **not** upload **.env** — it has secrets):

   - `config.py`
   - `parivesh_monitor.py`
   - `web_monitor.py`
   - `run_every_second.py`
   - `requirements.txt`
   - `Procfile`
   - `render.yaml`
   - `runtime.txt`
   - `.gitignore`
   - `.env.example`
   - `GET_24_7_LINK.md`
   - `MOBILE_ACCESS.md`
   - `README.md`
   - `SETUP_GUIDE.md`
   - `STEP5_TWILIO.md`
   - `schedule_daily.ps1`
   - `schedule_every_second.ps1`
   - `START_WEB_MONITOR.bat`

4. Add commit message: **Deploy PARIVESH monitor** → **Commit changes**.

After this, go to **Render.com** → your service (or create one from this repo) → **Manual Deploy** or wait for auto-deploy. Add the env vars (PHONE_NUMBER, TWILIO_*) in Render **Environment** — copy from your **.env** file; do not put .env in GitHub.
