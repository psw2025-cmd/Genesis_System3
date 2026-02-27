"""
Connectivity Probe - Test broker/data source connectivity
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))


def probe_connectivity() -> Dict[str, Any]:
    """Probe broker/data source connectivity."""
    probe = {
        "timestamp": datetime.now().isoformat(),
        "broker_available": False,
        "data_fetcher_available": False,
        "websocket_available": False,
        "rest_available": False,
        "status": "UNKNOWN",
        "details": {},
    }

    # Check if SmartApi is available
    try:
        from SmartApi.smartConnect import SmartConnect

        probe["broker_available"] = True
        probe["details"]["smartapi_import"] = "SUCCESS"
    except ImportError:
        probe["details"]["smartapi_import"] = "FAILED - SmartApi not installed"

    # Check if broker can be initialized
    try:
        from core.brokers.angel_one.broker import AngelOneBroker

        try:
            broker = AngelOneBroker(allow_data_only=True)
            probe["data_fetcher_available"] = True
            probe["rest_available"] = True
            probe["details"]["broker_init"] = "SUCCESS"
            probe["status"] = "CONNECTED"
        except Exception as e:
            probe["details"]["broker_init"] = f"FAILED - {str(e)[:100]}"
            probe["status"] = "NO_CREDENTIALS"
    except ImportError:
        probe["details"]["broker_init"] = "FAILED - Broker module not available"
        probe["status"] = "NO_BROKER"

    # Check WebSocket availability
    try:
        from src.angel.live_chain_ws import LiveChainWebSocket

        probe["websocket_available"] = True
        probe["details"]["websocket_import"] = "SUCCESS"
    except ImportError:
        probe["details"]["websocket_import"] = "FAILED - WebSocket module not available"

    # Check REST fallback
    try:
        from src.angel.live_chain_rest import LiveChainREST

        probe["rest_available"] = True
        probe["details"]["rest_import"] = "SUCCESS"
    except ImportError:
        probe["details"]["rest_import"] = "FAILED - REST module not available"

    # Final status determination
    if probe["status"] == "UNKNOWN":
        if not probe["broker_available"]:
            probe["status"] = "NO_BROKER"
        elif not probe["data_fetcher_available"]:
            probe["status"] = "NO_CREDENTIALS"
        else:
            probe["status"] = "CONNECTED"

    return probe


if __name__ == "__main__":
    probe = probe_connectivity()
    print(json.dumps(probe, indent=2))
