"""
Configuration for PARIVESH 2.0 agenda & MoM monitor.
Sources: https://parivesh.nic.in/#/ec-agenda-list and #/ec-mom-list
States: Tamil Nadu, Karnataka, Telangana (Environmental Clearance).
"""
import os
from pathlib import Path

# Your phone number for SMS alerts (with country code, no +)
PHONE_NUMBER = os.getenv("PHONE_NUMBER", "919940944929")

# PARIVESH 2.0 portal - Agenda and MoM for all states (we filter for TN, KA, TS)
BASE_URL = "https://parivesh.nic.in"
AGENDA_LIST_URL = "https://parivesh.nic.in/#/ec-agenda-list"
MOM_LIST_URL = "https://parivesh.nic.in/#/ec-mom-list"

# Public APIs discovered from PARIVESH 2.0
STATE_LIST_URL = f"{BASE_URL}/parivesh_api/trackYourProposal/getListOfAllState"
AGENDAMOM_API_BASE = f"{BASE_URL}/agendamom/getAgendaMomDocumentByCommitteeV2"

# Committees and reference types to query – we filter by state afterward
AGENDAMOM_COMMITTEES = ["SEIAA", "SEAC", "EAC"]
AGENDAMOM_REF_TYPES = ["AGENDA", "MOM"]

# States to monitor (Tamil Nadu, Karnataka, Telangana)
STATES_TO_MONITOR = [
    "Tamil Nadu",
    "Karnataka",
    "Telangana",
]

# File to store last known state (fingerprints / extracted items) to detect new updates
STATE_FILE = Path(__file__).resolve().parent / "parivesh_last_state.json"

# SMS: Twilio (set in .env)
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER", "")
