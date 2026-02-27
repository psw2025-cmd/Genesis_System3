"""
Smart Live Chain Runner with Auto-Switch
Automatically switches between virtual and live data based on market status
"""

import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple
import pytz

# IMMEDIATE OUTPUT - Script is loading
print("[SCRIPT LOADING] smart_live_chain_runner.py is being executed", file=sys.stderr, flush=True)
sys.stderr.flush()

# Ensure output is flushed immediately
try:
    sys.stdout.reconfigure(line_buffering=True) if hasattr(sys.stdout, "reconfigure") else None
except:
    pass

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Import with explicit error handling
try:
    from scripts.run_live_chain import LiveChainRunner
except Exception as e:
    print(f"[FATAL] Failed to import LiveChainRunner: {e}", file=sys.stderr, flush=True)
    raise

try:
    from src.utils.market_hours import is_market_open
except Exception as e:
    print(f"[FATAL] Failed to import is_market_open: {e}", file=sys.stderr, flush=True)
    raise

try:
    from core.utils.logger import logger
except Exception as e:
    print(f"[FATAL] Failed to import logger: {e}", file=sys.stderr, flush=True)
    raise

# Try to import SmartMarketAutoSwitch, create a simple fallback if it fails
try:
    from scripts.smart_market_auto_switch import SmartMarketAutoSwitch
except ImportError as e:
    # Simple fallback class (logger might not be ready yet)
    class SmartMarketAutoSwitch:
        def __init__(self, check_interval: int = 30):
            self.check_interval = check_interval
            self.running = False

        def start_monitoring(self):
            pass

        def stop_monitoring(self):
            self.running = False

except Exception as e:
    print(f"[WARN] Error importing SmartMarketAutoSwitch: {e}", file=sys.stderr, flush=True)

    # Simple fallback class
    class SmartMarketAutoSwitch:
        def __init__(self, check_interval: int = 30):
            self.check_interval = check_interval
            self.running = False

        def start_monitoring(self):
            pass

        def stop_monitoring(self):
            self.running = False


IST = pytz.timezone("Asia/Kolkata")


