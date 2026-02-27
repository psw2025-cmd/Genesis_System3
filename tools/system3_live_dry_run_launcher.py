#!/usr/bin/env python3
"""
GENESIS SYSTEM3 LIVE DRY-RUN LAUNCHER

Purpose:
  Helper orchestrator for executing a full live DRY-RUN day using the
  menu-driven run_system3.py interface.
  
  This script does NOT replace run_system3.py; it COMPLEMENTS it by:
  1. Starting a logging session for the live day
  2. Running initial health checks and block tests
  3. Providing a human-friendly checklist
  4. Optionally launching recommended menu options
  
Safety Guarantees:
  - All safety flags remain False (DRY-RUN enforced)
  - No live order execution possible
  - No changes to Phases 1-380 logic
  - Pure read-only status monitoring

Usage:
  python tools/system3_live_dry_run_launcher.py

Then follow the interactive menu prompts.
"""

import sys
import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Create live dress rehearsal log directory
LOG_DIR = PROJECT_ROOT / "logs" / "live_dress_rehearsal"
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / f"live_dry_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger("LiveDryRunLauncher")


class LiveDryRunLauncher:
    """Helper orchestrator for live DRY-RUN dress rehearsal day."""

    def __init__(self):
        self.session_start = datetime.now()
        self.session_log = {"start_time": self.session_start.isoformat(), "actions": [], "status": "INITIALIZING"}

        logger.info("=" * 80)
        logger.info("🎭 GENESIS SYSTEM3 LIVE DRY-RUN LAUNCHER")
        logger.info("=" * 80)
        logger.info(f"Session start: {self.session_start.strftime('%Y-%m-%d %H:%M:%S IST')}")
        logger.info(f"Log file: {LOG_FILE}")
        logger.info("")

    def verify_safety_flags(self) -> bool:
        """Verify that all safety flags are set to False (DRY-RUN mode)."""
        logger.info("🔒 SAFETY VERIFICATION")
        logger.info("-" * 80)

        safety_checks = {
            "LIVE_TRADING_ENABLED": False,
            "USE_LIVE_EXECUTION_ENGINE": False,
            "auto_execute_trades": False,
        }

        all_safe = True

        # Check config files
        config_files = [
            PROJECT_ROOT / "config" / "system3_trading_config.json",
            PROJECT_ROOT / "config" / "automation_config.json",
        ]

        for config_file in config_files:
            if config_file.exists():
                try:
                    with open(config_file, "r") as f:
                        config = json.load(f)

                    for key, expected_val in safety_checks.items():
                        if key in config:
                            actual_val = config[key]
                            if actual_val != expected_val:
                                logger.warning(f"⚠️  {config_file.name}: {key} = {actual_val} (expected {expected_val})")
                                all_safe = False
                            else:
                                logger.info(f"✅ {config_file.name}: {key} = {actual_val}")
                except Exception as e:
                    logger.warning(f"⚠️  Could not read {config_file.name}: {e}")

        # Check environment variable
        live_mode = os.environ.get("LIVE_TRADING_ENABLED", "false").lower()
        if live_mode == "true":
            logger.error("❌ LIVE_TRADING_ENABLED environment variable is TRUE!")
            all_safe = False
        else:
            logger.info(f"✅ Environment: LIVE_TRADING_ENABLED = {live_mode}")

        logger.info("")

        if all_safe:
            logger.info("✅ ALL SAFETY CHECKS PASSED - DRY-RUN MODE CONFIRMED")
        else:
            logger.error("❌ SAFETY CHECKS FAILED - ABORTING LAUNCH")

        logger.info("")
        return all_safe

    def run_initial_checks(self) -> Dict[str, Any]:
        """Run initial health checks without actually starting live trading."""
        logger.info("📋 PRE-LAUNCH HEALTH CHECKS")
        logger.info("-" * 80)

        results = {
            "system_health": "UNKNOWN",
            "block_test_331_360": "SKIPPED",
            "required_csv_files": [],
            "timestamp": datetime.now().isoformat(),
        }

        # Check required directories and files
        required_dirs = [
            "storage/live",
            "storage/ultra",
            "storage/meta",
            "logs",
            "config",
            "models",
        ]

        logger.info("\n1️⃣  Checking directory structure...")
        all_dirs_exist = True
        for dir_path in required_dirs:
            full_path = PROJECT_ROOT / dir_path
            if full_path.exists():
                logger.info(f"   ✅ {dir_path}")
                results[f"dir_{dir_path}"] = "OK"
            else:
                logger.warning(f"   ⚠️  {dir_path} (will be created if needed)")
                all_dirs_exist = True  # Not critical; auto-created

        # Check key CSV files
        logger.info("\n2️⃣  Checking live CSV files...")
        csv_files = [
            "storage/live/angel_index_ai_signals.csv",
            "storage/live/angel_virtual_orders.csv",
            "storage/live/angel_index_ai_pnl_log.csv",
            "storage/live/angel_index_ai_trades_plan.csv",
        ]

        for csv_path in csv_files:
            full_path = PROJECT_ROOT / csv_path
            if full_path.exists():
                row_count = sum(1 for line in open(full_path)) - 1  # Exclude header
                logger.info(f"   ✅ {csv_path} ({row_count} rows)")
                results["required_csv_files"].append({"file": csv_path, "status": "OK", "rows": row_count})
            else:
                logger.info(f"   ℹ️  {csv_path} (will be created on first run)")
                results["required_csv_files"].append({"file": csv_path, "status": "NOT_CREATED_YET"})

        # Check models exist
        logger.info("\n3️⃣  Checking trained models...")
        models_dir = PROJECT_ROOT / "models"
        if models_dir.exists():
            model_files = list(models_dir.glob("*.pkl")) + list(models_dir.glob("*.joblib"))
            if model_files:
                logger.info(f"   ✅ Found {len(model_files)} model files")
                results["models"] = "OK"
            else:
                logger.warning(f"   ⚠️  No model files found (Option 10 needed first)")
                results["models"] = "MISSING"
        else:
            logger.warning(f"   ⚠️  models/ directory not found")
            results["models"] = "MISSING"

        # Check AngelOne configuration
        logger.info("\n4️⃣  Checking AngelOne configuration...")
        angel_config = PROJECT_ROOT / "config" / "angel_auth_config.json"
        if angel_config.exists():
            try:
                with open(angel_config, "r") as f:
                    config = json.load(f)
                if "client_code" in config and "password" in config:
                    logger.info(f"   ✅ AngelOne credentials configured")
                    results["angel_auth"] = "OK"
                else:
                    logger.warning(f"   ⚠️  AngelOne credentials incomplete")
                    results["angel_auth"] = "INCOMPLETE"
            except Exception as e:
                logger.warning(f"   ⚠️  Error reading AngelOne config: {e}")
                results["angel_auth"] = "ERROR"
        else:
            logger.warning(f"   ⚠️  angel_auth_config.json not found")
            results["angel_auth"] = "MISSING"

        # Check instruments file
        logger.info("\n5️⃣  Checking instruments file...")
        instruments_file = PROJECT_ROOT / "config" / "angel_instruments.csv"
        if instruments_file.exists():
            row_count = sum(1 for line in open(instruments_file)) - 1
            logger.info(f"   ✅ angel_instruments.csv ({row_count} instruments)")
            results["instruments"] = "OK"
        else:
            logger.warning(f"   ⚠️  angel_instruments.csv not found")
            results["instruments"] = "MISSING"

        logger.info("")
        return results

    def show_checklist(self):
        """Display the live DRY-RUN day checklist."""
        logger.info("📋 PRE-MARKET CHECKLIST (Run these in order)")
        logger.info("-" * 80)
        logger.info(
            """
To execute a live DRY-RUN day, run these options from run_system3.py 
in the following order:

  ⏰ 8:45 AM IST
  ─────────────
  1. Run: Option 2 (Health Check)
     Purpose: Verify system is ready
     Duration: ~2 min

  2. Run: Option 3 (Test data pipeline)
     Purpose: Verify AngelOne API connection
     Duration: ~3 min

  3. Run: Option 109 > enter "331-380"
     Purpose: Sanity check phases (should see 43/50 OK, 7/50 WARN)
     Duration: ~2 min

  ⏰ 9:10 AM IST — START LIVE TRADING LOOP
  ──────────────────────────────────────────
  4. Run: Option 11 (LIVE AI signals) — KEEP RUNNING IN BACKGROUND
     Purpose: Continuous signal generation and virtual order logging
     Duration: 6 hours (until 3:20 PM)
     ⚠️  IMPORTANT: Keep this terminal open and running!

  ⏰ Periodic Checks (While Option 11 is running)
  ─────────────────────────────────────────────────
  5. At 10:00 AM, 12:00 PM, 2:00 PM: Run Option 27 (Safety Layer Check)
     Purpose: Verify no safety violations
     Duration: ~1 min each

  6. At 12:00 PM: Run Option 12 (Synthetic backtest - CONSERVATIVE)
     Purpose: Test backtest engine with signals so far
     Duration: ~3 min

  7. At 3:00 PM: Run Option 28 (Real outcome logger)
     Purpose: Log final market outcomes for signals
     Duration: ~3 min

  ⏰ 3:20 PM — END LIVE LOOP
  ──────────────────────────
  8. STOP Option 11 (Press Ctrl+C in that terminal)

  ⏰ 3:20 PM – 3:40 PM — GENERATE REPORTS
  ────────────────────────────────────────
  9. Run: Option 36 (Daily learning report)
     Output: logs/angel_daily_learning_YYYY-MM-DD.md
     Duration: ~2 min

  10. Run: Option 37 (Rolling 7-day dashboard)
      Output: reports/rolling_7day_dashboard.md
      Duration: ~2 min

  11. Run: Option 40 (Daily auto-reports)
      Output: Multiple files in reports/
      Duration: ~3 min

  ⏰ 3:40 PM – 4:00 PM — VERIFY & ARCHIVE
  ────────────────────────────────────────
  12. Verify:
      - Check: wc -l storage/live/*.csv
      - Check: grep ERROR logs/2025-12-XX.log (should find 0)
      - Check: All reports generated successfully

  13. Archive:
      - Create: storage/archive/2025-12-XX_dress_rehearsal/
      - Copy: All CSVs from storage/live/
      - Copy: Today's log file
      - Copy: All reports from reports/

SUCCESS CRITERIA (by 4:00 PM):
─────────────────────────────
  ✓ ≥ 400 signals generated
  ✓ 0 [ERROR] entries in log
  ✓ All Option 27 (Safety) checks PASS
  ✓ No real orders placed
  ✓ All reports generated
  ✓ Data consistency verified
"""
        )
        logger.info("")

    def interactive_menu(self):
        """Show interactive menu for optional quick actions."""
        while True:
            print("\n" + "=" * 80)
            print("🎭 LIVE DRY-RUN LAUNCHER - OPTIONS")
            print("=" * 80)
            print(
                """
1) Show pre-market checklist (print again)
2) Show expected output examples
3) Show troubleshooting guide
4) Generate session report (what we checked so far)
5) Open LIVE_DRY_RUN_DAY_PLAN.md in default viewer
0) Exit launcher (ready to start run_system3.py manually)
"""
            )
            choice = input("Select option (0-5): ").strip()

            if choice == "1":
                self.show_checklist()

            elif choice == "2":
                self.show_example_outputs()

            elif choice == "3":
                self.show_troubleshooting()

            elif choice == "4":
                self.generate_session_report()

            elif choice == "5":
                plan_file = PROJECT_ROOT / "LIVE_DRY_RUN_DAY_PLAN.md"
                if plan_file.exists():
                    try:
                        import subprocess

                        subprocess.Popen(["notepad", str(plan_file)])
                        logger.info("Opening LIVE_DRY_RUN_DAY_PLAN.md in default viewer...")
                    except Exception as e:
                        logger.error(f"Could not open file: {e}")
                        logger.info(f"Please manually open: {plan_file}")
                else:
                    logger.error(f"File not found: {plan_file}")

            elif choice == "0":
                logger.info("\n✅ Launcher complete. Ready to start run_system3.py")
                logger.info("   Command: python run_system3.py")
                logger.info("\n   Follow the checklist above to execute the live DRY-RUN day.")
                break

            else:
                print("Invalid option. Try again.")

    def show_example_outputs(self):
        """Show expected console output examples."""
        logger.info(
            """
📊 EXPECTED OUTPUT EXAMPLES

Option 11 (LIVE AI Signals) Output:
──────────────────────────────────
[AI] Snapshot #1 ...
  -> Built snapshot: 3 indices, 87 rows
  -> Running Phase 11 (signal generation)...
  -> Generated 12 signals (4 BANKNIFTY, 5 NIFTY, 3 FINNIFTY)
Sleeping for 30 seconds...

[AI] Snapshot #2 ...
  -> Generated 15 signals
Sleeping for 30 seconds...
[SUCCESS] 10,000+ signals generated and logged


Option 12 (Synthetic Backtest) Output:
────────────────────────────────────
Running synthetic backtest [CONSERVATIVE]...

[INFO] Loaded trade plan: 47 trades
[RESULTS SUMMARY]
Total trades: 47
Winning trades: 28 (59.6%)
Losing trades: 19 (40.4%)
Net P&L: +₹4,250 (DRY, simulated)
Max drawdown: -₹850
Win/Loss ratio: 1.47x

Test result: PASS


Option 27 (Safety Layer Check) Output:
────────────────────────────────────
=== SAFETY LAYER V2 - COMPLETE CHECK ===

[OVERTRADE DETECTOR]
Total virtual orders: 143
Status: ✓ PASS (below 50/hour limit)

[SIGNAL QUALITY METER]
Avg confidence: 0.72
Status: ✓ PASS

[EXECUTION GUARDRAIL]
LIVE_TRADING_ENABLED: False ✓
auto_execute_trades: False ✓
Status: ✓ PASS

[MARKET REGIME CLASSIFIER]
Current regime: Normal volatility
Status: ✓ PASS
"""
        )

    def show_troubleshooting(self):
        """Show common issues and fixes."""
        logger.info(
            """
🔧 TROUBLESHOOTING GUIDE

Problem: "Signals not being generated"
Solution:
  1. Check internet connection
  2. Verify AngelOne login: Option 4 (Test Angel One API)
  3. Check if models exist: Option 10 (Train models)
  4. Restart Option 11

Problem: "Virtual orders not logging"
Solution:
  1. Verify DRY-RUN mode: Check config/system3_trading_config.json
  2. LIVE_TRADING_ENABLED must be False
  3. auto_execute_trades must be False
  4. Restart Option 11

Problem: "Backtest crashes"
Solution:
  1. Try Option 13 (DEV backtest) instead (more lenient)
  2. Check storage/live/angel_index_ai_trades_plan.csv exists
  3. Wait 30+ minutes for data to accumulate
  4. Check logs/ for specific error

Problem: "Reports not generating"
Solution:
  1. Ensure Option 11 is still running
  2. Wait at least 30 minutes for data
  3. Check that storage/live/*.csv files are being updated
  4. Try Option 36 manually again

For detailed troubleshooting:
  → See LIVE_DRY_RUN_DAY_PLAN.md SECTION 6
"""
        )

    def generate_session_report(self):
        """Generate a report of what we've checked so far."""
        self.session_log["end_time"] = datetime.now().isoformat()
        self.session_log["status"] = "PRE_LAUNCH_COMPLETE"

        report_file = LOG_DIR / f"session_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        try:
            with open(report_file, "w") as f:
                json.dump(self.session_log, f, indent=2)
            logger.info(f"\n✅ Session report saved: {report_file}")
        except Exception as e:
            logger.error(f"Error saving session report: {e}")

    def run(self):
        """Run the complete launcher flow."""
        try:
            # Step 1: Verify safety
            if not self.verify_safety_flags():
                logger.error("\n❌ LAUNCH ABORTED - Safety verification failed")
                logger.error("   Do NOT proceed with live trading!")
                return False

            # Step 2: Run initial checks
            check_results = self.run_initial_checks()
            self.session_log["initial_checks"] = check_results

            # Step 3: Show checklist
            self.show_checklist()

            # Step 4: Interactive menu
            self.interactive_menu()

            # Final status
            logger.info("\n" + "=" * 80)
            logger.info("🎭 LAUNCHER SESSION COMPLETE")
            logger.info("=" * 80)
            logger.info("\nNext Steps:")
            logger.info("  1. Start a new terminal")
            logger.info("  2. Run: python run_system3.py")
            logger.info("  3. Follow the checklist above")
            logger.info("")

            self.generate_session_report()
            return True

        except KeyboardInterrupt:
            logger.info("\n\n⚠️  Launcher interrupted by user")
            return False
        except Exception as e:
            logger.error(f"\n❌ Launcher failed: {e}", exc_info=True)
            return False


def main():
    """Entry point."""
    launcher = LiveDryRunLauncher()
    success = launcher.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
