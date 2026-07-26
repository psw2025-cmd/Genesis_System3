#!/usr/bin/env python3
"""Repair one missing NSE F&O EOD session from official archive alternatives.

The script never overwrites an existing valid partition unless --force is used.
Before persistence it proves:
- the source is an NSE archive host;
- the ZIP contains a CSV;
- the internal trade date equals the requested date;
- option contracts and positive-volume rows exist.
"""
from __future__ import annotations

import argparse
import io
import json
import os
import sqlite3
import zipfile
from datetime import date, datetime, timezone
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]


def sha256_file(path: Path) -> str:
    import hashlib
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def candidates(day: date) -> list[str]:
    values = {
        "year": day.strftime("%Y"),
        "mon": day.strftime("%b").upper(),
        "day": day.strftime("%d"),
    }
    relative = "content/historical/DERIVATIVES/{year}/{mon}/fo{day}{mon}{year}bhav.csv.zip".format(**values)
    return [
        f"https://archives.nseindia.com/{relative}",
        f"https://nsearchives.nseindia.com/{relative}",
        f"https://www1.nseindia.com/{relative}",
        f"http://www1.nseindia.com/{relative}",
    ]


def pick(frame: pd.DataFrame, *names: str) -> str | None:
    mapping = {str(column).lower(): str(column) for column in frame.columns}
    return next((mapping[name.lower()] for name in names if name.lower() in mapping), None)


def verify_frame(frame: pd.DataFrame, requested: date) -> dict:
    date_col = pick(frame, "TIMESTAMP", "TradDt", "DATE")
    instrument_col = pick(frame, "INSTRUMENT", "FinInstrmTp")
    side_col = pick(frame, "OPTION_TYP", "OptnTp")
    volume_col = pick(frame, "CONTRACTS", "TtlTradgVol")
    mandatory = {
        "trade_date": date_col,
        "instrument": instrument_col,
        "option_type": side_col,
        "volume": volume_col,
    }
    missing = [name for name, column in mandatory.items() if not column]
    if missing:
        raise ValueError(f"missing mandatory columns: {missing}")

    dates = pd.to_datetime(frame[date_col], errors="coerce", dayfirst=True).dt.date
    unique_dates = sorted({value.isoformat() for value in dates.dropna().unique()})
    if unique_dates != [requested.isoformat()]:
        raise ValueError(f"internal trade dates {unique_dates} do not equal {requested}")

    instrument = frame[instrument_col].fillna("").astype(str).str.upper().str.strip()
    side = frame[side_col].fillna("").astype(str).str.upper().str.strip()
    option_mask = side.isin({"CE", "PE", "CALL", "PUT"}) | instrument.isin({"OPTIDX", "OPTSTK", "IDO", "STO"})
    volume = pd.to_numeric(frame[volume_col], errors="coerce").fillna(0)
    option_rows = int(option_mask.sum())
    positive_volume_rows = int((volume > 0).sum())
    positive_option_volume_rows = int((option_mask & (volume > 0)).sum())
    if option_rows == 0 or positive_option_volume_rows == 0:
        raise ValueError("download contains no traded option rows")
    return {
        "rows": int(len(frame)),
        "internal_dates": unique_dates,
        "option_rows": option_rows,
        "positive_volume_rows": positive_volume_rows,
        "positive_option_volume_rows": positive_option_volume_rows,
    }


def update_manifest(manifest_path: Path, day: date, output: Path, rows: int, source_url: str) -> None:
    connection = sqlite3.connect(manifest_path)
    try:
        connection.execute(
            """
            INSERT OR REPLACE INTO objects
            (object_key, source, symbol, start_date, end_date, status, rows, bytes,
             sha256, path, http_status, error, updated_utc)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                f"NSE_FO_{day:%Y%m%d}", "NSE_FO_EOD", "ALL", day.isoformat(), day.isoformat(),
                "DOWNLOADED", rows, output.stat().st_size, sha256_file(output), str(output), 200,
                f"REPAIRED_FROM_OFFICIAL_ARCHIVE:{source_url}", datetime.now(timezone.utc).isoformat(),
            ),
        )
        connection.commit()
    finally:
        connection.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    day = date.fromisoformat(args.date)
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    target = args.data_root / "nse_fo_eod" / str(day.year) / f"{day:%Y%m%d}_fo.parquet"
    evidence = {
        "requested_date": day.isoformat(),
        "target": str(target),
        "attempts": [],
        "live_trading_enabled": False,
        "order_placement_allowed": False,
    }

    if target.exists() and target.stat().st_size > 0 and not args.force:
        frame = pd.read_parquet(target)
        evidence.update({"status": "EXISTS_VALID", "verification": verify_frame(frame, day)})
        (output_dir / "repair_session.json").write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n")
        print(json.dumps(evidence, indent=2, sort_keys=True))
        return 0

    session = requests.Session()
    session.headers.update({
        "Accept": "*/*",
        "Referer": "https://www.nseindia.com/",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36",
    })
    for url in candidates(day):
        attempt = {"url": url}
        try:
            response = session.get(url, timeout=90, allow_redirects=True)
            attempt.update({
                "http_status": response.status_code,
                "response_bytes": len(response.content),
                "final_url": response.url,
            })
            response.raise_for_status()
            with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
                csv_names = [name for name in archive.namelist() if name.lower().endswith(".csv")]
                if not csv_names:
                    raise ValueError("ZIP_CONTAINS_NO_CSV")
                selected = max(csv_names, key=lambda name: archive.getinfo(name).file_size)
                raw = archive.read(selected)
                attempt["zip_member"] = selected
                attempt["csv_bytes"] = len(raw)
            frame = pd.read_csv(io.BytesIO(raw), low_memory=False, on_bad_lines="skip")
            verification = verify_frame(frame, day)
            target.parent.mkdir(parents=True, exist_ok=True)
            temporary = target.with_suffix(".parquet.part")
            frame.to_parquet(temporary, index=False, compression="zstd")
            os.replace(temporary, target)
            update_manifest(args.data_root / "manifest.sqlite3", day, target, len(frame), url)
            attempt["status"] = "PASS"
            evidence["attempts"].append(attempt)
            evidence.update({
                "status": "REPAIRED",
                "source_url": url,
                "verification": verification,
                "output_bytes": target.stat().st_size,
                "output_sha256": sha256_file(target),
            })
            path = output_dir / "repair_session.json"
            path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            print(json.dumps(evidence, indent=2, sort_keys=True))
            return 0
        except Exception as exc:
            attempt.update({"status": "FAIL", "error": f"{type(exc).__name__}: {exc}"})
            evidence["attempts"].append(attempt)

    evidence["status"] = "FAILED"
    path = output_dir / "repair_session.json"
    path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(evidence, indent=2, sort_keys=True))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