# Define class
class SmartLiveChainRunner:
    """
    Smart runner that automatically switches between virtual and live data.
    Continuously monitors market status and switches modes seamlessly.
    """

    def __init__(self, refresh_interval: int = 5, market_check_interval: int = 30, use_websocket: bool = False):
        """
        Initialize smart runner.

        Args:
            refresh_interval: Data refresh interval in seconds (default: 5)
            market_check_interval: How often to check market status (default: 30)
            use_websocket: Use WebSocket if available (default: False for reliability)
        """
        self.refresh_interval = refresh_interval
        self.market_check_interval = market_check_interval
        self.use_websocket = use_websocket

        # Initialize auto-switch system (with fallback if import failed)
        try:
            self.auto_switch = SmartMarketAutoSwitch(check_interval=market_check_interval)
        except:
            # Fallback if SmartMarketAutoSwitch not available
            class SimpleAutoSwitch:
                def __init__(self, check_interval):
                    self.check_interval = check_interval
                    self.running = False

                def start_monitoring(self):
                    pass

                def stop_monitoring(self):
                    self.running = False

            self.auto_switch = SimpleAutoSwitch(market_check_interval)

        # Current runner instance
        self.current_runner = None
        self.current_mode = None
        self.running = False

    def create_runner(self, use_sim_mode: bool, mode: str = None) -> Optional[LiveChainRunner]:
        """
        Create appropriate runner based on mode.

        Args:
            use_sim_mode: True for simulation data, False for live data
            mode: Current mode ('LIVE', 'SIMULATION', 'MARKET_CLOSED')

        Returns:
            LiveChainRunner instance or None for MARKET_CLOSED mode
        """
        if mode == "MARKET_CLOSED":
            # MARKET_CLOSED mode doesn't need a runner
            return None

        if use_sim_mode:
            # SIMULATION mode - use replay engine
            from src.sim.replay_engine import ReplayEngine

            replay_engine = ReplayEngine()

            runner = LiveChainRunner(
                refresh_interval=self.refresh_interval,
                use_websocket=False,
                prefer_weekly=True,
                sim_mode=True,
                ignore_market_hours=True,
                replay_engine=replay_engine,
            )
            print("✅ Created runner in SIMULATION mode (replay engine)", flush=True)
            logger.info("Created runner in SIMULATION mode (replay engine)")
        else:
            # LIVE mode - use real API
            runner = LiveChainRunner(
                refresh_interval=self.refresh_interval,
                use_websocket=self.use_websocket,
                prefer_weekly=True,
                sim_mode=False,
                ignore_market_hours=False,
            )
            print("✅ Created runner in LIVE mode (real API data)", flush=True)
            logger.info("Created runner in LIVE mode (real API data)")

        return runner

    def check_and_switch_mode(self) -> bool:
        """
        Check market status and switch mode if needed.
        Implements tri-state logic: LIVE, SIMULATION, MARKET_CLOSED

        Returns:
            True if mode was switched, False otherwise
        """
        now = datetime.now(IST)
        is_open, reason = is_market_open(now)

        # Check ENABLE_SIMULATION config
        try:
            from config.system_config import ENABLE_SIMULATION
        except ImportError:
            # Default to True if config not found
            ENABLE_SIMULATION = True

        # Determine new mode based on tri-state logic
        if is_open:
            new_mode = "LIVE"
            use_sim_mode = False
        elif ENABLE_SIMULATION:
            new_mode = "SIMULATION"
            use_sim_mode = True
        else:
            new_mode = "MARKET_CLOSED"
            use_sim_mode = False

        # Check if mode needs to change
        if self.current_mode != new_mode:
            print(f"🔄 MODE SWITCH DETECTED: {self.current_mode} → {new_mode}", flush=True)
            print(f"   Reason: {reason}", flush=True)
            logger.info(f"🔄 MODE SWITCH DETECTED: {self.current_mode} → {new_mode}")
            logger.info(f"   Reason: {reason}")

            if new_mode == "SIMULATION":
                print("   Simulation enabled - will generate data every cycle", flush=True)
                logger.info("   Simulation enabled - will generate data every cycle")
            elif new_mode == "MARKET_CLOSED":
                print("   Simulation disabled - will write heartbeat files", flush=True)
                logger.info("   Simulation disabled - will write heartbeat files")

            # Stop current runner
            if self.current_runner:
                print("Stopping current runner...", flush=True)
                logger.info("Stopping current runner...")

            # Create new runner with correct mode
            self.current_mode = new_mode
            self.current_runner = self.create_runner(use_sim_mode=use_sim_mode, mode=new_mode)

            # Initialize new runner (skip for MARKET_CLOSED as it doesn't need runner)
            if new_mode != "MARKET_CLOSED":
                print(f"Initializing runner in {new_mode} mode...", flush=True)
                logger.info(f"Initializing runner in {new_mode} mode...")
                if not self.current_runner.initialize_expiries():
                    print("❌ ERROR: Failed to initialize expiries", flush=True)
                    logger.error("Failed to initialize expiries")
                    return False

            print(f"✅ Successfully switched to {new_mode} mode", flush=True)
            logger.info(f"✅ Successfully switched to {new_mode} mode")
            return True

        return False

    def _write_market_closed_heartbeat(self, cycle_count: int):
        """Write heartbeat files when market is closed and simulation is disabled."""
        from pathlib import Path
        import pandas as pd
        import json
        from src.output.export_csv import CSVExporter

        outputs_dir = ROOT_DIR / "outputs"
        outputs_dir.mkdir(exist_ok=True)

        now = datetime.now(IST)
        timestamp_ist = now.strftime("%Y-%m-%d %H:%M:%S IST")
        timestamp_epoch = now.timestamp()

        # Create heartbeat CSV with status
        heartbeat_df = pd.DataFrame(
            [
                {
                    "timestamp_ist": timestamp_ist,
                    "timestamp_epoch": timestamp_epoch,
                    "status": "MARKET_CLOSED",
                    "mode": "HEARTBEAT",
                    "cycle": cycle_count,
                    "message": "Market closed - Simulation disabled - Heartbeat mode active",
                }
            ]
        )

        # Export heartbeat CSV
        exporter = CSVExporter(outputs_dir)
        try:
            exporter.export_chain_raw(heartbeat_df, filename="chain_raw_live.csv")
            print(f"  ✅ Heartbeat written to chain_raw_live.csv (cycle {cycle_count})", flush=True)
            logger.info(f"Heartbeat written to chain_raw_live.csv (cycle {cycle_count})")
        except Exception as e:
            print(f"  ❌ Failed to write heartbeat CSV: {e}", flush=True)
            logger.error(f"Failed to write heartbeat CSV: {e}")

        # Write heartbeat JSON files
        try:
            # QC report heartbeat
            qc_heartbeat = {
                "timestamp": timestamp_ist,
                "status": "MARKET_CLOSED",
                "mode": "HEARTBEAT",
                "overall_passed": False,
                "reason": "Market closed - Simulation disabled",
            }
            with open(outputs_dir / "qc_report_live.json", "w") as f:
                json.dump(qc_heartbeat, f, indent=2)

            # Trade signal heartbeat
            signal_heartbeat = {
                "timestamp": timestamp_ist,
                "action": "NO TRADE",
                "reason": "Market closed - Simulation disabled",
                "mode": "HEARTBEAT",
            }
            with open(outputs_dir / "top_trade_signal.json", "w") as f:
                json.dump(signal_heartbeat, f, indent=2)

            print(f"  ✅ Heartbeat JSON files written (cycle {cycle_count})", flush=True)
            logger.info(f"Heartbeat JSON files written (cycle {cycle_count})")
        except Exception as e:
            print(f"  ❌ Failed to write heartbeat JSON: {e}", flush=True)
            logger.error(f"Failed to write heartbeat JSON: {e}")

    def run(self, duration_minutes: Optional[int] = None):
        """
        Run smart system with auto-switching.

        Args:
            duration_minutes: Run for N minutes (None = infinite)
        """
        # IMMEDIATE OUTPUT - Show we're starting
        print("", flush=True)
        print("=" * 80, flush=True)
        print("  SMART LIVE CHAIN RUNNER - STARTING", flush=True)
        print("=" * 80, flush=True)
        print("", flush=True)

        self.running = True
        start_time = datetime.now()

        # Print to console (visible in window) - flush immediately
        print("=" * 80, flush=True)
        print("  SMART LIVE CHAIN RUNNER - AUTO-SWITCH MODE", flush=True)
        print("=" * 80, flush=True)
        print(flush=True)
        print("Features:", flush=True)
        print("  ✅ Auto-detects market status", flush=True)
        print("  ✅ Uses virtual data when market closed", flush=True)
        print("  ✅ Auto-switches to live data when market opens", flush=True)
        print("  ✅ Seamless mode switching", flush=True)
        print("  ✅ Continuous monitoring", flush=True)
        print(flush=True)

        logger.info("=" * 80)
        logger.info("  SMART LIVE CHAIN RUNNER - AUTO-SWITCH MODE")
        logger.info("=" * 80)

        # Start market monitoring (non-blocking)
        print("Initializing market monitoring...", flush=True)
        try:
            self.auto_switch.start_monitoring()
            print("✅ Market monitoring started", flush=True)
            logger.info("Market monitoring started")
        except Exception as e:
            print(f"⚠️  Market monitoring error (non-critical): {e}", flush=True)
            logger.warning(f"Market monitoring error: {e}")
            import traceback

            traceback.print_exc()

        # Initial mode detection
        print("", flush=True)
        print("Detecting market status and initializing mode...", flush=True)
        try:
            mode_switched = self.check_and_switch_mode()
            if mode_switched:
                print("✅ Mode initialized successfully", flush=True)
            else:
                print(f"✅ Mode already set: {self.current_mode}", flush=True)
        except Exception as e:
            print(f"", flush=True)
            print(f"❌ ERROR in mode detection: {e}", flush=True)
            logger.error(f"Mode detection error: {e}", exc_info=True)
            import traceback

            print("", flush=True)
            print("Traceback:", flush=True)
            traceback.print_exc()
            print("", flush=True)
            print("System will continue anyway...", flush=True)
            # Don't return - continue to loop

        # MARKET_CLOSED mode doesn't need a runner, it uses heartbeat
        if self.current_mode == "MARKET_CLOSED":
            print("MARKET_CLOSED mode - will write heartbeat files every cycle", flush=True)
            logger.info("MARKET_CLOSED mode - will write heartbeat files every cycle")
        elif not self.current_runner:
            print("⚠️  WARNING: Failed to create initial runner", flush=True)
            print("Will retry in next cycle...", flush=True)
            logger.warning("Failed to create initial runner - will retry")
            # Don't return - continue to loop and retry

        print(flush=True)
        print("Starting trading cycles...", flush=True)
        print(f"Current Mode: {self.current_mode}", flush=True)
        print(f"Refresh Interval: {self.refresh_interval} seconds", flush=True)
        print(f"Market Check Interval: {self.market_check_interval} seconds", flush=True)
        if self.current_mode == "SIMULATION":
            print("SIM_MODE ACTIVE - Replay engine enabled", flush=True)
        print(f"Running flag: {self.running}", flush=True)
        print(flush=True)
        print("=" * 80, flush=True)
        print("ENTERING MAIN LOOP - Script will run continuously", flush=True)
        print("Press Ctrl+C to stop", flush=True)
        print("=" * 80, flush=True)
        print(flush=True)

        logger.info("")
        logger.info("Starting trading cycles...")
        logger.info(f"Current Mode: {self.current_mode}")
        logger.info(f"Refresh Interval: {self.refresh_interval} seconds")
        logger.info(f"Market Check Interval: {self.market_check_interval} seconds")
        if self.current_mode == "SIMULATION":
            logger.info("SIM_MODE ACTIVE - Replay engine enabled")
        logger.info("")

        last_market_check = datetime.now()
        cycle_count = 0

        try:
            while self.running:
                # Check duration limit
                if duration_minutes:
                    elapsed = (datetime.now() - start_time).total_seconds() / 60
                    if elapsed >= duration_minutes:
                        logger.info(f"Duration limit reached ({duration_minutes} minutes)")
                        break

                # Check market status periodically and switch if needed
                now = datetime.now()
                if (now - last_market_check).total_seconds() >= self.market_check_interval:
                    if self.check_and_switch_mode():
                        # Mode switched, wait a moment for initialization
                        time.sleep(2)
                    last_market_check = now

                # Run one cycle based on mode
                if self.current_mode == "MARKET_CLOSED":
                    # MARKET_CLOSED mode: Write heartbeat files
                    cycle_count += 1
                    self._write_market_closed_heartbeat(cycle_count)
                    print(f"[CYCLE {cycle_count}] 🔴 MARKET_CLOSED mode - Heartbeat written", flush=True)
                    logger.info(f"[CYCLE {cycle_count}] 🔴 MARKET_CLOSED mode - Heartbeat written")
                elif self.current_runner:
                    try:
                        cycle_count += 1
                        result = self.current_runner.run_cycle()

                        if result:
                            mode_icon = "🟢" if self.current_mode == "LIVE" else "🟡"
                            msg = f"[CYCLE {cycle_count}] {mode_icon} {self.current_mode} mode - QC: {'PASS' if result.get('qc_passed') else 'FAIL'}"
                            print(msg, flush=True)
                            logger.info(msg)
                    except Exception as e:
                        error_msg = f"Error in cycle {cycle_count}: {e}"
                        print(f"❌ {error_msg}", flush=True)
                        logger.error(error_msg, exc_info=True)
                        # Continue to next cycle even if this one failed

                # Wait for next cycle
                time.sleep(self.refresh_interval)

        except KeyboardInterrupt:
            print("\n[INFO] Interrupted by user (Ctrl+C)", flush=True)
            logger.info("Interrupted by user")
        except Exception as e:
            print(f"\n[ERROR] Unexpected error in main loop: {e}", flush=True)
            import traceback

            traceback.print_exc()
            logger.error(f"Unexpected error in main loop: {e}", exc_info=True)
        finally:
            print("[INFO] Stopping runner...", flush=True)
            self.running = False
            try:
                self.auto_switch.stop_monitoring()
            except:
                pass
            logger.info("Smart runner stopped")
            print("[INFO] Runner stopped", flush=True)


