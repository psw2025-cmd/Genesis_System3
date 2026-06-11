#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SYSTEM3 GLOBAL HEALTH SCAN

Read-only diagnostics. It will:
  1) Verify basic project structure and Python deps.
  2) Run the production pipeline (220 -> 221 -> 239) in DRY-RUN.
  3) Run Phase-E validators for one cycle.
  4) Load the latest JSON metrics and validator reports.
  5) Scan recent logs for ERROR / CRITICAL lines.
  6) Print a compact summary that you can paste back to me.

Run from project root (venv activated):
  (venv) PS C:\Genesis_System3> python system3_global_health_scan.py
"""

import os
import sys
import json
import glob
import subprocess
from datetime import datetime
from textwrap import indent

ROOT = os.path.dirname(os.path.abspath(__file__))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def run_cmd(cmd, timeout=600):
    """Run a command and return (code, stdout, stderr)."""
    try:
        proc = subprocess.run(
            cmd,
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
    except Exception as e:
        return -999, "", f"{type(e).__name__}: {e}"


def find_latest(pattern):
    """Return path to latest file matching pattern, or None."""
    paths = glob.glob(pattern)
    if not paths:
        return None
    return max(paths, key=os.path.getmtime)


def print_section(title):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


# ---------------------------------------------------------------------------
# 1) Basic structure and dependency check
# ---------------------------------------------------------------------------

def check_structure_and_deps():
    print_section("CHECK 1 - PROJECT STRUCTURE AND PYTHON DEPENDENCIES")

    print(f"Project root : {ROOT}")
    print(f"Python exe   : {sys.executable}")

    required_dirs = [
        "phases",
        "storage",
        "storage/live",
        "storage/live/meta",
        "storage/live/metrics",
        "logs",
        "config",
    ]

    missing_dirs = []
    for d in required_dirs:
        path = os.path.join(ROOT, d)
        if os.path.isdir(path):
            print(f"[OK]  Dir exists: {d}")
        else:
            print(f"[MISS] Dir missing: {d}")
            missing_dirs.append(d)

    print()
    print("Checking core Python packages (import test):")
    missing_mods = []
    errors = {}

    for mod in ["pandas", "numpy", "psutil", "xgboost", "sklearn"]:
        try:
            __import__(mod)
            print(f"[OK]  {mod}")
        except Exception as e:
            print(f"[FAIL] {mod} -> {type(e).__name__}: {e}")
            missing_mods.append(mod)
            errors[mod] = repr(e)

    deps_ok = not missing_mods
    if deps_ok:
        print("\nDependencies status: OK - all required modules import correctly.")
    else:
        print("\nDependencies status: WARNING - some modules failed to import.")
        print("Missing modules:", ", ".join(missing_mods))

    return {
        "dirs_missing": missing_dirs,
        "deps_ok": deps_ok,
        "missing_mods": missing_mods,
    }


# ---------------------------------------------------------------------------
# 2) Safety / live trading flags
# ---------------------------------------------------------------------------

def check_safety_flags():
    print_section("CHECK 2 - SAFETY AND LIVE TRADING FLAGS")

    env_flag = os.environ.get("SYSTEM3_LIVE_TRADING_ALLOWED")
    print(f"SYSTEM3_LIVE_TRADING_ALLOWED env : {env_flag!r}")

    live_blocked = not bool(env_flag)

    # Just look for presence of classic flags in config files if they exist.
    config_files = [
        "live_trade_config.py",
        "live_trade_config.json",
        "angel_automation_config.json",
        "system3_ultra_safety.json",
    ]

    for name in config_files:
        path = os.path.join(ROOT, name)
        if not os.path.exists(path):
            continue
        print(f"\nScanning config file: {name}")
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
            for flag in [
                "LIVE_TRADING_ENABLED",
                "USE_LIVE_EXECUTION_ENGINE",
                "AUTO_EXECUTE_TRADES",
                "PAPER_TRADING_MODE",
            ]:
                if flag in text:
                    print(f"  Found flag name: {flag}")
        except Exception as e:
            print(f"  Could not read file: {e}")

    if live_blocked:
        print("\nSafety status: OK - env guard blocks live trading.")
    else:
        print("\nSafety status: WARNING - env guard would allow live trading.")

    return {"live_blocked": live_blocked}


# ---------------------------------------------------------------------------
# 3) Run production pipeline (220 -> 221 -> 239)
# ---------------------------------------------------------------------------

def run_production_pipeline():
    print_section("CHECK 3 - PRODUCTION PIPELINE DRY-RUN (220 -> 221 -> 239)")

    script = os.path.join(ROOT, "system3_production_pipeline_clean.py")
    if not os.path.exists(script):
        print(f"[ERROR] Script not found: {script}")
        return {"ok": False, "exit_code": None}

    cmd = [sys.executable, script]
    code, out, err = run_cmd(cmd, timeout=600)

    print(f"Exit code: {code}")
    if out:
        print("\n--- PIPELINE STDOUT (last part) ---")
        # Only show last 40 lines to keep output usable
        lines = out.splitlines()
        snippet = "\n".join(lines[-40:])
        print(indent(snippet, "  "))
    if err:
        print("\n--- PIPELINE STDERR (last part) ---")
        lines = err.splitlines()
        snippet = "\n".join(lines[-40:])
        print(indent(snippet, "  "))

    ok = (code == 0)
    if ok:
        print("\nPipeline status: OK - completed without process error.")
    else:
        print("\nPipeline status: ERROR - non-zero exit code, inspect above.")

    return {"ok": ok, "exit_code": code}


# ---------------------------------------------------------------------------
# 4) Run Phase-E validators once
# ---------------------------------------------------------------------------

def run_phase_e_validators():
    print_section("CHECK 4 - PHASE-E VALIDATORS (ONE CYCLE)")

    script = os.path.join(ROOT, "phase_e_watchdog.py")
    if not os.path.exists(script):
        print(f"[WARN] phase_e_watchdog.py not found at {script}")
        return {"ok": False, "exit_code": None}

    cmd = [
        sys.executable,
        script,
        "--max-checks",
        "1",
        "--interval",
        "5",
        "--no-lock-venv",
        "--log-level",
        "INFO",
    ]

    code, out, err = run_cmd(cmd, timeout=300)

    print(f"Exit code: {code}")
    if out:
        print("\n--- VALIDATOR STDOUT (last part) ---")
        lines = out.splitlines()
        snippet = "\n".join(lines[-40:])
        print(indent(snippet, "  "))
    if err:
        print("\n--- VALIDATOR STDERR (last part) ---")
        lines = err.splitlines()
        snippet = "\n".join(lines[-40:])
        print(indent(snippet, "  "))

    ok = (code == 0)
    if ok:
        print("\nValidator status: OK - watchdog ran one cycle.")
    else:
        print("\nValidator status: WARNING - non-zero exit, check messages above.")

    return {"ok": ok, "exit_code": code}


# ---------------------------------------------------------------------------
# 5) Parse latest JSON metrics and validator files
# ---------------------------------------------------------------------------

def inspect_json_metrics():
    print_section("CHECK 5 - JSON METRICS AND VALIDATOR REPORTS")

    results = {}

    # 5.1 Pipeline execution report
    pattern = os.path.join(
        ROOT, "storage", "live", "meta", "pipeline_execution_report_*.json"
    )
    path = find_latest(pattern)
    if path:
        print(f"Latest pipeline execution report: {path}")
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Try to pull a few useful fields if they exist
            perf_alerts = data.get("performance_alerts")
            warnings = data.get("warnings")
            errors = data.get("errors")
            phases = data.get("phases_executed") or data.get("phases") or "?"
            print(f"  Phases executed   : {phases}")
            print(f"  Performance alerts: {perf_alerts}")
            print(f"  Warnings          : {warnings}")
            print(f"  Errors            : {errors}")
            results["pipeline_report"] = data
        except Exception as e:
            print(f"  [ERROR] Could not read JSON: {e}")
    else:
        print("No pipeline_execution_report_*.json found.")

    # 5.2 Merge key validation
    pattern = os.path.join(
        ROOT, "storage", "live", "metrics", "merge_key_validation_*.json"
    )
    path = find_latest(pattern)
    if path:
        print(f"\nLatest merge key validation report: {path}")
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            status = data.get("status")
            alignment = data.get("alignment_percent")
            issues = data.get("issues")
            print(f"  Status            : {status}")
            print(f"  Alignment percent : {alignment}")
            if issues:
                print("  Issues:")
                for name, info in issues.items():
                    print(f"    - {name}: {info}")
            results["merge_key_validation"] = data
        except Exception as e:
            print(f"  [ERROR] Could not read JSON: {e}")
    else:
        print("\nNo merge_key_validation_*.json found.")

    # 5.3 Timestamp validation
    pattern = os.path.join(
        ROOT, "storage", "live", "metrics", "timestamp_validation_*.json"
    )
    path = find_latest(pattern)
    if path:
        print(f"\nLatest timestamp validation report: {path}")
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            status = data.get("status")
            nat_rate = data.get("ts_nat_rate")
            print(f"  Status        : {status}")
            print(f"  ts NaT rate   : {nat_rate}")
            results["timestamp_validation"] = data
        except Exception as e:
            print(f"  [ERROR] Could not read JSON: {e}")
    else:
        print("\nNo timestamp_validation_*.json found.")

    # 5.4 Venv integrity
    pattern = os.path.join(
        ROOT, "storage", "live", "metrics", "venv_integrity_*.json"
    )
    path = find_latest(pattern)
    if path:
        print(f"\nLatest venv integrity report: {path}")
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            status = data.get("status")
            print(f"  Status: {status}")
            results["venv_integrity"] = data
        except Exception as e:
            print(f"  [ERROR] Could not read JSON: {e}")
    else:
        print("\nNo venv_integrity_*.json found.")

    return results


# ---------------------------------------------------------------------------
# 6) Scan logs for ERROR / CRITICAL
# ---------------------------------------------------------------------------

def scan_logs():
    print_section("CHECK 6 - LOG SCAN (ERROR / CRITICAL SUMMARY)")

    logs_dir = os.path.join(ROOT, "logs")
    if not os.path.isdir(logs_dir):
        print("Logs directory not found.")
        return {}

    summary = {}

    for path in glob.glob(os.path.join(logs_dir, "*.log")):
        name = os.path.basename(path)
        err_count = 0
        crit_count = 0
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    if "ERROR" in line:
                        err_count += 1
                    if "CRITICAL" in line:
                        crit_count += 1
        except Exception as e:
            print(f"[WARN] Could not read log {name}: {e}")
            continue

        if err_count or crit_count:
            print(f"{name}: ERROR={err_count}, CRITICAL={crit_count}")
        summary[name] = {"ERROR": err_count, "CRITICAL": crit_count}

    if not summary:
        print("No log files found.")

    return summary


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    print("# SYSTEM3 GLOBAL HEALTH SCAN")
    print(f"- Generated at: {datetime.now().isoformat(timespec='seconds')}")
    print(f"- Root        : {ROOT}")

    struct_info = check_structure_and_deps()
    safety_info = check_safety_flags()
    pipe_info = run_production_pipeline()
    validators_info = run_phase_e_validators()
    metrics_info = inspect_json_metrics()
    log_summary = scan_logs()

    print_section("OVERALL SUMMARY (COPY THIS PART FOR ME)")

    print(f"dirs_missing          : {struct_info['dirs_missing']}")
    print(f"deps_ok               : {struct_info['deps_ok']}")
    print(f"missing_mods          : {struct_info['missing_mods']}")
    print(f"live_blocked          : {safety_info['live_blocked']}")
    print(f"pipeline_ok           : {pipe_info['ok']} (exit_code={pipe_info['exit_code']})")
    print(
        f"validators_ok         : {validators_info['ok']} "
        f"(exit_code={validators_info['exit_code']})"
    )

    # Try to pull a couple of key metrics if they exist
    mk = metrics_info.get("merge_key_validation") or {}
    tv = metrics_info.get("timestamp_validation") or {}
    pipe_rep = metrics_info.get("pipeline_report") or {}

    print(f"merge_key_status      : {mk.get('status')}")
    print(f"merge_key_alignment   : {mk.get('alignment_percent')}")
    print(f"timestamp_status      : {tv.get('status')}")
    print(f"timestamp_nat_rate    : {tv.get('ts_nat_rate')}")
    print(f"pipeline_warnings     : {pipe_rep.get('warnings')}")
    print(f"pipeline_errors       : {pipe_rep.get('errors')}")

    # Show any logs that have errors
    logs_with_errors = {
        name: counts
        for name, counts in log_summary.items()
        if counts["ERROR"] or counts["CRITICAL"]
    }
    print(f"logs_with_errors      : {logs_with_errors}")

    print("\nNOTE:")
    print("- This script is read-only and safe for DRY-RUN.")
    print("- Send me the OVERALL SUMMARY block plus any suspicious sections above.")
    print("- With that I can design a precise patch script for remaining issues.")


if __name__ == "__main__":
    main()
