"""Bounded NSE UDiFF bhavcopy backfill, stored outside Git.

Example:
  python -m scripts.nse_bulk_backfill --start 2024-09-24 --end 2026-09-23 --segment FO --segment CM --output /data/nse

Writes YYYYMMDD_{fo,cm}_bhavcopy.csv plus manifest.jsonl, so the dated
walk-forward replays can consume the resulting directory. NSE holidays and
missing dates remain explicit in the manifest. Use a durable data volume.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, timedelta
from hashlib import sha256
from io import BytesIO
import json
import os
from pathlib import Path
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from zipfile import ZipFile, BadZipFile


def fetch(day: date, segment: str, output: Path, *, attempts: int = 3) -> dict:
    if segment not in {"FO", "CM"}:
        raise ValueError("Unsupported NSE segment")
    stamp = day.strftime("%Y%m%d")
    filename = f"BhavCopy_NSE_{segment}_0_0_0_{stamp}_F_0000.csv.zip"
    source = f"https://nsearchives.nseindia.com/content/{segment.lower()}/{filename}"
    path = output / f"{stamp}_{segment.lower()}_bhavcopy.csv"
    if path.exists():
        existing = path.read_bytes()
        if not existing.startswith(b"TradDt,"):
            raise ValueError(f"Unexpected existing CSV schema: {path}")
        return dict(date=day.isoformat(), segment=segment, status="already_present",
                    csv_sha256=sha256(existing).hexdigest(), bytes=len(existing), source=source)
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
            temporary = path.with_suffix(".part")
            with temporary.open("xb") as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            temporary.replace(path)
            return dict(date=day.isoformat(), segment=segment, status="downloaded",
                        zip_sha256=sha256(zipped).hexdigest(),
                        csv_sha256=sha256(data).hexdigest(), bytes=len(data), source=source)
        except HTTPError as exc:
            if exc.code == 404:
                return dict(date=day.isoformat(), segment=segment,
                            status="source_404", source=source)
            last_error = f"HTTP_{exc.code}"
        except (URLError, BadZipFile, OSError, ValueError) as exc:
            last_error = type(exc).__name__
        time.sleep(min(2 ** attempt, 4))
    return dict(date=day.isoformat(), segment=segment, status="error",
                error=last_error, source=source)


def backfill(start: date, end: date, segments: list[str], output: Path,
             *, workers: int = 3) -> dict:
    if end < start or (end-start).days > 3660 or not 1 <= workers <= 4:
        raise ValueError("Invalid interval or worker count")
    output.mkdir(parents=True, exist_ok=True)
    days = []
    day = start
    while day <= end:
        if day.weekday() < 5:
            days.append(day)
        day += timedelta(days=1)
    jobs = [(day, segment) for day in days for segment in segments]
    if len(jobs) != len(set(jobs)):
        raise ValueError("Duplicate segment")
    results = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(fetch, day, segment, output) for day, segment in jobs]
        for future in as_completed(futures):
            results.append(future.result())
    results.sort(key=lambda row: (row["date"], row["segment"]))
    manifest = output / "manifest.jsonl"
    manifest.write_text("".join(json.dumps(row, sort_keys=True)+"\n" for row in results))
    totals = {status: sum(row["status"] == status for row in results)
              for status in ("downloaded", "already_present", "source_404", "error")}
    return {"requested": len(jobs), "results": totals, "manifest": str(manifest),
            "coverage_complete": totals["error"] == 0}


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
