#!/usr/bin/env python3
"""Reconcile persisted NSE F&O sessions against an independent NSE calendar.

Evidence hierarchy:
1. Actual persisted archive filenames and SQLite manifest.
2. pandas_market_calendars NSE schedule for the entire historical interval.
3. Official NSE holiday-master endpoint for the current calendar year when reachable.

The script is read-only and never changes market data.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sqlite3
from datetime import date, datetime, timezone
from pathlib import Path

import pandas as pd
import pandas_market_calendars as mcal
import requests

DATE_PATTERN = re.compile(r"(20\d{6})")
OFFICIAL_URL = "https://www.nseindia.com/api/holiday-master?type=trading"


def file_date(path: Path) -> date:
    match = DATE_PATTERN.search(path.name)
    if not match:
        raise ValueError(f"date not found in {path.name}")
    return datetime.strptime(match.group(1), "%Y%m%d").date()


def iso_dates(values) -> list[str]:
    return sorted(value.isoformat() for value in values)


def official_fo_holidays(year: int) -> tuple[set[date], dict]:
    headers = {
        "Accept": "application/json,text/plain,*/*",
        "Referer": "https://www.nseindia.com/resources/exchange-communication-holidays",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36",
    }
    evidence = {"url": OFFICIAL_URL, "year": year, "reachable": False, "rows": 0, "error": None}
    try:
        session = requests.Session()
        session.get("https://www.nseindia.com/", headers=headers, timeout=20)
        response = session.get(OFFICIAL_URL, headers=headers, timeout=30)
        response.raise_for_status()
        payload = response.json()
        rows = payload.get("FO") or []
        dates = {
            datetime.strptime(str(row["tradingDate"]), "%d-%b-%Y").date()
            for row in rows
            if row.get("tradingDate") and datetime.strptime(str(row["tradingDate"]), "%d-%b-%Y").year == year
        }
        evidence.update({"reachable": True, "rows": len(rows), "dates_for_year": len(dates)})
        return dates, evidence
    except Exception as exc:
        evidence["error"] = f"{type(exc).__name__}: {exc}"
        return set(), evidence


def read_manifest(path: Path) -> dict[date, str]:
    if not path.exists():
        return {}
    connection = sqlite3.connect(path)
    try:
        rows = connection.execute(
            "SELECT start_date, status FROM objects WHERE source='NSE_FO_EOD'"
        ).fetchall()
    finally:
        connection.close()
    result: dict[date, str] = {}
    for raw_date, status in rows:
        try:
            result[date.fromisoformat(str(raw_date))] = str(status)
        except Exception:
            continue
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    start = date.fromisoformat(args.start)
    end = date.fromisoformat(args.end)
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)

    files = sorted(args.data_root.glob("nse_fo_eod/**/*.parquet"))
    actual = {file_date(path) for path in files if start <= file_date(path) <= end}
    weekdays = {stamp.date() for stamp in pd.bdate_range(start, end)}

    calendar = mcal.get_calendar("NSE")
    schedule = calendar.schedule(start_date=start.isoformat(), end_date=end.isoformat())
    expected = {pd.Timestamp(value).date() for value in schedule.index}
    calendar_non_sessions = weekdays - expected
    missing_weekdays = weekdays - actual
    missing_expected_holidays = missing_weekdays & calendar_non_sessions
    missing_unexplained = missing_weekdays & expected
    unexpected_archive_sessions = actual - expected

    manifest = read_manifest(args.data_root / "manifest.sqlite3")
    manifest_unavailable = {day for day, status in manifest.items() if status == "UNAVAILABLE" and start <= day <= end}
    unavailable_expected_holiday = manifest_unavailable & calendar_non_sessions
    unavailable_expected_session = manifest_unavailable & expected

    current_year = end.year
    official_dates, official_evidence = official_fo_holidays(current_year)
    official_in_range = {day for day in official_dates if start <= day <= end and day.weekday() < 5}
    calendar_current_holidays = {day for day in calendar_non_sessions if day.year == current_year}
    official_missing_from_calendar = official_in_range - calendar_current_holidays
    calendar_missing_from_official = calendar_current_holidays - official_in_range

    rows = []
    for day in sorted(weekdays | actual):
        rows.append({
            "date": day.isoformat(),
            "weekday": day.strftime("%A"),
            "archive_file": int(day in actual),
            "calendar_expected_session": int(day in expected),
            "calendar_non_session": int(day in calendar_non_sessions),
            "manifest_status": manifest.get(day, ""),
            "official_current_year_holiday": int(day in official_in_range),
            "classification": (
                "ARCHIVE_SESSION" if day in actual and day in expected
                else "UNEXPECTED_ARCHIVE_NON_SESSION" if day in actual
                else "RECONCILED_HOLIDAY" if day in calendar_non_sessions
                else "UNEXPLAINED_MISSING_SESSION"
            ),
        })

    csv_path = output / "nse_fo_calendar_reconciliation.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]) if rows else ["date"])
        writer.writeheader()
        writer.writerows(rows)

    conflicts = len(missing_unexplained) + len(unexpected_archive_sessions)
    status = "PASS" if conflicts == 0 else "FAIL"
    proof = {
        "status": status,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "start": start.isoformat(),
        "end": end.isoformat(),
        "calendar_library": "pandas_market_calendars",
        "calendar_name": "NSE",
        "candidate_weekdays": len(weekdays),
        "calendar_expected_sessions": len(expected),
        "calendar_weekday_non_sessions": len(calendar_non_sessions),
        "archive_sessions": len(actual),
        "archive_files": len(files),
        "missing_weekdays": len(missing_weekdays),
        "missing_reconciled_as_holiday": len(missing_expected_holidays),
        "missing_unexplained_sessions": len(missing_unexplained),
        "unexpected_archive_sessions": len(unexpected_archive_sessions),
        "manifest_unavailable": len(manifest_unavailable),
        "manifest_unavailable_reconciled_holiday": len(unavailable_expected_holiday),
        "manifest_unavailable_expected_session": len(unavailable_expected_session),
        "missing_unexplained_dates": iso_dates(missing_unexplained),
        "unexpected_archive_dates": iso_dates(unexpected_archive_sessions),
        "manifest_unavailable_expected_session_dates": iso_dates(unavailable_expected_session),
        "official_current_year": {
            **official_evidence,
            "weekday_holidays_in_range": len(official_in_range),
            "official_missing_from_calendar": iso_dates(official_missing_from_calendar),
            "calendar_missing_from_official": iso_dates(calendar_missing_from_official),
        },
        "row_evidence_csv": str(csv_path),
        "live_trading_enabled": False,
        "order_placement_allowed": False,
    }
    json_path = output / "nse_fo_calendar_reconciliation.json"
    json_path.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(proof, indent=2, sort_keys=True))
    return 0 if status == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
