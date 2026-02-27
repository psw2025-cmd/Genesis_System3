"""
System3 Autorun Master - HARDENED VERSION
Full-Day Autonomous Automation with Enhanced Safety & Self-Healing

This script orchestrates a complete trading day:
- Pre-market: Runs phases 201-310
- 9:15am: Starts DRY-RUN autopilot
- Every 30min: Runs phases 220-260
- Every 2hr: Refreshes curated training file
- Periodic: Runs OP1, OP2, OP3 loops
- 3:30pm: Auto-archive signals
- 3:35pm: EOD learning
- 4:00pm: Auto-shutdown

SAFETY: DRY-RUN ONLY - No real trading functions ever triggered.
HARDENED: Enhanced error handling, retry logic, self-healing.
"""

import sys
import os
import time
import json
import logging
import subprocess
import threading
import traceback
from pathlib import Path
from datetime import datetime, time as dt_time, timedelta
from typing import Dict, Any, Optional

# Ensure project root is in path
ROOT_DIR = Path(__file__).parent.absolute()
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Setup logging
LOGS_DIR = ROOT_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOGS_DIR / f"system3_autorun_master_{datetime.now().strftime('%Y%m%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)

# Heartbeat file (now written exclusively by UltimateHeartbeatManager)
HEARTBEAT_FILE = ROOT_DIR / "system3_daily_heartbeat.json"

# Heartbeat manager (single source of truth)
from system3_ultimate_heartbeat_manager import UltimateHeartbeatManager
SHUTDOWN_FLAG_FILE = ROOT_DIR / "system3_shutdown_flag.json"

# State tracking
STATE = {
    "autopilot_running": False,
    "autopilot_process": None,
    "last_phase_run": None,
    "last_curated_refresh": None,
    "last_op_cycle": None,
    "shutdown_requested": False,
    "heartbeat_errors": 0,
    "max_heartbeat_errors": 5,
}

# Phase imports (201-310) - same as original
PHASE_IMPORTS = {}

# Load phases 201-230 from diagnostics
try:
    from system3_phase_201_230_diagnostics import PHASE_IMPORTS as DIAG_IMPORTS
    for phase_num in range(201, 231):
        if phase_num in DIAG_IMPORTS:
            module_name, func_name = DIAG_IMPORTS[phase_num]
            try:
                module = __import__(f"core.engine.{module_name}", fromlist=[func_name])
                PHASE_IMPORTS[phase_num] = getattr(module, func_name)
            except Exception as e:
                logger.warning(f"Failed to import phase {phase_num}: {e}")
except Exception as e:
    logger.warning(f"Failed to load phase imports from 201-230 diagnostics: {e}")

# Load phases 231-260
try:
    from system3_phase_231_260_diagnostics import PHASE_MODULES as DIAG_MODULES
    for phase_num in range(231, 261):
        if phase_num in DIAG_MODULES:
            PHASE_IMPORTS[phase_num] = DIAG_MODULES[phase_num]
except Exception as e:
    logger.warning(f"Failed to load phase imports from 231-260 diagnostics: {e}")

# Load phases 261-300
try:
    from system3_phase_261_300_diagnostics import PHASE_MODULES as DIAG_MODULES
    for phase_num in range(261, 301):
        if phase_num in DIAG_MODULES:
            PHASE_IMPORTS[phase_num] = DIAG_MODULES[phase_num]
except Exception as e:
    logger.warning(f"Failed to load phase imports from 261-300 diagnostics: {e}")

# Load phases 301-310
try:
    from system3_phases_301_310_diagnostics import PHASE_MODULES as DIAG_MODULES
    for phase_num in range(301, 311):
        if phase_num in DIAG_MODULES:
            PHASE_IMPORTS[phase_num] = DIAG_MODULES[phase_num]
except Exception as e:
    logger.warning(f"Failed to load phase imports from 301-310 diagnostics: {e}")

if PHASE_IMPORTS:
    logger.info(f"Loaded {len(PHASE_IMPORTS)} phases into autorun master (range: {min(PHASE_IMPORTS.keys())}-{max(PHASE_IMPORTS.keys())})")
else:
    logger.warning("No phases loaded into autorun master!")


def check_shutdown_flag() -> bool:
    """Check if shutdown flag file exists (prevents restart after shutdown)."""
    if SHUTDOWN_FLAG_FILE.exists():
        try:
            with SHUTDOWN_FLAG_FILE.open("r") as f:
                flag_data = json.load(f)
            shutdown_date = flag_data.get("shutdown_date")
            if shutdown_date == datetime.now().strftime("%Y-%m-%d"):
                return True
        except Exception:
            pass
    return False


