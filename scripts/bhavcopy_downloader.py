"""
NSE FO Bhavcopy Auto-Downloader
================================
Downloads NSE Futures & Options bhavcopy (End-of-Day data archive) from
NSE archives for every trading day at 18:30 IST.

Data source: https://nsearchives.nseindia.com/content/fo/
Format: ZIP containing CSV with OI, volume, OHLC for all F&O contracts.

Scheduled at 18:30 IST weekdays via system3_job_scheduler.json.
Stores to: storage/bhavcopy/YYYYMMDD_fo_bhavcopy.csv

Why: Bhavcopy gives us real historical OI for ALL strikes — this is the
     ground truth for OI change % computation when live APIs are unavailable.

Usage:
  python scripts/bhavcopy_downloader.py              # today
  python scripts/bhavcopy_downloader.py --date 2026-06-12
  python scripts/bhavcopy_downloader.py --backfill 30  # last 30 trading days
  python scripts/bhavcopy_downloader.py --verify      # check what's cached
"""

import argparse
import io
import os
import sys
import time
import zipfile
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

import requests
import pandas as pd

BHAVCOPY_DIR = ROOT_DIR / "storage" / "bhavcopy"

# NSE bhavcopy URL patterns (try new format first, then old)
_URL_NEW = ("https://nsearchives.nseindia.com/content/fo/"
            "BhavCopy_NSE_FO_0_0_0_{date_str}_F_0000.csv.zip")
_URL_OLD = ("https://nsearchives.nseindia.com/content/historical/DERIVATIVES/"
            "{yyyy}/{mon_upper}/fo{dd}{mon_upper}{yyyy}bhav.csv.zip")

# Tracking summary for CHANGE_LOG
_downloaded: list = []
_skipped: list = []
_failed: list = []


def _get_session() -> requests.Session:
    s = requests.Session()
    s.headers.update({
        "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 Chrome/124.0 Safari/537.36"),
        "Accept": "*/*",
        "Referer": "https://www.nseindia.com/",
        "Accept-Language": "en-US,en;q=0.9",
    })
    try:
        s.get("https://www.nseindia.com", timeout=8)
    except Exception:
        pass
    return s


def _trading_days(start: date, end: date) -> list[date]:
    """Returns list of weekdays between start and end (inclusive)."""
    days = []
    cur = start
    while cur <= end:
        if cur.weekday() < 5:  # Mon-Fri only
            days.append(cur)
        cur += timedelta(days=1)
    return days


def download_bhavcopy(ref_date: date, session: requests.Session) -> str:
    """
    Download bhavcopy for ref_date. Returns "downloaded", "exists", or "failed".
    """
    date_str = ref_date.strftime("%Y%m%d")
    local_path = BHAVCOPY_DIR / f"{date_str}_fo_bhavcopy.csv"

    if local_path.exists():
        print(f"  {date_str}: already cached ({local_path.stat().st_size:,} bytes)")
        _skipped.append(date_str)
        return "exists"

    # Build candidate URLs (new format first, then old)
    dd = ref_date.strftime("%d")
    mon = ref_date.strftime("%b").upper()
    yyyy = ref_date.strftime("%Y")

    urls = [
        _URL_NEW.format(date_str=date_str),
        _URL_OLD.format(yyyy=yyyy, mon_upper=mon, dd=dd),
    ]

    for url in urls:
        try:
            print(f"  {date_str}: fetching {url.split('/')[-1]} ...", end=" ", flush=True)
            resp = session.get(url, timeout=30)
            if resp.status_code != 200:
                print(f"HTTP {resp.status_code}")
                continue

            # Extract CSV from zip archive
            with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
                csv_files = [n for n in zf.namelist() if n.lower().endswith(".csv")]
                if not csv_files:
                    print("no CSV in zip")
                    continue
                raw_csv = zf.read(csv_files[0])

            # Parse and validate the CSV
            df = pd.read_csv(io.StringIO(raw_csv.decode("utf-8", errors="replace")),
                             low_memory=False)
            if df.empty:
                print("empty CSV")
                continue

            # Quick validation: check for option rows
            has_opt = False
            for col in df.columns:
                if col in ("INSTRUMENT", "FinInstrmTp"):
                    has_opt = "OPTIDX" in df[col].astype(str).values
                    break

            # Save regardless (even futures data is useful for future extension)
            BHAVCOPY_DIR.mkdir(parents=True, exist_ok=True)
            df.to_csv(local_path, index=False)

            size_kb = local_path.stat().st_size // 1024
            print(f"OK ({len(df):,} rows, {size_kb:,} KB, opt={has_opt})")
            _downloaded.append(date_str)
            return "downloaded"

        except Exception as e:
            print(f"ERROR: {e}")
            continue

    _failed.append(date_str)
    return "failed"


