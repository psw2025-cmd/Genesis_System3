"""
Soak Test for Live Chain System - Runs for 10 minutes at 5s refresh
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.run_live_chain import LiveChainRunner
from core.utils.logger import logger
from datetime import datetime
import pytz


def main():
    """Run 10-minute soak test."""
    logger.info("=" * 60)
    logger.info("STARTING SOAK TEST - 10 minutes at 5s refresh")
    logger.info("=" * 60)

    runner = LiveChainRunner(refresh_interval=5, use_websocket=False, prefer_weekly=True)  # Use REST for reliability

    start_time = datetime.now(pytz.timezone("Asia/Kolkata"))

    try:
        results = runner.run(duration_minutes=10, max_cycles=120)  # 10 min * 60s / 5s = 120 cycles max

        end_time = datetime.now(pytz.timezone("Asia/Kolkata"))
        duration = (end_time - start_time).total_seconds() / 60

        # Generate proof
        proof = {
            "test_type": "SOAK_TEST",
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_minutes": duration,
            "refresh_interval_seconds": 5,
            "total_cycles": runner.cycle_count,
            "expected_cycles": int(duration * 60 / 5),
            "cycles_completed": len(results) if results else 0,
            "websocket_reconnects": runner.ws_manager.reconnect_count if runner.ws_manager else 0,
            "qc_pass_rate": sum(1 for r in results if r.get("qc_passed", False)) / len(results) * 100 if results else 0,
            "trade_signals_generated": (
                sum(1 for r in results if r.get("trade_signal", {}).get("action") == "TRADE") if results else 0
            ),
            "top_underlyings": (
                list(set(r.get("top_underlying") for r in results if r.get("top_underlying"))) if results else []
            ),
        }

        # Write proof file
        proof_path = ROOT_DIR / "SOAK_TEST_PROOF.md"
        with open(proof_path, "w") as f:
            f.write("# Soak Test Proof\n\n")
            f.write(f"**Test Date**: {start_time.strftime('%Y-%m-%d %H:%M:%S IST')}\n\n")
            f.write(f"**Duration**: {duration:.2f} minutes\n\n")
            f.write(f"**Refresh Interval**: 5 seconds\n\n")
            f.write(f"**Total Cycles**: {runner.cycle_count}\n\n")
            f.write(f"**Expected Cycles**: {proof['expected_cycles']}\n\n")
            f.write(f"**QC Pass Rate**: {proof['qc_pass_rate']:.1f}%\n\n")
            f.write(f"**Trade Signals Generated**: {proof['trade_signals_generated']}\n\n")
            f.write(f"**WebSocket Reconnects**: {proof['websocket_reconnects']}\n\n")
            f.write(
                f"**Top Underlyings Selected**: {', '.join(proof['top_underlyings']) if proof['top_underlyings'] else 'None'}\n\n"
            )
            f.write("## Sample Results\n\n")
            if results:
                f.write("```json\n")
                import json

                f.write(json.dumps(results[:5], indent=2, default=str))
                f.write("\n```\n")

        logger.info(f"Soak test completed. Proof saved to {proof_path}")
        logger.info(f"Cycles: {runner.cycle_count}, Duration: {duration:.2f} minutes")

        return 0

    except Exception as e:
        logger.error(f"Soak test failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
