#!/usr/bin/env python3
"""Run corrected-framework Phase-1 diagnostics on a frozen model artifact."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.options_research.corrected_framework_diagnostics import (
    analyse_artifact,
    write_reports,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    report = analyse_artifact(args.artifact_root)
    files = write_reports(report, args.output_dir)
    print(json.dumps({
        "status": report["status"],
        "validation_candidates": report["pre_frozen_validation_gate"]["candidates_evaluated"],
        "validation_candidates_passing": report["pre_frozen_validation_gate"]["candidates_passing"],
        "frozen_should_have_remained_closed": report["decision"]["frozen_should_have_remained_closed_under_new_gate"],
        "reports_written": len(files),
        "live_trading_enabled": False,
        "order_placement_allowed": False,
        "promotion_allowed": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
