#!/usr/bin/env python3
"""Continuous closure orchestrator — scan → verify → watchdog → cards → auto-resume.

Usage:
  python scripts/system3_continuous_closure_orchestrator.py
  python scripts/system3_continuous_closure_orchestrator.py --offline
  python scripts/system3_continuous_closure_orchestrator.py --prod-base https://genesis-system3-web-doq2wplepa-el.a.run.app

Writes:
  reports/latest/continuous_closure/summary.json
  reports/latest/continuous_closure/resume_state.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dashboard.backend.continuous_closure_service import (  # noqa: E402
    DEFAULT_PROD,
    build_continuous_closure_report,
    write_closure_artifacts,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="System3 continuous closure orchestrator")
    parser.add_argument("--prod-base", default=DEFAULT_PROD)
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Skip live URL probes (repo/reports only)",
    )
    args = parser.parse_args()

    report = build_continuous_closure_report(
        ROOT,
        prod_base=args.prod_base,
        include_live=not args.offline,
    )
    summary_path, state_path = write_closure_artifacts(ROOT, report)
    print(json.dumps({"summary": report.get("summary"), "summary_path": str(summary_path), "resume_path": str(state_path)}, indent=2))
    nxt = (report.get("phases") or {}).get("auto_resume") or {}
    if nxt:
        print(f"AUTO_RESUME next={nxt.get('next_id')} state={nxt.get('state')}")
    else:
        print("AUTO_RESUME next=NONE (no open cards)")
    # Exit 0 always for observability runs; open cards are not a process failure.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
