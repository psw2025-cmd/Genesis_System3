"""Dhan proactive token auto-refresh entry point and daemon."""
from __future__ import annotations

import json
import sys
from typing import Any

from core.brokers.dhan.token_watchdog import watchdog_cycle, run_watchdog_loop


def run_daemon(interval_seconds: float = 900.0) -> dict[str, Any]:
    """Run one watchdog cycle or continuous daemon."""
    return watchdog_cycle()


def main() -> int:
    res = watchdog_cycle()
    print(json.dumps(res, sort_keys=True))
    action = str(res.get("action") or "")
    success = action in ("SKIPPED_HEALTHY", "ROTATED_AND_VERIFIED") or bool(res.get("rotated"))
    return 0 if success else 2


if __name__ == "__main__":
    sys.exit(main())
