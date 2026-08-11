"""Retired legacy Render worker entry point.

Genesis System3 production runtime and bounded analyzer jobs are owned by Google
Cloud. This historical forever-daemon used to start independent Dhan token
refresh/watchdog threads. Running it alongside the GCP token-rotation job creates
split-brain authentication: Dhan accepts the newest generated token, while the
Google Secret Manager version used by Cloud Run can immediately become invalid.

This entry point is therefore permanently fail-closed. Use
``scripts/gcp_worker_job.py`` for bounded analyzer/PAPER jobs and
``scripts/gcp_dhan_token_rotation_job.py`` as the sole Dhan token mint authority.

No order route is available here and LIVE trading is never enabled.
"""
from __future__ import annotations

import json
import os
import sys

os.environ["LIVE_TRADING_ENABLED"] = "0"
os.environ["SYSTEM3_LIVE_TRADING_ALLOWED"] = "0"
os.environ["AUTO_EXECUTE_TRADES"] = "0"
os.environ["ANALYZE_MODE"] = "1"
os.environ["SYSTEM3_MODE"] = "ANALYZER"


def main() -> int:
    proof = {
        "status": "RETIRED",
        "component": "scripts/cloud_worker.py",
        "replacement": "scripts/gcp_worker_job.py",
        "dhan_token_authority": "scripts/gcp_dhan_token_rotation_job.py",
        "token_generation_attempted": False,
        "live_trading_enabled": False,
        "order_placement_allowed": False,
        "raw_token_exposed": False,
        "message": "Legacy forever-daemon disabled to prevent Dhan token split-brain.",
    }
    print(json.dumps(proof, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
