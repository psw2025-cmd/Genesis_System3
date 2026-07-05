#!/usr/bin/env python3
"""
System3 Watchdog Status Report Generator

Reads watchdog logs and state files to generate a status report.
Used during/after runtime to show:
  - Current master process status
  - Restart history
  - Heartbeat staleness
  - Health metrics
  - Overall system status (GREEN/YELLOW/RED)

Usage:
  python tools/system3_watchdog_status_reporter.py [--output WATCHDOG_RUNTIME_STATUS.md]
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple

ROOT_DIR = Path(__file__).parent.parent.absolute()
STATE_DIR = ROOT_DIR / "state"
LOGS_DIR = ROOT_DIR / "logs"
HEARTBEAT_FILE = ROOT_DIR / "system3_daily_heartbeat.json"
WATCHDOG_LOG_FILE = LOGS_DIR / f"system3_watchdog_{datetime.now().strftime('%Y%m%d')}.log"
MASTER_PID_FILE = STATE_DIR / "system3_master.pid"
WATCHDOG_PID_FILE = STATE_DIR / "system3_watchdog.pid"


def read_pid_file(path: Path) -> Optional[int]:
    """Read PID from JSON file."""
    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return int(data.get("pid"))
    except Exception:
        return None


def check_process_alive(pid: int) -> bool:
    """Check if a process with given PID is alive."""
    try:
        import psutil

        return psutil.pid_exists(pid)
    except Exception:
        return False


def read_heartbeat() -> Optional[Dict]:
    """Read the latest heartbeat file."""
    if not HEARTBEAT_FILE.exists():
        return None
    try:
        with HEARTBEAT_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def heartbeat_age_seconds() -> Optional[float]:
    """Get heartbeat age in seconds."""
    hb = read_heartbeat()
    if not hb:
        return None

    try:
        timestamp_str = (
            hb.get("_last_updated")
            or hb.get("timestamp")
            or (hb.get("system_info", {}) if isinstance(hb, dict) else {}).get("timestamp")
        )
        if not timestamp_str:
            return None

        hb_time = datetime.fromisoformat(timestamp_str)
        return (datetime.now() - hb_time).total_seconds()
    except Exception:
        return None


def parse_watchdog_logs() -> Dict:
    """
    Parse watchdog logs to extract key events.
    Returns dict with restart count, last restart reason, etc.
    """
    result = {
        "restarts_today": 0,
        "last_restart_reason": "none",
        "last_restart_time": None,
        "warn_count": 0,
        "error_count": 0,
        "latest_status_line": None,
    }

    if not WATCHDOG_LOG_FILE.exists():
        return result

    try:
        with WATCHDOG_LOG_FILE.open("r", encoding="utf-8") as f:
            lines = f.readlines()

        for line in reversed(lines):  # Read from end
            if "Master restart successful" in line:
                result["restarts_today"] += 1
                if not result["last_restart_time"]:
                    # Extract timestamp from log line
                    try:
                        result["last_restart_time"] = line.split(" ")[0:2]
                    except Exception:
                        pass

            if "MASTER_SILENT_HANG" in line:
                if not result["last_restart_reason"]:
                    result["last_restart_reason"] = "silent hang (stale heartbeat + idle CPU)"

            if "Heartbeat stale" in line and "while master running" in line:
                if not result["last_restart_reason"]:
                    result["last_restart_reason"] = "stale heartbeat while running"

            if "[WARNING]" in line or "WARNING" in line:
                result["warn_count"] += 1

            if "[ERROR]" in line or "ERROR" in line:
                result["error_count"] += 1

            if "STATUS ts=" in line and not result["latest_status_line"]:
                result["latest_status_line"] = line.strip()

    except Exception as e:
        pass

    return result


def determine_status() -> Tuple[str, str]:
    """
    Determine overall system status: GREEN / YELLOW / RED
    Returns (status, reason)
    """
    hb_age = heartbeat_age_seconds()
    master_pid = read_pid_file(MASTER_PID_FILE)
    watchdog_pid = read_pid_file(WATCHDOG_PID_FILE)

    master_alive = check_process_alive(master_pid) if master_pid else False
    watchdog_alive = check_process_alive(watchdog_pid) if watchdog_pid else False

    # RED: Master not running or heartbeat very stale
    if not master_alive and hb_age and hb_age < 600:  # Master stopped recently
        return "RED", "Master not running and heartbeat recent (possible crash)"

    if hb_age and hb_age > 300:  # Heartbeat stale for >5 min
        return "YELLOW", f"Heartbeat stale for {int(hb_age)}s (>5 min)"

    if not watchdog_alive:
        return "YELLOW", "Watchdog not running (expected after market close)"

    if hb_age and hb_age > 120:  # Heartbeat stale for >2 min
        return "YELLOW", f"Heartbeat slightly stale ({int(hb_age)}s)"

    # GREEN: Everything nominal
    return "GREEN", "System running normally"


def generate_report() -> str:
    """Generate a markdown status report."""
    hb = read_heartbeat()
    hb_age = heartbeat_age_seconds()
    master_pid = read_pid_file(MASTER_PID_FILE)
    watchdog_pid = read_pid_file(WATCHDOG_PID_FILE)
    master_alive = check_process_alive(master_pid) if master_pid else False
    watchdog_alive = check_process_alive(watchdog_pid) if watchdog_pid else False
    log_data = parse_watchdog_logs()
    status, reason = determine_status()

    status_emoji = {"GREEN": "🟢", "YELLOW": "🟡", "RED": "🔴"}.get(status, "❓")

    lines = [
        "# 🔍 System3 Watchdog Runtime Status",
        "",
        f"**Report Time:** {datetime.now().isoformat()}",
        f"**Overall Status:** {status_emoji} **{status}** - {reason}",
        "",
        "---",
        "",
        "## Process Status",
        "",
        f"| Process | PID | Status | Last Update |",
        f"|---------|-----|--------|-------------|",
        f"| Watchdog | {watchdog_pid or 'none'} | {'✅ Running' if watchdog_alive else '⏹️ Stopped'} | {log_data.get('latest_status_line', 'N/A')[:50] if log_data.get('latest_status_line') else 'N/A'} |",
        f"| Master | {master_pid or 'none'} | {'✅ Running' if master_alive else '⏹️ Stopped'} | {(datetime.now()).isoformat()[:19]} |",
        "",
        "## Heartbeat Status",
        "",
    ]

    if hb_age is not None:
        hb_status = "✅ Fresh" if hb_age < 60 else "⚠️ Stale" if hb_age < 300 else "❌ Very Stale"
        lines.append(f"- **Age:** {hb_status} - {int(hb_age)} seconds old")
    else:
        lines.append("- **Age:** ❓ Unknown (no heartbeat file)")

    if hb and "system_info" in hb:
        sys_info = hb.get("system_info", {})
        lines.append(f"- **Mode:** {sys_info.get('mode', 'unknown')}")
        lines.append(f"- **Uptime:** {sys_info.get('uptime_seconds', 'unknown')} seconds")

    lines.extend(
        [
            "",
            "## Restart History (Today)",
            "",
            f"- **Total Restarts:** {log_data.get('restarts_today', 0)}",
            f"- **Last Restart Reason:** {log_data.get('last_restart_reason', 'none')}",
            f"- **Warnings in Logs:** {log_data.get('warn_count', 0)}",
            f"- **Errors in Logs:** {log_data.get('error_count', 0)}",
            "",
            "## Recent Logs",
            "",
        ]
    )

    # Try to extract last N log lines
    if WATCHDOG_LOG_FILE.exists():
        try:
            with WATCHDOG_LOG_FILE.open("r", encoding="utf-8") as f:
                log_lines = f.readlines()[-20:]  # Last 20 lines

            lines.append("```")
            lines.extend([line.rstrip() for line in log_lines])
            lines.append("```")
        except Exception:
            lines.append("(Unable to read log file)")
    else:
        lines.append("(No log file yet)")

    lines.extend(
        [
            "",
            "---",
            "",
            "## Interpretation Guide",
            "",
            "| Status | Meaning | Action |",
            "|--------|---------|--------|",
            "| 🟢 GREEN | System running normally | None - all good |",
            "| 🟡 YELLOW | Minor issues (stale HB, recent crash) | Monitor, may auto-recover |",
            "| 🔴 RED | Critical issue (master not running, HB very stale) | Check logs, may need restart |",
            "",
            f"**Last Generated:** {datetime.now().isoformat()}",
        ]
    )

    return "\n".join(lines)


def main():
    report = generate_report()

    # Print to console
    print(report)

    # Write to file
    output_file = ROOT_DIR / "WATCHDOG_RUNTIME_STATUS.md"
    try:
        output_file.write_text(report, encoding="utf-8")
        print(f"\n✅ Status report written to: {output_file}")
    except Exception as e:
        print(f"\n⚠️  Failed to write status report: {e}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
