"""
Run PARIVESH monitor every second for instant SMS when agenda/MoM is updated.
Leave this script running (or schedule it to start at logon).
"""
import time
from parivesh_monitor import run_check

# Seconds between checks (1 = every second; increase if the portal is slow or blocks you)
INTERVAL_SECONDS = 1

if __name__ == "__main__":
    print(f"PARIVESH monitor: checking every {INTERVAL_SECONDS} second(s). Press Ctrl+C to stop.")
    while True:
        try:
            run_check()
        except Exception as e:
            print(f"Check failed: {e}")
        time.sleep(INTERVAL_SECONDS)
