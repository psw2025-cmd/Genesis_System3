#!/usr/bin/env python3
"""
Continuous monitoring: backend health, broker connection, LIVE gating.
Appends results to proof/MONITORING_LOG_YYYYMMDD.txt.
Run periodically (e.g. cron/scheduled task) or manually.
"""
import os
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROOF_DIR = ROOT / "proof"
BASE_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")


def main():
    PROOF_DIR.mkdir(exist_ok=True)
    today = datetime.now().strftime("%Y%m%d")
    log_file = PROOF_DIR / f"MONITORING_LOG_{today}.txt"

    lines = [
        "",
        "---",
        datetime.now().isoformat(),
        f"Backend: {BASE_URL}",
    ]

    try:
        import requests

        # Health
        r_health = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if r_health.status_code != 200:
            lines.append(f"  /api/health: FAIL status={r_health.status_code}")
        else:
            h = r_health.json()
            mode = (h.get("mode") or "?").upper()
            broker_connected = False
            if isinstance(h.get("broker"), dict):
                broker_connected = h["broker"].get("connected", False)
            if not broker_connected and h.get("broker_status") == "connected":
                broker_connected = True
            live_allowed = h.get("live_allowed", None)
            live_blockers = h.get("live_blockers", [])
            lines.append(
                f"  /api/health: OK mode={mode} broker_connected={broker_connected} live_allowed={live_allowed}"
            )
            lines.append(f"  live_blockers={live_blockers}")
            if mode == "LIVE" and not broker_connected:
                lines.append("  [WARN] LIVE mode with broker disconnected - gating should block")
            elif mode != "LIVE" and not broker_connected:
                lines.append("  [OK] LIVE gating: mode not LIVE when broker disconnected")
        # State
        r_state = requests.get(f"{BASE_URL}/api/state", timeout=5)
        if r_state.status_code != 200:
            lines.append(f"  /api/state: FAIL status={r_state.status_code}")
        else:
            lines.append(f"  /api/state: OK")
    except Exception as e:
        lines.append(f"  ERROR: {e}")

    with open(log_file, "a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"[OK] Monitoring log appended: {log_file.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
