"""Bounded NSE UDiFF bhavcopy backfill, stored outside Git.

Example:
  python -m scripts.nse_bulk_backfill --start 2024-09-24 --end 2026-09-23 --segment FO --segment CM --output /data/nse

Writes YYYYMMDD_{fo,cm}_bhavcopy.csv, source receipts and unique manifests, so the dated
walk-forward replays can consume the resulting directory. NSE holidays and
missing dates remain explicit. A 404 never proves closure. Use a durable data volume.
"""
from __future__ import annotations

import argparse
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timedelta, timezone
from hashlib import sha256
from io import BytesIO, StringIO
import json
import os
from pathlib import Path
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from zipfile import ZipFile, BadZipFile


def validate_csv(data: bytes, day: date) -> int:
    """File names and HTTP success do not establish the observation date."""
    table = csv.DictReader(StringIO(data.decode("utf-8-sig")))
    if "TradDt" not in (table.fieldnames or ()):
        raise ValueError("Missing trade-date column")
    count = 0
    for row in table:
        if row["TradDt"] != day.isoformat():
            raise ValueError("CSV trade date differs from requested date")
        count += 1
    if count == 0:
        raise ValueError("Empty market snapshot")
    return count


def fetch(day: date, segment: str, output: Path, *, attempts: int = 3) -> dict:
    if segment not in {"FO", "CM"}:
        raise ValueError("Unsupported NSE segment")
    stamp = day.strftime("%Y%m%d")
    filename = f"BhavCopy_NSE_{segment}_0_0_0_{stamp}_F_0000.csv.zip"
    source = f"https://nsearchives.nseindia.com/content/{segment.lower()}/{filename}"
    path = output / f"{stamp}_{segment.lower()}_bhavcopy.csv"
    receipt_path = path.with_suffix(".receipt.json")
    if path.exists():
        existing = path.read_bytes()
        digest = sha256(existing).hexdigest()
        try:
            receipt = json.loads(receipt_path.read_text())
            if (receipt["csv_sha256"] != digest or receipt["source"] != source
                    or receipt["date"] != day.isoformat() or receipt["segment"] != segment
                    or not receipt.get("first_observed_at") or not receipt.get("zip_sha256")):
                raise ValueError("Unbound cached snapshot")
            validate_csv(existing, day)
            return {**receipt, "status": "already_present"}
        except (OSError, KeyError, ValueError, UnicodeDecodeError):
            return dict(date=day.isoformat(), segment=segment, status="existing_unverified",
                        csv_sha256=digest, bytes=len(existing), source=source)
    last_error = None
    for attempt in range(attempts):
        try:
            request = Request(source, headers={"User-Agent": "Mozilla/5.0",
                                               "Accept": "application/zip"})
            with urlopen(request, timeout=25) as response:
                zipped = response.read(30_000_001)
            if len(zipped) > 30_000_000:
                raise ValueError("ZIP exceeds size limit")
            with ZipFile(BytesIO(zipped)) as archive:
                names = [n for n in archive.namelist() if n.lower().endswith(".csv")]
                if len(names) != 1:
                    raise ValueError("Archive must contain exactly one CSV")
                data = archive.read(names[0])
            if not data.startswith(b"TradDt,") or len(data) > 100_000_000:
                raise ValueError("Unexpected or oversized NSE CSV")
            rows = validate_csv(data, day)
            observed = datetime.now(timezone.utc).isoformat()
            temporary = path.with_suffix(".part")
            with temporary.open("xb") as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            temporary.replace(path)
            receipt = dict(date=day.isoformat(), segment=segment, status="downloaded",
                        zip_sha256=sha256(zipped).hexdigest(),
                        csv_sha256=sha256(data).hexdigest(), bytes=len(data), source=source,
                        first_observed_at=observed, row_count=rows)
            with receipt_path.open("x") as stream:
                json.dump(receipt, stream, sort_keys=True)
                stream.flush()
                os.fsync(stream.fileno())
            return receipt
        except HTTPError as exc:
            if exc.code == 404:
                return dict(date=day.isoformat(), segment=segment,
                            status="source_404", source=source,
                            attempted_at=datetime.now(timezone.utc).isoformat(),
                            closure_proven=False)
            last_error = f"HTTP_{exc.code}"
        except (URLError, BadZipFile, OSError, ValueError) as exc:
            last_error = type(exc).__name__
        if attempt + 1 < attempts:
            time.sleep(min(2 ** attempt, 4))
    return dict(date=day.isoformat(), segment=segment, status="error",
                error=last_error, source=source,
                attempted_at=datetime.now(timezone.utc).isoformat())


def backfill(start: date, end: date, segments: list[str], output: Path,
             *, workers: int = 3, progress=None) -> dict:
    if end < start or (end-start).days > 3660 or not 1 <= workers <= 4:
        raise ValueError("Invalid interval or worker count")
    if not segments or any(segment not in {"FO", "CM"} for segment in segments):
        raise ValueError("At least one valid segment required")
    output.mkdir(parents=True, exist_ok=True)
    days = []
    day = start
    while day <= end:
        # Special exchange sessions can occur on weekends. Never skip by weekday.
        days.append(day)
        day += timedelta(days=1)
    jobs = [(day, segment) for day in days for segment in segments]
    if len(jobs) != len(set(jobs)):
        raise ValueError("Duplicate segment")
    results = []
    run_stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    manifest = output / f"manifest-{run_stamp}.jsonl"
    with manifest.open("x") as stream, ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(fetch, day, segment, output) for day, segment in jobs]
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            stream.write(json.dumps(result, sort_keys=True) + "\n")
            stream.flush()
            if progress is not None:
                progress(len(results), len(jobs), result)
    results.sort(key=lambda row: (row["date"], row["segment"]))
    totals = {status: sum(row["status"] == status for row in results)
              for status in ("downloaded", "already_present", "source_404", "error", "existing_unverified")}
    return {"requested": len(jobs), "results": totals, "manifest": str(manifest),
            "calendar_scope": "ALL_CALENDAR_DATES_INCLUDING_WEEKENDS",
            "download_attempts_completed": len(results) == len(jobs),
            "coverage_complete": len(results) == len(jobs) and all(
                row["status"] in {"downloaded", "already_present"} for row in results),
            "missing_dates_are_holidays": False}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", required=True, type=date.fromisoformat)
    parser.add_argument("--end", required=True, type=date.fromisoformat)
    parser.add_argument("--segment", required=True, action="append", choices=("FO", "CM"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(backfill(args.start, args.end, args.segment, args.output), indent=2))


if __name__ == "__main__":
    main()
