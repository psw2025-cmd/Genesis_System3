"""Retired local Dhan token-generation setup wizard.

Dhan PIN/TOTP/token lifecycle is now owned by Google Secret Manager and the
canonical Cloud Run rotation Job. This historical local wizard is intentionally
non-mutating so it cannot create a token that invalidates production.
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
                "local_credential_write_allowed": False,
                "token_generation_attempted": False,
                "live_trading_enabled": False,
                "order_placement_allowed": False,
                "raw_token_exposed": False,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
