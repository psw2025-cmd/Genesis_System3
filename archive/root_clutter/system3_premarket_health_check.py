#!/usr/bin/env python3
"""
System3 Pre-Market Health Check
Comprehensive health check to run before market open.

Verifies:
- Disk space availability
- Network connectivity
- Critical files existence
- Python environment
- Dependencies installed
- Last shutdown was clean
- Configuration validity
- System readiness
"""

import sys
import json
import shutil
import socket
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any

PROJECT_ROOT = Path(__file__).parent.absolute()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Setup logging
import logging
LOGS_DIR = PROJECT_ROOT / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOGS_DIR / f"premarket_health_check_{datetime.now().strftime('%Y%m%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# Critical files to check
CRITICAL_FILES = {
    "system3_autorun_master.py": PROJECT_ROOT / "system3_autorun_master.py",
    "system3_watchdog.py": PROJECT_ROOT / "system3_watchdog.py",
    "system3_live_day_autopilot.py": PROJECT_ROOT / "system3_live_day_autopilot.py",
    "START_AUTORUN_AND_WATCHDOG.bat": PROJECT_ROOT / "START_AUTORUN_AND_WATCHDOG.bat",
    "venv/Scripts/python.exe": PROJECT_ROOT / "venv" / "Scripts" / "python.exe",
    "storage/live/angel_index_ai_signals.csv": PROJECT_ROOT / "storage" / "live" / "angel_index_ai_signals.csv",
    "storage/live/angel_index_ai_signals_curated.csv": PROJECT_ROOT / "storage" / "live" / "angel_index_ai_signals_curated.csv",
}

# Critical dependencies
CRITICAL_DEPENDENCIES = [
    "pandas",
    "numpy",
    "psutil",
    "requests",
]


def check_disk_space(min_gb: float = 1.0) -> Tuple[bool, Dict[str, Any]]:
    """Check if sufficient disk space available."""
    try:
        total, used, free = shutil.disk_usage(PROJECT_ROOT)
        free_gb = free / (1024**3)
        total_gb = total / (1024**3)
        used_percent = (used / total) * 100
        
        result = {
            "status": "PASS" if free_gb >= min_gb else "FAIL",
            "free_gb": round(free_gb, 2),
            "total_gb": round(total_gb, 2),
            "used_percent": round(used_percent, 2),
            "min_required_gb": min_gb,
        }
        
        if free_gb < min_gb:
            logger.error(f"❌ Disk space check FAILED: {free_gb:.2f} GB free (need {min_gb} GB)")
        else:
            logger.info(f"✅ Disk space check PASSED: {free_gb:.2f} GB free")
        
        return free_gb >= min_gb, result
    except Exception as e:
        logger.error(f"❌ Disk space check ERROR: {e}")
        return False, {"status": "ERROR", "error": str(e)}


def check_internet_connectivity(timeout: int = 5) -> Tuple[bool, Dict[str, Any]]:
    """Check internet connectivity."""
    test_hosts = [
        ("8.8.8.8", 53),  # Google DNS
        ("1.1.1.1", 53),  # Cloudflare DNS
    ]
    
    for host, port in test_hosts:
        try:
            socket.create_connection((host, port), timeout=timeout)
            logger.info(f"✅ Internet connectivity check PASSED (connected to {host})")
            return True, {"status": "PASS", "host": host}
        except (socket.error, OSError) as e:
            continue
    
    logger.error("❌ Internet connectivity check FAILED (cannot reach test hosts)")
    return False, {"status": "FAIL", "error": "Cannot reach test hosts"}


def check_critical_files() -> Tuple[bool, Dict[str, Any]]:
    """Check if all critical files exist."""
    missing_files = []
    existing_files = []
    
    for name, path in CRITICAL_FILES.items():
        if path.exists():
            existing_files.append(name)
        else:
            missing_files.append(name)
    
    result = {
        "status": "PASS" if not missing_files else "FAIL",
        "total": len(CRITICAL_FILES),
        "existing": len(existing_files),
        "missing": len(missing_files),
        "missing_files": missing_files,
    }
    
    if missing_files:
        logger.error(f"❌ Critical files check FAILED: {len(missing_files)} file(s) missing")
        for file in missing_files:
            logger.error(f"   - {file}")
    else:
        logger.info(f"✅ Critical files check PASSED: All {len(CRITICAL_FILES)} files exist")
    
    return len(missing_files) == 0, result


