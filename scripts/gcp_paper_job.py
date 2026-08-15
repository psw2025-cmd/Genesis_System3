#!/usr/bin/env python3
"""Cloud Run Job entrypoint for the durable Genesis System3 paper ledger."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on", "enabled"}


def main() -> int:
    # Hard fail before importing trading modules if a deployment ever drifts.
    forbidden = {
        name: os.environ.get(name)
        for name in ("LIVE_TRADING_ENABLED", "SYSTEM3_LIVE_TRADING_ALLOWED", "AUTO_EXECUTE_TRADES")
        if _truthy(os.environ.get(name))
    }
    if forbidden:
        print(json.dumps({"status": "FAIL", "reason": "LIVE_FLAGS_FORBIDDEN", "flags": sorted(forbidden)}), file=sys.stderr)
        return 2
    os.environ["LIVE_TRADING_ENABLED"] = "0"
    os.environ["SYSTEM3_LIVE_TRADING_ALLOWED"] = "0"
    os.environ["AUTO_EXECUTE_TRADES"] = "0"
    os.environ["ANALYZE_MODE"] = "1"
    os.environ["SYSTEM3_MODE"] = "analyzer"
    os.environ["SYSTEM3_REAL_ONLY"] = "1"

    from dashboard.backend.durable_paper_job import run_durable_paper_once

    try:
        result = run_durable_paper_once()
        print(json.dumps(result, sort_keys=True, default=str), flush=True)
        # Missing Dhan chain is a truthful business-data PENDING state, not an
        # infrastructure crash. The URL keeps the last durable ledger visible.
        return 0 if result.get("status") in {"PASS", "PENDING_NO_DHAN_CHAIN", "SKIPPED_LEASE_HELD"} else 1
    except Exception as exc:
        print(
            json.dumps(
                {
                    "status": "FAIL",
                    "error_type": type(exc).__name__,
                    "message": str(exc)[:240],
                    "live_trading_enabled": False,
                    "broker_order_endpoints_called": False,
                },
                sort_keys=True,
            ),
            file=sys.stderr,
            flush=True,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
