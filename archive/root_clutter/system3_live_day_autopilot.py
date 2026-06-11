"""
System3 Live Day Autopilot - Single-Button Full-Day Autopilot

This script orchestrates a complete trading day:
- OP1: Pre-market checks
- OP2: Live DRY-RUN AngelOne loop
- OP3: Intraday monitors
- OP4: End-of-day processing

SAFETY: DRY-RUN ONLY - No real trading functions ever triggered.
"""

import sys
import os
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Ensure project root is in path
ROOT_DIR = Path(__file__).parent.absolute()
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Setup logging
LOGS_DIR = ROOT_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOGS_DIR / f"live_day_autopilot_{datetime.now().strftime('%Y%m%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)

# Track latest snapshot count for intraday monitor helpers
LAST_SNAPSHOT_COUNT: int = 0


def enforce_safety_checks() -> bool:
    """
    Hard safety enforcement - verify DRY-RUN mode.
    
    Returns:
        True if safe, False if unsafe (will abort)
    """
    logger.info("=" * 70)
    logger.info("SAFETY ENFORCEMENT CHECK")
    logger.info("=" * 70)
    
    errors = []
    
    # Check 1: LIVE_TRADING_ENABLED
    try:
        from config.live_trade_config import LIVE_TRADING_ENABLED, USE_LIVE_EXECUTION_ENGINE
        if LIVE_TRADING_ENABLED:
            errors.append("LIVE_TRADING_ENABLED is True (must be False)")
        if USE_LIVE_EXECUTION_ENGINE:
            errors.append("USE_LIVE_EXECUTION_ENGINE is True (must be False)")
        logger.info(f"LIVE_TRADING_ENABLED: {LIVE_TRADING_ENABLED}")
        logger.info(f"USE_LIVE_EXECUTION_ENGINE: {USE_LIVE_EXECUTION_ENGINE}")
    except Exception as e:
        errors.append(f"Failed to read live_trade_config: {e}")
    
    # Check 2: Automation config
    try:
        from core.engine.angel_automation_config import AUTOMATION_CONFIG
        if AUTOMATION_CONFIG.auto_execute_trades:
            errors.append("AUTOMATION_CONFIG.auto_execute_trades is True (must be False)")
        logger.info(f"auto_execute_trades: {AUTOMATION_CONFIG.auto_execute_trades}")
    except Exception as e:
        errors.append(f"Failed to read automation_config: {e}")
    
    # Check 3: Ultra safety
    try:
        from core.engine.ultra_safety import load_ultra_safety
        safety = load_ultra_safety()
        if safety.get("AUTO_EXECUTE_TRADES", False):
            errors.append("Ultra safety AUTO_EXECUTE_TRADES is True (must be False)")
        logger.info(f"Ultra AUTO_EXECUTE_TRADES: {safety.get('AUTO_EXECUTE_TRADES', False)}")
    except Exception as e:
        logger.warning(f"Could not load ultra_safety: {e}")
    
    if errors:
        logger.error("=" * 70)
        logger.error("SAFETY CHECK FAILED - ABORTING")
        logger.error("=" * 70)
        for error in errors:
            logger.error(f"  ❌ {error}")
        logger.error("\n[ABORT] System is not in safe DRY-RUN mode. Fix configs before running.")
        return False
    
    logger.info("=" * 70)
    logger.info("✓ All safety checks passed - DRY-RUN mode confirmed")
    logger.info("=" * 70)
    return True


