"""
System3 Phase 94 - Notification Engine

Central notification router, writing events to a log only (no external sends yet).
"""

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Paths
STORAGE_ULTRA = PROJECT_ROOT / "storage" / "ultra" / "ph76_ph100"

# Output files
OUTPUT_LOG = STORAGE_ULTRA / "phase94_notifications.log"
OUTPUT_MD = STORAGE_ULTRA / "phase94_notifications.md"

STORAGE_ULTRA.mkdir(parents=True, exist_ok=True)

# Event type counts
event_counts = defaultdict(int)


def notify(event_type: str, payload: Dict[str, Any]) -> None:
    """Send a notification (writes to log only)."""
    timestamp = datetime.now().isoformat()
    entry = {
        "timestamp": timestamp,
        "event_type": event_type,
        "payload": payload,
    }

    # Write to log
    log_entry = f"[{timestamp}] {event_type}: {json.dumps(payload)}\n"
    with OUTPUT_LOG.open("a", encoding="utf-8") as f:
        f.write(log_entry)

    event_counts[event_type] += 1


def self_test() -> None:
    """Run self-test with sample notifications."""
    print("\n" + "=" * 70)
    print("SYSTEM3 PHASE 94 - NOTIFICATION ENGINE - SELF TEST")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Send sample notifications
    notify(
        "BIG_LOSS",
        {
            "underlying": "NIFTY",
            "pnl_pct": -15.5,
            "trade_id": "test_001",
        },
    )

    notify(
        "HIGH_CONF_SIGNAL",
        {
            "underlying": "BANKNIFTY",
            "confidence": 0.95,
            "expected_move": 0.45,
        },
    )

    notify(
        "RISK_LIMIT_NEAR",
        {
            "current_risk_pct": 4.8,
            "limit_pct": 5.0,
            "underlying": "FINNIFTY",
        },
    )

    # Generate MD summary
    generate_md_summary()

    print(f"[PH94] Sent test notifications ({len(event_counts)} events)")
    print(f"[PH94] Notification log: {OUTPUT_LOG}")


def generate_md_summary() -> None:
    """Generate markdown summary of notifications."""
    with OUTPUT_MD.open("w", encoding="utf-8") as f:
        f.write("# System3 Phase 94 - Notification Summary\n\n")
        f.write(f"**Date**: {datetime.now().isoformat()}\n\n")

        f.write("## Event Type Counts\n\n")
        f.write("| Event Type | Count |\n")
        f.write("|------------|-------|\n")

        for event_type, count in sorted(event_counts.items()):
            f.write(f"| {event_type} | {count} |\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="System3 Phase 94 - Notification Engine")
    parser.add_argument("--self-test", action="store_true", help="Run self-test")

    args = parser.parse_args()

    try:
        if args.self_test:
            self_test()
        else:
            parser.print_help()

        print("\n[PH94] Notification engine complete.")
        return 0
    except Exception as e:
        print(f"\n[PH94] Error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
