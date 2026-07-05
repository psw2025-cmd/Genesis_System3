"""
System3 Phase 95 - Operator Activity Log

Track operator actions in a structured log.
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
OUTPUT_LOG = STORAGE_ULTRA / "phase95_operator_actions.log"
OUTPUT_MD = STORAGE_ULTRA / "phase95_operator_actions.md"

STORAGE_ULTRA.mkdir(parents=True, exist_ok=True)

# Action counts
action_counts = defaultdict(int)


def log_operator_action(action: str, details: Dict[str, Any]) -> None:
    """Log an operator action."""
    timestamp = datetime.now().isoformat()
    entry = {
        "timestamp": timestamp,
        "action": action,
        "details": details,
    }

    # Write to log
    log_entry = f"[{timestamp}] ACTION={action} {json.dumps(details)}\n"
    with OUTPUT_LOG.open("a", encoding="utf-8") as f:
        f.write(log_entry)

    action_counts[action] += 1


def self_test() -> None:
    """Run self-test with sample actions."""
    print("\n" + "=" * 70)
    print("SYSTEM3 PHASE 95 - OPERATOR ACTIVITY LOG - SELF TEST")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Log sample actions
    log_operator_action(
        "ran_dashboard",
        {
            "phase": 91,
            "output": "phase91_live_dashboard.md",
        },
    )

    log_operator_action(
        "ran_full_validation",
        {
            "phase": "validation",
            "result": "51/51 passed",
        },
    )

    log_operator_action(
        "viewed_logs",
        {
            "log_file": "system3_ultra_20251130.log",
        },
    )

    # Generate MD summary
    generate_md_summary()

    print(f"[PH95] Logged sample operator actions")
    print(f"[PH95] Activity log: {OUTPUT_LOG}")


def generate_md_summary() -> None:
    """Generate markdown summary of actions."""
    with OUTPUT_MD.open("w", encoding="utf-8") as f:
        f.write("# System3 Phase 95 - Operator Activity Summary\n\n")
        f.write(f"**Date**: {datetime.now().isoformat()}\n\n")

        f.write("## Action Counts\n\n")
        f.write("| Action | Count |\n")
        f.write("|--------|-------|\n")

        for action, count in sorted(action_counts.items()):
            f.write(f"| {action} | {count} |\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="System3 Phase 95 - Operator Activity Log")
    parser.add_argument("--self-test", action="store_true", help="Run self-test")

    args = parser.parse_args()

    try:
        if args.self_test:
            self_test()
        else:
            parser.print_help()

        print("\n[PH95] Operator activity logging complete.")
        return 0
    except Exception as e:
        print(f"\n[PH95] Error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
