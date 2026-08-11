#!/usr/bin/env python3
"""System3 health watchdog.

This watchdog is observation/housekeeping only.  Dhan token mutation was
permanently removed; the canonical GCP Cloud Run rotation job is the sole Dhan
token authority.
"""
from __future__ import annotations

import json
import shutil
import sys
import time
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
    """Observe Dhan token JWT status. Never generate, renew, or persist it."""
    try:
        sys.path.insert(0, str(ROOT))
        from core.brokers.dhan.token_manager import get_token_status

        status = get_token_status()
        if status.get("valid"):
            return {
                "check": "broker_token",
                "status": "OK",
                "detail": f"token JWT valid, expires {status.get('expires_at', 'unknown')}",
                "mutation_attempted": False,
            }
        return {
            "check": "broker_token",
            "status": "ALERT",
            "detail": "token invalid; canonical GCP rotation job must recover it",
            "mutation_attempted": False,
        }
    except Exception as exc:
        return {
            "check": "broker_token",
            "status": "ERROR",
            "detail": type(exc).__name__,
            "mutation_attempted": False,
        }


def check_scheduler_config() -> dict:
    cfg_path = ROOT / "config" / "system3_job_scheduler.json"
    try:
        cfg = json.loads(cfg_path.read_text())
        jobs = cfg.get("jobs", [])
        if not jobs:
            return {"check": "scheduler_config", "status": "ALERT", "detail": "Config valid JSON but zero jobs"}
        return {"check": "scheduler_config", "status": "OK", "detail": f"{len(jobs)} jobs configured"}
    except json.JSONDecodeError as exc:
        return {"check": "scheduler_config", "status": "CRITICAL", "detail": f"Invalid JSON: {exc}"}
    except Exception as exc:
        return {"check": "scheduler_config", "status": "ERROR", "detail": type(exc).__name__}


def check_gain_rank_today() -> dict:
    history_file = STATE_DIR / "gain_rank_history.json"
    today = date.today().isoformat()
    history = load_json(history_file, [])
    today_entry = next((e for e in history if e.get("date") == today), None)
    if today_entry:
        return {"check": "gain_rank_today", "status": "OK", "detail": f"{len(today_entry.get('predictions', []))} predictions for {today}"}
    return {"check": "gain_rank_today", "status": "NOT_RUN_YET", "detail": f"No gain_rank entry for {today} yet"}


def check_disk_pressure() -> dict:
    try:
        total, used, free = shutil.disk_usage(ROOT)
        pct_used = used / total * 100
        if pct_used > 85:
            archive_dir = REPORTS_DIR / "archive"
            cleared = 0
            if archive_dir.exists():
                cutoff = time.time() - (30 * 86400)
                for item in archive_dir.rglob("*"):
                    if item.is_file() and item.stat().st_mtime < cutoff:
                        item.unlink()
                        cleared += 1
            return {"check": "disk_pressure", "status": "AUTO_FIXED", "detail": f"Disk {pct_used:.0f}% used. Cleared {cleared} old archive files."}
        return {"check": "disk_pressure", "status": "OK", "detail": f"Disk {pct_used:.0f}% used ({free//1024//1024}MB free)"}
    except Exception as exc:
        return {"check": "disk_pressure", "status": "ERROR", "detail": type(exc).__name__}


def check_validation_freshness() -> dict:
    val_dir = STATE_DIR / "market_validations"
    if not val_dir.exists():
        return {"check": "validation_data", "status": "MISSING", "detail": "state/market_validations/ directory does not exist"}
    files = sorted(val_dir.glob("market_validation_*.json"))
    if not files:
        return {"check": "validation_data", "status": "EMPTY", "detail": "No validation files found"}
    latest = files[-1].stem.replace("market_validation_", "")
    return {"check": "validation_data", "status": "OK", "detail": f"{len(files)} validation files, latest: {latest}"}


def main():
    log("Health watchdog starting (broker token mutation disabled)")
    checks = [check_broker_token(), check_scheduler_config(), check_gain_rank_today(), check_disk_pressure(), check_validation_freshness()]
    alerts = [c for c in checks if c["status"] in ("CRITICAL", "FAILED", "ALERT")]
    fixed = [c for c in checks if c["status"] == "AUTO_FIXED"]
    for check in checks:
        log(f"{check['check']}: {check['status']} — {check['detail']}")
    result = {
        "run_at": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
        "alerts": len(alerts),
        "auto_fixed": len(fixed),
        "overall": "CRITICAL" if alerts else "OK",
    }
    save_json(ALERT_FILE, result)
    return 1 if alerts else 0


if __name__ == "__main__":
    sys.exit(main())
