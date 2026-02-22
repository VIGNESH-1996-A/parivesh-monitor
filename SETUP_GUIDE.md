# Step-by-step setup: PARIVESH SMS notifications to 9940944929

Follow these steps in order.

---

## Step 1: Check Python is installed

1. Open **PowerShell** or **Command Prompt** (in Cursor: **Terminal → New Terminal**, or press **Ctrl + `**).
2. Type:
   ```powershell
   python --version
   ```
3. You should see something like `Python 3.10.x` or `Python 3.11.x`.  
   - If you see "not recognized", [download and install Python](https://www.python.org/downloads/) and tick **"Add Python to PATH"** during setup, then close and reopen the terminal.

---

## Step 2: Go to the project folder

In the same terminal, run:

```powershell
cd v:\PARIVESH
```

---

## Step 3: Install required packages

Run:

```powershell
pip install -r requirements.txt
```

Wait until it finishes. If you see an error like "pip is not recognized", try:

```powershell
python -m pip install -r requirements.txt
```

---

## Step 4: Get a Twilio account (for sending SMS)

1. Go to **[https://www.twilio.com](https://www.twilio.com)** and sign up (free account is enough).
2. After login, open the **Twilio Console** (dashboard).
3. Note these three things (you’ll use them in Step 5):
   - **Account SID** (e.g. `ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`)
   - **Auth Token** (click "Show" to see it)
   - A **Phone Number**: Console → **Phone Numbers → Manage → Buy a number** (or use a trial number; for India you may need a number that can send to India or use trial limits).

---

## Step 5: Create your `.env` file

1. In File Explorer, go to **v:\PARIVESH**.
2. Find the file **`.env.example`**.
3. **Copy** it and **paste** in the same folder. Rename the copy to **`.env`** (remove `.example`).
4. Open **`.env`** in Notepad or Cursor.
5. Replace the placeholder values with your real values (keep the format exactly as below):

   ```env
   PHONE_NUMBER=919940944929
   TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   TWILIO_AUTH_TOKEN=your_auth_token_here
   TWILIO_FROM_NUMBER=+15551234567
   ```

   - `PHONE_NUMBER` is already set for **9940944929** (with country code 91). Don’t add a `+`.
   - `TWILIO_FROM_NUMBER` must include the `+` (e.g. `+15551234567` or your Twilio Indian number).
6. **Save** the file and close it.

---

## Step 6: Run the monitor once

In the terminal (still in `v:\PARIVESH`), run:

```powershell
python parivesh_monitor.py
```

- First run only **saves** the current state; it usually **won’t** send an SMS.
- If you see **"SMS skipped"**, check that `.env` has the correct Twilio values and no extra spaces.
- If you see **"No new agenda/MoM updates detected"**, the script ran correctly; SMS will be sent on a **later** run when something new appears on the portal.

---

## Step 7 (Optional): Run automatically every few hours

1. Press **Win + R**, type **`taskschd.msc`**, press Enter (opens Task Scheduler).
2. Click **Create Basic Task**.
3. **Name:** e.g. `PARIVESH EC Monitor` → **Next**.
4. **Trigger:** Daily → **Next**.
5. **Start:** today’s date, time e.g. 9:00 AM → **Next**.
6. **Action:** Start a program → **Next**.
7. **Program/script:** `python`  
   **Add arguments:** `v:\PARIVESH\parivesh_monitor.py`  
   **Start in:** `v:\PARIVESH`  
   → **Next** → **Finish**.
8. To run every 6 hours: right‑click the task → **Properties** → **Triggers** → **Edit** → tick **Repeat task every** → choose **6 hours** → **OK** → **OK**.

---

## Quick reference

| Step | What to do |
|------|------------|
| 1 | `python --version` – check Python |
| 2 | `cd v:\PARIVESH` |
| 3 | `pip install -r requirements.txt` |
| 4 | Sign up at twilio.com, get SID, Auth Token, and a phone number |
| 5 | Copy `.env.example` to `.env`, fill in Twilio values and save |
| 6 | `python parivesh_monitor.py` |
| 7 | (Optional) Create scheduled task to run the script every 6–12 hours |

After this, whenever the script runs and finds a **new** agenda or MoM for Tamil Nadu, Karnataka, or Telangana on PARIVESH, it will send an SMS to **9940944929**.
