"""
System3 Phase 219 - Breakout Structure Analyzer

Detects support/resistance levels and breakout zones.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

STORAGE_META = PROJECT_ROOT / "storage" / "meta"
STORAGE_META.mkdir(parents=True, exist_ok=True)
BREAKOUT_JSON = STORAGE_META / "system3_breakout_zones.json"

LOG_DIR = PROJECT_ROOT / "logs" / "research"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH = LOG_DIR / "system3_breakout_analyzer.log"

SIGNALS_CSV = PROJECT_ROOT / "storage" / "live" / "dhan_index_ai_signals.csv"


def run_phase219(**kwargs) -> Dict[str, Any]:
    """
    Run Phase 219: Breakout Structure Analyzer.

    Returns:
        dict: {
            "phase": 219,
            "status": "OK" or "WARN" or "ERROR",
            "details": "short summary",
            "outputs": {
                "breakout_zones": int,
                "breakout_file": str,
            },
            "errors": [],
        }
    """
    errors = []
    breakout_zones = []

    try:
        if not SIGNALS_CSV.exists():
            return {
                "phase": 219,
                "status": "WARN",
                "details": "Signals CSV not found",
                "outputs": {"breakout_zones": 0, "breakout_file": str(BREAKOUT_JSON)},
                "errors": [],
            }

        # Load data
        try:
            df = pd.read_csv(SIGNALS_CSV)
        except Exception:
            df = pd.read_csv(SIGNALS_CSV, engine="python", on_bad_lines="skip")

        if "underlying" not in df.columns or "spot" not in df.columns:
            return {
                "phase": 219,
                "status": "WARN",
                "details": "Required columns not found",
                "outputs": {"breakout_zones": 0, "breakout_file": str(BREAKOUT_JSON)},
                "errors": [],
            }

        # Detect support/resistance levels
        for underlying, group in df.groupby("underlying"):
            if len(group) < 10:
                continue

            if "spot" in group.columns:
                prices = group["spot"].dropna()
                if len(prices) < 5:
                    continue

                # Simple support/resistance detection
                recent_high = prices.tail(20).max() if len(prices) >= 20 else prices.max()
                recent_low = prices.tail(20).min() if len(prices) >= 20 else prices.min()
                current_price = prices.iloc[-1]

                # Identify potential breakout zones
                if current_price > recent_high * 0.98:
                    breakout_zones.append(
                        {
                            "underlying": underlying,
                            "zone_type": "RESISTANCE_BREAKOUT",
                            "level": recent_high,
                            "current_price": current_price,
                            "timestamp": group["ts"].iloc[-1] if "ts" in group.columns else datetime.now().isoformat(),
                        }
                    )
                elif current_price < recent_low * 1.02:
                    breakout_zones.append(
                        {
                            "underlying": underlying,
                            "zone_type": "SUPPORT_BREAKDOWN",
                            "level": recent_low,
                            "current_price": current_price,
                            "timestamp": group["ts"].iloc[-1] if "ts" in group.columns else datetime.now().isoformat(),
                        }
                    )

        # Save breakout zones
        breakout_data = {
            "zones": breakout_zones,
            "generated": datetime.now().isoformat(),
        }
        with BREAKOUT_JSON.open("w", encoding="utf-8") as f:
            json.dump(breakout_data, f, indent=2)

        # Log important candidates
        with LOG_PATH.open("w", encoding="utf-8") as f:
            f.write(f"System3 Breakout Analyzer Log\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 70 + "\n\n")
            f.write(f"Breakout Zones Detected: {len(breakout_zones)}\n\n")
            for zone in breakout_zones:
                f.write(f"Underlying: {zone['underlying']}\n")
                f.write(f"Type: {zone['zone_type']}\n")
                f.write(f"Level: {zone['level']:.2f}\n")
                f.write(f"Current: {zone['current_price']:.2f}\n")
                f.write(f"Timestamp: {zone['timestamp']}\n\n")

        status = "OK" if breakout_zones else "WARN"
        details = f"Detected {len(breakout_zones)} breakout zones"

        return {
            "phase": 219,
            "status": status,
            "details": details,
            "outputs": {
                "breakout_zones": len(breakout_zones),
                "breakout_file": str(BREAKOUT_JSON),
                "log_path": str(LOG_PATH),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 219,
            "status": "ERROR",
            "details": f"Phase 219 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 219 - BREAKOUT STRUCTURE ANALYZER")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase219()

    print(f"Phase 219: {result['details']}")
    if result.get("errors"):
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    if result["outputs"]:
        print(f"\nBreakout JSON: {result['outputs']['breakout_file']}")
        print(f"Zones: {result['outputs']['breakout_zones']}")

    return 0 if result["status"] in ("OK", "WARN") else 1


if __name__ == "__main__":
    sys.exit(main())
