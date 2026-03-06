"""
PARIVESH 2.0 EC Agenda & MoM Monitor.
Sources: https://parivesh.nic.in/#/ec-agenda-list and https://parivesh.nic.in/#/ec-mom-list
Filters for Tamil Nadu, Karnataka, Telangana and sends SMS when new agenda or MoM is detected.

This version uses the official PARIVESH 2.0 JSON APIs:
- State list: /parivesh_api/trackYourProposal/getListOfAllState
- Agenda/MoM: /agendamom/getAgendaMomDocumentByCommitteeV2
"""
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Tuple

import requests

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from config import (
    AGENDA_LIST_URL,
    MOM_LIST_URL,
    BASE_URL,
    STATE_LIST_URL,
    AGENDAMOM_API_BASE,
    AGENDAMOM_COMMITTEES,
    AGENDAMOM_REF_TYPES,
    PHONE_NUMBER,
    STATES_TO_MONITOR,
    STATE_FILE,
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_FROM_NUMBER,
)

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": USER_AGENT})


def try_fetch_json(url: str, params: Optional[Dict[str, Any]] = None) -> Optional[Any]:
    """Fetch URL as JSON. Returns parsed dict/list or None on failure."""
    try:
        r = SESSION.get(url, params=params, timeout=30)
        if r.status_code != 200:
            print(f"Non-200 from {url}: {r.status_code}")
            return None
        return r.json()
    except Exception as e:
        print(f"Error fetching JSON {url}: {e}")
        return None


def items_mention_states(text: str) -> bool:
    """True if text mentions any of our monitored states."""
    if not text:
        return False
    t = text.lower()
    return any(s.lower() in t for s in STATES_TO_MONITOR)


def load_last_state() -> dict:
    """Load last known state from JSON file."""
    if not STATE_FILE.exists():
        return {}
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_last_state(state: dict) -> None:
    """Save current state to JSON file."""
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def send_sms(body: str) -> bool:
    """Send SMS via Twilio."""
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER]):
        print("SMS skipped: set Twilio env vars in .env")
        return False
    to_number = PHONE_NUMBER if PHONE_NUMBER.startswith("+") else f"+{PHONE_NUMBER}"
    try:
        from twilio.rest import Client

        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        client.messages.create(to=to_number, from_=TWILIO_FROM_NUMBER, body=body)
        print("SMS sent to", to_number)
        return True
    except Exception as e:
        print("SMS failed:", e)
        return False


