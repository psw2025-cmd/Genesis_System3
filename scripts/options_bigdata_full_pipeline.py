#!/usr/bin/env python3
"""One-command analyzer-only big-data, verification, training, and backtest pipeline.

This wrapper is resumable. Bounded runs process the next unfinished manifest objects.
It never enables live trading, never calls order APIs, and never promotes a model.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_ROOT = Path(os.getenv("SYSTEM3_RESEARCH_DATA_ROOT", ROOT / "storage" / "research_options"))
DEFAULT_REPORT_DIR = ROOT / "reports" / "latest" / "options_bigdata_research"
TRUTHY = {"1", "true", "yes", "on"}


def ensure_analyzer_only() -> None:
    for name in ("LIVE_TRADING_ENABLED", "SYSTEM3_LIVE_TRADING_ALLOWED"):
        if str(os.getenv(name, "0")).strip().lower() in TRUTHY:
            raise RuntimeError(f"{name} must remain disabled")


def run_step(name: str, command: list[str], cwd: Path) -> dict:
    completed = subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)
    return {
        "name": name,
        "return_code": completed.returncode,
        "passed": completed.returncode == 0,
        "command": command,
        "stdout_tail": completed.stdout[-4000:],
        "stderr_tail": completed.stderr[-4000:],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", type=Path, default=DEFAULT_DATA_ROOT)
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    parser.add_argument("--security-master", type=Path, default=ROOT / "security_id_list.csv")
    parser.add_argument("--nse-start", default="2016-07-26")
    parser.add_argument("--dhan-start", default=(date.today() - timedelta(days=365 * 5)).isoformat())
    parser.add_argument("--end", default=date.today().isoformat())
    parser.add_argument("--interval", choices=["1", "5", "15", "25", "60"], default="1")
    parser.add_argument("--batch-limit", type=int, default=500, help="Next unfinished objects; 0 means unbounded")
    parser.add_argument("--delay-seconds", type=float, default=0.25)
    parser.add_argument("--retries", type=int, default=4)
    parser.add_argument("--exchanges", default="NSE,BSE")
    parser.add_argument("--horizon-bars", type=int, default=30)
    parser.add_argument("--cost-bps", type=float, default=40.0)
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--decision-time", default="10:00")
    parser.add_argument("--skip-nse", action="store_true")
    parser.add_argument("--skip-dhan", action="store_true")
    parser.add_argument("--skip-train", action="store_true")
    args = parser.parse_args()

    ensure_analyzer_only()
    args.report_dir.mkdir(parents=True, exist_ok=True)
    python = sys.executable
    downloader = ROOT / "scripts" / "options_bigdata_download.py"
    trainer = ROOT / "scripts" / "options_research_train_backtest.py"
    limit_args = [] if args.batch_limit == 0 else ["--limit", str(args.batch_limit)]
    common = [
        "--security-master", str(args.security_master), "--end", args.end, "--interval", args.interval,
        "--data-root", str(args.data_root), "--report-dir", str(args.report_dir),
        "--delay-seconds", str(args.delay_seconds), "--retries", str(args.retries),
        "--exchanges", args.exchanges,
    ]

    steps: list[dict] = []
    if not args.skip_nse:
        steps.append(run_step(
            "download_nse_eod",
            [python, str(downloader), "download-nse", "--start", args.nse_start, *common, *limit_args],
            ROOT,
        ))
    if not args.skip_dhan:
        steps.append(run_step(
            "download_dhan_rolling",
            [python, str(downloader), "download-dhan", "--start", args.dhan_start, *common, *limit_args],
            ROOT,
        ))
    steps.append(run_step(
        "verify_downloaded_data",
        [python, str(downloader), "verify", "--start", args.dhan_start, *common],
        ROOT,
    ))
    if not args.skip_train:
        steps.append(run_step(
            "train_and_backtest",
            [
                python, str(trainer), "--data-root", str(args.data_root), "--report-dir", str(args.report_dir),
                "--horizon-bars", str(args.horizon_bars), "--cost-bps", str(args.cost_bps),
                "--top-k", str(args.top_k), "--decision-time", args.decision_time,
            ],
            ROOT,
        ))

    passed = sum(step["passed"] for step in steps)
    failed = len(steps) - passed
    payload = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PIPELINE_EXECUTED" if failed == 0 else "PARTIAL_OR_BLOCKED",
        "steps": len(steps),
        "steps_passed": passed,
        "steps_failed_or_blocked": failed,
        "batch_limit": args.batch_limit,
        "data_root": str(args.data_root),
        "promotion_allowed": False,
        "live_trading_enabled": False,
        "order_placement_allowed": False,
        "step_results": steps,
    }
    output = args.report_dir / "full_pipeline_summary.json"
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0 if failed == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
