"""
Dhan Token Auto-Refresh Scheduler
===================================
Runs once at startup, waits until 08:30 AM, refreshes token, then loops daily.
Designed to run as a background daemon alongside the main system.

Usage:
  python scripts/dhan_token_auto_refresh.py          # daemon mode (runs forever)
  python scripts/dhan_token_auto_refresh.py --now    # refresh immediately and exit
  python scripts/dhan_token_auto_refresh.py --verify # verify current token and exit
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from core.brokers.dhan.token_manager import (
    consume_oauth_token,
    refresh_token,
    verify_token,
)

REFRESH_HOUR = 8
REFRESH_MINUTE = 30
RETRY_DELAY_S = 300  # retry every 5 min if first attempt fails


def seconds_until_next_refresh() -> float:
    now = datetime.now()
    target = now.replace(hour=REFRESH_HOUR, minute=REFRESH_MINUTE, second=0, microsecond=0)
    if now >= target:
        target += timedelta(days=1)
    return (target - now).total_seconds()


def run_daemon():
    print(f"[TokenDaemon] Started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"[TokenDaemon] Will refresh token daily at {REFRESH_HOUR:02d}:{REFRESH_MINUTE:02d}")

    # Verify on startup
    v = verify_token()
    if v.get("valid"):
        hrs = v.get("hours_remaining", "?")
        exp = v.get("expires_at", "")
        name = v.get("name") or f"client ...{v.get('client_id','?')}"
        print(f"[TokenDaemon] Token VALID for {name} — expires in {hrs}h ({exp})")
    else:
        print(f"[TokenDaemon] Token INVALID ({v.get('reason')}) — refreshing now...")
        result = refresh_token()
        if result["success"]:
            print(
                f"[TokenDaemon] Refreshed via {result['strategy']} — {result['token_preview']} expires {result.get('expires_at','?')}"
            )
        else:
            print(f"[TokenDaemon] FAILED: {result['message']}")

    while True:
        wait = seconds_until_next_refresh()
        wake = datetime.now() + timedelta(seconds=wait)
        print(f"[TokenDaemon] Sleeping until {wake.strftime('%Y-%m-%d %H:%M')} ({wait/3600:.1f}h)")
        time.sleep(wait)

        print(f"[TokenDaemon] {datetime.now().strftime('%H:%M:%S')} — refreshing token...")
        for attempt in range(1, 4):
            result = refresh_token()
            if result["success"]:
                print(f"[TokenDaemon] ✅ Token refreshed via {result['strategy']} — {result['token_preview']}")
                break
            else:
                print(f"[TokenDaemon] ❌ Attempt {attempt}/3 failed: {result['message']}")
                if attempt < 3:
                    print(f"[TokenDaemon] Retrying in {RETRY_DELAY_S}s...")
                    time.sleep(RETRY_DELAY_S)
        else:
            print("[TokenDaemon] All 3 attempts failed — check DHAN_PIN and DHAN_TOTP_SECRET")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Dhan Token Auto-Refresh Daemon")
    parser.add_argument("--now", action="store_true", help="Refresh immediately and exit")
    parser.add_argument("--verify", action="store_true", help="Verify current token and exit")
    parser.add_argument("--oauth", action="store_true", help="Show OAuth consent URL (manual browser login)")
    parser.add_argument("--consume", metavar="TOKEN_ID", help="Consume tokenId from OAuth browser redirect")
    args = parser.parse_args()

    if args.consume:
        r = consume_oauth_token(args.consume)
        print(json.dumps(r, indent=2))
    elif args.verify:
        v = verify_token()
        print(json.dumps(v, indent=2))
    elif args.now:
        r = refresh_token()
        print(json.dumps(r, indent=2))
    elif args.oauth:
        from core.brokers.dhan.token_manager import refresh_token as _rt

        r = _rt(force_oauth=True)
        print(json.dumps(r, indent=2))
    else:
        run_daemon()
