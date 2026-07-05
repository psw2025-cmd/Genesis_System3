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

import os
import sys
from pathlib import Path

# VENV ENFORCEMENT: Verify running inside System3 venv
EXPECTED_VENV = Path(__file__).parent.absolute() / "venv"
if "venv" not in sys.executable and "virtualenv" not in sys.executable:
    # Not running inside any venv - try to restart with venv python
    venv_python = EXPECTED_VENV / "Scripts" / "python.exe"
    if venv_python.exists():
        print(f"⚠️ Not running in venv - restarting with {venv_python}")
        import subprocess

        sys.exit(subprocess.call([str(venv_python), __file__] + sys.argv[1:]))
    else:
        raise EnvironmentError(
            f"Not running inside System3 venv.\n"
            f"Current: {sys.executable}\n"
            f"Expected venv: {EXPECTED_VENV}\n"
            f"Please run: {venv_python} {__file__}"
        )

# CRITICAL FIX: Add venv site-packages to Python path FIRST
ROOT_DIR = Path(__file__).parent.absolute()
VENV_SITE_PACKAGES = ROOT_DIR / "venv" / "Lib" / "site-packages"
if VENV_SITE_PACKAGES.exists() and str(VENV_SITE_PACKAGES) not in sys.path:
    sys.path.insert(0, str(VENV_SITE_PACKAGES))

# Ensure project root is in path
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import json
import logging
import subprocess
import threading
import time
import traceback
from datetime import datetime
from datetime import time as dt_time
from datetime import timedelta
from typing import Any, Dict, Optional

from system3_ultimate_heartbeat_manager import UltimateHeartbeatManager

# Optional psutil (used for PID/health guards)
try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

# Setup logging (force fresh handlers so file is always written)
LOGS_DIR = ROOT_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOGS_DIR / f"system3_autorun_master_{datetime.now().strftime('%Y%m%d')}.log"

EXPECTED_VENV_PYTHON = ROOT_DIR / "venv" / "Scripts" / "python.exe"


def _configure_logging() -> logging.Logger:
    root = logging.getLogger()
    for h in list(root.handlers):
        root.removeHandler(h)
    root.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
    fh.setFormatter(formatter)
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    root.addHandler(fh)
    root.addHandler(sh)
    return logging.getLogger(__name__)


logger = _configure_logging()

# Forward pipeline guard (non-fatal): detect forward-signal corruption early
try:
    from system3_forward_pipeline_guard import run_guard as forward_guard

    guard_result = forward_guard(auto_heal=True)
    if guard_result.get("status") != "OK":
        logger.warning("Forward pipeline guard warnings: %s", guard_result.get("details", "unknown"))
    else:
        logger.info("Forward pipeline guard passed: %s", guard_result.get("details", ""))
except Exception as e:
    logger.warning(f"Forward pipeline guard skipped: {e}")

# Import market calendar for intelligent market state detection
try:
    from core.utils.market_calendar import (
        MarketState,
        get_market_state,
        should_run_autopilot,
    )

    MARKET_CALENDAR_AVAILABLE = True
except ImportError:
    MARKET_CALENDAR_AVAILABLE = False
    logger.warning("Market calendar not available - using basic time checks")

# Heartbeat file
HEARTBEAT_FILE = ROOT_DIR / "system3_daily_heartbeat.json"
SHUTDOWN_FLAG_FILE = ROOT_DIR / "system3_shutdown_flag.json"
STATE_DIR = ROOT_DIR / "state"
STATE_DIR.mkdir(parents=True, exist_ok=True)
MASTER_PID_FILE = STATE_DIR / "system3_master.pid"
WATCHDOG_PID_FILE = STATE_DIR / "system3_watchdog.pid"

SIGNALS_FILE = ROOT_DIR / "dhan_index_ai_signals.csv"

# Thresholds and intervals
OP2_STALL_THRESHOLD = 300  # seconds without activity before considering OP2 stalled
OP2_STALL_BACKOFF = 120  # seconds to wait after a stall-triggered restart attempt
OP2_RESTART_CAP = 3  # max OP2 restarts per day
STATUS_LOG_INTERVAL = 300  # structured status line every 5 minutes
HEARTBEAT_STALE_THRESHOLD = 240  # guard against reusing stale masters

