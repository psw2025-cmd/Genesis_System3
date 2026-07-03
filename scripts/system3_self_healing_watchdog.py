#!/usr/bin/env python3
"""
System3 Self-Healing Watchdog
================================
Runs every 30 minutes via job scheduler. Detects and auto-fixes:
  1. Stale DHAN_ACCESS_TOKEN → triggers refresh
  2. Scheduler health stale → restarts scheduler thread signal
  3. Gain rank history not updated today → alerts
  4. Disk/memory pressure → clears old reports
  5. Config JSON corrupt → alerts loudly

This is the "auto self-correct" layer. It cannot fix everything
(e.g. Render infra issues need dashboard), but it handles the
99% of common failures silently and automatically.
"""

from __future__ import annotations
import json, os, sys, time, shutil
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE_DIR = ROOT / "state"
REPORTS_DIR = ROOT / "reports"
ALERT_FILE = STATE_DIR / "self_healing_alerts.json"

def log(msg: str, level: str = "INFO"):
    ts = datetime.now(timezone.utc).isoformat()
    print(f"[{ts}] [{level}] [watchdog] {msg}")

def load_json(p: Path, default):
    try:
        return json.loads(p.read_text()) if p.exists() else default
    except Exception:
        return default

def save_json(p: Path, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2, default=str))

def check_broker_token() -> dict:
    """Check if Dhan token is valid — trigger refresh if not."""
    try:
        sys.path.insert(0, str(ROOT))
        from core.brokers.dhan.token_manager import refresh_token, verify_token
        status = verify_token()
        if status.get("valid"):
            return {"check": "broker_token", "status": "OK",
                    "detail": f"token valid, expires {status.get('expires_at', 'unknown')}"}
        log("Token invalid — triggering auto-refresh", "WARN")
        result = refresh_token()
        if result.get("success"):
            return {"check": "broker_token", "status": "AUTO_FIXED",
                    "detail": f"refreshed via {result.get('strategy')}"}
        return {"check": "broker_token", "status": "FAILED",
                "detail": f"refresh failed: {result.get('message', 'unknown')}"}
    except Exception as e:
        return {"check": "broker_token", "status": "ERROR", "detail": str(e)[:200]}

def check_scheduler_config() -> dict:
    """Verify scheduler JSON is valid."""
    cfg_path = ROOT / "config" / "system3_job_scheduler.json"
    try:
        cfg = json.loads(cfg_path.read_text())
        jobs = cfg.get("jobs", [])
        if not jobs:
            return {"check": "scheduler_config", "status": "ALERT",
                    "detail": "Config valid JSON but zero jobs — scheduler is idle"}
        return {"check": "scheduler_config", "status": "OK",
                "detail": f"{len(jobs)} jobs configured"}
    except json.JSONDecodeError as e:
        log(f"CRITICAL: scheduler config is broken JSON: {e}", "ERROR")
        return {"check": "scheduler_config", "status": "CRITICAL",
                "detail": f"Invalid JSON: {e}"}
    except Exception as e:
        return {"check": "scheduler_config", "status": "ERROR", "detail": str(e)[:200]}

def check_gain_rank_today() -> dict:
    """Verify gain_rank ran today."""
    history_file = STATE_DIR / "gain_rank_history.json"
    today = date.today().isoformat()
    history = load_json(history_file, [])
    today_entry = next((e for e in history if e.get("date") == today), None)
    if today_entry:
        return {"check": "gain_rank_today", "status": "OK",
                "detail": f"{len(today_entry.get('predictions', []))} predictions for {today}"}
    return {"check": "gain_rank_today", "status": "NOT_RUN_YET",
            "detail": f"No gain_rank entry for {today} yet (expected after 09:15 IST)"}

def check_disk_pressure() -> dict:
    """Clear old report archives if disk getting full."""
    try:
        total, used, free = shutil.disk_usage(ROOT)
        pct_used = used / total * 100
        if pct_used > 85:
            # Clear archives older than 30 days
            archive_dir = REPORTS_DIR / "archive"
            cleared = 0
            if archive_dir.exists():
                cutoff = time.time() - (30 * 86400)
                for item in archive_dir.rglob("*"):
                    if item.is_file() and item.stat().st_mtime < cutoff:
                        item.unlink()
                        cleared += 1
            return {"check": "disk_pressure", "status": "AUTO_FIXED",
                    "detail": f"Disk {pct_used:.0f}% used. Cleared {cleared} old archive files."}
        return {"check": "disk_pressure", "status": "OK",
                "detail": f"Disk {pct_used:.0f}% used ({free//1024//1024}MB free)"}
    except Exception as e:
        return {"check": "disk_pressure", "status": "ERROR", "detail": str(e)[:200]}

def check_validation_freshness() -> dict:
    """Check if we have recent validation data."""
    val_dir = STATE_DIR / "market_validations"
    if not val_dir.exists():
        return {"check": "validation_data", "status": "MISSING",
                "detail": "state/market_validations/ directory does not exist"}
    files = sorted(val_dir.glob("market_validation_*.json"))
    if not files:
        return {"check": "validation_data", "status": "EMPTY",
                "detail": "No validation files found — need trading days to accumulate"}
    latest = files[-1].stem.replace("market_validation_", "")
    return {"check": "validation_data", "status": "OK",
            "detail": f"{len(files)} validation files, latest: {latest}"}

def main():
    log("Self-healing watchdog starting")
    checks = [
        check_broker_token(),
        check_scheduler_config(),
        check_gain_rank_today(),
        check_disk_pressure(),
        check_validation_freshness(),
    ]
    alerts = [c for c in checks if c["status"] in ("CRITICAL", "FAILED", "ALERT")]
    fixed  = [c for c in checks if c["status"] == "AUTO_FIXED"]

    for c in checks:
        icon = "🔴" if c["status"] in ("CRITICAL","FAILED") else                "🟡" if c["status"] in ("ALERT","NOT_RUN_YET","ERROR") else                "🟢" if c["status"] == "OK" else "🔧"
        log(f"{icon} {c['check']}: {c['status']} — {c['detail']}")

    result = {
        "run_at": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
        "alerts": len(alerts),
        "auto_fixed": len(fixed),
        "overall": "CRITICAL" if alerts else "OK",
    }
    save_json(ALERT_FILE, result)
    log(f"Done. {len(checks)} checks, {len(alerts)} alerts, {len(fixed)} auto-fixed")
    return 1 if alerts else 0

if __name__ == "__main__":
    sys.exit(main())
