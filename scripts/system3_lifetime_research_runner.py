#!/usr/bin/env python3
"""Run lifetime walk-forward research and write proof reports."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dashboard.backend.lifetime_research_engine import run_lifetime_research


def main() -> int:
    parser = argparse.ArgumentParser(description="System3 lifetime research runner")
    parser.add_argument("--root", default=str(ROOT))
    args = parser.parse_args()
    result = run_lifetime_research(Path(args.root).resolve())
    print(json.dumps({"status": result.get("status"), "outcome_rows_loaded": result.get("outcome_rows_loaded"), "champion": result.get("champion"), "blockers": result.get("blockers")}, indent=2, default=str))
    return 0 if result.get("status") in {"CHAMPION_SELECTED", "BLOCKED"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