def check_python_version() -> Tuple[bool, Dict[str, Any]]:
    """Check Python version."""
    try:
        version = sys.version_info
        version_str = f"{version.major}.{version.minor}.{version.micro}"
        
        # Require Python 3.8+
        is_valid = version.major == 3 and version.minor >= 8
        
        result = {
            "status": "PASS" if is_valid else "FAIL",
            "version": version_str,
            "major": version.major,
            "minor": version.minor,
            "micro": version.micro,
        }
        
        if is_valid:
            logger.info(f"✅ Python version check PASSED: {version_str}")
        else:
            logger.error(f"❌ Python version check FAILED: {version_str} (need 3.8+)")
        
        return is_valid, result
    except Exception as e:
        logger.error(f"❌ Python version check ERROR: {e}")
        return False, {"status": "ERROR", "error": str(e)}


def check_dependencies() -> Tuple[bool, Dict[str, Any]]:
    """Check if critical dependencies are installed."""
    missing_deps = []
    existing_deps = []
    
    for dep in CRITICAL_DEPENDENCIES:
        try:
            __import__(dep)
            existing_deps.append(dep)
        except ImportError:
            missing_deps.append(dep)
    
    result = {
        "status": "PASS" if not missing_deps else "FAIL",
        "total": len(CRITICAL_DEPENDENCIES),
        "existing": len(existing_deps),
        "missing": len(missing_deps),
        "missing_deps": missing_deps,
    }
    
    if missing_deps:
        logger.error(f"❌ Dependencies check FAILED: {len(missing_deps)} package(s) missing")
        for dep in missing_deps:
            logger.error(f"   - {dep}")
    else:
        logger.info(f"✅ Dependencies check PASSED: All {len(CRITICAL_DEPENDENCIES)} packages installed")
    
    return len(missing_deps) == 0, result


def check_last_shutdown_clean() -> Tuple[bool, Dict[str, Any]]:
    """Check if last shutdown was clean."""
    shutdown_flag_file = PROJECT_ROOT / "system3_shutdown_flag.json"
    heartbeat_file = PROJECT_ROOT / "system3_daily_heartbeat.json"
    
    result = {
        "status": "UNKNOWN",
        "shutdown_flag_exists": False,
        "shutdown_date": None,
        "shutdown_reason": None,
        "heartbeat_exists": False,
        "heartbeat_age_seconds": None,
    }
    
    # Check shutdown flag
    if shutdown_flag_file.exists():
        try:
            with shutdown_flag_file.open("r") as f:
                shutdown_data = json.load(f)
            result["shutdown_flag_exists"] = True
            result["shutdown_date"] = shutdown_data.get("shutdown_date")
            result["shutdown_reason"] = shutdown_data.get("reason", "unknown")
            
            # Check if shutdown was today or yesterday (both OK)
            shutdown_date = shutdown_data.get("shutdown_date")
            today = datetime.now().strftime("%Y-%m-%d")
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            
            if shutdown_date in [today, yesterday]:
                result["status"] = "PASS"
                logger.info(f"✅ Last shutdown check PASSED: Clean shutdown on {shutdown_date}")
            else:
                result["status"] = "WARN"
                logger.warning(f"⚠️  Last shutdown check WARN: Shutdown date {shutdown_date} is old")
        except Exception as e:
            result["status"] = "ERROR"
            logger.error(f"❌ Last shutdown check ERROR: {e}")
    else:
        result["status"] = "WARN"
        logger.warning("⚠️  Last shutdown check WARN: No shutdown flag found (first run?)")
    
    # Check heartbeat age
    if heartbeat_file.exists():
        try:
            with heartbeat_file.open("r") as f:
                heartbeat_data = json.load(f)
            timestamp_str = heartbeat_data.get("timestamp")
            if timestamp_str:
                heartbeat_time = datetime.fromisoformat(timestamp_str)
                age_seconds = (datetime.now() - heartbeat_time).total_seconds()
                result["heartbeat_exists"] = True
                result["heartbeat_age_seconds"] = round(age_seconds, 1)
                
                # Heartbeat should be stale if system is not running (expected)
                if age_seconds > 300:  # 5 minutes
                    logger.info(f"ℹ️  Heartbeat is stale ({age_seconds:.0f} seconds old) - Expected if system not running")
        except Exception as e:
            logger.warning(f"⚠️  Could not read heartbeat: {e}")
    
    return result["status"] in ["PASS", "WARN"], result


