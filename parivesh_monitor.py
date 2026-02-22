"""
PARIVESH EC Agenda & MoM Monitor.
Checks for new agenda / Minutes of Meeting on PARIVESH for Tamil Nadu, Karnataka, Telangana
and sends SMS to the configured phone number.
"""
from __future__ import annotations

import json
import hashlib
from pathlib import Path
from urllib.parse import urljoin
from typing import Optional

import requests
from bs4 import BeautifulSoup

# Load .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from config import (
    PHONE_NUMBER,
    STATES_TO_MONITOR,
    get_state_meeting_url,
    STATE_FILE,
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_FROM_NUMBER,
)

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": USER_AGENT})


def fetch_page(url: str) -> Optional[str]:
    """Fetch HTML of a URL. Returns None on failure."""
    try:
        r = SESSION.get(url, timeout=30)
        r.raise_for_status()
        return r.text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None


def extract_agenda_mom_links(html: str, base_url: str) -> list:
    """
    Extract links that look like agenda or MoM (minutes) from the page.
    Returns list of {"href": ..., "text": ...}.
    """
    if not html:
        return []
    soup = BeautifulSoup(html, "html.parser")
    links = []
    for a in soup.find_all("a", href=True):
        href = (a.get("href") or "").strip()
        text = (a.get_text() or "").strip()
        href_lower = href.lower()
        text_lower = text.lower()
        # Match agenda, minutes, MoM, PDFs often used for agenda/MoM
        if any(
            x in href_lower or x in text_lower
            for x in ("agenda", "minutes", "mom", "minute", "meeting", "schedule")
        ) or (href_lower.endswith(".pdf") and ("agenda" in text_lower or "minute" in text_lower or "meeting" in text_lower)):
            full_url = urljoin(base_url, href) if not href.startswith("http") else href
            links.append({"href": full_url, "text": text[:200]})
    return links


def content_fingerprint(html: str) -> str:
    """Simple hash of relevant content for change detection."""
    if not html:
        return ""
    # Normalize: strip script/style and extra whitespace
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()
    text = soup.get_text(separator=" ", strip=True)
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()


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
    """Send SMS via Twilio. Returns True if sent successfully."""
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER]):
        print("SMS skipped: set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER in .env")
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
    """Check all three states for new agenda/MoM and send SMS if something new."""
    last = load_last_state()
    new_highlights = []
    current_state = {}

    for state in STATES_TO_MONITOR:
        name = state["name"]
        state_id = state["state_id"]
        url = get_state_meeting_url(state_id)
        html = fetch_page(url)
        if not html:
            current_state[name] = last.get(name, {})
            continue

        fingerprint = content_fingerprint(html)
        links = extract_agenda_mom_links(html, url)
        prev = last.get(name, {})
        prev_fp = prev.get("fingerprint", "")
        prev_links = prev.get("links", [])

        current_state[name] = {"fingerprint": fingerprint, "links": links}

        # New if fingerprint changed or new links appeared
        new_links = [l for l in links if l not in prev_links]
        if fingerprint != prev_fp or new_links:
            msg = f"PARIVESH: New update for {name} (EC Agenda/MoM)."
            if new_links:
                msg += f" New links: {new_links[0].get('href', '')[:80]}..."
            new_highlights.append(msg)

    save_last_state(current_state)

    if new_highlights:
        body = " | ".join(new_highlights)[:1600]  # Twilio single SMS length limit
        send_sms(body)
    else:
        print("No new agenda/MoM updates detected.")


if __name__ == "__main__":
    run_check()