# State tracking
STATE = {
    "autopilot_running": False,
    "autopilot_process": None,
    "last_phase_run": None,
    "last_curated_refresh": None,
    "last_op_cycle": None,
    "last_signal_write": None,
    "last_op2_activity": None,
    "op2_restart_count": 0,
    "op2_restart_date": None,
    "shutdown_requested": False,
    "heartbeat_errors": 0,
    "max_heartbeat_errors": 5,
    "last_error_type": "none",
    "status_last_logged": None,
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

# Load phases 311-330
try:
    # Try to load from existing phase files directly
    for phase_num in range(311, 331):
        try:
            module_name = f"system3_phase{phase_num}_"
            # Find matching phase file in core/engine
            phase_dir = ROOT_DIR / "core" / "engine"
            matching_files = list(phase_dir.glob(f"system3_phase{phase_num}_*.py"))
            if matching_files:
                phase_file = matching_files[0]
                module_name = phase_file.stem
                func_name = f"run_phase_{phase_num}"
                try:
                    module = __import__(f"core.engine.{module_name}", fromlist=[func_name])
                    # Prefer run_phase_{num}; fallback to run_phase{num} if present
                    if hasattr(module, func_name):
                        PHASE_IMPORTS[phase_num] = getattr(module, func_name)
                    else:
                        alt_func = f"run_phase{phase_num}"
                        if hasattr(module, alt_func):
                            PHASE_IMPORTS[phase_num] = getattr(module, alt_func)
                        else:
                            raise AttributeError(f"Missing {func_name} and {alt_func}")
                except Exception as e:
                    logger.warning(f"Failed to import phase {phase_num}: {e}")
        except Exception as e:
            pass
except Exception as e:
    logger.warning(f"Failed to load phase imports from 311-330: {e}")

# Load phases 331-340
try:
    from system3_phase_331_340_diagnostics import PHASE_IMPORTS as DIAG_IMPORTS

    for phase_num in range(331, 341):
        if phase_num in DIAG_IMPORTS:
            module_name, func_name = DIAG_IMPORTS[phase_num]
            try:
                module = __import__(f"core.engine.{module_name}", fromlist=[func_name])
                PHASE_IMPORTS[phase_num] = getattr(module, func_name)
            except Exception as e:
                logger.warning(f"Failed to import phase {phase_num}: {e}")
except Exception as e:
    logger.warning(f"Failed to load phase imports from 331-340 diagnostics: {e}")

# Load phases 361-380 from registry (includes signal pipeline, strategy analysis, data quality, self-test)
try:
    from core.engine.system3_phases_361_380_registry import PHASES_361_380_REGISTRY

    for phase_num, (module_name, func_name, category, mode) in PHASES_361_380_REGISTRY.items():
        try:
            module = __import__(f"core.engine.{module_name}", fromlist=[func_name])
            PHASE_IMPORTS[phase_num] = getattr(module, func_name)
            logger.debug(f"Loaded phase {phase_num} ({category})")
        except Exception as e:
            logger.warning(f"Failed to load phase {phase_num}: {e}")
except Exception as e:
    logger.warning(f"Failed to load phase imports from 361-380 registry: {e}")

if PHASE_IMPORTS:
    logger.info(
        f"Loaded {len(PHASE_IMPORTS)} phases into autorun master (range: {min(PHASE_IMPORTS.keys())}-{max(PHASE_IMPORTS.keys())})"
    )
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
            "reason": "scheduled_shutdown_4pm",
        }
        with SHUTDOWN_FLAG_FILE.open("w", encoding="utf-8") as f:
            json.dump(flag_data, f, indent=2)
        logger.info("Shutdown flag written")
    except Exception as e:
        logger.error(f"Failed to write shutdown flag: {e}")


def _module_origin(mod_name: str) -> Optional[str]:
    try:
        import importlib.util

        spec = importlib.util.find_spec(mod_name)
        return spec.origin if spec and spec.origin else None
    except Exception:
        return None