def check_configuration() -> Tuple[bool, Dict[str, Any]]:
    """Check configuration validity."""
    errors = []
    warnings = []
    
    # Check LIVE_TRADING_ENABLED
    try:
        from config.live_trade_config import LIVE_TRADING_ENABLED, USE_LIVE_EXECUTION_ENGINE
        if LIVE_TRADING_ENABLED:
            errors.append("LIVE_TRADING_ENABLED is True (must be False)")
        if USE_LIVE_EXECUTION_ENGINE:
            errors.append("USE_LIVE_EXECUTION_ENGINE is True (must be False)")
    except ImportError as e:
        warnings.append(f"Cannot import live_trade_config: {e}")
    except Exception as e:
        warnings.append(f"Error reading live_trade_config: {e}")
    
    # Check automation config
    try:
        from core.engine.angel_automation_config import AUTOMATION_CONFIG
        if AUTOMATION_CONFIG.auto_execute_trades:
            errors.append("AUTOMATION_CONFIG.auto_execute_trades is True (must be False)")
    except ImportError as e:
        warnings.append(f"Cannot import automation_config: {e}")
    except Exception as e:
        warnings.append(f"Error reading automation_config: {e}")
    
    result = {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "warnings": warnings,
    }
    
    if errors:
        logger.error("❌ Configuration check FAILED:")
        for error in errors:
            logger.error(f"   - {error}")
    elif warnings:
        logger.warning("⚠️  Configuration check PASSED with warnings:")
        for warning in warnings:
            logger.warning(f"   - {warning}")
    else:
        logger.info("✅ Configuration check PASSED: All safety flags correct")
    
    return len(errors) == 0, result


def check_log_file_sizes(max_mb: float = 100.0) -> Tuple[bool, Dict[str, Any]]:
    """Check log file sizes."""
    large_files = []
    total_size_mb = 0
    
    if LOGS_DIR.exists():
        for log_file in LOGS_DIR.rglob("*.log"):
            try:
                size_mb = log_file.stat().st_size / (1024**2)
                total_size_mb += size_mb
                if size_mb > max_mb:
                    large_files.append({
                        "file": str(log_file.relative_to(PROJECT_ROOT)),
                        "size_mb": round(size_mb, 2),
                    })
            except Exception:
                pass
    
    result = {
        "status": "PASS" if not large_files else "WARN",
        "total_size_mb": round(total_size_mb, 2),
        "large_files": large_files,
        "max_mb": max_mb,
    }
    
    if large_files:
        logger.warning(f"⚠️  Log file size check WARN: {len(large_files)} file(s) > {max_mb} MB")
        for file_info in large_files:
            logger.warning(f"   - {file_info['file']}: {file_info['size_mb']} MB")
    else:
        logger.info(f"✅ Log file size check PASSED: Total {total_size_mb:.2f} MB")
    
    return True, result  # Not blocking, just warning