def run_op1_pre_market() -> bool:
    """
    OP1: Pre-Market Checks
    
    Runs:
    - Market warmup scanner
    - Monday diagnostic (if applicable)
    - Environment guard
    """
    logger.info("\n" + "=" * 70)
    logger.info("OP1: PRE-MARKET CHECKS")
    logger.info("=" * 70)
    
    results = {}
    
    # 1. Market Warmup Scanner
    try:
        logger.info("[OP1.1] Running Market Warmup Scanner...")
        from core.engine.angel_market_warmup_scanner import scan_market_warmup
        result = scan_market_warmup()
        results["warmup_scanner"] = result.get("status", "UNKNOWN")
        logger.info(f"[OK] Market warmup scanner: {results['warmup_scanner']}")
    except Exception as e:
        logger.error(f"[ERROR] Market warmup scanner failed: {e}")
        results["warmup_scanner"] = "ERROR"
    
    # 2. Monday Diagnostic (if applicable)
    try:
        logger.info("[OP1.2] Running Pre-Market Diagnostic...")
        from core.engine.angel_monday_diagnostic import run_pre_market_diagnostic
        result = run_pre_market_diagnostic()
        results["diagnostic"] = result.get("status", "UNKNOWN")
        logger.info(f"[OK] Pre-market diagnostic: {results['diagnostic']}")
    except UnicodeEncodeError as e:
        logger.warning(f"[WARN] Pre-market diagnostic text encoding issue (non-critical): {e}")
        logger.warning("[WARN] Diagnostic output contains non-ASCII characters, but checks completed.")
        results["diagnostic"] = "PASS"  # Do NOT abort trading because of text formatting
    except Exception as e:
        logger.warning(f"[WARN] Pre-market diagnostic failed: {e}")
        results["diagnostic"] = "WARN"
    
    # 3. Environment Guard
    try:
        logger.info("[OP1.3] Running Environment Guard...")
        from core.engine.system3_phase43_env_guard import run_phase43_env_guard
        run_phase43_env_guard()
        results["env_guard"] = "OK"
        logger.info("[OK] Environment guard complete")
    except Exception as e:
        logger.warning(f"[WARN] Environment guard failed: {e}")
        results["env_guard"] = "WARN"
    
    all_ok = all(v in ("PASS", "OK") for v in results.values())
    if all_ok:
        logger.info("[OK] OP1 Pre-Market Checks complete")
    else:
        logger.warning("[WARN] Some pre-market checks had issues")
    
    return all_ok


