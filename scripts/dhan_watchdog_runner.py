"""Retired standalone Dhan token-watchdog runner.

Kept only as a compatibility path for old startup references. It never creates,
renews, or persists a Dhan token.
"""
from __future__ import annotations

import json


def main() -> int:
    print(
        json.dumps(
            {
                "status": "RETIRED",
                "authority": "gcp-cloud-run-job",
                "job": "genesis-system3-dhan-token-rotate",
                "token_generation_attempted": False,
                "live_trading_enabled": False,
                "order_placement_allowed": False,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
