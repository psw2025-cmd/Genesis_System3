"""
System3 Ultra - Ultra Prediction Engine (Shadow Live) — DISABLED.

This module previously used Dhan broker (DhanBroker) to build live
option-chain snapshots. System3 is Dhan-only — this path is not operational.

Menu option 80 in system3_ultra.py is blocked at the handler level.
Calling run_ultra_live_shadow_once() returns a DISABLED status immediately.
The original 237-line implementation is preserved in git history.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional

PROJECT_ROOT = Path(__file__).parent.parent.parent
ULTRA_DIR = PROJECT_ROOT / "storage" / "ultra"
ULTRA_DIR.mkdir(parents=True, exist_ok=True)

UNDERLYINGS = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]

_DISABLED_REASON = (
    "ultra_live_signals_shadow is disabled. System3 is Dhan-only. " "Dhan broker path is not operational."
)


def load_model_with_meta(model_dir: Path, underlying: str, prefix: str = "") -> Optional[Dict[str, Any]]:
    """Stub — no broker needed for model loading; kept for future Dhan integration."""
    return None


def run_ultra_live_shadow_once() -> Dict[str, Any]:
    """DISABLED — Dhan broker path. Returns DISABLED status immediately."""
    print(f"[DISABLED] {_DISABLED_REASON}")
    return {"status": "DISABLED", "message": _DISABLED_REASON}


def main() -> None:
    """Main entry point."""
    result = run_ultra_live_shadow_once()
    print(f"\n[INFO] {result.get('message', 'Shadow signals not generated')}")


if __name__ == "__main__":
    main()
