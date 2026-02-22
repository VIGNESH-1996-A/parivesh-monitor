"""
PARIVESH 2.0 EC Agenda & MoM Monitor.
Sources: https://parivesh.nic.in/#/ec-agenda-list and https://parivesh.nic.in/#/ec-mom-list
Filters for Tamil Nadu, Karnataka, Telangana and sends SMS when new agenda or MoM is detected.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, List, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from config import (
    AGENDA_LIST_URL,
    MOM_LIST_URL,
    BASE_URL,
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


def fetch_page(url: str) -> Optional[str]:
    """Fetch HTML/JSON from URL. Returns None on failure."""
    try:
        r = SESSION.get(url, timeout=30)
        r.raise_for_status()
        return r.text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None


def try_fetch_json(url: str) -> Optional[Any]:
    """Try to fetch URL as JSON. Returns parsed dict/list or None."""
    try:
        r = SESSION.get(url, timeout=15)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception:
        return None


def content_fingerprint(html: str) -> str:
    """Hash of page content for change detection."""
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    text = soup.get_text(separator=" ", strip=True)
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()


def extract_embedded_json(html: str) -> Optional[Any]:
    """Try to find JSON in script tags (e.g. __NEXT_DATA__, window.__STATE__)."""
    if not html:
        return None
    # Common SPA patterns: id="__NEXT_DATA__", type="application/json", window.__INITIAL_STATE__
    soup = BeautifulSoup(html, "html.parser")
    for script in soup.find_all("script", type="application/json"):
        try:
            return json.loads(script.string or "{}")
        except Exception:
            continue
    for script in soup.find_all("script", id=re.compile(r"__.*DATA__|__.*STATE__", re.I)):
        try:
            return json.loads(script.string or "{}")
        except Exception:
            continue
    return None


def items_mention_states(text: str) -> bool:
    """True if text mentions any of our monitored states."""
    if not text:
        return False
    t = text.lower()
    return any(s.lower() in t for s in STATES_TO_MONITOR)


def extract_rows_for_states(html: str, base_url: str) -> List[dict]:
    """
    Extract table rows or list items that mention Tamil Nadu, Karnataka, or Telangana.
    Returns list of {"state": ..., "text": ..., "href": ...} for change detection.
    """
    if not html:
        return []
    soup = BeautifulSoup(html, "html.parser")
    out = []
    for tag in soup.find_all(["tr", "li", "div"], class_=re.compile(r"row|item|list|card", re.I)) or soup.find_all("tr"):
        text = (tag.get_text() or "").strip()
        if not items_mention_states(text):
            continue
        href = ""
        a = tag.find("a", href=True)
        if a:
            href = urljoin(base_url, a["href"]) if not (a["href"].startswith("http") or a["href"].startswith("#")) else a["href"]
        state = next((s for s in STATES_TO_MONITOR if s.lower() in text.lower()), "")
        out.append({"state": state, "text": text[:150], "href": href})
    # Also collect any link whose text or href mentions agenda/mom and state
    for a in soup.find_all("a", href=True):
        text = (a.get_text() or "").strip()
        href = a.get("href") or ""
        if items_mention_states(text) or items_mention_states(href):
            full_url = urljoin(base_url, href) if not (href.startswith("http") or href.startswith("#")) else href
            state = next((s for s in STATES_TO_MONITOR if s.lower() in (text + href).lower()), "")
            out.append({"state": state, "text": text[:150] or href[:80], "href": full_url})
    return out


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
    Check PARIVESH 2.0 agenda and MoM pages for new content for TN, Karnataka, Telangana.
    Uses page fingerprinting and optional embedded/API data.
    """
    last = load_last_state()
    new_highlights = []

    # PARIVESH 2.0 SPA: server typically serves same HTML for all routes; fragment is client-side.
    # Fetch main page (agenda and mom content may be loaded by JS from same or different API).
    agenda_html = fetch_page(BASE_URL)
    mom_html = fetch_page(BASE_URL)  # Same base; SPA uses hash to show agenda vs mom

    # Also try path-based URLs in case server has SSR or different endpoints
    agenda_alt = fetch_page(BASE_URL + "/ec-agenda-list")
    mom_alt = fetch_page(BASE_URL + "/ec-mom-list")

    agenda_html = agenda_html or agenda_alt
    mom_html = mom_html or mom_alt

    agenda_fp = content_fingerprint(agenda_html or "")
    mom_fp = content_fingerprint(mom_html or "")

    agenda_items = extract_rows_for_states(agenda_html or "", BASE_URL)
    mom_items = extract_rows_for_states(mom_html or "", BASE_URL)

    # Try common API patterns (no guarantee PARIVESH exposes these)
    for path in ["/api/ec/agenda", "/api/ec/mom", "/parivesh/api/ec-agenda-list", "/parivesh/api/ec-mom-list"]:
        data = try_fetch_json(BASE_URL + path)
        if data and isinstance(data, list) and len(data) > 0:
            for row in data:
                if isinstance(row, dict):
                    row_text = json.dumps(row)[:200]
                else:
                    row_text = str(row)[:200]
                if items_mention_states(row_text):
                    if "agenda" in path.lower():
                        agenda_items.append({"state": "", "text": row_text, "href": ""})
                    else:
                        mom_items.append({"state": "", "text": row_text, "href": ""})

    prev_agenda_fp = last.get("agenda_fingerprint", "")
    prev_mom_fp = last.get("mom_fingerprint", "")
    prev_agenda_items = last.get("agenda_items", [])
    prev_mom_items = last.get("mom_items", [])

    # Normalize item to a stable key for comparison (avoids false "new" from timestamps/order)
    def item_key(i: dict) -> tuple:
        return (i.get("state", ""), (i.get("text") or "")[:120].strip())

    prev_agenda_keys = {item_key(i) for i in prev_agenda_items}
    prev_mom_keys = {item_key(i) for i in prev_mom_items}

    # Only trigger when there is at least one genuinely NEW item (not on fingerprint change).
    # Skip alert on first run (no previous state) so we don't spam for existing content.
    had_prev_agenda = prev_agenda_fp != "" or len(prev_agenda_items) > 0
    had_prev_mom = prev_mom_fp != "" or len(prev_mom_items) > 0

    new_agenda_items = [i for i in agenda_items if item_key(i) not in prev_agenda_keys]
    new_mom_items = [i for i in mom_items if item_key(i) not in prev_mom_keys]

    new_agenda = had_prev_agenda and len(new_agenda_items) > 0
    new_mom = had_prev_mom and len(new_mom_items) > 0

    current = {
        "agenda_fingerprint": agenda_fp,
        "mom_fingerprint": mom_fp,
        "agenda_items": agenda_items,
        "mom_items": mom_items,
    }
    save_last_state(current)

    # Build clear lines: "State - SEIAA - agenda" / "State - SEIAA - MoM" only for newly added items
    def states_from_new_items(items: List[dict]) -> List[str]:
        seen = set()
        ordered = []
        for s in STATES_TO_MONITOR:
            if s in [i.get("state") for i in items if i.get("state")] and s not in seen:
                ordered.append(s)
                seen.add(s)
        for i in items:
            st = (i.get("state") or "").strip()
            if st and st not in seen:
                ordered.append(st)
                seen.add(st)
        return ordered

    if new_agenda:
        for state in states_from_new_items(new_agenda_items):
            new_highlights.append(f"{state} - SEIAA - agenda")
    if new_mom:
        for state in states_from_new_items(new_mom_items):
            new_highlights.append(f"{state} - SEIAA - MoM")

    # Send SMS only when new agenda or MoM is detected (24/7 monitoring, alert only on change)
    if new_highlights:
        body = "PARIVESH 2.0:\n" + "\n".join(new_highlights)
        if len(body) > 1600:
            body = body[:1597] + "..."
        send_sms(body)
    else:
        print("No new agenda/MoM updates detected for TN, KA, TS.")


if __name__ == "__main__":
    run_check()
