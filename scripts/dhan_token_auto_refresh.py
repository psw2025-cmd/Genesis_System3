"""Retired local Dhan token auto-refresh entry point.

The sole token-generation authority is now the Google Cloud Run Job
``genesis-system3-dhan-token-rotate``. This module intentionally performs no
Dhan token generation or renewal so local/Codespace/legacy workers cannot
invalidate the production Secret Manager token.
"""
from __future__ import annotations

import json


def _retired(action: str = "status") -> dict:
    return {
        "status": "RETIRED",
        "action": action,
        "token_generation_attempted": False,
        "token_renewal_attempted": False,
        "authority": "gcp-cloud-run-job",
        "job": "genesis-system3-dhan-token-rotate",
        "live_trading_enabled": False,
        "order_placement_allowed": False,
        "raw_token_exposed": False,
    }


def run_daemon():
    """Compatibility entry point: exits without starting a token writer."""
    print(json.dumps(_retired("daemon_disabled"), sort_keys=True))
    return _retired("daemon_disabled")


def main() -> int:
    print(json.dumps(_retired("cli_disabled"), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
