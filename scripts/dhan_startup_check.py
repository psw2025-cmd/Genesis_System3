"""Read-only compatibility stub for the retired local Dhan startup repair.

Production Dhan token lifecycle is owned exclusively by the Google Cloud Run
rotation Job. Local startup must never mint/renew a token or launch token writer
daemons because a new Dhan token invalidates the production token stored in
Google Secret Manager.
"""
from __future__ import annotations

import json


def run_startup_check(status_only: bool = False) -> dict:
    result = {
        "status": "RETIRED_READ_ONLY",
        "status_only": True,
        "requested_status_only": bool(status_only),
        "actions": [],
        "token_generation_attempted": False,
        "daemon_started": False,
        "watchdog_started": False,
        "authority": "gcp-cloud-run-job",
        "job": "genesis-system3-dhan-token-rotate",
        "live_trading_enabled": False,
        "order_placement_allowed": False,
        "raw_token_exposed": False,
    }
    print(json.dumps(result, sort_keys=True))
    return result


def main() -> int:
    run_startup_check(status_only=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
