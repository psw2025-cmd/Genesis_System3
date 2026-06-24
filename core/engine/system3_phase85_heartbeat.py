"""
System3 Phase 85 - Heartbeat Engine

Maintain a heartbeat log: System3 alive + status, for monitoring.
"""

import argparse
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Paths
STORAGE_ULTRA = PROJECT_ROOT / "storage" / "ultra" / "ph76_ph100"

# Output file
OUTPUT_LOG = STORAGE_ULTRA / "phase85_heartbeat.log"

STORAGE_ULTRA.mkdir(parents=True, exist_ok=True)

# Defaults
DEFAULT_ITERATIONS = 5
DEFAULT_INTERVAL = 5


def get_system_status() -> Dict[str, str]:
    """Get current system status."""
    try:
        from core.engine.dhan_automation_config import AUTOMATION_CONFIG
        from core.engine.ultra_safety import load_ultra_safety

        safety = load_ultra_safety()
        auto_exec = safety.get("AUTO_EXECUTE_TRADES", False) or AUTOMATION_CONFIG.auto_execute_trades

        mode = "ULTRA"  # Default
        safety_status = "SAFE" if not auto_exec else "LOCKDOWN"

        return {
            "mode": mode,
            "auto_exec": "TRUE" if auto_exec else "FALSE",
            "safety": safety_status,
        }
    except Exception:
        return {
            "mode": "BASELINE",
            "auto_exec": "FALSE",
            "safety": "SAFE",
        }


def write_heartbeat(status: Dict[str, str]) -> None:
    """Write heartbeat entry to log."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = (
        f"[{timestamp}] status=ALIVE mode={status['mode']} auto_exec={status['auto_exec']} safety={status['safety']}\n"
    )

    with OUTPUT_LOG.open("a", encoding="utf-8") as f:
        f.write(entry)


def run_heartbeat(iterations: int, interval_seconds: int) -> None:
    """Run heartbeat loop."""
    print("\n" + "=" * 70)
    print("SYSTEM3 PHASE 85 - HEARTBEAT ENGINE")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    print(f"[PH85] Starting heartbeat: {iterations} iterations, {interval_seconds}s interval\n")

    for i in range(iterations):
        status = get_system_status()
        write_heartbeat(status)
        print(f"[PH85] Heartbeat iteration {i+1}/{iterations}")

        if i < iterations - 1:  # Don't sleep after last iteration
            time.sleep(interval_seconds)

    print(f"\n[PH85] Heartbeat complete. Log written to {OUTPUT_LOG}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="System3 Phase 85 - Heartbeat Engine")
    parser.add_argument("--iterations", type=int, default=DEFAULT_ITERATIONS, help="Number of iterations")
    parser.add_argument("--interval-seconds", type=int, default=DEFAULT_INTERVAL, help="Interval between heartbeats")

    args = parser.parse_args()

    try:
        run_heartbeat(args.iterations, args.interval_seconds)
        return 0
    except KeyboardInterrupt:
        print("\n[PH85] Heartbeat interrupted by user.")
        return 0
    except Exception as e:
        print(f"\n[PH85] Error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
