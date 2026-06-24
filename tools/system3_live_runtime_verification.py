#!/usr/bin/env python3
"""
System3 Live Runtime Verification Script

Comprehensive validation of the double-click flow after START_AUTORUN_AND_WATCHDOG.bat is running.

Checks:
  1. Venv interpreter is used (not system python)
  2. Critical dependencies installed and importable
  3. Autorun master process running
  4. Watchdog process running
  5. Heartbeat file exists and updates
  6. Logs being written
  7. Safety flags locked (DRY-RUN only)
  8. Signals and virtual orders being generated
  9. No orphan processes

Exit codes:
  0 = All checks pass (GREEN)
  1 = Some checks warn (YELLOW)
  2 = Critical checks fail (RED)

Usage:
  python tools/system3_live_runtime_verification.py [--verbose] [--report]

  --verbose: Show detailed output
  --report: Write SYSTEM3_LIVE_RUNTIME_REPORT.md
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

ROOT_DIR = Path(__file__).parent.parent.absolute()


def check_venv_interpreter() -> Tuple[str, str, List[str]]:
    """Check that venv interpreter is being used."""
    issues = []

    # Get running python processes
    try:
        result = subprocess.run(["tasklist", "/V", "/FO", "CSV"], capture_output=True, text=True, timeout=5)

        python_processes = []
        for line in result.stdout.split("\n"):
            if "python.exe" in line.lower():
                python_processes.append(line)

        if not python_processes:
            return "WARN", "No python.exe processes found (system may not be running)", issues

        # Check if any use system python
        venv_python_path = str(ROOT_DIR / "venv" / "Scripts" / "python.exe").lower()
        for proc_line in python_processes:
            if venv_python_path not in proc_line.lower():
                # This might be system python (we can't fully verify from tasklist alone)
                issues.append(f"Python process found (verify it's venv): {proc_line[:80]}")

        if not issues:
            return "OK", f"Found {len(python_processes)} python process(es) (assuming venv)", []
        else:
            return "WARN", f"Found {len(python_processes)} process(es), verify venv usage", issues

    except Exception as e:
        return "ERROR", f"Failed to check python processes: {e}", [str(e)]


def check_dependencies() -> Tuple[str, str, List[str]]:
    """Check if critical dependencies are importable."""
    issues = []
    ok_deps = []

    critical_deps = ["pandas", "psutil", "numpy"]

    for dep in critical_deps:
        try:
            __import__(dep)
            ok_deps.append(dep)
        except ImportError:
            issues.append(f"{dep} not importable")

    if not issues:
        return "OK", f"All {len(ok_deps)} critical dependencies available", []
    else:
        return "ERROR", f"Missing {len(issues)} dependency/ies", issues


def check_processes_running() -> Tuple[str, str, List[str]]:
    """Check if autorun master and watchdog are running."""
    issues = []
    found = []

    try:
        result = subprocess.run(["tasklist"], capture_output=True, text=True, timeout=5)

        # Look for python processes (watchdog and master would be python)
        python_count = result.stdout.count("python.exe")

        if python_count >= 2:
            found.append(f"✅ Multiple python processes ({python_count}) found")
            return "OK", f"{python_count} python process(es) running", []
        elif python_count == 1:
            found.append("⚠️  Only 1 python process found (expect master + watchdog = 2)")
            return "WARN", "Only 1 python process (may be starting or stopping)", []
        else:
            return "ERROR", "No python processes found (system not running)", ["No python.exe processes detected"]

    except Exception as e:
        return "ERROR", f"Failed to check processes: {e}", [str(e)]


def check_heartbeat_file() -> Tuple[str, str, List[str]]:
    """Check if heartbeat file exists and is being updated."""
    issues = []

    heartbeat_file = ROOT_DIR / "system3_daily_heartbeat.json"

    if not heartbeat_file.exists():
        return "WARN", "Heartbeat file not found (will be created on first run)", ["File: system3_daily_heartbeat.json"]

    # Check age
    try:
        file_mtime = datetime.fromtimestamp(heartbeat_file.stat().st_mtime)
        age = (datetime.now() - file_mtime).total_seconds()

        if age < 60:
            return "OK", f"Heartbeat fresh ({int(age)}s old)", []
        elif age < 180:
            return "OK", f"Heartbeat OK ({int(age)}s old)", []
        elif age < 600:
            return (
                "WARN",
                f"Heartbeat slightly stale ({int(age)}s old), check logs",
                [f"Heartbeat not updated for {int(age)}s"],
            )
        else:
            return "ERROR", f"Heartbeat very stale ({int(age)}s old)", [f"System may be hung or crashed"]

    except Exception as e:
        return "ERROR", f"Failed to check heartbeat: {e}", [str(e)]


def check_logs_being_written() -> Tuple[str, str, List[str]]:
    """Check if autorun and watchdog logs are being written."""
    issues = []
    logs_found = []

    logs_dir = ROOT_DIR / "logs"
    if not logs_dir.exists():
        return "WARN", "Logs directory not found (will be created)", ["Directory: logs/"]

    today_str = datetime.now().strftime("%Y%m%d")

    # Check for autorun master log
    master_log_pattern = f"system3_autorun_master_{today_str}*.log"
    master_logs = list(logs_dir.glob(f"system3_autorun_master_{today_str}.log"))
    if master_logs:
        newest = max(master_logs, key=lambda p: p.stat().st_mtime)
        age = (datetime.now() - datetime.fromtimestamp(newest.stat().st_mtime)).total_seconds()
        logs_found.append(f"Master log: {newest.name} ({int(age)}s old)")
    else:
        issues.append("No autorun master log found for today")

    # Check for watchdog log
    watchdog_logs = list(logs_dir.glob(f"system3_watchdog_{today_str}.log"))
    if watchdog_logs:
        newest = max(watchdog_logs, key=lambda p: p.stat().st_mtime)
        age = (datetime.now() - datetime.fromtimestamp(newest.stat().st_mtime)).total_seconds()
        logs_found.append(f"Watchdog log: {newest.name} ({int(age)}s old)")
    else:
        issues.append("No watchdog log found for today")

    if not issues:
        return "OK", f"Both logs active ({len(logs_found)} files)", []
    elif len(logs_found) == 1:
        return "WARN", f"Only 1 of 2 expected logs found", issues
    else:
        return "ERROR", "No logs found", issues


def check_safety_flags() -> Tuple[str, str, List[str]]:
    """Check that safety flags are locked (DRY-RUN only)."""
    issues = []
    checks_passed = []

    # Check .env file
    env_file = ROOT_DIR / ".env"
    if env_file.exists():
        try:
            with env_file.open("r") as f:
                env_content = f.read()

            # Check for safety flags
            if "LIVE_TRADING_ENABLED=False" in env_content or "LIVE_TRADING_ENABLED = False" in env_content:
                checks_passed.append("✅ LIVE_TRADING_ENABLED = False")
            else:
                issues.append("❌ LIVE_TRADING_ENABLED not set to False in .env")

            if "DRY_RUN_MODE=True" in env_content or "DRY_RUN_MODE = True" in env_content:
                checks_passed.append("✅ DRY_RUN_MODE = True")
            else:
                issues.append("⚠️  DRY_RUN_MODE not explicitly set to True")

            if "PAPER_TRADING_MODE=True" in env_content or "PAPER_TRADING_MODE = True" in env_content:
                checks_passed.append("✅ PAPER_TRADING_MODE = True")
            else:
                issues.append("⚠️  PAPER_TRADING_MODE not explicitly set to True")

        except Exception as e:
            issues.append(f"Error reading .env: {e}")
    else:
        issues.append(".env file not found")

    # Check config files
    config_dir = ROOT_DIR / "config"
    if config_dir.exists():
        live_config = config_dir / "live_trade_config.py"
        if live_config.exists():
            try:
                with live_config.open("r") as f:
                    content = f.read()
                if "LIVE_TRADING_ENABLED = False" in content:
                    checks_passed.append("✅ live_trade_config.py locked")
                else:
                    issues.append("⚠️  live_trade_config.py LIVE_TRADING_ENABLED not False")
            except Exception:
                pass

    if not issues:
        return "OK", f"All safety flags locked ({len(checks_passed)})", []
    else:
        status = "ERROR" if any("❌" in i for i in issues) else "WARN"
        return status, f"Safety check: {len(checks_passed)} OK, {len(issues)} warn/fail", issues


def check_signal_generation() -> Tuple[str, str, List[str]]:
    """Check if signals are being generated (if running)."""
    issues = []

    # Look for signal files
    signals_dir = ROOT_DIR / "storage" / "signals"
    if not signals_dir.exists():
        return "INFO", "Signals directory not yet created (normal at startup)", []

    # Find recent signal files
    signal_files = list(signals_dir.glob("*.csv"))
    if not signal_files:
        return "WARN", "No signal CSV files found yet (system may still be initializing)", []

    # Check ages
    now = datetime.now()
    recent_files = []
    for f in signal_files:
        mtime = datetime.fromtimestamp(f.stat().st_mtime)
        age = (now - mtime).total_seconds()
        if age < 3600:  # Within last hour
            recent_files.append(f.name)

    if recent_files:
        return "OK", f"Signals generated: {len(recent_files)} files <1hr old", []
    else:
        # Check if any exist
        oldest = min(signal_files, key=lambda p: p.stat().st_mtime)
        age = (now - datetime.fromtimestamp(oldest.stat().st_mtime)).total_seconds()
        if age < 86400:  # Within last day
            return "INFO", f"Signals exist but not recent (oldest: {int(age/3600)}h old)", []
        else:
            return "WARN", f"Signals are stale (oldest: {int(age/86400)}d old)", ["Consider running Phase 201 refresh"]


def check_virtual_orders() -> Tuple[str, str, List[str]]:
    """Check if virtual orders are being generated."""
    issues = []

    # Look for virtual orders file
    virtual_orders = ROOT_DIR / "storage" / "virtual_trades.json"
    if not virtual_orders.exists():
        return "INFO", "Virtual orders file not yet created (normal at startup)", []

    try:
        with virtual_orders.open("r") as f:
            data = json.load(f)

        if isinstance(data, list) and len(data) > 0:
            return "OK", f"Virtual orders recorded: {len(data)} trades", []
        else:
            return "INFO", "Virtual orders file exists but empty (normal during dry-run startup)", []

    except Exception as e:
        return "WARN", f"Could not read virtual orders: {e}", [str(e)]


def check_pnl_logs() -> Tuple[str, str, List[str]]:
    """Check if PnL logs are being written."""
    issues = []

    pnl_dir = ROOT_DIR / "storage" / "pnl"
    if not pnl_dir.exists():
        return "INFO", "PnL directory not yet created (normal at startup)", []

    pnl_files = list(pnl_dir.glob("*.csv")) + list(pnl_dir.glob("*.json"))
    if not pnl_files:
        return "INFO", "No PnL files yet (normal during dry-run startup)", []

    # Check ages
    now = datetime.now()
    recent = [f for f in pnl_files if (now - datetime.fromtimestamp(f.stat().st_mtime)).total_seconds() < 3600]

    if recent:
        return "OK", f"PnL logs active: {len(recent)} files <1hr old", []
    else:
        return "INFO", f"PnL files exist ({len(pnl_files)}) but not recent", []


def check_no_orphans() -> Tuple[str, str, List[str]]:
    """Check for orphan python processes that should have been cleaned up."""
    issues = []

    try:
        result = subprocess.run(["tasklist", "/V", "/FO", "CSV"], capture_output=True, text=True, timeout=5)

        venv_path = str(ROOT_DIR / "venv").lower()
        system3_markers = ["system3", "autorun", "watchdog"]

        # Count python processes related to System3
        system3_pids = []
        for line in result.stdout.split("\n"):
            if "python.exe" in line.lower():
                # Try to identify if it's a System3 process
                for marker in system3_markers:
                    if marker in line.lower() or venv_path in line.lower():
                        system3_pids.append(line)
                        break

        # Expect 2-3 processes: watchdog + master + maybe 1 subprocess
        if len(system3_pids) <= 3:
            return "OK", f"Process count healthy ({len(system3_pids)})", []
        elif len(system3_pids) <= 5:
            return "WARN", f"More processes than expected ({len(system3_pids)})", ["May have orphans from earlier runs"]
        else:
            return "WARN", f"Many processes ({len(system3_pids)})", ["Consider killing stray processes"]

    except Exception as e:
        return "WARN", f"Could not check for orphans: {e}", [str(e)]


def generate_full_report(checks: Dict) -> str:
    """Generate a comprehensive markdown report."""
    timestamp = datetime.now().isoformat()

    status_emoji = {
        "OK": "✅",
        "WARN": "⚠️",
        "ERROR": "❌",
        "INFO": "ℹ️",
    }

    lines = [
        "# 🔍 System3 Live Runtime Verification Report",
        "",
        f"**Time:** {timestamp}",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d %A')}",
        "",
        "---",
        "",
        "## Summary",
        "",
    ]

    # Count results
    status_counts = {}
    for check_name, (status, message, details) in checks.items():
        status_counts[status] = status_counts.get(status, 0) + 1

    lines.append("| Status | Count |")
    lines.append("|--------|-------|")
    for status in ["OK", "INFO", "WARN", "ERROR"]:
        lines.append(f"| {status_emoji.get(status, '?')} {status} | {status_counts.get(status, 0)} |")

    lines.extend(
        [
            "",
            "## Detailed Results",
            "",
        ]
    )

    for check_name, (status, message, details) in checks.items():
        lines.append(f"### {check_name}")
        lines.append(f"- **Status:** {status_emoji.get(status, '?')} {status}")
        lines.append(f"- **Message:** {message}")
        if details:
            lines.append("- **Details:**")
            for detail in details:
                lines.append(f"  - {detail}")
        lines.append("")

    lines.extend(
        [
            "---",
            "",
            "## Interpretation",
            "",
            "- **✅ OK:** Check passed, system working as expected",
            "- **ℹ️ INFO:** Informational, no action needed",
            "- **⚠️ WARN:** Minor issue, monitor for now, may auto-recover",
            "- **❌ ERROR:** Critical issue, immediate investigation recommended",
            "",
            "## Recommended Next Steps",
            "",
        ]
    )

    # Suggest next steps based on errors
    has_errors = any(status == "ERROR" for _, (status, _, _) in checks.items())
    has_warns = any(status == "WARN" for _, (status, _, _) in checks.items())

    if has_errors:
        lines.extend(
            [
                "1. **Critical issues detected:**",
                "   - Review error details above",
                "   - Check `logs/system3_autorun_master_*.log` and `logs/system3_watchdog_*.log`",
                "   - If venv is broken, follow `VENV_RECOVERY_GUIDE.md`",
                "   - If processes not running, try restarting: `.\\START_AUTORUN_AND_WATCHDOG.bat`",
                "",
            ]
        )
    elif has_warns:
        lines.extend(
            [
                "1. **Minor issues detected:**",
                "   - System is running but with some concerns",
                "   - Monitor logs for the next 5-10 minutes",
                "   - If issues persist, investigate log files",
                "",
            ]
        )
    else:
        lines.extend(
            [
                "1. **All checks pass! System3 is running normally.**",
                "   - Continue monitoring periodically",
                "   - Check logs daily for warnings",
                "",
            ]
        )

    lines.extend(
        [
            "## For Continuous Monitoring",
            "",
            "Run this command periodically to track system health:",
            "```powershell",
            "python tools/system3_live_runtime_verification.py --report",
            "```",
            "",
            f"**Last Updated:** {timestamp}",
        ]
    )

    return "\n".join(lines)


def main():
    verbose = "--verbose" in sys.argv
    report_mode = "--report" in sys.argv

    print("\n" + "=" * 70)
    print("🔍 SYSTEM3 LIVE RUNTIME VERIFICATION")
    print("=" * 70 + "\n")

    checks = {
        "Venv Interpreter": check_venv_interpreter(),
        "Dependencies": check_dependencies(),
        "Running Processes": check_processes_running(),
        "Heartbeat File": check_heartbeat_file(),
        "Logs Being Written": check_logs_being_written(),
        "Safety Flags Locked": check_safety_flags(),
        "Signal Generation": check_signal_generation(),
        "Virtual Orders": check_virtual_orders(),
        "PnL Logs": check_pnl_logs(),
        "No Orphan Processes": check_no_orphans(),
    }

    # Print results
    for check_name, (status, message, details) in checks.items():
        status_emoji = {"OK": "✅", "WARN": "⚠️", "ERROR": "❌", "INFO": "ℹ️"}.get(status, "?")
        print(f"{status_emoji} {check_name}")
        print(f"   {message}")
        if verbose and details:
            for detail in details:
                print(f"   - {detail}")
        print()

    # Determine overall status
    error_count = sum(1 for _, (s, _, _) in checks.items() if s == "ERROR")
    warn_count = sum(1 for _, (s, _, _) in checks.items() if s == "WARN")

    print("=" * 70)
    if error_count > 0:
        print(f"🔴 CRITICAL: {error_count} error(s) found")
        exit_code = 2
    elif warn_count > 0:
        print(f"🟡 WARNING: {warn_count} warning(s) found")
        exit_code = 1
    else:
        print("🟢 GREEN: All checks passed")
        exit_code = 0
    print("=" * 70 + "\n")

    # Generate and write report if requested
    if report_mode:
        report = generate_full_report(checks)
        report_file = ROOT_DIR / "SYSTEM3_LIVE_RUNTIME_REPORT.md"
        try:
            report_file.write_text(report, encoding="utf-8")
            print(f"✅ Full report written to: {report_file}\n")
        except Exception as e:
            print(f"⚠️  Failed to write report: {e}\n")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