def run_check() -> None:
    """
    Check PARIVESH 2.0 agenda and MoM APIs for new content for TN, Karnataka, Telangana.
    Uses official JSON APIs and only alerts when genuinely new records appear.
    """
    last = load_last_state()
    new_highlights: List[str] = []

    # ------------------------------------------------------------------
    # 1) Helpers for interpreting API rows
    # ------------------------------------------------------------------

    def detect_state_for_row(row: Dict[str, Any]) -> str:
        """Best-effort detection of state from a row."""
        for key in ("stateName", "state_name", "state", "state_name_en"):
            val = row.get(key)
            if isinstance(val, str) and items_mention_states(val):
                for s in STATES_TO_MONITOR:
                    if s.lower() in val.lower():
                        return s
        row_text = json.dumps(row, ensure_ascii=False)
        for s in STATES_TO_MONITOR:
            if s.lower() in row_text.lower():
                return s
        return ""

    def row_id_and_title(row: Dict[str, Any]) -> Tuple[str, str]:
        """Try to extract a stable ID/title pair for a row."""
        for key in (
            "id",
            "agendaId",
            "agenda_id",
            "momId",
            "mom_id",
            "documentId",
            "docId",
            "document_id",
            "proposal_no",
        ):
            if key in row and row.get(key) is not None:
                return str(row.get(key)), str(row.get(key))
        for key in ("title", "agendaTitle", "momTitle", "subject", "fileName", "documentTitle"):
            if key in row and isinstance(row.get(key), str):
                t = row.get(key) or ""
                return t[:80], t[:80]
        row_text = json.dumps(row, ensure_ascii=False)
        return row_text[:80], row_text[:80]

    # ------------------------------------------------------------------
    # 2) Fetch agenda & MoM items for all committees, filter to TN/KA/TS
    # ------------------------------------------------------------------

    agenda_items: List[Dict[str, Any]] = []
    mom_items: List[Dict[str, Any]] = []

    for committee in AGENDAMOM_COMMITTEES:
        for ref_type in AGENDAMOM_REF_TYPES:
            params = {"committee": committee, "ref_type": ref_type, "workgroupId": 1}
            data = try_fetch_json(AGENDAMOM_API_BASE, params=params)
            if data is None:
                continue
            rows = []
            if isinstance(data, dict) and isinstance(data.get("data"), list):
                rows = data["data"]
            elif isinstance(data, list):
                rows = data
            if not rows:
                continue

            for row in rows:
                if not isinstance(row, dict):
                    continue
                state = detect_state_for_row(row)
                if not state:
                    continue
                _id, title = row_id_and_title(row)
                record = {
                    "state": state,
                    "committee": committee,
                    "ref_type": ref_type,
                    "id": _id,
                    "title": title,
                    "raw": row,
                }
                if ref_type.upper() == "AGENDA":
                    agenda_items.append(record)
                else:
                    mom_items.append(record)

    # ------------------------------------------------------------------
    # 3) Detect genuinely new rows vs previous state
    # ------------------------------------------------------------------

    prev_agenda_items = last.get("agenda_items", [])
    prev_mom_items = last.get("mom_items", [])

    def item_key(i: Dict[str, Any]) -> Tuple[str, str, str, str]:
        """Stable key to detect genuinely new rows."""
        return (
            (i.get("state") or "").strip(),
            (i.get("committee") or "").strip().upper(),
            (i.get("ref_type") or "").strip().upper(),
            (i.get("id") or "").strip(),
        )

    prev_agenda_keys = {item_key(i) for i in prev_agenda_items if isinstance(i, dict)}
    prev_mom_keys = {item_key(i) for i in prev_mom_items if isinstance(i, dict)}

    had_prev_agenda = len(prev_agenda_items) > 0
    had_prev_mom = len(prev_mom_items) > 0

    new_agenda_items = [i for i in agenda_items if item_key(i) not in prev_agenda_keys]
    new_mom_items = [i for i in mom_items if item_key(i) not in prev_mom_keys]

    new_agenda = had_prev_agenda and len(new_agenda_items) > 0
    new_mom = had_prev_mom and len(new_mom_items) > 0

    current = {
        "agenda_items": agenda_items,
        "mom_items": mom_items,
    }
    save_last_state(current)

    # ------------------------------------------------------------------
    # 4) Build human-readable SMS lines per state
    # ------------------------------------------------------------------

    def states_from_new_items(items: List[Dict[str, Any]]) -> List[str]:
        seen = set()
        ordered: List[str] = []
        for s in STATES_TO_MONITOR:
            for i in items:
                st = (i.get("state") or "").strip()
                if st and st.lower() == s.lower() and st not in seen:
                    ordered.append(st)
                    seen.add(st)
        for i in items:
            st = (i.get("state") or "").strip()
            if st and st not in seen:
                ordered.append(st)
                seen.add(st)
        return ordered

    if new_agenda:
        for state in states_from_new_items(new_agenda_items):
            new_highlights.append(f"{state} - SEIAA/SEAC/EAC - agenda")
    if new_mom:
        for state in states_from_new_items(new_mom_items):
            new_highlights.append(f"{state} - SEIAA/SEAC/EAC - MoM")

    # ------------------------------------------------------------------
    # 5) Send SMS only when new agenda or MoM is detected
    # ------------------------------------------------------------------
    if new_highlights:
        lines = ["PARIVESH 2.0:"]
        lines.extend(new_highlights)
        lines.append(f"Agenda list: {AGENDA_LIST_URL}")
        lines.append(f"MoM list: {MOM_LIST_URL}")
        body = "\n".join(lines)
        if len(body) > 1600:
            body = body[:1597] + "..."
        send_sms(body)
    else:
        print("No new agenda/MoM updates detected for TN, KA, TS.")


if __name__ == "__main__":
    run_check()