def check_signal_files() -> Tuple[bool, Dict[str, Any]]:
    """Check signal files exist and have data."""
    signals_file = PROJECT_ROOT / "storage" / "live" / "angel_index_ai_signals.csv"
    curated_file = PROJECT_ROOT / "storage" / "live" / "angel_index_ai_signals_curated.csv"
    
    result = {
        "status": "PASS",
        "signals_file_exists": False,
        "signals_file_rows": 0,
        "curated_file_exists": False,
        "curated_file_rows": 0,
    }
    
    # Check signals file
    if signals_file.exists():
        try:
            import pandas as pd
            df = pd.read_csv(signals_file, engine="python", on_bad_lines="skip")
            result["signals_file_exists"] = True
            result["signals_file_rows"] = len(df)
        except Exception as e:
            logger.warning(f"⚠️  Could not read signals file: {e}")
    else:
        result["status"] = "WARN"
        logger.warning("⚠️  Signals file not found (expected if first run)")
    
    # Check curated file
    if curated_file.exists():
        try:
            import pandas as pd
            df = pd.read_csv(curated_file, engine="python", on_bad_lines="skip")
            result["curated_file_exists"] = True
            result["curated_file_rows"] = len(df)
        except Exception as e:
            logger.warning(f"⚠️  Could not read curated file: {e}")
    else:
        result["status"] = "WARN"
        logger.warning("⚠️  Curated file not found (expected if first run)")
    
    if result["status"] == "PASS":
        logger.info(f"✅ Signal files check PASSED: {result['signals_file_rows']} signals, {result['curated_file_rows']} curated")
    
    return True, result  # Not blocking, just informational


def run_all_checks() -> Dict[str, Any]:
    """Run all health checks."""
    logger.info("=" * 80)
    logger.info("SYSTEM3 PRE-MARKET HEALTH CHECK")
    logger.info("=" * 80)
    logger.info(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 80)
    logger.info("")
    
    checks = {
        "disk_space": check_disk_space(),
        "internet": check_internet_connectivity(),
        "critical_files": check_critical_files(),
        "python_version": check_python_version(),
        "dependencies": check_dependencies(),
        "last_shutdown": check_last_shutdown_clean(),
        "configuration": check_configuration(),
        "log_files": check_log_file_sizes(),
        "signal_files": check_signal_files(),
    }
    
    # Compile results
    results = {}
    all_passed = True
    blocking_failures = []
    warnings = []
    
    for check_name, (passed, result) in checks.items():
        results[check_name] = result
        if not passed:
            all_passed = False
            # Some checks are non-blocking (warnings)
            if check_name in ["log_files", "signal_files"]:
                warnings.append(check_name)
            else:
                blocking_failures.append(check_name)
    
    # Print summary
    logger.info("")
    logger.info("=" * 80)
    logger.info("HEALTH CHECK SUMMARY")
    logger.info("=" * 80)
    
    for check_name, (passed, result) in checks.items():
        status_icon = "✅" if passed else "❌" if check_name in blocking_failures else "⚠️"
        logger.info(f"{status_icon} {check_name.replace('_', ' ').title()}: {result.get('status', 'UNKNOWN')}")
    
    logger.info("")
    logger.info("=" * 80)
    
    if all_passed or len(blocking_failures) == 0:
        if warnings:
            logger.info("✅ HEALTH CHECK PASSED (with warnings)")
            logger.info("⚠️  Non-blocking warnings present - system ready but review recommended")
        else:
            logger.info("✅ HEALTH CHECK PASSED - SYSTEM READY FOR MARKET")
    else:
        logger.error("❌ HEALTH CHECK FAILED - FIX ISSUES BEFORE STARTING")
        logger.error(f"Blocking failures: {', '.join(blocking_failures)}")
    
    logger.info("=" * 80)
    
    # Save results
    results_file = PROJECT_ROOT / "docs" / f"premarket_health_check_{datetime.now().strftime('%Y%m%d')}.json"
    results_file.parent.mkdir(parents=True, exist_ok=True)
    
    summary = {
        "timestamp": datetime.now().isoformat(),
        "overall_status": "PASS" if (all_passed or len(blocking_failures) == 0) else "FAIL",
        "blocking_failures": blocking_failures,
        "warnings": warnings,
        "checks": results,
    }
    
    with results_file.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, default=str)
    
    logger.info(f"✅ Results saved to: {results_file}")
    
    return summary


def main():
    """Main entry point."""
    try:
        summary = run_all_checks()
        
        # Exit code: 0 = pass, 1 = fail
        if summary["overall_status"] == "PASS":
            return 0
        else:
            return 1
    except Exception as e:
        logger.error(f"❌ Health check crashed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(main())

