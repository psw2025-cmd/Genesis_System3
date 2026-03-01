"""
Data Source State Machine for System3 Ultra Dashboard

States:
- not_ready: No data has ever been fetched (first run, or permanent failure)
- cached: Market closed and last known data exists (timestamp < 24h old)
- live: Market open and streaming active (data younger than LIVE_THRESHOLD_SEC)

live_allowed is true only when market open AND data_source == "live".
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import pytz

IST = pytz.timezone("Asia/Kolkata")

# Age thresholds
LIVE_THRESHOLD_SEC = 5  # Data considered "live" if younger than this (streaming active)
CACHE_MAX_AGE_SEC = 24 * 3600  # Cached data valid for 24 hours
LAST_KNOWN_FILE = "last_known.json"


def _get_outputs_dir() -> Path:
    """Resolve outputs directory."""
    return Path(__file__).parent.parent.parent / "outputs"


def _parse_iso(ts: Optional[str]) -> Optional[datetime]:
    """Parse ISO timestamp to datetime (timezone-aware)."""
    if not ts:
        return None
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = IST.localize(dt)
        return dt
    except Exception:
        return None


def _get_file_mtime_ist(path: Path) -> Optional[datetime]:
    """Get file mtime as IST datetime."""
    if not path.exists():
        return None
    try:
        mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=IST)
        return mtime
    except Exception:
        return None


def get_last_data_timestamp(outputs_dir: Path) -> Optional[datetime]:
    """
    Get timestamp of most recent data from health.json, last_known.json, or chain_raw_live.csv.
    """
    # 1. last_known.json (canonical cache)
    last_known = outputs_dir / LAST_KNOWN_FILE
    if last_known.exists():
        try:
            data = json.loads(last_known.read_text())
            ts = _parse_iso(data.get("timestamp"))
            if ts:
                return ts
        except Exception:
            pass

    # 2. health.json last_data_fetch
    health_file = outputs_dir / "health.json"
    if health_file.exists():
        try:
            health = json.loads(health_file.read_text())
            ts = _parse_iso(health.get("last_data_fetch"))
            if ts:
                return ts
        except Exception:
            pass

    # 3. chain_raw_live.csv mtime
    chain_file = outputs_dir / "chain_raw_live.csv"
    return _get_file_mtime_ist(chain_file)


def has_cached_data(outputs_dir: Path) -> bool:
    """True if any persisted data exists (chain, health, last_known)."""
    chain_file = outputs_dir / "chain_raw_live.csv"
    health_file = outputs_dir / "health.json"
    last_known = outputs_dir / LAST_KNOWN_FILE
    return chain_file.exists() or health_file.exists() or last_known.exists()


def compute_data_source(
    market_is_open: bool,
    last_data_ts: Optional[datetime],
    outputs_dir: Path,
) -> Tuple[str, Optional[datetime], float]:
    """
    Compute data_source state, last_data_time, and data_age_seconds.

    Returns:
        (data_source, last_data_time, data_age_seconds)
        last_data_time is None if no data; data_age_seconds is -1 if no data.
    """
    now = datetime.now(IST)
    if last_data_ts is None:
        last_data_ts = get_last_data_timestamp(outputs_dir)

    if last_data_ts is None:
        return ("not_ready", None, -1.0)

    age_sec = (now - last_data_ts).total_seconds()

    if market_is_open:
        if age_sec <= LIVE_THRESHOLD_SEC and age_sec >= 0:
            return ("live", last_data_ts, age_sec)
        # Market open but data stale - still show cached with warning
        if age_sec <= CACHE_MAX_AGE_SEC:
            return ("cached", last_data_ts, age_sec)
        return ("not_ready", last_data_ts, age_sec)

    # Market closed
    if age_sec <= CACHE_MAX_AGE_SEC and age_sec >= 0:
        return ("cached", last_data_ts, age_sec)
    if age_sec > CACHE_MAX_AGE_SEC:
        return ("not_ready", last_data_ts, age_sec)
    return ("not_ready", last_data_ts, age_sec)


def write_last_known(outputs_dir: Path, timestamp: Optional[datetime] = None) -> None:
    """
    Write last_known.json after a successful data fetch.
    Call this from the trading system / fetcher when data is persisted.
    """
    if timestamp is None:
        timestamp = datetime.now(IST)
    last_known = outputs_dir / LAST_KNOWN_FILE
    data = {
        "timestamp": timestamp.isoformat(),
        "chain_file": "chain_raw_live.csv",
        "health_file": "health.json",
        "updated_at": datetime.now(IST).isoformat(),
    }
    try:
        with open(last_known, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Warning: Failed to write last_known.json: {e}")