def verify_cache() -> None:
    """List all cached bhavcopy files with metadata."""
    BHAVCOPY_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted(BHAVCOPY_DIR.glob("*_fo_bhavcopy.csv"))
    if not files:
        print("  No bhavcopy files cached yet.")
        print(f"  Cache location: {BHAVCOPY_DIR}")
        return

    print(f"\n  {'Date':<12} {'Rows':>8} {'Size':>10}  Symbols")
    print(f"  {'-'*12} {'-'*8} {'-'*10}  -------")

    for f in files[-20:]:  # Show last 20
        date_str = f.stem.split("_")[0]
        try:
            df = pd.read_csv(f, low_memory=False, nrows=5)
            # Get row count efficiently
            with open(f) as fh:
                row_count = sum(1 for _ in fh) - 1
            size_kb = f.stat().st_size // 1024

            # Find symbol column
            sym_col = next((c for c in df.columns if c in ("SYMBOL", "TckrSymb")), None)
            syms = ""
            if sym_col:
                full_df = pd.read_csv(f, usecols=[sym_col], low_memory=False)
                key_syms = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"]
                found = [s for s in key_syms
                         if (full_df[sym_col].astype(str).str.upper() == s).any()]
                syms = ", ".join(found) if found else "unknown"
            print(f"  {date_str:<12} {row_count:>8,} {size_kb:>8,} KB  {syms}")
        except Exception as e:
            print(f"  {date_str:<12} {'ERROR':>8}            {e}")

    total_mb = sum(f.stat().st_size for f in files) / (1024 * 1024)
    print(f"\n  Total: {len(files)} files, {total_mb:.1f} MB")


def _write_change_log(today: str, n_downloaded: int, n_failed: int) -> None:
    log_file = ROOT_DIR / "CHANGE_LOG.md"
    if not log_file.exists():
        return
    entry = (f"\n**[{today}] [bhavcopy_downloader.py]** "
             f"DOWNLOAD: {n_downloaded} bhavcopy files cached, {n_failed} failed. "
             f"Dates: {_downloaded}\n")
    content = log_file.read_text()
    # Insert before the sentinel line
    sentinel = "<!-- APPEND NEW ENTRIES ABOVE THIS LINE -->"
    if sentinel in content:
        content = content.replace(sentinel, f"{entry}\n{sentinel}", 1)
        log_file.write_text(content)


def main() -> None:
    parser = argparse.ArgumentParser(description="NSE FO bhavcopy downloader")
    parser.add_argument("--date", help="Download for specific date (YYYY-MM-DD)")
    parser.add_argument("--backfill", type=int, metavar="N",
                        help="Download last N trading days")
    parser.add_argument("--verify", action="store_true",
                        help="Show cache inventory, no download")
    parser.add_argument("--delay", type=float, default=2.0,
                        help="Seconds between requests (default: 2.0)")
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f"  NSE FO BHAVCOPY DOWNLOADER — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")

    if args.verify:
        verify_cache()
        return

    BHAVCOPY_DIR.mkdir(parents=True, exist_ok=True)

    if args.date:
        target_dates = [datetime.strptime(args.date, "%Y-%m-%d").date()]
    elif args.backfill:
        end = date.today() - timedelta(days=1)  # don't try today (market may not be closed)
        start = end - timedelta(days=args.backfill * 2)  # extra to account for weekends
        all_days = _trading_days(start, end)
        target_dates = all_days[-args.backfill:]  # take last N trading days
    else:
        # Default: yesterday (today's bhavcopy only available after market close + NSE processing)
        yesterday = date.today() - timedelta(days=1)
        while yesterday.weekday() >= 5:
            yesterday -= timedelta(days=1)
        target_dates = [yesterday]

    print(f"\n  Downloading bhavcopy for {len(target_dates)} date(s):")
    session = _get_session()

    for i, d in enumerate(target_dates):
        download_bhavcopy(d, session)
        if i < len(target_dates) - 1:
            time.sleep(args.delay)  # Polite delay between requests

    print(f"\n  Summary:")
    print(f"    Downloaded : {len(_downloaded)}")
    print(f"    Already had: {len(_skipped)}")
    print(f"    Failed     : {len(_failed)}")
    if _failed:
        print(f"    Failed dates: {_failed}")

    if _downloaded:
        today_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        _write_change_log(today_str, len(_downloaded), len(_failed))

    if _failed and not _downloaded and not _skipped:
        print("\n  WARNING: All downloads failed. NSE archive may be temporarily unavailable.")
        print("  The DataSourceManager will use nsepython/jugaad-data as alternatives.")
        sys.exit(1)


if __name__ == "__main__":
    main()
