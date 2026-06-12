"""
Connectivity Probe — Dhan broker / data source only.

System3 is Dhan-only. This probe verifies that the Dhan SDK can be
imported and that basic module availability is healthy. Angel One /
SmartAPI paths are intentionally excluded.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))


def probe_connectivity() -> Dict[str, Any]:
    """Probe Dhan broker / data source connectivity."""
    probe: Dict[str, Any] = {
        "timestamp": datetime.now().isoformat(),
        "mode": "dhan-only",
        "dhan_sdk_available": False,
        "angel_broker_shim": False,
        "live_chain_ws_shim": False,
        "status": "UNKNOWN",
        "details": {},
    }

    # Dhan SDK import check
    try:
        import dhanhq  # noqa: F401
        probe["dhan_sdk_available"] = True
        probe["details"]["dhanhq_import"] = "SUCCESS"
    except ImportError:
        probe["details"]["dhanhq_import"] = "FAILED — dhanhq not installed"

    # Angel One broker shim (should import cleanly, raise only on use)
    try:
        from core.brokers.angel_one.broker import AngelOneBroker  # noqa: F401
        probe["angel_broker_shim"] = True
        probe["details"]["angel_broker_shim"] = "SUCCESS — disabled shim present"
    except Exception as exc:
        probe["details"]["angel_broker_shim"] = f"FAILED — {exc}"

    # live_chain_ws shim (should import cleanly)
    try:
        from src.angel.live_chain_ws import LiveChainWebSocket  # noqa: F401
        probe["live_chain_ws_shim"] = True
        probe["details"]["live_chain_ws_shim"] = "SUCCESS — disabled shim present"
    except Exception as exc:
        probe["details"]["live_chain_ws_shim"] = f"FAILED — {exc}"

    # Overall status
    if probe["dhan_sdk_available"]:
        probe["status"] = "DHAN_READY"
    else:
        probe["status"] = "DHAN_SDK_MISSING"

    return probe


if __name__ == "__main__":
    result = probe_connectivity()
    print(json.dumps(result, indent=2))
