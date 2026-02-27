"""
Runtime Python Consistency Audit

Safely inspects running System3-related Python processes and records whether
they are using the expected venv interpreter.

Outputs:
- state/runtime_python_process_audit.json
- RUNTIME_PYTHON_AUDIT.md (lightweight markdown summary)

DRY-RUN safe: read-only, no process termination.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

import psutil

ROOT_DIR = Path(__file__).resolve().parent.parent
VENV_PYTHON = ROOT_DIR / "venv" / "Scripts" / "python.exe"
STATE_DIR = ROOT_DIR / "state"
STATE_DIR.mkdir(parents=True, exist_ok=True)
JSON_OUT = STATE_DIR / "runtime_python_process_audit.json"
MD_OUT = ROOT_DIR / "RUNTIME_PYTHON_AUDIT.md"

TARGET_KEYWORDS = {
    "system3_autorun_master.py",
    "system3_watchdog.py",
    "system3_live_day_autopilot.py",
    "system3_live",
    "system3",
}


def _is_relevant(cmdline: List[str]) -> bool:
    joined = " ".join(cmdline).lower()
    return any(keyword.lower() in joined for keyword in TARGET_KEYWORDS)


def _collect() -> Dict[str, Any]:
    rows = []
    for proc in psutil.process_iter(["pid", "name", "cmdline", "exe", "cwd"]):
        try:
            cmdline = proc.info.get("cmdline") or []
            if not cmdline:
                continue
            if not _is_relevant(cmdline):
                continue
            exe = proc.info.get("exe") or ""
            cwd = proc.info.get("cwd") or ""
            rows.append(
                {
                    "pid": proc.info.get("pid"),
                    "exe": exe,
                    "cwd": cwd,
                    "cmdline": cmdline,
                    "is_venv": os.path.abspath(exe) == os.path.abspath(VENV_PYTHON),
                }
            )
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
        except Exception:
            continue

    return {
        "timestamp": datetime.now().isoformat(),
        "expected_python": str(VENV_PYTHON),
        "processes": rows,
    }


def _write_md(data: Dict[str, Any]):
    lines = []
    lines.append("# Runtime Python Audit")
    lines.append("")
    lines.append(f"Timestamp: {data['timestamp']}")
    lines.append(f"Expected venv python: {data['expected_python']}")
    lines.append("")
    lines.append("| PID | Executable | VENV? | CWD | Command |")
    lines.append("| --- | ---------- | ----- | --- | ------- |")
    if not data["processes"]:
        lines.append("| (none) | - | - | - | - |")
    for row in data["processes"]:
        lines.append(
            f"| {row['pid']} | {row['exe']} | {'YES' if row['is_venv'] else 'NO'} | "
            f"{row['cwd']} | {' '.join(row['cmdline'])} |"
        )

    MD_OUT.write_text("\n".join(lines), encoding="utf-8")


def main():
    data = _collect()
    JSON_OUT.write_text(json.dumps(data, indent=2), encoding="utf-8")
    _write_md(data)
    print(f"Wrote {JSON_OUT} and {MD_OUT}")


if __name__ == "__main__":
    main()
