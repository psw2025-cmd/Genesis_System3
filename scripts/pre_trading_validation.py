"""
Pre-Trading Validation - Complete System Check Before Paper Trading Starts
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

import pytz

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def check_python_environment():
    """Check Python version and venv."""
    issues = []
    try:
        import sys

        if sys.version_info < (3, 8):
            issues.append(f"Python version {sys.version_info.major}.{sys.version_info.minor} < 3.8")
        else:
            print(f"  [OK] Python version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    except Exception as e:
        issues.append(f"Python check failed: {e}")

    venv_path = ROOT_DIR / "venv" / "Scripts" / "python.exe"
    if not venv_path.exists():
        issues.append("Virtual environment not found")
    else:
        print(f"  [OK] Virtual environment found")

    return issues


def check_directories():
    """Check required directories exist."""
    issues = []
    required_dirs = [
        "outputs",
        "logs",
        "storage/live",
        "storage/meta",
        "src/trading",
        "src/storage",
        "src/sim",
        "src/validation",
    ]

    for dir_path in required_dirs:
        full_path = ROOT_DIR / dir_path
        if not full_path.exists():
            issues.append(f"Directory missing: {dir_path}")
        else:
            print(f"  [OK] Directory exists: {dir_path}")

    return issues


def check_configuration():
    """Check configuration files and flags."""
    issues = []

    # Check live_trade_config.py
    config_file = ROOT_DIR / "config" / "live_trade_config.py"
    if not config_file.exists():
        issues.append("config/live_trade_config.py not found")
    else:
        print(f"  [OK] Configuration file exists")

        # Check flags
        try:
            sys.path.insert(0, str(ROOT_DIR))
            from config.live_trade_config import (
                LIVE_TRADING_ENABLED,
                USE_LIVE_EXECUTION_ENGINE,
            )

            if LIVE_TRADING_ENABLED:
                issues.append("CRITICAL: LIVE_TRADING_ENABLED is True (should be False)")
            else:
                print(f"  [OK] LIVE_TRADING_ENABLED = False")

            if USE_LIVE_EXECUTION_ENGINE:
                issues.append("CRITICAL: USE_LIVE_EXECUTION_ENGINE is True (should be False)")
            else:
                print(f"  [OK] USE_LIVE_EXECUTION_ENGINE = False")
        except Exception as e:
            issues.append(f"Failed to check config flags: {e}")

    return issues


def check_base_data():
    """Check if base CSV data exists."""
    issues = []

    base_csv = ROOT_DIR / "storage" / "live" / "option_chain_ALL_INDICES.csv"
    if not base_csv.exists():
        issues.append("Base CSV not found: storage/live/option_chain_ALL_INDICES.csv")
        print(f"  [WARN] Base CSV not found - simulation will use default data")
    else:
        print(f"  [OK] Base CSV found: {base_csv.name}")
        try:
            import pandas as pd

            df = pd.read_csv(base_csv, nrows=1)
            print(f"  [OK] Base CSV is readable ({len(df.columns)} columns)")
        except Exception as e:
            issues.append(f"Base CSV not readable: {e}")

    return issues


def check_components():
    """Check if all required components can be imported."""
    issues = []

    components = [
        ("src.trading.paper_executor", "PaperExecutor"),
        ("src.trading.pnl_tracker", "PnLTracker"),
        ("src.storage.trade_history", "TradeHistoryStore"),
        ("src.sim.replay_engine", "ReplayEngine"),
        ("src.validation.qc_validator", "QCValidator"),
    ]

    # Check critical components
    for module_path, class_name in components:
        try:
            module = __import__(module_path, fromlist=[class_name])
            cls = getattr(module, class_name)
            print(f"  [OK] {class_name} can be imported")
        except Exception as e:
            issues.append(f"Cannot import {class_name}: {e}")

    # Check LiveChainRunner separately (may have optional dependencies)
    try:
        from scripts.run_live_chain import LiveChainRunner

        print(f"  [OK] LiveChainRunner can be imported")
    except Exception as e:
        # This is a warning, not critical (may fail if broker dependencies missing)
        print(f"  [WARN] LiveChainRunner import check skipped (may need broker setup): {str(e)[:50]}")

    return issues


def check_output_files():
    """Check if output files can be created."""
    issues = []

    outputs_dir = ROOT_DIR / "outputs"
    outputs_dir.mkdir(parents=True, exist_ok=True)

    test_files = [
        "pnl_live.json",
        "positions_live.json",
        "paper_trades_live.csv",
        "top_trade_signal.json",
        "qc_report_live.json",
    ]

    for file_name in test_files:
        test_path = outputs_dir / file_name
        try:
            # Try to write
            if file_name.endswith(".json"):
                json.dump({}, open(test_path, "w"))
            else:
                test_path.touch()
            print(f"  [OK] Can write: {file_name}")
            # Clean up test file if it was empty
            if test_path.stat().st_size == 0:
                test_path.unlink()
        except Exception as e:
            issues.append(f"Cannot write {file_name}: {e}")

    return issues


def check_previous_session():
    """Check if previous session data exists and handle it."""
    issues = []
    warnings = []

    pnl_file = ROOT_DIR / "outputs" / "pnl_live.json"
    trades_file = ROOT_DIR / "outputs" / "paper_trades_live.csv"

    if pnl_file.exists():
        try:
            pnl = json.load(open(pnl_file))
            session_time = pnl.get("timestamp_ist", "Unknown")
            warnings.append(f"Previous session PnL found (from {session_time})")
            print(f"  [INFO] Previous session data found - will be archived")
        except:
            warnings.append("Previous session PnL file exists but unreadable")

    if trades_file.exists():
        try:
            import pandas as pd

            df = pd.read_csv(trades_file)
            warnings.append(f"Previous session trades found ({len(df)} rows)")
            print(f"  [INFO] Previous session trades found - will be archived")
        except:
            warnings.append("Previous session trades file exists but unreadable")

    return issues, warnings


def main():
    """Run all pre-trading checks."""
    print("\n" + "=" * 80)
    print("  PRE-TRADING VALIDATION - COMPLETE SYSTEM CHECK")
    print("=" * 80 + "\n")

    all_issues = []
    all_warnings = []

    # Check 1: Python Environment
    print("[1/7] Checking Python Environment...")
    issues = check_python_environment()
    all_issues.extend(issues)
    print()

    # Check 2: Directories
    print("[2/7] Checking Required Directories...")
    issues = check_directories()
    all_issues.extend(issues)
    print()

    # Check 3: Configuration
    print("[3/7] Checking Configuration...")
    issues = check_configuration()
    all_issues.extend(issues)
    print()

    # Check 4: Base Data
    print("[4/7] Checking Base Data...")
    issues = check_base_data()
    all_issues.extend(issues)
    print()

    # Check 5: Components
    print("[5/7] Checking Components...")
    issues = check_components()
    all_issues.extend(issues)
    print()

    # Check 6: Output Files
    print("[6/7] Checking Output Files...")
    issues = check_output_files()
    all_issues.extend(issues)
    print()

    # Check 7: Previous Session
    print("[7/7] Checking Previous Session...")
    issues, warnings = check_previous_session()
    all_issues.extend(issues)
    all_warnings.extend(warnings)
    print()

    # Summary
    print("=" * 80)
    if all_issues:
        print(f"  [FAIL] Found {len(all_issues)} CRITICAL issues:")
        for i, issue in enumerate(all_issues, 1):
            print(f"    {i}. {issue}")
        print("\n  [ACTION REQUIRED] Fix issues before starting paper trading")
        return False
    else:
        print("  [OK] All pre-trading checks PASSED")
        if all_warnings:
            print(f"\n  [WARNINGS] {len(all_warnings)} warnings (non-critical):")
            for i, warn in enumerate(all_warnings, 1):
                print(f"    {i}. {warn}")
        return True
    print("=" * 80 + "\n")


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
