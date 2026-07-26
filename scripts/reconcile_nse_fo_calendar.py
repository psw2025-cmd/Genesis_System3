#!/usr/bin/env python3
"""Reconcile persisted NSE F&O sessions against independent calendar evidence.

Evidence hierarchy:
1. Actual official NSE archive files, their internal dates and traded option rows.
2. pandas_market_calendars NSE schedule across the historical interval.
3. Official NSE holiday-master endpoint for the current calendar year.
4. Explicit exchange circular exceptions not yet represented by the maintained
   calendar library.
5. A separately classified source-unavailable trading session is allowed only
   when the date is proven open and multiple archive alternatives are proven
   unavailable. It is never converted into synthetic market data.

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

SUPPLEMENTAL_FO_HOLIDAYS = {
    date(2020, 5, 25): {
        "description": "Id-Ul-Fitr (Ramzan ID)",
        "reference": "NSE/FAOP/42878; NSE Clearing F&O holiday calendar 2020",
    },
    date(2024, 1, 22): {
        "description": "Public holiday under Negotiable Instruments Act",
        "reference": "NSE/FAOP/60340; NCL/CMPT/60343",
    },
    date(2024, 11, 20): {
        "description": "Maharashtra Assembly General Elections",
        "reference": "NSE F&O election holiday circular dated 2024-11-12",
    },
    date(2026, 1, 15): {
        "description": "Municipal Corporation Elections in Maharashtra",
        "reference": "NSE/FAOP/72262",
    },
}

# This is not classified as a holiday. It remains an explicit data gap.
# The trading date is independently proven open, while four NSE archive URL
# variants returned 404 or TLS failure. No interpolation or fabricated rows are
# permitted for this session.
KNOWN_SOURCE_UNAVAILABLE_SESSIONS = {
    date(2021, 3, 30): {
        "classification": "TRADING_SESSION_SOURCE_UNAVAILABLE",
        "market_open_evidence": [
            "SEBI/NSE March 2021 trading statistics include 30-Mar-2021",
            "NSE 2021 holiday list declares 29-Mar-2021, not 30-Mar-2021, as Holi holiday",
        ],
        "archive_attempts": [
            "https://archives.nseindia.com/content/historical/DERIVATIVES/2021/MAR/fo30MAR2021bhav.csv.zip -> HTTP 404",
            "https://nsearchives.nseindia.com/content/historical/DERIVATIVES/2021/MAR/fo30MAR2021bhav.csv.zip -> HTTP 404",
            "https://www1.nseindia.com/content/historical/DERIVATIVES/2021/MAR/fo30MAR2021bhav.csv.zip -> TLS failure",
            "http://www1.nseindia.com/content/historical/DERIVATIVES/2021/MAR/fo30MAR2021bhav.csv.zip -> redirected TLS failure",
        ],
        "synthetic_reconstruction_allowed": False,
    },
}


def file_date(path: Path) -> date:
    match = DATE_PATTERN.search(path.name)
    if not match:
        raise ValueError(f"date not found in {path.name}")
    return datetime.strptime(match.group(1), "%Y%m%d").date()


def iso_dates(values) -> list[str]:
    return sorted(value.isoformat() for value in values)


def pick(frame: pd.DataFrame, *names: str) -> str | None:
    mapping = {str(column).lower(): str(column) for column in frame.columns}
    return next((mapping[name.lower()] for name in names if name.lower() in mapping), None)


def archive_session_evidence(path: Path, expected_day: date) -> dict:
    try:
        frame = pd.read_parquet(path)
        date_col = pick(frame, "TradDt", "TIMESTAMP", "DATE")
        instrument_col = pick(frame, "FinInstrmTp", "INSTRUMENT")
        option_col = pick(frame, "OptnTp", "OPTION_TYP")
        volume_col = pick(frame, "TtlTradgVol", "CONTRACTS")
        missing = [
            name for name, column in {
                "date": date_col, "instrument": instrument_col,
                "option_type": option_col, "volume": volume_col,
            }.items() if not column
        ]
        if missing:
            return {"valid": False, "error": f"missing columns {missing}"}
        internal = pd.to_datetime(frame[date_col], errors="coerce", dayfirst=True).dt.date
        internal_dates = sorted({value.isoformat() for value in internal.dropna().unique()})
        instrument = frame[instrument_col].fillna("").astype(str).str.upper().str.strip()
        option_type = frame[option_col].fillna("").astype(str).str.upper().str.strip()
        volume = pd.to_numeric(frame[volume_col], errors="coerce").fillna(0)
        option_mask = option_type.isin({"CE", "PE", "CALL", "PUT"}) | instrument.isin(
            {"IDO", "STO", "OPTIDX", "OPTSTK"}
        )
        traded_option_rows = int((option_mask & (volume > 0)).sum())
        valid = internal_dates == [expected_day.isoformat()] and traded_option_rows > 0
        return {
            "valid": valid,
            "file": str(path),
            "rows": int(len(frame)),
            "internal_dates": internal_dates,
            "option_rows": int(option_mask.sum()),
            "traded_option_rows": traded_option_rows,
        }
    except Exception as exc:
        return {"valid": False, "file": str(path), "error": f"{type(exc).__name__}: {exc}"}


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
        dates = set()
        for row in rows:
            raw = row.get("tradingDate")
            if not raw:
                continue
            parsed = datetime.strptime(str(raw), "%d-%b-%Y").date()
            if parsed.year == year:
                dates.add(parsed)
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
    path_by_date = {file_date(path): path for path in files if start <= file_date(path) <= end}
    actual = set(path_by_date)
    weekdays = {stamp.date() for stamp in pd.bdate_range(start, end)}

    calendar = mcal.get_calendar("NSE")
    schedule = calendar.schedule(start_date=start.isoformat(), end_date=end.isoformat())
    library_expected = {pd.Timestamp(value).date() for value in schedule.index}
    library_non_sessions = weekdays - library_expected

    current_year = end.year
    official_dates, official_evidence = official_fo_holidays(current_year)
    official_in_range = {day for day in official_dates if start <= day <= end and day.weekday() < 5}
    supplemental = {day for day in SUPPLEMENTAL_FO_HOLIDAYS if start <= day <= end}
    declared_holidays = official_in_range | supplemental

    library_unexpected = actual - library_expected
    special_session_evidence = {
        day.isoformat(): archive_session_evidence(path_by_date[day], day)
        for day in sorted(library_unexpected)
    }
    confirmed_special_sessions = {
        date.fromisoformat(raw_day)
        for raw_day, evidence in special_session_evidence.items()
        if evidence.get("valid")
    }
    unconfirmed_special_sessions = library_unexpected - confirmed_special_sessions

    adjusted_expected = (library_expected | confirmed_special_sessions) - declared_holidays
    adjusted_non_sessions = weekdays - adjusted_expected
    missing_weekdays = weekdays - actual
    missing_reconciled_holidays = missing_weekdays & adjusted_non_sessions
    all_missing_expected = adjusted_expected - actual
    known_source_unavailable = {
        day for day in all_missing_expected if day in KNOWN_SOURCE_UNAVAILABLE_SESSIONS
    }
    missing_unexplained = all_missing_expected - known_source_unavailable
    unexpected_archive_sessions = actual - adjusted_expected

    manifest = read_manifest(args.data_root / "manifest.sqlite3")
    manifest_unavailable = {
        day for day, status in manifest.items()
        if status == "UNAVAILABLE" and start <= day <= end
    }
    unavailable_reconciled_holiday = manifest_unavailable & adjusted_non_sessions
    unavailable_expected_session = manifest_unavailable & adjusted_expected
    unavailable_known_source_gap = unavailable_expected_session & known_source_unavailable
    unavailable_unexplained = unavailable_expected_session - known_source_unavailable

    official_missing_from_library = official_in_range - library_non_sessions
    library_current_holidays = {day for day in library_non_sessions if day.year == current_year}
    library_missing_from_official = library_current_holidays - official_in_range

    rows = []
    for day in sorted(weekdays | actual):
        if day in actual and day in confirmed_special_sessions:
            classification = "ARCHIVE_CONFIRMED_SPECIAL_SESSION"
        elif day in actual and day in adjusted_expected:
            classification = "ARCHIVE_SESSION"
        elif day in actual:
            classification = "UNEXPECTED_ARCHIVE_SESSION"
        elif day in known_source_unavailable:
            classification = "DOCUMENTED_SOURCE_UNAVAILABLE_SESSION"
        elif day in adjusted_non_sessions:
            classification = "RECONCILED_HOLIDAY"
        else:
            classification = "UNEXPLAINED_MISSING_SESSION"
        rows.append({
            "date": day.isoformat(),
            "weekday": day.strftime("%A"),
            "archive_file": int(day in actual),
            "library_expected_session": int(day in library_expected),
            "confirmed_special_session": int(day in confirmed_special_sessions),
            "official_or_supplemental_holiday": int(day in declared_holidays),
            "adjusted_expected_session": int(day in adjusted_expected),
            "known_source_unavailable": int(day in known_source_unavailable),
            "manifest_status": manifest.get(day, ""),
            "classification": classification,
        })

    csv_path = output / "nse_fo_calendar_reconciliation.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]) if rows else ["date"])
        writer.writeheader()
        writer.writerows(rows)

    conflicts = len(missing_unexplained) + len(unexpected_archive_sessions) + len(unconfirmed_special_sessions)
    if conflicts:
        status = "FAIL"
    elif known_source_unavailable:
        status = "PASS_WITH_DOCUMENTED_GAP"
    else:
        status = "PASS"
    availability_coverage = len(actual) / len(adjusted_expected) if adjusted_expected else 0.0
    proof = {
        "status": status,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "start": start.isoformat(),
        "end": end.isoformat(),
        "calendar_library": "pandas_market_calendars",
        "calendar_name": "NSE",
        "candidate_weekdays": len(weekdays),
        "library_expected_sessions": len(library_expected),
        "library_weekday_non_sessions": len(library_non_sessions),
        "official_current_year_holidays": len(official_in_range),
        "supplemental_exchange_holidays": len(supplemental),
        "confirmed_special_sessions": len(confirmed_special_sessions),
        "adjusted_expected_sessions": len(adjusted_expected),
        "adjusted_weekday_non_sessions": len(adjusted_non_sessions),
        "archive_sessions": len(actual),
        "archive_files": len(files),
        "archive_session_coverage": availability_coverage,
        "archive_session_coverage_pct": availability_coverage * 100.0,
        "missing_weekdays": len(missing_weekdays),
        "missing_reconciled_as_holiday": len(missing_reconciled_holidays),
        "documented_source_unavailable_sessions": len(known_source_unavailable),
        "missing_unexplained_sessions": len(missing_unexplained),
        "unexpected_archive_sessions": len(unexpected_archive_sessions),
        "unconfirmed_special_sessions": len(unconfirmed_special_sessions),
        "manifest_unavailable": len(manifest_unavailable),
        "manifest_unavailable_reconciled_holiday": len(unavailable_reconciled_holiday),
        "manifest_unavailable_expected_session": len(unavailable_expected_session),
        "manifest_unavailable_documented_source_gap": len(unavailable_known_source_gap),
        "manifest_unavailable_unexplained": len(unavailable_unexplained),
        "documented_source_unavailable_dates": iso_dates(known_source_unavailable),
        "missing_unexplained_dates": iso_dates(missing_unexplained),
        "unexpected_archive_dates": iso_dates(unexpected_archive_sessions),
        "unconfirmed_special_dates": iso_dates(unconfirmed_special_sessions),
        "confirmed_special_dates": iso_dates(confirmed_special_sessions),
        "manifest_unavailable_expected_session_dates": iso_dates(unavailable_expected_session),
        "known_source_unavailable_evidence": {
            day.isoformat(): KNOWN_SOURCE_UNAVAILABLE_SESSIONS[day]
            for day in sorted(known_source_unavailable)
        },
        "supplemental_holiday_evidence": {
            day.isoformat(): SUPPLEMENTAL_FO_HOLIDAYS[day] for day in sorted(supplemental)
        },
        "special_session_evidence": special_session_evidence,
        "official_current_year": {
            **official_evidence,
            "weekday_holidays_in_range": len(official_in_range),
            "official_missing_from_library": iso_dates(official_missing_from_library),
            "library_missing_from_official": iso_dates(library_missing_from_official),
        },
        "row_evidence_csv": str(csv_path),
        "synthetic_sessions_inserted": 0,
        "live_trading_enabled": False,
        "order_placement_allowed": False,
    }
    json_path = output / "nse_fo_calendar_reconciliation.json"
    json_path.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(proof, indent=2, sort_keys=True))
    return 0 if status in {"PASS", "PASS_WITH_DOCUMENTED_GAP"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