def enforce_venv_runtime() -> bool:
    """Ensure we are running under the expected venv interpreter."""
    expected = str(EXPECTED_VENV_PYTHON)
    actual = sys.executable
    if not EXPECTED_VENV_PYTHON.exists():
        logger.error(f"Expected venv python missing at {expected}")
        return False
    if os.path.abspath(actual) != os.path.abspath(expected):
        logger.error(f"Wrong interpreter detected: {actual} (expected {expected}). Exiting for safety.")
        return False

    # Basic import origin checks (psutil + pandas) to ensure we are on venv site-packages
    psutil_origin = _module_origin("psutil")
    pandas_origin = _module_origin("pandas")
    origins = {"psutil": psutil_origin, "pandas": pandas_origin}
    for name, origin in origins.items():
        if origin and "venv" not in origin.lower():
            logger.error(f"{name} appears to be imported from non-venv location: {origin}")
            return False

    logger.info(f"Interpreter OK: {actual} (venv confirmed)")
    return True


def _safe_load_pid(pid_file: Path) -> Optional[Dict[str, Any]]:
    if not pid_file.exists():
        return None
    try:
        with pid_file.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.debug(f"Failed to read pid file {pid_file}: {e}")
        return None


def _write_pid(pid_file: Path, script_name: str):
    try:
        payload = {
            "pid": os.getpid(),
            "script": script_name,
            "started": datetime.now().isoformat(),
        }
        pid_file.parent.mkdir(parents=True, exist_ok=True)
        with pid_file.open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        logger.info(f"PID file written: {pid_file} -> {payload['pid']}")
    except Exception as e:
        logger.warning(f"Could not write PID file {pid_file}: {e}")


def _remove_pid(pid_file: Path):
    try:
        if pid_file.exists():
            pid_file.unlink()
    except Exception as e:
        logger.debug(f"Failed to remove pid file {pid_file}: {e}")


def _pid_alive(pid: int, marker: Optional[str] = None) -> bool:
    if not PSUTIL_AVAILABLE:
        return False
    try:
        proc = psutil.Process(pid)
        if marker:
            cmdline = " ".join(proc.cmdline()) if proc.cmdline() else ""
            return marker in cmdline and proc.is_running()
        return proc.is_running()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False
    except Exception as e:
        logger.debug(f"PID check failed for {pid}: {e}")
        return False


def _heartbeat_age_seconds() -> Optional[float]:
    if not HEARTBEAT_FILE.exists():
        return None
    try:
        with HEARTBEAT_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
        timestamp_str = (
            data.get("_last_updated") or data.get("timestamp") or data.get("system_info", {}).get("timestamp")
        )
        if not timestamp_str:
            return None
        hb_time = datetime.fromisoformat(timestamp_str)
        return (datetime.now() - hb_time).total_seconds()
    except Exception as e:
        logger.debug(f"Failed to read heartbeat age: {e}")
        return None


def _file_mtime(path: Path) -> Optional[datetime]:
    try:
        if path.exists():
            return datetime.fromtimestamp(path.stat().st_mtime)
    except Exception as e:
        logger.debug(f"Failed to read mtime for {path}: {e}")
    return None


def _reset_op2_counter_if_new_day():
    today = datetime.now().strftime("%Y-%m-%d")
    if STATE["op2_restart_date"] != today:
        STATE["op2_restart_date"] = today
        STATE["op2_restart_count"] = 0


def _dt_from_iso(ts: Optional[str]) -> Optional[datetime]:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts)
    except Exception:
        return None


def _latest_activity_timestamp() -> Optional[datetime]:
    """Return the latest timestamp among OP2-related activity markers."""
    candidates = [
        _dt_from_iso(STATE.get("last_signal_write")),
        _dt_from_iso(STATE.get("last_op_cycle")),
        _dt_from_iso(STATE.get("last_op2_activity")),
    ]
    candidates = [c for c in candidates if c is not None]
    return max(candidates) if candidates else None


