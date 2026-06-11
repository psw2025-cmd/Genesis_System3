#!/usr/bin/env python3
"""
Archive the current heartbeat to storage/heartbeat_archive/ with a timestamped filename.
Optional retention: set HEARTBEAT_ARCHIVE_RETENTION_DAYS to delete older files.
"""

from __future__ import annotations

import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
HEARTBEAT_FILE = Path(os.environ.get("HEARTBEAT_FILE", PROJECT_ROOT / "system3_daily_heartbeat.json"))
ARCHIVE_DIR = PROJECT_ROOT / "storage" / "heartbeat_archive"
RETENTION_DAYS = int(os.environ.get("HEARTBEAT_ARCHIVE_RETENTION_DAYS", "0"))


def archive_once() -> Path:
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%S%fZ")
    target = ARCHIVE_DIR / f"heartbeat_{timestamp}.json"
    if not HEARTBEAT_FILE.exists():
        raise FileNotFoundError(f"Heartbeat file not found: {HEARTBEAT_FILE}")
    shutil.copy2(HEARTBEAT_FILE, target)
    return target


def apply_retention():
    if RETENTION_DAYS <= 0:
        return
    cutoff = datetime.utcnow() - timedelta(days=RETENTION_DAYS)
    for path in ARCHIVE_DIR.glob("heartbeat_*.json"):
        try:
            ts_part = path.stem.replace("heartbeat_", "")
            dt = datetime.strptime(ts_part, "%Y%m%dT%H%M%S%fZ")
            if dt < cutoff:
                path.unlink(missing_ok=True)
        except Exception:
            continue


def main() -> int:
    try:
        archived = archive_once()
        apply_retention()
        print(f"✅ Archived heartbeat to {archived}")
        return 0
    except Exception as e:
        print(f"❌ Failed to archive heartbeat: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
