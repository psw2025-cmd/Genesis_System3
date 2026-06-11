#!/usr/bin/env python3
"""
Fail-fast heartbeat freshness check for monitoring/cron.
- Exits 0 if heartbeat is present and _last_updated (or system_info.timestamp) is within threshold.
- Exits 1 with message if stale or missing.

Usage:
  python check_heartbeat_freshness.py [--threshold-seconds 180] [--file path]

Environment overrides:
  HEARTBEAT_FRESHNESS_THRESHOLD_SECONDS
  HEARTBEAT_FILE
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_THRESHOLD = 180
DEFAULT_FILE = Path("system3_daily_heartbeat.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate heartbeat freshness")
    parser.add_argument("--threshold-seconds", type=int, default=None, help="Max allowed age in seconds (default 180)")
    parser.add_argument("--file", type=Path, default=None, help="Heartbeat file path")
    return parser.parse_args()


def load_heartbeat(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Heartbeat file not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def extract_timestamp(hb: dict) -> str:
    if not isinstance(hb, dict):
        return ""
    return (
        hb.get("_last_updated")
        or hb.get("timestamp")
        or hb.get("system_info", {}).get("timestamp")
    )


def main() -> int:
    args = parse_args()
    threshold = args.threshold_seconds or int(os.environ.get("HEARTBEAT_FRESHNESS_THRESHOLD_SECONDS", DEFAULT_THRESHOLD))
    hb_file = args.file or Path(os.environ.get("HEARTBEAT_FILE", DEFAULT_FILE))

    try:
        hb = load_heartbeat(hb_file)
        ts_str = extract_timestamp(hb)
        if not ts_str:
            print(f"❌ Missing timestamp in heartbeat: {hb_file}")
            return 1
        hb_time = datetime.fromisoformat(ts_str)
        if hb_time.tzinfo is None:
            # Assume local time if no timezone info
            hb_time = hb_time.replace(tzinfo=None)
        now = datetime.now()
        age = (now - hb_time).total_seconds()
        if age > threshold:
            print(f"❌ Heartbeat stale: age={age:.0f}s threshold={threshold}s file={hb_file}")
            return 1
        print(f"✅ Heartbeat fresh: age={age:.0f}s threshold={threshold}s file={hb_file}")
        return 0
    except Exception as e:
        print(f"❌ Heartbeat check failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
