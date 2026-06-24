#!/usr/bin/env python3
"""
Production instrument master sync — Dhan official daily scrip master.

Official sources (DhanHQ v2 docs):
  https://images.dhan.co/api-data/api-scrip-master-detailed.csv  (preferred)
  https://images.dhan.co/api-data/api-scrip-master.csv

Updated by Dhan ~08:30 IST weekdays. Run at 08:35 IST via scheduler.

Writes:
  storage/instruments/api-scrip-master-detailed.csv
  storage/instruments/master_meta.json
  storage/instruments/OpenAPIScripMaster.json  (normalized runtime cache)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "storage" / "instruments"
DETAILED_CSV = OUT_DIR / "api-scrip-master-detailed.csv"
COMPACT_CSV = OUT_DIR / "api-scrip-master.csv"
META_JSON = OUT_DIR / "master_meta.json"
RUNTIME_JSON = OUT_DIR / "OpenAPIScripMaster.json"

DHAN_DETAILED_URL = os.environ.get(
    "DHAN_INSTRUMENT_MASTER_URL",
    "https://images.dhan.co/api-data/api-scrip-master-detailed.csv",
)
DHAN_COMPACT_URL = "https://images.dhan.co/api-data/api-scrip-master.csv"
MIN_ROWS = int(os.environ.get("DHAN_INSTRUMENT_MIN_ROWS", "50000"))


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _download(url: str, dest: Path, timeout: int = 120) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "System3-InstrumentsSync/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = resp.read()
    if len(data) < 1000:
        raise RuntimeError(f"Download too small from {url}: {len(data)} bytes")
    dest.write_bytes(data)


def _build_runtime_json(csv_path: Path) -> int:
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    import pandas as pd

    from core.data.instruments_master import dataframe_from_dhan_csv

    df = dataframe_from_dhan_csv(pd.read_csv(csv_path, low_memory=False))
    if df.empty:
        raise RuntimeError("Normalized instruments dataframe is empty")
    records = df.to_dict(orient="records")
    RUNTIME_JSON.write_text(json.dumps(records), encoding="utf-8")
    return len(records)


def sync(force: bool = False) -> Dict[str, Any]:
    """Download latest Dhan scrip master and rebuild runtime cache."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    url = DHAN_DETAILED_URL
    dest = DETAILED_CSV
    try:
        _download(url, dest)
        source = "dhan_detailed_csv"
    except Exception as detailed_err:
        if not force:
            raise RuntimeError(f"Detailed master download failed: {detailed_err}") from detailed_err
        _download(DHAN_COMPACT_URL, COMPACT_CSV)
        dest = COMPACT_CSV
        url = DHAN_COMPACT_URL
        source = "dhan_compact_csv"

    import pandas as pd

    row_count = sum(1 for _ in open(dest, encoding="utf-8", errors="replace")) - 1
    if row_count < MIN_ROWS:
        raise RuntimeError(f"Instrument master row count too low: {row_count} < {MIN_ROWS}")

    runtime_rows = _build_runtime_json(dest)
    meta = {
        "synced_utc": _utc(),
        "source": source,
        "source_url": url,
        "csv_path": str(dest.relative_to(ROOT)),
        "runtime_json": str(RUNTIME_JSON.relative_to(ROOT)),
        "row_count": row_count,
        "runtime_rows": runtime_rows,
        "sha256": _sha256(dest),
        "vendor": "dhan",
        "refresh_policy": "daily_0835_ist",
    }
    META_JSON.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return meta


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync Dhan official instrument master")
    parser.add_argument("--force", action="store_true", help="Try compact CSV if detailed fails")
    args = parser.parse_args()
    meta = sync(force=args.force)
    print("DHAN_INSTRUMENTS_SYNC_COMPLETE")
    print(json.dumps(meta, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
