"""
Smart Market Auto-Switch System
Automatically detects market status and switches between virtual and live data
Continuously monitors and switches seamlessly
"""

import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

import pytz

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.utils.logger import logger
from src.utils.market_hours import get_market_status, is_market_open

IST = pytz.timezone("Asia/Kolkata")


class SmartMarketAutoSwitch:
    """
    Smart system that auto-detects market status and switches between
    virtual and live data automatically.
    """

    def __init__(self, check_interval: int = 30):
        """
        Initialize smart auto-switch system.

        Args:
            check_interval: How often to check market status (seconds, default: 30)
        """
        self.check_interval = check_interval
        self.current_mode = None  # 'LIVE' or 'VIRTUAL'
        self.market_status_file = ROOT_DIR / "outputs" / "market_status.json"
        self.switch_count = 0
        self.last_check = None
        self.running = False

    def check_market_status(self) -> Dict:
        """
        Check current market status with detailed information.

        Returns:
            Dict with market status details
        """
        now = datetime.now(IST)
        is_open, reason = is_market_open(now)
        status = get_market_status(now)

        result = {
            "timestamp": now.isoformat(),
            "timestamp_ist": now.strftime("%Y-%m-%d %H:%M:%S IST"),
            "is_open": is_open,
            "reason": reason,
            "mode": "LIVE" if is_open else "VIRTUAL",
            "next_open": status.get("next_open"),
            "seconds_until_open": status.get("seconds_until_open"),
        }

        return result

    def should_use_live_data(self) -> bool:
        """
        Determine if system should use live data.

        Returns:
            True if market is open and should use live data
        """
        now = datetime.now(IST)
        is_open, _ = is_market_open(now)
        return is_open

    def get_mode(self) -> str:
        """
        Get current mode (LIVE or VIRTUAL).

        Returns:
            'LIVE' or 'VIRTUAL'
        """
        return "LIVE" if self.should_use_live_data() else "VIRTUAL"

    def save_market_status(self, status: Dict):
        """Save market status to file."""
        import json

        outputs_dir = ROOT_DIR / "outputs"
        outputs_dir.mkdir(exist_ok=True)

        try:
            with open(self.market_status_file, "w", encoding="utf-8") as f:
                json.dump(status, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save market status: {e}")

    def monitor_and_switch(self):
        """
        Continuously monitor market status and switch modes automatically.
        This runs in a separate thread.
        """
        self.running = True
        logger.info("Smart market auto-switch monitor started")

        while self.running:
            try:
                status = self.check_market_status()
                new_mode = status["mode"]

                # Check if mode changed
                if self.current_mode is not None and self.current_mode != new_mode:
                    self.switch_count += 1
                    logger.info(f"🔄 MODE SWITCH: {self.current_mode} → {new_mode}")
                    logger.info(f"   Reason: {status['reason']}")

                    # Log switch event
                    switch_log = {
                        "switch_number": self.switch_count,
                        "from_mode": self.current_mode,
                        "to_mode": new_mode,
                        "timestamp": status["timestamp"],
                        "reason": status["reason"],
                    }

                    # Save switch log
                    switch_file = ROOT_DIR / "outputs" / "mode_switches.json"
                    import json

                    switches = []
                    if switch_file.exists():
                        try:
                            with open(switch_file, "r") as f:
                                switches = json.load(f)
                        except:
                            pass
                    switches.append(switch_log)
                    with open(switch_file, "w") as f:
                        json.dump(switches[-50:], f, indent=2)  # Keep last 50 switches

                self.current_mode = new_mode
                self.last_check = datetime.now(IST)

                # Save current status
                self.save_market_status(status)

                # Wait before next check
                time.sleep(self.check_interval)

            except Exception as e:
                logger.error(f"Error in market monitor: {e}", exc_info=True)
                time.sleep(self.check_interval)

    def start_monitoring(self):
        """Start monitoring in background thread."""
        monitor_thread = threading.Thread(target=self.monitor_and_switch, daemon=True)
        monitor_thread.start()
        return monitor_thread

    def stop_monitoring(self):
        """Stop monitoring."""
        self.running = False


def main():
    """Test the smart auto-switch system."""
    print("=" * 80)
    print("  SMART MARKET AUTO-SWITCH - TEST")
    print("=" * 80)
    print()

    switch = SmartMarketAutoSwitch(check_interval=10)

    # Test current status
    print("Current Market Status:")
    status = switch.check_market_status()
    print(f"  Mode: {status['mode']}")
    print(f"  Market Open: {status['is_open']}")
    print(f"  Reason: {status['reason']}")
    print(f"  Time: {status['timestamp_ist']}")
    if status.get("next_open"):
        print(f"  Next Open: {status['next_open']}")
    print()

    # Test mode detection
    mode = switch.get_mode()
    print(f"Recommended Mode: {mode}")
    print()

    # Start monitoring for 1 minute (test)
    print("Starting 1-minute monitoring test...")
    print("(In production, this runs continuously)")
    print()

    switch.start_monitoring()
    time.sleep(60)  # Monitor for 1 minute
    switch.stop_monitoring()

    print()
    print(f"Monitoring complete. Total switches: {switch.switch_count}")
    print()
    print("=" * 80)

    return 0


if __name__ == "__main__":
    sys.exit(main())
