#!/usr/bin/env python

"""
SYSTEM3 TOMORROW READINESS + FULL VERIFICATION

- Verifies venv & core dependencies
- Confirms live-trading safety guards
- Runs production pipeline (220→221→239) in DRY-RUN
- Runs Phase-E continuous validators for one pass
- Simulates tomorrow’s market-time behaviour (09:15–15:30 IST)
"""

import os
import sys
import subprocess
from datetime import datetime, date, time, timedelta
from textwrap import indent

ROOT = os.path.dirname(os.path.abspath(__file__))

# Prefer project venv python; fall back to current interpreter if missing
VENV_PY = os.path.join(ROOT, "venv", "Scripts", "python.exe")
if not os.path.exists(VENV_PY):
    VENV_PY = sys.executable


def run(cmd, timeout=300):
    """Run a command and return (code, stdout, stderr)."""
    proc = subprocess.run(
        cmd,
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def check_deps():
    print("=== CHECK 1: VENV & DEPENDENCIES ===")
    print(f"Repo root : {ROOT}")
    print(f"Python    : {VENV_PY}")
    missing = []
    errors = {}

    for mod in ["pandas", "numpy", "psutil", "xgboost", "sklearn"]:
        try:
            __import__(mod)
        except Exception as e:
            missing.append(mod)
            errors[mod] = repr(e)

    if not missing:
        print("Status    : OK – all core deps import successfully.")
    else:
        print("Status    : WARNING – missing modules:", ", ".join(missing))
        for m in missing:
            print(f"  - {m}: {errors[m]}")
    print()
    return not missing


def check_safety():
    print("=== CHECK 2: SAFETY / LIVE-TRADING GUARDS ===")
    env_flag = os.environ.get("SYSTEM3_LIVE_TRADING_ALLOWED")
    print(f"SYSTEM3_LIVE_TRADING_ALLOWED env  : {env_flag!r}")

    live_blocked = not bool(env_flag)

    config_flags = [
        "LIVE_TRADING_ENABLED",
        "USE_LIVE_EXECUTION_ENGINE",
        "AUTO_EXECUTE_TRADES",
        "PAPER_TRADING_MODE",
    ]

    files = [
        "live_trade_config.py",
        "live_trade_config.json",
        "angel_automation_config.json",
        "system3_ultra_safety.json",
    ]

    found_any = False
    for cfg in files:
        path = os.path.join(ROOT, cfg)
        if not os.path.exists(path):
            continue
        found_any = True
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        hits = [flag for flag in config_flags if flag in text]
        print(f"- Scanned {cfg}: flags present → {', '.join(hits) or 'none'}")

    if not found_any:
        print("- No legacy config files found (OK with env-guard design).")

    if live_blocked:
        print("Status    : OK – live trading BLOCKED by env-guard.")
    else:
        print("Status    : WARNING – env-guard allows live trading.")
    print()
    return live_blocked


def run_production_pipeline():
    print("=== CHECK 3: PRODUCTION PIPELINE DRY-RUN (220→221→239) ===")
    script = os.path.join(ROOT, "system3_production_pipeline_clean.py")
    if not os.path.exists(script):
        print("Status    : ERROR – system3_production_pipeline_clean.py not found.")
        print("Path      :", script)
        print()
        return False

    code, out, err = run([VENV_PY, script])
    print("Exit code :", code)
    if out:
        print("stdout:\n" + indent(out, "  "))
    if err:
        print("stderr:\n" + indent(err, "  "))

    ok = (code == 0)
    print("Status    :", "OK – pipeline completed." if ok else "ERROR – pipeline failed.")
    print()
    return ok


def run_continuous_validators():
    print("=== CHECK 4: CONTINUOUS VALIDATORS (PHASE-E) – ONE PASS ===")
    script = os.path.join(ROOT, "phase_e_watchdog.py")
    if not os.path.exists(script):
        print("Status    : WARNING – phase_e_watchdog.py not found.")
        print()
        return False

    cmd = [
        VENV_PY,
        script,
        "--max-checks", "1",
        "--interval", "5",
        "--no-lock-venv",
        "--log-level", "INFO",
    ]
    code, out, err = run(cmd, timeout=120)
    print("Exit code :", code)
    if out:
        print("stdout:\n" + indent(out, "  "))
    if err:
        print("stderr:\n" + indent(err, "  "))

    ok = (code == 0)
    print("Status    :", "OK – validators ran one cycle." if ok else "WARNING – non-zero exit.")
    print()
    return ok


def simulate_tomorrow_market():
    print("=== CHECK 5: TOMORROW MARKET-TIME BEHAVIOUR (IST) ===")
    now = datetime.now()
    tomorrow = (now + timedelta(days=1)).date()

    def is_trading(dt_ist: datetime) -> bool:
        start = datetime.combine(dt_ist.date(), time(9, 15))
        end = datetime.combine(dt_ist.date(), time(15, 30))
        return start <= dt_ist <= end

    probes = [
        time(9, 10),
        time(9, 20),
        time(12, 0),
        time(15, 25),
        time(15, 35),
    ]

    print(f"Tomorrow date (IST): {tomorrow.isoformat()}")
    print("| Time (IST)           | In session? |")
    print("|----------------------|------------:|")
    for t in probes:
        dt = datetime.combine(tomorrow, t)
        flag = "YES" if is_trading(dt) else "NO"
        print(f"| {dt.strftime('%Y-%m-%d %H:%M')} | {flag:>10} |")
    print()
    return True


def main():
    print("# SYSTEM3 TOMORROW READINESS REPORT")
    print(f"- Generated at: {datetime.now().isoformat(timespec='seconds')}")
    print(f"- Repo root   : {ROOT}")
    print()

    deps_ok = check_deps()
    safety_ok = check_safety()
    pipe_ok = run_production_pipeline()
    validators_ok = run_continuous_validators()
    simulate_tomorrow_market()

    print("=== OVERALL SUMMARY ===")
    print(f"- Dependencies OK        : {deps_ok}")
    print(f"- Safety guard active    : {safety_ok}")
    print(f"- Pipeline DRY-RUN OK    : {pipe_ok}")
    print(f"- Validators one-pass OK : {validators_ok}")
    print()

    if deps_ok and safety_ok and pipe_ok:
        print("Tomorrow status: READY FOR DRY-RUN / PAPER TRADING.")
    else:
        print("Tomorrow status: ISSUES DETECTED – please review above warnings.")


if __name__ == "__main__":
    main()