def write_shutdown_flag():
    """Write shutdown flag file to prevent watchdog restart."""
    try:
        flag_data = {
            "shutdown_date": datetime.now().strftime("%Y-%m-%d"),
            "shutdown_time": datetime.now().isoformat(),
            "reason": "scheduled_shutdown_4pm"
        }
        with SHUTDOWN_FLAG_FILE.open("w", encoding="utf-8") as f:
            json.dump(flag_data, f, indent=2)
        logger.info("Shutdown flag written")
    except Exception as e:
        logger.error(f"Failed to write shutdown flag: {e}")


def enforce_safety_checks() -> bool:
    """Hard safety enforcement - verify DRY-RUN mode."""
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
        ultra_safety_path = ROOT_DIR / "core" / "config" / "system3_ultra_safety.json"
        if ultra_safety_path.exists():
            with ultra_safety_path.open("r") as f:
                safety = json.load(f)
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


def update_heartbeat():
    """Continuously update heartbeat via UltimateHeartbeatManager (single writer)."""
    last_success = datetime.now()
    consecutive_failures = 0
    max_failures = 5
    manager = UltimateHeartbeatManager()

    while not STATE["shutdown_requested"]:
        try:
            if not manager.update_heartbeat():
                raise RuntimeError("Heartbeat manager returned failure")
            last_success = datetime.now()
            consecutive_failures = 0
            STATE["heartbeat_errors"] = 0
        except Exception as e:
            consecutive_failures += 1
            STATE["heartbeat_errors"] = consecutive_failures
            logger.error(f"Failed to update heartbeat (attempt {consecutive_failures}/{max_failures}): {e}")
            if consecutive_failures >= max_failures:
                logger.critical("Heartbeat failed too many times - potential freeze detected!")
                STATE["shutdown_requested"] = True
                break

        if (datetime.now() - last_success).total_seconds() > 120:
            logger.critical("Heartbeat appears frozen - no successful update in 2 minutes!")
            STATE["shutdown_requested"] = True
            break

        time.sleep(60)


def run_phases_range(start: int, end: int) -> Dict[str, Any]:
    """Run phases in a range with retry logic."""
    logger.info(f"Running phases {start}-{end}...")
    results = {"ok": 0, "warn": 0, "error": 0, "skipped": 0}
    
    for phase_num in range(start, end + 1):
        if phase_num in PHASE_IMPORTS:
            try:
                func = PHASE_IMPORTS[phase_num]
                # Retry logic for network-dependent phases
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        result = func()
                        status = result.get("status", "UNKNOWN")
                        if status == "OK":
                            results["ok"] += 1
                        elif status == "WARN":
                            results["warn"] += 1
                        else:
                            results["error"] += 1
                        logger.info(f"Phase {phase_num}: {status}")
                        break
                    except (ConnectionError, TimeoutError, OSError) as e:
                        if attempt < max_retries - 1:
                            logger.warning(f"Phase {phase_num} network error (attempt {attempt + 1}/{max_retries}), retrying...")
                            time.sleep(2)
                            continue
                        else:
                            raise
            except Exception as e:
                logger.error(f"Phase {phase_num} failed: {e}")
                logger.debug(traceback.format_exc())
                results["error"] += 1
        else:
            results["skipped"] += 1
    
    STATE["last_phase_run"] = datetime.now().isoformat()
    logger.info(f"Phase run complete: {results}")
    return results


def refresh_curated_file():
    """Refresh curated training file with retry logic."""
    logger.info("Refreshing curated training file...")
    max_retries = 3
    for attempt in range(max_retries):
        try:
            from system3_prep_for_new_day import build_curated_training_from_archive
            root = Path(__file__).parent.absolute()
            build_curated_training_from_archive(root)
            STATE["last_curated_refresh"] = datetime.now().isoformat()
            logger.info("Curated file refreshed successfully")
            return True
        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(f"Failed to refresh curated file (attempt {attempt + 1}/{max_retries}), retrying...")
                time.sleep(5)
                continue
            else:
                logger.error(f"Failed to refresh curated file after {max_retries} attempts: {e}")
                return False


def run_op1():
    """OP1: Pre-Market Diagnostic with retry logic."""
    logger.info("Running OP1: Pre-Market Diagnostic...")
    try:
        from core.engine.angel_market_warmup_scanner import scan_market_warmup
        result = scan_market_warmup()
        logger.info(f"OP1 complete: {result.get('status', 'UNKNOWN')}")
        return True
    except Exception as e:
        logger.error(f"OP1 failed: {e}")
        return False


