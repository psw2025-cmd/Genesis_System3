import json
import os
import subprocess
import sys
import textwrap
from datetime import datetime, timedelta, time, timezone
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

# ---------------------------------------------------------------------
# Helper: run a subprocess and capture output safely
# ---------------------------------------------------------------------

def run_cmd(cmd: List[str], cwd: Path) -> Tuple[int, str, str]:
    proc = subprocess.Popen(
        cmd,
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    out, err = proc.communicate()
    return proc.returncode, out.strip(), err.strip()


# ---------------------------------------------------------------------
# Section A: basic paths and environment
# ---------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent
VENV_PY = REPO_ROOT / "venv" / "Scripts" / "python.exe"
REPORT_PATH = REPO_ROOT / "SYSTEM3_TOMORROW_READINESS_REPORT.md"

def check_paths() -> Dict[str, Any]:
    results: Dict[str, Any] = {
        "repo_root": str(REPO_ROOT),
        "venv_python_exists": VENV_PY.is_file(),
        "venv_python_path": str(VENV_PY),
        "issues": [],
    }
    if not results["venv_python_exists"]:
        results["issues"].append("venv Python not found at venv\\Scripts\\python.exe")
    return results


# ---------------------------------------------------------------------
# Section B: venv / dependency sanity
# ---------------------------------------------------------------------

def check_venv_and_deps() -> Dict[str, Any]:
    info: Dict[str, Any] = {
        "ok": False,
        "exit_code": None,
        "stdout": "",
        "stderr": "",
        "issues": [],
    }
    if not VENV_PY.is_file():
        info["issues"].append("Venv python missing.")
        return info

    code = textwrap.dedent(
        """
        import importlib, sys
        mods = ["pandas", "numpy", "psutil", "xgboost", "sklearn"]
        missing = []
        for m in mods:
            try:
                importlib.import_module(m)
            except Exception:
                missing.append(m)
        if missing:
            print("MISSING:" + ",".join(missing))
            sys.exit(1)
        else:
            print("OK:all_deps_present")
        """
    )

    exit_code, out, err = run_cmd([str(VENV_PY), "-c", code], REPO_ROOT)
    info["exit_code"] = exit_code
    info["stdout"] = out
    info["stderr"] = err

    if exit_code == 0 and "OK:all_deps_present" in out:
        info["ok"] = True
    else:
        info["issues"].append("Some dependencies are missing or venv is broken.")
    return info


# ---------------------------------------------------------------------
# Section C: safety flags / live-trading guards
# ---------------------------------------------------------------------

def _load_json_if_exists(path: Path) -> Optional[Dict[str, Any]]:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def check_safety_flags() -> Dict[str, Any]:
    info: Dict[str, Any] = {
        "LIVE_TRADING_ENABLED": None,
        "USE_LIVE_EXECUTION_ENGINE": None,
        "AUTO_EXECUTE_TRADES": None,
        "PAPER_TRADING_MODE": None,
        "SYSTEM3_LIVE_TRADING_ALLOWED_env": os.getenv("SYSTEM3_LIVE_TRADING_ALLOWED"),
        "all_safe": False,
        "issues": [],
        "files_checked": [],
    }

    # Known config files – adjust paths if your project uses different ones
    safety_files = [
        REPO_ROOT / "config" / "system3_ultra_safety.json",
        REPO_ROOT / "config" / "angel_automation_config.json",
        REPO_ROOT / "core" / "config" / "live_trade_config.json",
    ]

    # Read JSON-like configs
    for path in safety_files:
        if not path.is_file():
            continue
        info["files_checked"].append(str(path))
        data = _load_json_if_exists(path)
        if not isinstance(data, dict):
            continue
        for k in ["LIVE_TRADING_ENABLED", "USE_LIVE_EXECUTION_ENGINE",
                  "AUTO_EXECUTE_TRADES", "PAPER_TRADING_MODE"]:
            if k in data and info.get(k) is None:
                info[k] = data[k]

    # Evaluate
    safe = True
    # Flags that must be explicitly False
    for flag in ["LIVE_TRADING_ENABLED", "USE_LIVE_EXECUTION_ENGINE",
                 "AUTO_EXECUTE_TRADES"]:
        val = info[flag]
        if val is None:
            info["issues"].append(f"{flag} not found in configs.")
        elif bool(val):
            safe = False
            info["issues"].append(f"{flag} is TRUE – must be FALSE for DRY-RUN.")
    # Flag that should be True
    if info["PAPER_TRADING_MODE"] is not None and not bool(info["PAPER_TRADING_MODE"]):
        safe = False
        info["issues"].append("PAPER_TRADING_MODE is False – expected True in DRY-RUN.")

    # Env guard (must be falsy / unset)
    env_val = info["SYSTEM3_LIVE_TRADING_ALLOWED_env"]
    if env_val not in (None, "", "0", "false", "False", "FALSE"):
        safe = False
        info["issues"].append(
            f"SYSTEM3_LIVE_TRADING_ALLOWED env is set to {env_val!r} – should be unset/false."
        )

    info["all_safe"] = safe
    return info


# ---------------------------------------------------------------------
# Section D: one-shot production pipeline dry-run
# ---------------------------------------------------------------------

def run_production_pipeline() -> Dict[str, Any]:
    """
    Runs system3_production_pipeline_clean.py (or fallback) once.
    Assumes it respects DRY-RUN guards already.
    """
    info: Dict[str, Any] = {
        "script": None,
        "exit_code": None,
        "stdout": "",
        "stderr": "",
        "ok": False,
        "issues": [],
    }

    candidates = [
        REPO_ROOT / "system3_production_pipeline_clean.py",
        REPO_ROOT / "system3_production_pipeline.py",
    ]
    script = next((p for p in candidates if p.is_file()), None)
    if script is None:
        info["issues"].append("No production pipeline script found.")
        return info

    info["script"] = str(script)
    exit_code, out, err = run_cmd(
        [str(VENV_PY), str(script), "--once"], REPO_ROOT
    )
    info["exit_code"] = exit_code
    info["stdout"] = out
    info["stderr"] = err

    if exit_code == 0:
        info["ok"] = True
    else:
        info["issues"].append("Production pipeline exited with non-zero status.")
    return info


# ---------------------------------------------------------------------
# Section E: continuous validators / Phase-E one-shot
# ---------------------------------------------------------------------

def run_validators_one_shot() -> Dict[str, Any]:
    info: Dict[str, Any] = {
        "script": None,
        "exit_code": None,
        "stdout": "",
        "stderr": "",
        "ok": False,
        "issues": [],
    }
    script = REPO_ROOT / "phase_e_watchdog.py"
    if not script.is_file():
        info["issues"].append("phase_e_watchdog.py not found – skipping validator run.")
        return info

    info["script"] = str(script)
    exit_code, out, err = run_cmd(
        [str(VENV_PY), str(script), "--one-shot"], REPO_ROOT
    )
    info["exit_code"] = exit_code
    info["stdout"] = out
    info["stderr"] = err
    if exit_code == 0:
        info["ok"] = True
    else:
        info["issues"].append("phase_e_watchdog one-shot exited with non-zero status.")
    return info


# ---------------------------------------------------------------------
# Section F: simulate tomorrow’s market-time behaviour
# ---------------------------------------------------------------------

def simulate_tomorrow_schedule() -> Dict[str, Any]:
    """
    Purely informational – does NOT start anything.
    Uses simple 09:15–15:30 IST rule.
    """
    ist = timezone(timedelta(hours=5, minutes=30))
    today_ist = datetime.now(ist).date()
    tomorrow = today_ist + timedelta(days=1)
    # Simple assumption: Mon–Fri trading, Sat/Sun closed
    weekday = tomorrow.weekday()  # 0=Mon
    is_trading_day = weekday < 5

    sample_times = [
        time(9, 10),
        time(9, 20),
        time(12, 0),
        time(15, 25),
        time(15, 35),
    ]

    windows = []
    for t in sample_times:
        dt = datetime.combine(tomorrow, t, tzinfo=ist)
        within = time(9, 15) <= t <= time(15, 30)
        windows.append(
            {
                "timestamp_ist": dt.isoformat(),
                "within_market_hours": within,
            }
        )

    return {
        "tomorrow_date_ist": str(tomorrow),
        "is_trading_day": is_trading_day,
        "samples": windows,
        "note": "Based on static 09:15–15:30 IST rule; real code may add holidays."
    }


# ---------------------------------------------------------------------
# Section G: write markdown report
# ---------------------------------------------------------------------

def write_report(
    paths_info: Dict[str, Any],
    venv_info: Dict[str, Any],
    safety_info: Dict[str, Any],
    pipeline_info: Dict[str, Any],
    validator_info: Dict[str, Any],
    schedule_info: Dict[str, Any],
) -> None:
    lines: List[str] = []
    now = datetime.now().isoformat(timespec="seconds")

    lines.append(f"# SYSTEM3 TOMORROW READINESS REPORT")
    lines.append("")
    lines.append(f"- Generated at: `{now}`")
    lines.append(f"- Repo root: `{paths_info['repo_root']}`")
    lines.append("")

    # Summary table
    def status(ok: bool) -> str:
        return "✅ OK" if ok else "⚠️ CHECK"

    overall_ok = (
        paths_info["venv_python_exists"]
        and venv_info.get("ok", False)
        and safety_info.get("all_safe", False)
        and pipeline_info.get("ok", False)
        and validator_info.get("ok", False)
    )

    lines.append("## Summary")
    lines.append("")
    lines.append("| Check | Status | Notes |")
    lines.append("|-------|--------|-------|")
    lines.append(
        f"| Paths & venv python | {status(paths_info['venv_python_exists'])} | {paths_info['venv_python_path']} |"
    )
    lines.append(
        f"| Venv dependencies  | {status(venv_info.get('ok', False))} | {venv_info.get('stdout','').replace('|','/')} |"
    )
    lines.append(
        f"| Safety flags / live-trading guard | {status(safety_info.get('all_safe', False))} | LIVE_TRADING_ENABLED={safety_info['LIVE_TRADING_ENABLED']} |"
    )
    lines.append(
        f"| Production pipeline dry-run | {status(pipeline_info.get('ok', False))} | script={pipeline_info.get('script')} |"
    )
    lines.append(
        f"| Continuous validators one-shot | {status(validator_info.get('ok', False))} | script={validator_info.get('script')} |"
    )
    lines.append(
        f"| Overall readiness | {status(overall_ok)} | DRY-RUN only, real-money still blocked |"
    )
    lines.append("")

    # Safety details
    lines.append("## Safety / Live-Trading Guards")
    lines.append("")
    lines.append("- `LIVE_TRADING_ENABLED`: "
                 f"`{safety_info['LIVE_TRADING_ENABLED']}`")
    lines.append("- `USE_LIVE_EXECUTION_ENGINE`: "
                 f"`{safety_info['USE_LIVE_EXECUTION_ENGINE']}`")
    lines.append("- `AUTO_EXECUTE_TRADES`: "
                 f"`{safety_info['AUTO_EXECUTE_TRADES']}`")
    lines.append("- `PAPER_TRADING_MODE`: "
                 f"`{safety_info['PAPER_TRADING_MODE']}`")
    lines.append(
        "- `SYSTEM3_LIVE_TRADING_ALLOWED` env: "
        f"`{safety_info['SYSTEM3_LIVE_TRADING_ALLOWED_env']}`"
    )
    if safety_info["issues"]:
        lines.append("")
        lines.append("**Safety issues detected:**")
        for issue in safety_info["issues"]:
            lines.append(f"- {issue}")
    else:
        lines.append("")
        lines.append("All safety checks passed; live trading remains blocked.")

    # Pipeline
    lines.append("")
    lines.append("## Production Pipeline Dry-Run")
    lines.append("")
    lines.append(f"- Script: `{pipeline_info.get('script')}`")
    lines.append(f"- Exit code: `{pipeline_info.get('exit_code')}`")
    if pipeline_info["stdout"]:
        lines.append("")
        lines.append("<details><summary>stdout</summary>")
        lines.append("")
        lines.append("```text")
        lines.append(pipeline_info["stdout"])
        lines.append("```")
        lines.append("</details>")
    if pipeline_info["stderr"]:
        lines.append("")
        lines.append("<details><summary>stderr</summary>")
        lines.append("")
        lines.append("```text")
        lines.append(pipeline_info["stderr"])
        lines.append("```")
        lines.append("</details>")
    if pipeline_info["issues"]:
        lines.append("")
        lines.append("**Pipeline issues:**")
        for issue in pipeline_info["issues"]:
            lines.append(f"- {issue}")

    # Validators
    lines.append("")
    lines.append("## Continuous Validators One-Shot")
    lines.append("")
    lines.append(f"- Script: `{validator_info.get('script')}`")
    lines.append(f"- Exit code: `{validator_info.get('exit_code')}`")
    if validator_info["stdout"]:
        lines.append("")
        lines.append("```text")
        lines.append(validator_info["stdout"])
        lines.append("```")
    if validator_info["stderr"]:
        lines.append("")
        lines.append("_stderr:_")
        lines.append("")
        lines.append("```text")
        lines.append(validator_info["stderr"])
        lines.append("```")
    if validator_info["issues"]:
        lines.append("")
        lines.append("**Validator issues:**")
        for issue in validator_info["issues"]:
            lines.append(f"- {issue}")

    # Tomorrow behaviour
    lines.append("")
    lines.append("## Tomorrow Market-Time Behaviour (Simulation)")
    lines.append("")
    lines.append(f"- Tomorrow (IST): `{schedule_info['tomorrow_date_ist']}`")
    lines.append(f"- Trading day (Mon–Fri): `{schedule_info['is_trading_day']}`")
    lines.append("")
    lines.append("| Time (IST) | Within 09:15–15:30? |")
    lines.append("|-----------|----------------------|")
    for s in schedule_info["samples"]:
        ts = s["timestamp_ist"]
        within = "Yes" if s["within_market_hours"] else "No"
        lines.append(f"| {ts} | {within} |")
    lines.append("")
    lines.append(f"> Note: {schedule_info['note']}")
    lines.append("")

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------
# main
# ---------------------------------------------------------------------

def main() -> None:
    paths_info = check_paths()
    venv_info = check_venv_and_deps()
    safety_info = check_safety_flags()
    pipeline_info = run_production_pipeline()
    validator_info = run_validators_one_shot()
    schedule_info = simulate_tomorrow_schedule()
    write_report(
        paths_info,
        venv_info,
        safety_info,
        pipeline_info,
        validator_info,
        schedule_info,
    )

    print("SYSTEM3_TOMORROW_READINESS_REPORT.md generated.")
    if not (paths_info["venv_python_exists"]
            and venv_info.get("ok", False)
            and safety_info.get("all_safe", False)
            and pipeline_info.get("ok", False)
            and validator_info.get("ok", False)):
        print("\nSome checks reported issues – see the markdown report for details.")
    else:
        print("\nAll verification checks passed for DRY-RUN operation tomorrow.")


if __name__ == "__main__":
    main()