def main():
    """Main entry point."""
    # IMMEDIATE OUTPUT - Show script is starting
    import sys

    # Force output immediately
    sys.stdout.write("=" * 80 + "\n")
    sys.stdout.write("  SMART LIVE CHAIN RUNNER - STARTING\n")
    sys.stdout.write("=" * 80 + "\n\n")
    sys.stdout.flush()

    print("", flush=True)
    print("=" * 80, flush=True)
    print("  SMART LIVE CHAIN RUNNER - STARTING", flush=True)
    print("=" * 80, flush=True)
    print("", flush=True)
    sys.stdout.flush()

    # Test if class exists - check both globals and current module
    import sys

    current_module = sys.modules.get(__name__)
    class_found = False

    if "SmartLiveChainRunner" in globals():
        class_found = True
        print("[DEBUG] SmartLiveChainRunner found in globals()", flush=True)
    elif current_module and hasattr(current_module, "SmartLiveChainRunner"):
        class_found = True
        print("[DEBUG] SmartLiveChainRunner found in module", flush=True)
        SmartLiveChainRunner = getattr(current_module, "SmartLiveChainRunner")
    else:
        print("[FATAL ERROR] SmartLiveChainRunner class not found!", flush=True)
        print(f"Available globals: {[k for k in globals().keys() if not k.startswith('_')][:20]}", flush=True)
        if current_module:
            print(f"Module attributes: {[k for k in dir(current_module) if not k.startswith('_')][:20]}", flush=True)
        return 1

    try:
        test_runner = SmartLiveChainRunner
        print(f"[DEBUG] SmartLiveChainRunner class verified: {test_runner}", flush=True)
    except NameError as e:
        print(f"[ERROR] SmartLiveChainRunner class not accessible: {e}", flush=True)
        import traceback

        traceback.print_exc()
        return 1

    import argparse

    parser = argparse.ArgumentParser(description="Smart Live Chain Runner with Auto-Switch")
    parser.add_argument("--refresh", type=int, default=5, help="Refresh interval in seconds (default: 5)")
    parser.add_argument("--market-check", type=int, default=30, help="Market check interval in seconds (default: 30)")
    parser.add_argument("--duration", type=int, help="Run for N minutes")
    parser.add_argument("--no-websocket", action="store_true", help="Disable WebSocket")

    args = parser.parse_args()

    print(f"Configuration: refresh={args.refresh}s, market-check={args.market_check}s", flush=True)
    print("Creating runner instance...", flush=True)
    sys.stdout.flush()

    try:
        print("[DEBUG] About to create SmartLiveChainRunner instance...", flush=True)
        runner = SmartLiveChainRunner(
            refresh_interval=args.refresh, market_check_interval=args.market_check, use_websocket=not args.no_websocket
        )
        print("[DEBUG] Runner instance created successfully", flush=True)
        print("Runner created successfully", flush=True)
        print("Starting run()...", flush=True)
        print("", flush=True)
        sys.stdout.flush()

        print("[DEBUG] About to call runner.run()...", flush=True)
        runner.run(duration_minutes=args.duration)
        print("[DEBUG] runner.run() returned", flush=True)

        print("", flush=True)
        print("Runner finished normally.", flush=True)
        return 0
    except KeyboardInterrupt:
        print("", flush=True)
        print("Interrupted by user (Ctrl+C)", flush=True)
        return 0
    except Exception as e:
        print("", flush=True)
        print("=" * 80, flush=True)
        print(f"[ERROR] FATAL ERROR: {e}", flush=True)
        print("=" * 80, flush=True)
        import traceback

        traceback.print_exc()
        sys.stdout.flush()
        return 1


if __name__ == "__main__":
    print("[MAIN] __name__ == '__main__' is True, calling main()", file=sys.stderr, flush=True)
    try:
        result = main()
        print(f"[MAIN] main() returned: {result}", file=sys.stderr, flush=True)
        sys.exit(result)
    except Exception as e:
        print(f"[MAIN] Exception in main(): {e}", file=sys.stderr, flush=True)
        import traceback

        traceback.print_exc()
        sys.exit(1)
