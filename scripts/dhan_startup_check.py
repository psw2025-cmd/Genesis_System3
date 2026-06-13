"""
Dhan Startup Safety Check — Layer 0
=====================================
Run this on every system boot / session start BEFORE anything else.

What it does:
  1. Reads current token from .secrets/dhan.env
  2. Checks expiry via JWT decode (no API call needed)
  3. If expired or < 1h remaining → refreshes immediately using PIN+TOTP
  4. Starts daemon if not already running
  5. Starts watchdog if not already running
  6. Prints a clear status summary

Usage:
  python scripts/dhan_startup_check.py           # check + fix + start daemons
  python scripts/dhan_startup_check.py --status  # just print status, no action

Add to ~/.bashrc (already done) or system startup for automatic execution.
"""

import sys
import os
import json
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def _load_env() -> dict:
    env = {}
    env_file = ROOT / ".secrets" / "dhan.env"
    if not env_file.exists():
        return env
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip()
    return env


def _token_status(token: str) -> dict:
    """Decode JWT token — no API needed."""
    import base64
    if not token:
        return {"valid": False, "reason": "no_token", "hours_remaining": -999}
    try:
        parts = token.split(".")
        pad = parts[1] + "=" * (4 - len(parts[1]) % 4)
        payload = json.loads(base64.urlsafe_b64decode(pad))
        exp = payload.get("exp")
        if not exp:
            return {"valid": False, "reason": "no_expiry_in_jwt"}
        exp_dt = datetime.fromtimestamp(exp)
        hours = (exp_dt - datetime.now()).total_seconds() / 3600
        return {
            "valid": hours > 0,
            "expires_at": exp_dt.isoformat(),
            "hours_remaining": round(hours, 2),
            "reason": "ok" if hours > 0 else f"expired_{abs(hours):.1f}h_ago",
        }
    except Exception as e:
        return {"valid": False, "reason": str(e), "hours_remaining": -999}


def _process_running(pattern: str) -> bool:
    result = subprocess.run(["pgrep", "-f", pattern], capture_output=True)
    return result.returncode == 0


def _start_daemon(script: str, log: str) -> int:
    """Start a Python daemon, return PID."""
    python = sys.executable
    p = subprocess.Popen(
        [python, "-u", str(ROOT / "scripts" / script)],
        stdout=open(ROOT / "logs" / log, "a"),
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    return p.pid


def run_startup_check(status_only: bool = False) -> dict:
    env = _load_env()
    token = env.get("DHAN_ACCESS_TOKEN", "")
    has_pin  = bool(env.get("DHAN_PIN", "").strip())
    has_totp = bool(env.get("DHAN_TOTP_SECRET", "").strip())

    status = _token_status(token)
    hours  = status.get("hours_remaining", -999)

    print("\n╔═══════════════════════════════════════════╗")
    print("║   DHAN STARTUP CHECK — Genesis System3    ║")
    print("╚═══════════════════════════════════════════╝")
    print(f"  Time          : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Token valid   : {status['valid']}")
    print(f"  Hours left    : {hours:.1f}h")
    print(f"  Expires at    : {status.get('expires_at', 'unknown')}")
    print(f"  PIN+TOTP set  : {has_pin and has_totp}")

    actions_taken = []

    if status_only:
        print(f"  Daemon running: {_process_running('dhan_token_auto_refresh')}")
        print(f"  Watchdog run  : {_process_running('token_watchdog')}")
        print()
        return {"status": status, "actions": []}

    # REFRESH if expired or < 1h left
    if not status["valid"] or hours < 1.0:
        if hours < 0:
            print(f"\n  ⚠ Token EXPIRED {abs(hours):.1f}h ago — refreshing immediately...")
        else:
            print(f"\n  ⚠ Token expiring soon ({hours:.1f}h) — refreshing now...")

        try:
            from dotenv import load_dotenv
            load_dotenv(ROOT / ".secrets" / "dhan.env", override=True)
            from core.brokers.dhan.token_manager import refresh_token
            result = refresh_token()
            if result.get("success"):
                print(f"  ✅ Token refreshed via {result['strategy']} — expires {result.get('expires_at','?')}")
                actions_taken.append("token_refreshed")
                # Re-read status after refresh
                env = _load_env()
                status = _token_status(env.get("DHAN_ACCESS_TOKEN", ""))
                hours = status.get("hours_remaining", 0)
            else:
                print(f"  ❌ Refresh FAILED: {result['message']}")
                print(f"     Run manually: python scripts/dhan_token_auto_refresh.py --oauth")
                actions_taken.append("refresh_failed")
        except Exception as e:
            print(f"  ❌ Refresh error: {e}")
            actions_taken.append("refresh_error")
    else:
        print(f"  ✅ Token healthy — {hours:.1f}h remaining")

    # Ensure DAEMON is running
    if not _process_running("dhan_token_auto_refresh"):
        print("  ⚠ Daemon not running — starting...")
        try:
            pid = _start_daemon("dhan_token_auto_refresh.py", "dhan_token_daemon.log")
            print(f"  ✅ Daemon started (PID {pid})")
            actions_taken.append(f"daemon_started_pid_{pid}")
        except Exception as e:
            print(f"  ❌ Daemon start failed: {e}")
    else:
        print("  ✅ Daemon running")

    # Ensure WATCHDOG is running
    if not _process_running("token_watchdog"):
        print("  ⚠ Watchdog not running — starting...")
        try:
            pid = _start_daemon("dhan_watchdog_runner.py", "dhan_watchdog.log")
            print(f"  ✅ Watchdog started (PID {pid})")
            actions_taken.append(f"watchdog_started_pid_{pid}")
        except Exception as e:
            print(f"  ❌ Watchdog start failed: {e}")
    else:
        print("  ✅ Watchdog running")

    print()
    return {"status": status, "actions": actions_taken}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Dhan Startup Safety Check")
    parser.add_argument("--status", action="store_true", help="Status only, no auto-fix")
    args = parser.parse_args()
    run_startup_check(status_only=args.status)