def _record_interpreter_telemetry():
    """Persist interpreter telemetry alongside heartbeat for audits."""
    telemetry = {
        "timestamp": datetime.now().isoformat(),
        "python_executable": sys.executable,
        "expected_python": str(EXPECTED_VENV_PYTHON),
        "venv_active": os.environ.get("VIRTUAL_ENV") is not None,
        "site_packages_source": (
            str(VENV_SITE_PACKAGES)
            if VENV_SITE_PACKAGES in [Path(p) for p in sys.path if Path(p).exists()]
            else "unknown"
        ),
    }
    telemetry_file = STATE_DIR / "runtime_interpreter_telemetry.json"
    try:
        with telemetry_file.open("w", encoding="utf-8") as f:
            json.dump(telemetry, f, indent=2)
    except Exception as e:
        logger.debug(f"Failed to write interpreter telemetry: {e}")

    if HEARTBEAT_FILE.exists():
        try:
            with HEARTBEAT_FILE.open("r", encoding="utf-8") as f:
                hb = json.load(f)
            hb["interpreter"] = telemetry
            with HEARTBEAT_FILE.open("w", encoding="utf-8") as f:
                json.dump(hb, f, indent=2)
        except Exception as e:
            logger.debug(f"Failed to augment heartbeat with interpreter telemetry: {e}")


def _log_status_line(start_time: datetime, restart_count_today: int):
    now = datetime.now()
    hb_age = _heartbeat_age_seconds()
    uptime = (now - start_time).total_seconds()
    line = (
        f"STATUS ts={now.strftime('%H:%M:%S')} master_pid={os.getpid()} "
        f"uptime_s={int(uptime)} heartbeat_age_s={int(hb_age) if hb_age is not None else 'n/a'} "
        f"op2_restarts_today={STATE['op2_restart_count']} restarts_today={restart_count_today} "
        f"last_op_cycle={STATE.get('last_op_cycle')} last_error={STATE.get('last_error_type')}"
    )
    logger.info(line)
    STATE["status_last_logged"] = now.isoformat()


def _check_autopilot_process():
    """Update autopilot_running flag if process exited; sync activity markers."""
    proc = STATE.get("autopilot_process")
    if proc:
        if proc.poll() is not None:
            STATE["autopilot_running"] = False
            STATE["autopilot_process"] = None


def _check_op2_stall(now: datetime) -> None:
    """Detect OP2 stall via signal mtime and activity markers, self-heal if needed."""
    _reset_op2_counter_if_new_day()
    if not STATE.get("autopilot_running"):
        return

    signals_mtime = _file_mtime(SIGNALS_FILE)
    if signals_mtime:
        STATE["last_signal_write"] = signals_mtime.isoformat()

    latest = _latest_activity_timestamp()
    if latest is None:
        latest = datetime.now() - timedelta(seconds=OP2_STALL_THRESHOLD + 10)
    age = (now - latest).total_seconds()

    if age <= OP2_STALL_THRESHOLD:
        return

    # Additional guard: ensure process is alive before acting
    proc = STATE.get("autopilot_process")
    alive = proc and proc.poll() is None
    if not alive:
        STATE["autopilot_running"] = False
        return

    if STATE["op2_restart_count"] >= OP2_RESTART_CAP:
        logger.critical(
            f"OP2 stall detected but restart cap reached ({OP2_RESTART_CAP}). Manual intervention required."
        )
        STATE["last_error_type"] = "op2_stall_cap"
        return

    logger.warning(f"OP2 stall detected (no activity for {int(age)}s). Initiating controlled restart.")
    STATE["last_error_type"] = "op2_stall"
    try:
        proc.terminate()
        proc.wait(timeout=5)
    except Exception as e:
        logger.warning(f"Failed to terminate stalled OP2 process: {e}")
    STATE["autopilot_running"] = False
    STATE["autopilot_process"] = None
    STATE["op2_restart_count"] += 1
    time.sleep(OP2_STALL_BACKOFF)
    run_op2()


def _ensure_singleton_master() -> bool:
    """Guarantee at most one master; reuse healthy existing instance."""
    existing = _safe_load_pid(MASTER_PID_FILE)
    if existing and "pid" in existing:
        pid = existing.get("pid")
        if _pid_alive(pid, "system3_autorun_master"):
            hb_age = _heartbeat_age_seconds()
            if hb_age is not None and hb_age <= HEARTBEAT_STALE_THRESHOLD:
                logger.info(f"Existing master already running (PID {pid}, heartbeat {hb_age:.0f}s). Idempotent exit.")
                return False
            else:
                logger.warning(
                    f"Existing master PID {pid} looks stale (heartbeat age: {hb_age}). Attempting controlled takeover."
                )
                try:
                    proc = psutil.Process(pid) if PSUTIL_AVAILABLE else None
                    if proc:
                        proc.terminate()
                        proc.wait(timeout=5)
                except Exception as e:
                    logger.warning(f"Failed to terminate stale master {pid}: {e}")
                time.sleep(2)
        # stale pid file or dead process
        _remove_pid(MASTER_PID_FILE)

    _write_pid(MASTER_PID_FILE, "system3_autorun_master.py")
    return True