def run_op2():
    """OP2: Live Signal Generation (via autopilot) with retry logic."""
    if STATE["autopilot_running"]:
        logger.info("OP2: Autopilot already running")
        return True
    
    logger.info("Starting OP2: Live Signal Generation (DRY-RUN autopilot)...")
    max_retries = 3
    for attempt in range(max_retries):
        try:
            autopilot_script = ROOT_DIR / "system3_live_day_autopilot.py"
            if autopilot_script.exists():
                process = subprocess.Popen(
                    [sys.executable, str(autopilot_script)],
                    cwd=str(ROOT_DIR),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                STATE["autopilot_process"] = process
                STATE["autopilot_running"] = True
                logger.info("OP2: Autopilot started")
                return True
            else:
                logger.error("OP2: Autopilot script not found")
                return False
        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(f"OP2 failed (attempt {attempt + 1}/{max_retries}), retrying...")
                time.sleep(2)
                continue
            else:
                logger.error(f"OP2 failed after {max_retries} attempts: {e}")
                return False


def run_op3():
    """OP3: Trade Decision & Planning with retry logic."""
    logger.info("Running OP3: Trade Decision & Planning...")
    try:
        from core.engine.angel_trade_decision import main as op3_main
        op3_main()
        logger.info("OP3 complete")
        return True
    except Exception as e:
        logger.error(f"OP3 failed: {e}")
        return False


def run_op_cycle():
    """Run OP1, OP2, OP3 cycle."""
    logger.info("=" * 70)
    logger.info("Running OP Cycle (OP1 -> OP2 -> OP3)")
    logger.info("=" * 70)
    
    op1_ok = run_op1()
    op2_ok = run_op2()
    op3_ok = run_op3()
    
    STATE["last_op_cycle"] = datetime.now().isoformat()
    
    if op1_ok and op2_ok and op3_ok:
        logger.info("OP Cycle complete: All OK")
        return True
    else:
        logger.warning(f"OP Cycle complete: OP1={op1_ok}, OP2={op2_ok}, OP3={op3_ok}")
        return False


def archive_signals():
    """Archive signals at end of day with retry logic."""
    logger.info("Archiving signals...")
    max_retries = 3
    for attempt in range(max_retries):
        try:
            from system3_prep_for_new_day import archive_old_live_signals
            result = archive_old_live_signals()
            logger.info(f"Signals archived: {result}")
            return True
        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(f"Failed to archive signals (attempt {attempt + 1}/{max_retries}), retrying...")
                time.sleep(5)
                continue
            else:
                logger.error(f"Failed to archive signals after {max_retries} attempts: {e}")
                return False


def run_eod_learning():
    """Run end-of-day learning with retry logic."""
    logger.info("Running EOD Learning...")
    max_retries = 3
    for attempt in range(max_retries):
        try:
            from core.engine.angel_daily_learning_digest import main as eod_main
            eod_main()
            logger.info("EOD Learning complete")
            return True
        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(f"EOD Learning failed (attempt {attempt + 1}/{max_retries}), retrying...")
                time.sleep(5)
                continue
            else:
                logger.error(f"EOD Learning failed after {max_retries} attempts: {e}")
                return False


def is_market_time() -> bool:
    """Check if current time is during market hours (9:15-15:30)."""
    now = datetime.now()
    current_time = now.time()
    market_open = dt_time(9, 15)
    market_close = dt_time(15, 30)
    return market_open <= current_time <= market_close


def is_weekday() -> bool:
    """Check if today is a weekday."""
    return datetime.now().weekday() < 5  # 0-4 = Monday-Friday


def main():
    """Main automation loop."""
    logger.info("=" * 70)
    logger.info("SYSTEM3 AUTORUN MASTER - STARTING (HARDENED)")
    logger.info("=" * 70)
    logger.info(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Root: {ROOT_DIR}")
    logger.info("=" * 70)

    # Enforce continuous heartbeat updates for the UltimateHeartbeatManager.
    os.environ.setdefault("HEARTBEAT_CONTINUOUS", "1")
    os.environ.setdefault("HEARTBEAT_INTERVAL_SECONDS", "60")
    
    # Check if shutdown flag exists (prevent restart after shutdown)
    if check_shutdown_flag():
        logger.info("=" * 70)
        logger.info("Shutdown flag detected - Master already shut down today.")
        logger.info("Exiting to prevent restart loop.")
        logger.info("=" * 70)
        return 0
    
    # Safety check
    if not enforce_safety_checks():
        logger.error("Safety checks failed. Aborting.")
        return 1
    
    # Start heartbeat thread
    heartbeat_thread = threading.Thread(target=update_heartbeat, daemon=True)
    heartbeat_thread.start()
    logger.info("Heartbeat thread started")
    
    # Pre-market: Run phases 201-310
    if is_weekday():
        logger.info("=" * 70)
        logger.info("PRE-MARKET: Running phases 201-310")
        logger.info("=" * 70)
        run_phases_range(201, 310)
    
    # Main loop
    last_phase_run_time = None
    last_curated_refresh_time = None
    last_op_cycle_time = None
    
    try:
        while not STATE["shutdown_requested"]:
            now = datetime.now()
            current_time = now.time()
            
            # 9:15am: Start autopilot
            if current_time >= dt_time(9, 15) and not STATE["autopilot_running"] and is_weekday():
                logger.info("=" * 70)
                logger.info("9:15 AM: Starting DRY-RUN Autopilot")
                logger.info("=" * 70)
                run_op2()
            
            # Every 30 minutes: Run phases 220-260
            if (last_phase_run_time is None or 
                (now - last_phase_run_time).total_seconds() >= 1800):
                if is_market_time() and is_weekday():
                    logger.info("=" * 70)
                    logger.info("30-MIN INTERVAL: Running phases 220-260")
                    logger.info("=" * 70)
                    run_phases_range(220, 260)
                    last_phase_run_time = now
            
            # Every 2 hours: Refresh curated file
            if (last_curated_refresh_time is None or 
                (now - last_curated_refresh_time).total_seconds() >= 7200):
                if is_market_time() and is_weekday():
                    logger.info("=" * 70)
                    logger.info("2-HOUR INTERVAL: Refreshing curated file")
                    logger.info("=" * 70)
                    refresh_curated_file()
                    last_curated_refresh_time = now
            
            # Periodic: Run OP cycles (every hour during market hours)
            if (last_op_cycle_time is None or 
                (now - last_op_cycle_time).total_seconds() >= 3600):
                if is_market_time() and is_weekday():
                    logger.info("=" * 70)
                    logger.info("HOURLY: Running OP Cycle")
                    logger.info("=" * 70)
                    run_op_cycle()
                    last_op_cycle_time = now
            
            # 3:30pm: Archive signals
            if current_time >= dt_time(15, 30) and current_time < dt_time(15, 31):
                if is_weekday() and not STATE.get("archived_today", False):
                    logger.info("=" * 70)
                    logger.info("3:30 PM: Archiving signals")
                    logger.info("=" * 70)
                    archive_signals()
                    STATE["archived_today"] = True
            
            # 3:35pm: EOD Learning
            if current_time >= dt_time(15, 35) and current_time < dt_time(15, 36):
                if is_weekday() and not STATE.get("eod_learning_done", False):
                    logger.info("=" * 70)
                    logger.info("3:35 PM: Running EOD Learning")
                    logger.info("=" * 70)
                    run_eod_learning()
                    STATE["eod_learning_done"] = True
            
            # 4:00pm: Shutdown (only once per day, or exit immediately if past 4 PM)
            if current_time >= dt_time(16, 0):
                if is_weekday():
                    if not STATE.get("shutdown_completed_today", False):
                        logger.info("=" * 70)
                        logger.info("4:00 PM: Shutting down")
                        logger.info("=" * 70)
                        STATE["shutdown_completed_today"] = True
                        STATE["shutdown_requested"] = True
                        write_shutdown_flag()  # Write flag to prevent watchdog restart
                        break
                    else:
                        # Shutdown already completed today - exit immediately
                        logger.info("=" * 70)
                        logger.info("Past 4:00 PM - Shutdown already completed today. Exiting.")
                        logger.info("=" * 70)
                        STATE["shutdown_requested"] = True
                        write_shutdown_flag()
                        break
            
            # Sleep for 60 seconds
            time.sleep(60)
    
    except KeyboardInterrupt:
        logger.info("\n[INFO] Interrupted by user (Ctrl+C).")
        STATE["shutdown_requested"] = True
    except Exception as e:
        logger.error(f"\n[ERROR] Fatal error: {e}", exc_info=True)
        write_shutdown_flag()  # Write flag on fatal error
        return 1
    
    # Cleanup
    if STATE["autopilot_process"]:
        logger.info("Stopping autopilot...")
        try:
            STATE["autopilot_process"].terminate()
            STATE["autopilot_running"] = False
        except Exception as e:
            logger.error(f"Error stopping autopilot: {e}")
    
    logger.info("=" * 70)
    logger.info("SYSTEM3 AUTORUN MASTER - SHUTDOWN COMPLETE")
    logger.info("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