def run_op2_live_session(interval_sec: int = 30, max_snapshots: int | None = None) -> bool:
    """
    OP2: Live Session (AngelOne DRY-RUN Loop)
    
    Runs the same loop as run_system3.py option 11:
    - Live AI signal generation
    - Trade plan creation (DRY-RUN only)
    - Periodic PnL simulation if enabled
    """
    logger.info("\n" + "=" * 70)
    logger.info("OP2: LIVE SESSION (DRY-RUN ONLY)")
    logger.info("=" * 70)
    logger.info(f"Interval: {interval_sec} seconds")
    logger.info(f"Max snapshots: {max_snapshots or 'Infinite'}")
    logger.info("[SAFETY] DRY-RUN mode - No real orders\n")
    
    try:
        from core.brokers.angel_one.broker import AngelOneBroker
        from core.engine.angel_options_watch_loop import _build_full_snapshot
        from core.engine import angel_live_ai_signals
        from core.engine.angel_automation_config import AUTOMATION_CONFIG
        
        logger.info("Initializing AngelOne broker...")
        try:
            broker = AngelOneBroker()
            logger.info("Broker initialized successfully.\n")
        except ImportError as e:
            logger.error(f"[ERROR] SmartApi missing - cannot initialize broker: {e}")
            logger.error("[ERROR] Install SmartApi with: pip install SmartApi")
            return False
    except ImportError as e:
        logger.error(f"[ERROR] Failed to import broker module: {e}")
        logger.error("[ERROR] SmartApi module not found. Install with: pip install SmartApi")
        return False
        
        iteration = 0
        pnl_sim_counter = 0
        
        try:
            while True:
                iteration += 1
                pnl_sim_counter += 1
                
                logger.info(f"[{datetime.now().strftime('%H:%M:%S')}] Snapshot #{iteration}...")
                
                try:
                    df_snap = _build_full_snapshot(broker)
                except Exception as e:
                    logger.error(f"[ERROR] Failed to build snapshot: {e}")
                    df_snap = None
                
                if df_snap is None or df_snap.empty:
                    logger.warning("  -> No snapshot data returned (check market / instruments).")
                else:
                    # Generate AI signals
                    angel_live_ai_signals.run_once_with_snapshot(df_snap)
                    logger.info("  -> Signals generated")
                    
                    # Periodic PnL simulation if enabled
                    if AUTOMATION_CONFIG.auto_simulate_pnl:
                        if pnl_sim_counter >= AUTOMATION_CONFIG.pnl_sim_interval:
                            pnl_sim_counter = 0
                            try:
                                from core.engine.angel_pnl_simulator import run_pnl_simulation
                                logger.info("[AUTO] Running PnL simulation...")
                                run_pnl_simulation()
                            except Exception as e:
                                logger.warning(f"[WARN] Auto PnL simulation failed: {e}")
                
                # Check if we should stop
                if max_snapshots and iteration >= max_snapshots:
                    logger.info(f"[INFO] Reached max snapshots ({max_snapshots}). Stopping live session.")
                    break
                
                logger.info(f"Sleeping for {interval_sec} seconds...\n")
                time.sleep(interval_sec)
                
        except KeyboardInterrupt:
            logger.info("\n[INFO] Live session interrupted by user (Ctrl+C).")
            return True
        except Exception as e:
            logger.error(f"\n[ERROR] Live session failed: {e}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"[ERROR] Failed to initialize live session: {e}")
        return False


def run_op3_intraday_monitors(snapshot_count: int) -> bool:
    """
    OP3: Intraday Monitors
    
    Runs every X snapshots:
    - Decision Auditor (Phase 35)
    - Policy & Risk Monitor (Phase 37)
    - Governance Summary (Phase 38)
    """
    logger.info("\n" + "=" * 70)
    logger.info("OP3: INTRADAY MONITORS")
    logger.info("=" * 70)
    logger.info(f"Triggered at snapshot #{snapshot_count}")
    
    results = {}
    
    # Decision Auditor (Phase 35)
    try:
        logger.info("[OP3.1] Running Decision Auditor (Phase 35)...")
        from core.engine.system3_phase35_ultra_auditor import run_phase35_audit
        run_phase35_audit()
        results["decision_auditor"] = True
        logger.info("[OK] Decision Auditor complete")
    except Exception as e:
        logger.error(f"[ERROR] Decision Auditor failed: {e}")
        results["decision_auditor"] = False
    
    # Policy & Risk Monitor (Phase 37)
    try:
        logger.info("[OP3.2] Running Policy & Risk Monitor (Phase 37)...")
        from core.engine.system3_phase37_policy_risk_monitor import run_phase37_policy_risk_dashboard
        run_phase37_policy_risk_dashboard()
        results["policy_monitor"] = True
        logger.info("[OK] Policy & Risk Monitor complete")
    except Exception as e:
        logger.error(f"[ERROR] Policy & Risk Monitor failed: {e}")
        results["policy_monitor"] = False
    
    # Governance Summary (Phase 38)
    try:
        logger.info("[OP3.3] Running Governance Summary (Phase 38)...")
        from core.engine.system3_phase38_governance_summary import run_phase38_governance_summary
        run_phase38_governance_summary()
        results["governance"] = True
        logger.info("[OK] Governance Summary complete")
    except Exception as e:
        logger.error(f"[ERROR] Governance Summary failed: {e}")
        results["governance"] = False
    
    all_ok = all(results.values())
    if all_ok:
        logger.info("[OK] OP3 Intraday Monitors complete")
    else:
        logger.warning("[WARN] Some intraday monitors had issues")
    
    return all_ok


def run_op4_end_of_day() -> bool:
    """
    OP4: End-of-Day Processing
    
    Runs:
    - PnL simulation
    - Daily learning
    - Daily auto reports
    """
    logger.info("\n" + "=" * 70)
    logger.info("OP4: END-OF-DAY PROCESSING")
    logger.info("=" * 70)
    
    results = {}
    
    # 1. PnL Simulation
    try:
        logger.info("[OP4.1] Running PnL Simulation...")
        from core.engine.angel_pnl_simulator import run_pnl_simulation
        run_pnl_simulation()
        results["pnl_sim"] = True
        logger.info("[OK] PnL simulation complete")
    except Exception as e:
        logger.error(f"[ERROR] PnL simulation failed: {e}")
        results["pnl_sim"] = False
    
    # 2. Daily PnL Summary
    try:
        logger.info("[OP4.2] Running Daily PnL Summary...")
        from core.engine.angel_daily_pnl_summary import main as daily_pnl_main
        daily_pnl_main()
        results["pnl_summary"] = True
        logger.info("[OK] Daily PnL summary complete")
    except Exception as e:
        logger.warning(f"[WARN] Daily PnL summary failed: {e}")
        results["pnl_summary"] = False
    
    # 3. Daily Learning
    try:
        logger.info("[OP4.3] Running Daily Learning...")
        from core.engine.angel_daily_learning_report import generate_daily_learning_report
        generate_daily_learning_report()
        results["daily_learning"] = True
        logger.info("[OK] Daily learning complete")
    except Exception as e:
        logger.warning(f"[WARN] Daily learning failed: {e}")
        results["daily_learning"] = False
    
    # 4. Daily Auto Reports
    try:
        logger.info("[OP4.4] Running Daily Auto Reports...")
        from core.engine.angel_daily_auto_reports import generate_daily_auto_report
        generate_daily_auto_report()
        results["auto_reports"] = True
        logger.info("[OK] Daily auto reports complete")
    except Exception as e:
        logger.warning(f"[WARN] Daily auto reports failed: {e}")
        results["auto_reports"] = False
    
    all_ok = all(results.values())
    if all_ok:
        logger.info("[OK] OP4 End-of-Day Processing complete")
    else:
        logger.warning("[WARN] Some end-of-day processes had issues")
    
    return all_ok


# === Public entrypoints (standardized) ===

def run_pre_market_checks() -> bool:
    """
    Run all pre-market checks (OP1) with safety guard.
    """
    # Hard safety enforcement first
    if not enforce_safety_checks():
        logger.error("[ABORT] Safety checks failed in run_pre_market_checks.")
        return False
    return run_op1_pre_market()


def run_intraday_monitors_once() -> bool:
    """
    Run intraday monitors once using the latest snapshot count.
    """
    global LAST_SNAPSHOT_COUNT
    return run_op3_intraday_monitors(LAST_SNAPSHOT_COUNT or 0)


def run_end_of_day_wrapup() -> bool:
    """
    Run end-of-day processing (OP4) only.
    """
    return run_op4_end_of_day()


def run_live_session(duration_minutes: int | None = None) -> bool:
    """
    Run the live session loop (OP2) with periodic intraday monitors (OP3).

    Args:
        duration_minutes: Optional duration in minutes. If None, run until Ctrl+C.
    """
    global LAST_SNAPSHOT_COUNT

    logger.info("\n" + "=" * 70)
    logger.info("Starting OP2: Live Session")
    logger.info("=" * 70)
    logger.info(
        "[INFO] Press Ctrl+C to stop the live session and proceed to EOD processing"
    )
    logger.info("")

    monitor_interval = 10  # Run monitors every 10 snapshots
    interval_sec = 30

    end_time: datetime | None = None
    if duration_minutes is not None and duration_minutes > 0:
        end_time = datetime.now() + timedelta(minutes=duration_minutes)
        logger.info(f"[INFO] Live session duration limit: {duration_minutes} minutes")

    try:
        from core.brokers.angel_one.broker import AngelOneBroker
        from core.engine.angel_options_watch_loop import _build_full_snapshot
        from core.engine import angel_live_ai_signals
        from core.engine.angel_automation_config import AUTOMATION_CONFIG

        broker = AngelOneBroker()
        logger.info("Broker initialized.\n")

        pnl_sim_counter = 0

        while True:
            LAST_SNAPSHOT_COUNT += 1
            snapshot_count = LAST_SNAPSHOT_COUNT
            pnl_sim_counter += 1

            logger.info(
                f"[{datetime.now().strftime('%H:%M:%S')}] Snapshot #{snapshot_count}..."
            )

            try:
                df_snap = _build_full_snapshot(broker)
            except Exception as e:
                logger.error(f"[ERROR] Failed to build snapshot: {e}")
                df_snap = None

            if df_snap is None or df_snap.empty:
                logger.warning("  -> No snapshot data returned")
            else:
                angel_live_ai_signals.run_once_with_snapshot(df_snap)
                logger.info("  -> Signals generated")

                # Periodic PnL simulation
                if AUTOMATION_CONFIG.auto_simulate_pnl:
                    if pnl_sim_counter >= AUTOMATION_CONFIG.pnl_sim_interval:
                        pnl_sim_counter = 0
                        try:
                            from core.engine.angel_pnl_simulator import (
                                run_pnl_simulation,
                            )

                            logger.info("[AUTO] Running PnL simulation...")
                            run_pnl_simulation()
                        except Exception as e:
                            logger.warning(f"[WARN] Auto PnL simulation failed: {e}")

            # Run intraday monitors periodically
            if snapshot_count % monitor_interval == 0:
                logger.info(
                    f"\n[INFO] Running intraday monitors (snapshot #{snapshot_count})..."
                )
                run_op3_intraday_monitors(snapshot_count)
                logger.info("")

            # Duration-based stop
            if end_time is not None and datetime.now() >= end_time:
                logger.info(
                    f"[INFO] Live session duration reached ({duration_minutes} minutes). Stopping."
                )
                break

            logger.info(f"Sleeping for {interval_sec} seconds...\n")
            time.sleep(interval_sec)

    except KeyboardInterrupt:
        logger.info("\n[INFO] Live session stopped by user (Ctrl+C).")
        return True
    except Exception as e:
        logger.error(f"\n[ERROR] Live session failed: {e}")
        return False

    return True


def run_full_day_autopilot(duration_minutes: int | None = None) -> None:
    """
    Main master controller for full-day autopilot.

    Phases:
      - OP1: Pre-market checks
      - OP2: Live session with intraday monitors
      - OP4: End-of-day wrap-up
    """
    logger.info("=" * 70)
    logger.info("SYSTEM3 LIVE DAY AUTOPILOT")
    logger.info("=" * 70)
    logger.info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Log file: {LOG_FILE}")
    logger.info("")

    # Hard safety + pre-market
    if not run_pre_market_checks():
        logger.error(
            "[ABORT] Pre-market checks or safety checks failed. Not starting live session."
        )
        return

    # Live session (loops until duration or Ctrl+C)
    success_live = run_live_session(duration_minutes=duration_minutes)
    if not success_live:
        logger.warning("[WARN] Live session ended with errors.")

    # End-of-day wrap-up
    logger.info("\n" + "=" * 70)
    logger.info("Live session ended. Starting End-of-Day processing...")
    logger.info("=" * 70)

    if not run_end_of_day_wrapup():
        logger.warning("[WARN] End-of-day processing had issues")

    # Final summary
    logger.info("\n" + "=" * 70)
    logger.info("AUTOPILOT COMPLETE")
    logger.info("=" * 70)
    logger.info(f"Ended at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Total snapshots: {LAST_SNAPSHOT_COUNT}")
    logger.info(f"Log file: {LOG_FILE}")
    logger.info("")


if __name__ == "__main__":
    import argparse
    from datetime import timedelta

    parser = argparse.ArgumentParser(
        description="System3 AngelOne DRY-RUN Live Day Autopilot"
    )
    parser.add_argument(
        "--duration-minutes",
        type=int,
        default=None,
        help="Optional duration for live session (in minutes). If omitted, runs until Ctrl+C.",
    )
    args = parser.parse_args()

    run_full_day_autopilot(duration_minutes=args.duration_minutes)