def enforce_safety_checks() -> bool:
    """Hard safety enforcement - verify DRY-RUN mode."""
    logger.info("=" * 70)
    logger.info("SAFETY ENFORCEMENT CHECK")
    logger.info("=" * 70)

    errors = []

    # Check 1: LIVE_TRADING_ENABLED
    try:
        from config.live_trade_config import (
            LIVE_TRADING_ENABLED,
            USE_LIVE_EXECUTION_ENGINE,
        )

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
        from core.engine.dhan_automation_config import AUTOMATION_CONFIG

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
            _record_interpreter_telemetry()
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
                            logger.warning(
                                f"Phase {phase_num} network error (attempt {attempt + 1}/{max_retries}), retrying..."
                            )
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
        from core.engine.dhan_market_warmup_scanner import scan_market_warmup

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
                now = datetime.now().isoformat()
                STATE["last_op2_activity"] = now
                STATE["last_signal_write"] = STATE.get("last_signal_write") or now
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
        from core.engine.dhan_trade_decision import main as op3_main

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

    now_iso = datetime.now().isoformat()
    STATE["last_op_cycle"] = now_iso
    STATE["last_op2_activity"] = now_iso

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
            from core.engine.dhan_daily_learning_digest import main as eod_main

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
    start_time = datetime.now()
    logger.info("=" * 70)
    logger.info("SYSTEM3 AUTORUN MASTER - STARTING (HARDENED)")
    logger.info("=" * 70)
    logger.info(f"Date: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Root: {ROOT_DIR}")

    if not enforce_venv_runtime():
        return 1

    if not _ensure_singleton_master():
        return 0

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

    # Seed last_signal_write if file exists
    sig_mtime = _file_mtime(SIGNALS_FILE)
    if sig_mtime:
        STATE["last_signal_write"] = sig_mtime.isoformat()

    # Pre-market: Run phases 201-310
    if is_weekday():
        logger.info("=" * 70)
        logger.info("PRE-MARKET: Running phases 201-310")
        logger.info("=" * 70)
        run_phases_range(201, 310)

    # Pre-market: Run new phases 361-375 (signal pipeline, strategy analysis, data quality)
    if is_weekday():
        logger.info("=" * 70)
        logger.info("PRE-MARKET: Running phases 361-375 (new system3 block)")
        logger.info("=" * 70)
        run_phases_range(361, 375)

    # Main loop
    last_phase_run_time = None
    last_curated_refresh_time = None
    last_op_cycle_time = None
    restart_count_today = 0

    try:
        while not STATE["shutdown_requested"]:
            now = datetime.now()
            current_time = now.time()

            _check_autopilot_process()
            _check_op2_stall(now)

            # 9:15am: Start autopilot
            if current_time >= dt_time(9, 15) and not STATE["autopilot_running"] and is_weekday():
                logger.info("=" * 70)
                logger.info("9:15 AM: Starting DRY-RUN Autopilot")
                logger.info("=" * 70)
                run_op2()

            # Every 30 minutes: Run phases 220-260 with production pipeline
            if last_phase_run_time is None or (now - last_phase_run_time).total_seconds() >= 1800:
                if is_market_time() and is_weekday():
                    logger.info("=" * 70)
                    logger.info("30-MIN INTERVAL: Generating signals BEFORE phases 220-260")
                    logger.info("=" * 70)

                    # CRITICAL FIX: Generate signals BEFORE running analysis phases
                    try:
                        from core.engine.dhan_live_ai_signals import (
                            run_once_with_snapshot,
                        )
                        from core.engine.dhan_options_watch_loop import (
                            load_latest_watch_snapshot,
                        )

                        # Load latest snapshot from watch file
                        df_snapshot = load_latest_watch_snapshot()
                        if df_snapshot is not None and not df_snapshot.empty:
                            logger.info(f"  → Loaded {len(df_snapshot)} rows from watch snapshot")
                            run_once_with_snapshot(df_snapshot)
                            logger.info("  → Signal generation complete")
                            STATE["last_signal_write"] = datetime.now().isoformat()
                        else:
                            logger.warning("  → No snapshot data available for signal generation")
                    except Exception as e:
                        logger.error(f"  → Signal generation failed: {e}")
                        import traceback

                        logger.error(traceback.format_exc())

                    # PRODUCTION PIPELINE: Run Phase 220 → 221 → 239 BEFORE OP2
                    logger.info("=" * 70)
                    logger.info("30-MIN INTERVAL: Running Production Pipeline (220→221→239)")
                    logger.info("=" * 70)
                    try:
                        from system3_production_pipeline import run_production_pipeline

                        pipeline_report = run_production_pipeline(verbose=True)

                        if pipeline_report.get("errors"):
                            logger.error(f"Production pipeline had {len(pipeline_report['errors'])} errors")
                            for error in pipeline_report["errors"]:
                                logger.error(f"  → {error}")
                        else:
                            logger.info("✓ Production pipeline completed successfully")
                            logger.info(f"  → Phases: {', '.join(pipeline_report.get('phases_executed', []))}")
                            logger.info(f"  → Duration: {pipeline_report.get('total_duration_seconds', 0):.2f}s")

                            # Log performance alerts
                            if pipeline_report.get("performance_alerts"):
                                for alert in pipeline_report["performance_alerts"]:
                                    logger.warning(alert)
                    except Exception as e:
                        logger.error(f"Production pipeline failed: {e}")
                        import traceback

                        logger.error(traceback.format_exc())

                    logger.info("=" * 70)
                    logger.info("30-MIN INTERVAL: Running phases 220-260")
                    logger.info("=" * 70)
                    run_phases_range(220, 260)
                    last_phase_run_time = now

            # Every 2 hours: Refresh curated file
            if last_curated_refresh_time is None or (now - last_curated_refresh_time).total_seconds() >= 7200:
                if is_market_time() and is_weekday():
                    logger.info("=" * 70)
                    logger.info("2-HOUR INTERVAL: Refreshing curated file")
                    logger.info("=" * 70)
                    refresh_curated_file()
                    last_curated_refresh_time = now

            # Periodic: Run OP cycles (every hour during market hours)
            if last_op_cycle_time is None or (now - last_op_cycle_time).total_seconds() >= 3600:
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

            # 3:40pm: Post-Close Audit (before shutdown)
            if current_time >= dt_time(15, 40) and current_time < dt_time(15, 41):
                if is_weekday() and not STATE.get("post_close_audit_done", False):
                    logger.info("=" * 70)
                    logger.info("3:40 PM: Running Post-Close Signal Audit")
                    logger.info("=" * 70)
                    try:
                        from datetime import date

                        from core.validation.post_close_signal_audit import (
                            main as run_post_close_audit,
                        )

                        audit_result = run_post_close_audit(target_date=date.today())
                        if audit_result == 0:
                            logger.info("Post-close audit completed successfully")
                        else:
                            logger.warning("Post-close audit found issues - check report")
                        STATE["post_close_audit_done"] = True
                    except Exception as e:
                        logger.error(f"Post-close audit failed: {e}")
                        import traceback

                        logger.error(traceback.format_exc())
                    logger.info("=" * 70)

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

            # Lightweight structured status line
            last_logged = _dt_from_iso(STATE.get("status_last_logged"))
            if last_logged is None or (now - last_logged).total_seconds() >= STATUS_LOG_INTERVAL:
                _log_status_line(start_time, restart_count_today)

            time.sleep(60)

    except KeyboardInterrupt:
        logger.info("\n[INFO] Interrupted by user (Ctrl+C).")
        STATE["shutdown_requested"] = True
    except Exception as e:
        logger.error(f"\n[ERROR] Fatal error: {e}", exc_info=True)
        STATE["last_error_type"] = "fatal"
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

    _remove_pid(MASTER_PID_FILE)

    logger.info("=" * 70)
    logger.info("SYSTEM3 AUTORUN MASTER - SHUTDOWN COMPLETE")
    logger.info("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
