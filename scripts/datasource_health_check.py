"""
Data Source Health Check
========================
Probes all data sources and reports their status.
Runs at 08:00 IST daily via system3_job_scheduler.json.

Saves results to state/datasource_health.json for dashboard display.
Emits alert if fewer than 2 sources are operational (CRITICAL resilience).

Usage:
  python scripts/datasource_health_check.py
  python scripts/datasource_health_check.py --json    # machine-readable output
  python scripts/datasource_health_check.py --quick   # NSE + bhavcopy only
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))


def _status_icon(status: str) -> str:
    if status == "OK":
        return "[OK]"
    if status in ("EMPTY", "SKIP"):
        return "[--]"
    return "[XX]"


def main() -> None:
    parser = argparse.ArgumentParser(description="Data source health check")
    parser.add_argument("--json", action="store_true", help="Print JSON output only")
    parser.add_argument("--quick", action="store_true", help="Check NSE + bhavcopy only")
    args = parser.parse_args()

    if not args.json:
        print(f"\n{'='*60}")
        print(f"  DATA SOURCE HEALTH CHECK — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")

    from core.data.datasource_manager import get_manager
    mgr = get_manager()

    if args.quick:
        # Quick check: just NSE + bhavcopy (fast, used in pre-market)
        from datetime import date
        from datetime import timedelta

        results = {}
        import time

        # P2: NSE
        t0 = time.time()
        try:
            df, spot = mgr._try_nse("NIFTY")
            ms = int((time.time() - t0) * 1000)
            if df is not None and not df.empty:
                results["nse"] = {"status": "OK", "latency_ms": ms, "rows": len(df), "spot": spot}
            else:
                results["nse"] = {"status": "EMPTY", "latency_ms": ms}
        except Exception as e:
            ms = int((time.time() - t0) * 1000)
            results["nse"] = {"status": "FAIL", "error": str(e)[:80], "latency_ms": ms}

        # P4: Bhavcopy
        yesterday = date.today() - __import__("datetime").timedelta(days=1)
        t0 = time.time()
        try:
            bdf, bspot = mgr._try_bhavcopy("NIFTY", yesterday)
            ms = int((time.time() - t0) * 1000)
            if bdf is not None and not bdf.empty:
                results["bhavcopy"] = {"status": "OK", "latency_ms": ms, "rows": len(bdf)}
            else:
                results["bhavcopy"] = {"status": "EMPTY", "latency_ms": ms}
        except Exception as e:
            ms = int((time.time() - t0) * 1000)
            results["bhavcopy"] = {"status": "FAIL", "error": str(e)[:80], "latency_ms": ms}

        health = {"timestamp": datetime.now().isoformat(timespec="seconds"),
                  "mode": "quick", "sources": results}
    else:
        # Full check
        health = mgr.health_check()

    if args.json:
        print(json.dumps(health, indent=2))
        return

    # Human-readable output
    print(f"\n  {'Source':<14} {'Status':<8} {'Latency':>10}  {'Detail'}")
    print(f"  {'-'*14} {'-'*8} {'-'*10}  {'-'*30}")

    source_order = ["dhan", "nse", "nsepython", "bhavcopy", "jugaad", "yfinance"]
    sources = health.get("sources", {})

    for src in source_order:
        if src not in sources:
            continue
        info = sources[src]
        status = info.get("status", "?")
        icon = _status_icon(status)
        latency = f"{info.get('latency_ms', 0):>6}ms"
        detail = ""
        if status == "OK":
            rows = info.get("rows", 0)
            spot = info.get("spot", 0)
            detail = f"{rows} rows" + (f", spot={spot:.0f}" if spot else "")
        elif "error" in info:
            detail = info["error"][:50]

        print(f"  {src:<14} {icon} {status:<5}  {latency}  {detail}")

    ok_count = health.get("ok_sources", sum(1 for s in sources.values() if s.get("status") == "OK"))
    resilience = health.get("resilience", "UNKNOWN")
    print(f"\n  Resilience: {resilience} ({ok_count}/{len(sources)} sources operational)")

    if resilience == "CRITICAL":
        print("\n  !!! CRITICAL: All data sources failed — system cannot rank today !!!")
        print("  Actions:")
        print("    1. Check internet connectivity")
        print("    2. Verify NSE archive: https://nsearchives.nseindia.com/content/fo/")
        print("    3. Install missing libraries: pip install nsepython jugaad-data yfinance")
        print("    4. Run bhavcopy backfill: python scripts/bhavcopy_downloader.py --backfill 5")
    elif resilience == "LOW":
        print("\n  WARNING: Only 1 source operational — run backfill to restore bhavcopy:")
        print("    python scripts/bhavcopy_downloader.py --backfill 10")

    # Log to CHANGE_LOG if CRITICAL
    if resilience in ("CRITICAL", "LOW"):
        log_file = ROOT_DIR / "CHANGE_LOG.md"
        if log_file.exists():
            ts = datetime.now().strftime("%Y-%m-%d %H:%M")
            entry = (f"\n**[{ts}] [datasource_health_check.py]** "
                     f"ALERT: Data source resilience = {resilience} ({ok_count} OK). "
                     f"Source status: {json.dumps({k: v.get('status') for k, v in sources.items()})}\n")
            content = log_file.read_text()
            sentinel = "<!-- APPEND NEW ENTRIES ABOVE THIS LINE -->"
            if sentinel in content:
                content = content.replace(sentinel, f"{entry}\n{sentinel}", 1)
                log_file.write_text(content)


if __name__ == "__main__":
    main()
