from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from dashboard.backend.paper_pipeline_v8 import build_pipeline_status, run_pipeline_once, run_self_test


def main() -> int:
    p = argparse.ArgumentParser(description="System3 Core Pipeline V8 paper/analyzer proof runner")
    p.add_argument("--self-test", action="store_true", help="Run local safety self-test only")
    p.add_argument("--proof-dir", default="reports/latest/core_pipeline_v8_selftest")
    p.add_argument("--run-once", action="store_true", help="Run pipeline once against repo state")
    p.add_argument("--status", action="store_true", help="Print current pipeline status")
    p.add_argument("--no-create-paper", action="store_true", help="Do not create paper orders; forecast/gate only")
    args = p.parse_args()

    if args.self_test:
        result = run_self_test(ROOT / args.proof_dir)
        print(json.dumps(result, indent=2))
        return 0 if result.get("status") == "PASS" else 2
    if args.run_once:
        result = run_pipeline_once(ROOT, create_paper_orders=not args.no_create_paper, source="manual_cli")
        print(json.dumps(result, indent=2, default=str))
        return 0
    if args.status:
        result = build_pipeline_status(ROOT)
        print(json.dumps(result, indent=2, default=str))
        return 0
    p.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
