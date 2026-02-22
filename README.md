# PARIVESH 2.0 EC Agenda & MoM SMS Notifications

Sends an **SMS to 9940944929** whenever a new **Agenda** or **Minutes of Meeting (MoM)** for Environmental Clearance is updated on **PARIVESH 2.0** for:

- **Tamil Nadu**
- **Karnataka**
- **Telangana**

**Sources:** [EC Agenda list](https://parivesh.nic.in/#/ec-agenda-list) and [EC MoM list](https://parivesh.nic.in/#/ec-mom-list) on [parivesh.nic.in](https://parivesh.nic.in).

## How it works

1. The script periodically fetches the PARIVESH 2.0 pages (agenda and MoM lists) and looks for new or changed content.
2. It filters for Tamil Nadu, Karnataka, and Telangana and compares with the last saved state.
3. If it detects a change (new or updated agenda/MoM), it sends an SMS to your number via Twilio.

## Setup

### 1. Install Python

Use Python 3.8 or newer.

### 2. Install dependencies

```bash
cd v:\PARIVESH
pip install -r requirements.txt
```

### 3. Configure environment

Copy the example env file and add your Twilio credentials:

```bash
copy .env.example .env
```

Edit `.env`:

- **PHONE_NUMBER** – Already set to `919940944929`. Change only if you want a different number.
- **TWILIO_ACCOUNT_SID** – From [Twilio Console](https://console.twilio.com).
- **TWILIO_AUTH_TOKEN** – From Twilio Console.
- **TWILIO_FROM_NUMBER** – Your Twilio phone number (e.g. `+1234567890`). For SMS to India you need an Indian number or an international Twilio number that can send to India.

### 4. Run the monitor

**One-time check:**

```bash
python parivesh_monitor.py
```

**Automated runs (Windows Task Scheduler):**

1. Open **Task Scheduler**.
2. Create Basic Task → Name: e.g. "PARIVESH EC Monitor" → Trigger: **Daily** (or every few hours).
3. Action: **Start a program**  
   - Program: `python` (or full path to `python.exe`)  
   - Arguments: `v:\PARIVESH\parivesh_monitor.py`  
   - Start in: `v:\PARIVESH`
4. Save. The task will run at the set time and send SMS only when a new agenda/MoM is detected.

**Run every 6 hours (PowerShell one-liner to create a scheduled task):**

```powershell
$action = New-ScheduledTaskAction -Execute "python" -Argument "v:\PARIVESH\parivesh_monitor.py" -WorkingDirectory "v:\PARIVESH"
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 6) -RepetitionDuration (New-TimeSpan -Days 365)
Register-ScheduledTask -TaskName "PARIVESH_EC_Monitor" -Action $action -Trigger $trigger
```

## State IDs

The script uses these state IDs for the portal URLs:

- Tamil Nadu: 33  
- Karnataka: 29  
- Telangana: 36  

If a state’s page doesn’t load or doesn’t match your state, check the PARIVESH portal for the correct `state_id` and update `config.py` → `STATES_TO_MONITOR`.

## Files

- `parivesh_monitor.py` – Main script: fetch pages, detect changes, send SMS.
- `config.py` – Phone number, state list, Twilio env vars, state file path.
- `parivesh_last_state.json` – Created automatically; stores last known content so only **new** updates trigger SMS.

## SMS provider

This setup uses **Twilio**. For SMS to Indian numbers you need either:

- A Twilio number that can send to India, or  
- Another provider (e.g. MSG91) – you’d need to replace the `send_sms()` implementation in `parivesh_monitor.py` with that provider’s API.
