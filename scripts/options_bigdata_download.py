#!/usr/bin/env python3
"""CLI for resumable analyzer-only NSE/BSE options historical research data."""
from __future__ import annotations

import argparse
import json
import os
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from src.options_research import (
    Manifest, RollingRequest, Underlying, build_plan, download_dhan, download_nse_eod,
    download_security_master, ensure_analyzer_only, flatten_rolling_response, load_universe,
    relative_strikes, sha256_file, verify_data as _verify_data, write_frame,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_ROOT = Path(os.getenv("SYSTEM3_RESEARCH_DATA_ROOT", ROOT / "storage" / "research_options"))
DEFAULT_REPORT_DIR = ROOT / "reports" / "latest" / "options_bigdata_research"


def verify_data(data_root: Path, manifest: Manifest, limit: int | None = None) -> dict:
    """Compatibility wrapper; data_root is already encoded in manifest paths."""
    del data_root
    return _verify_data(manifest, limit)


def write_report(report_dir: Path, payload: dict) -> None:
    report_dir.mkdir(parents=True, exist_ok=True)
    payload.update({
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "live_trading_enabled": False,
        "order_placement_allowed": False,
    })
    (report_dir / "summary.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Options Big-Data Research", "", f"- Status: **{payload.get('status')}**",
        "- Live trading: `OFF`", "- Order placement: `BLOCKED`", "",
    ]
    lines.extend(f"- {key}: `{value}`" for key, value in payload.items() if key != "status")
    (report_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["plan", "download-nse", "download-dhan", "verify", "all"])
    parser.add_argument("--security-master", type=Path, default=ROOT / "security_id_list.csv")
    parser.add_argument("--start", default=(date.today() - timedelta(days=365 * 5)).isoformat())
    parser.add_argument("--end", default=date.today().isoformat())
    parser.add_argument("--interval", choices=["1", "5", "15", "25", "60"], default="1")
    parser.add_argument("--data-root", type=Path, default=DEFAULT_DATA_ROOT)
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    parser.add_argument("--limit", type=int, default=None, help="Next unfinished objects; 0 means unbounded")
    parser.add_argument("--delay-seconds", type=float, default=0.25)
    parser.add_argument("--retries", type=int, default=4)
    parser.add_argument("--exchanges", default="NSE,BSE")
    args = parser.parse_args()
    if args.limit == 0:
        args.limit = None

    ensure_analyzer_only()
    start, end = date.fromisoformat(args.start), date.fromisoformat(args.end)
    security_master = args.security_master
    if not security_master.exists() or security_master.stat().st_size == 0:
        security_master = args.data_root / "reference" / "api-scrip-master-detailed.csv"
        download_security_master(security_master)
    exchanges = tuple(value.strip().upper() for value in args.exchanges.split(",") if value.strip())
    universe = load_universe(security_master, exchanges)
    plan = build_plan(universe, start, end, args.interval)
    counts = {
        "underlyings": len(universe),
        "index_underlyings": sum(item.instrument == "OPTIDX" for item in universe),
        "stock_underlyings": sum(item.instrument == "OPTSTK" for item in universe),
        "nse_underlyings": sum(item.exchange_segment == "NSE_FNO" for item in universe),
        "bse_underlyings": sum(item.exchange_segment == "BSE_FNO" for item in universe),
        "security_master": str(security_master),
        "dhan_planned_requests": len(plan),
        "date_start": start.isoformat(), "date_end": end.isoformat(),
        "interval_minutes": int(args.interval), "data_root": str(args.data_root),
    }
    if args.command == "plan":
        payload = {"status": "PLAN_ONLY", **counts, "downloaded_rows": 0, "downloaded_files": 0}
        write_report(args.report_dir, payload)
        print(json.dumps(payload, indent=2))
        return 0

    manifest = Manifest(args.data_root / "manifest.sqlite3")
    if args.command == "verify":
        payload = {**counts, **_verify_data(manifest, args.limit)}
        write_report(args.report_dir, payload)
        print(json.dumps(payload, indent=2))
        return 0 if payload["status"] == "PASS" else 2

    results: dict[str, object] = {}
    if args.command in {"download-nse", "all"}:
        results["nse"] = download_nse_eod(start, end, args.data_root, manifest, args.limit)
    if args.command in {"download-dhan", "all"}:
        results["dhan"] = download_dhan(
            plan, args.data_root, manifest, args.limit, args.delay_seconds, args.retries,
        )
    blocked = any(isinstance(result, dict) and result.get("status") == "BLOCKED" for result in results.values())
    failed = any(isinstance(result, dict) and result.get("failed", 0) for result in results.values())
    payload = {
        "status": "BLOCKED" if blocked else ("PARTIAL" if failed else "PASS"),
        **counts, **manifest.summary(), "results": results,
    }
    write_report(args.report_dir, payload)
    print(json.dumps(payload, indent=2))
    return 0 if payload["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
