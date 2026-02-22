"""
Configuration for PARIVESH agenda/MoM monitor.
States: Tamil Nadu, Karnataka, Telangana (Environmental Clearance).
"""
import os
from pathlib import Path

# Your phone number for SMS alerts (with country code, no +)
PHONE_NUMBER = os.getenv("PHONE_NUMBER", "919940944929")

# PARIVESH portal base URLs
BASE_URL = "https://environmentclearance.nic.in"
MEETING_SCHEDULE_URL = f"{BASE_URL}/report/meeting_schedule.aspx"

# State-wise SEIAA meeting schedule (agenda & MoM). state_id values may vary; adjust if links don't work.
# Common NIC state codes: Tamil Nadu 33, Karnataka 29, Telangana 36
STATES_TO_MONITOR = [
    {"name": "Tamil Nadu", "state_id": "33"},
    {"name": "Karnataka", "state_id": "29"},
    {"name": "Telangana", "state_id": "36"},
]

def get_state_meeting_url(state_id: str) -> str:
    return f"{BASE_URL}/report/meeting_schedule_b.aspx?state_id={state_id}"

# File to store last known agenda/MoM links (to detect new updates)
STATE_FILE = Path(__file__).resolve().parent / "parivesh_last_state.json"

# SMS: Twilio (set in .env)
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER", "")  # e.g. +1234567890 or Twilio Indian number
