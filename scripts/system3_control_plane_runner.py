#!/usr/bin/env python3
"""
System3 Global Control Plane Runner.

Runs all read-only verification scripts and creates one consolidated status report.

This tool is intentionally safe:
- does not enable live trading
- does not place/modify/cancel orders
- does not edit .env, secrets, credentials, or broker token files
- does not patch runtime logic
- writes reports only under reports/latest and reports/history via child scripts

Outputs:
- reports/latest/system3_control_plane_status.json
- reports/latest/system3_control_plane_status.md
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

SCRIPT_SEQUENCE = [
    ("markdown_inventory", "scripts/system3_markdown_inventory.py"),
    ("option_visibility", "scripts/system3_option_visibility_audit.py"),
    ("model_accuracy", "scripts/system3_model_accuracy_tracker.py"),
    ("blocker_finder", "scripts/system3_blocker_finder.py"),
]

EXPECTED_REPORTS = [
    "reports/latest/markdown_inventory.json",
    "reports/latest/markdown_inventory.md",
    "reports/latest/documentation_contradictions.md",
    "reports/latest/option_strike_visibility.json",
    "reports/latest/option_strike_visibility.md",
    "reports/latest/model_accuracy_report.json",
    "reports/latest/model_accuracy_report.md",
    "reports/latest/system3_blocker_report.json",
    "reports/latest/system3_blocker_report.md",
]

FORBIDDEN_PATH_FRAGMENTS = [
    ".env",
    ".secrets",
    "secret",
    "token",
    "credential",
]


@dataclass
class ScriptRun:
    name: str
    path: str
    returncode: int
    status: str
    stdout_tail: str
    stderr_tail: str


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[1]


def tail(text: str, limit: int = 3500) -> str:
    return text[-limit:] if text else ""


def run_script(root: Path, name: str, script: str, api_base: Optional[str], timeout: int) -> ScriptRun:
    script_path = root / script
    if not script_path.exists():
        return ScriptRun(name, script, 127, "MISSING_SCRIPT", "", f"Missing: {script}")
    cmd = [sys.executable, str(script_path)]
    if api_base:
        cmd.extend(["--api-base", api_base])
    env = os.environ.copy()
    if api_base:
        env["SYSTEM3_API_BASE"] = api_base
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(root),
            text=True,
            capture_output=True,
            timeout=timeout,
            env=env,
        )
        status = "PASS" if proc.returncode == 0 else "FAIL"
        return ScriptRun(name, script, proc.returncode, status, tail(proc.stdout), tail(proc.stderr))
    except subprocess.TimeoutExpired as exc:
        return ScriptRun(name, script, 124, "TIMEOUT", tail(exc.stdout or ""), tail(exc.stderr or ""))
    except Exception as exc:
        return ScriptRun(name, script, 126, "ERROR", "", f"{type(exc).__name__}: {exc}")


def safe_load_json(path: Path) -> Optional[Any]:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return None


def build_report_status(root: Path) -> Dict[str, Any]:
    reports = {}
    for rel in EXPECTED_REPORTS:
        p = root / rel
        reports[rel] = {
            "exists": p.exists(),
            "size_bytes": p.stat().st_size if p.exists() else 0,
        }
    blocker_json = safe_load_json(root / "reports" / "latest" / "system3_blocker_report.json")
    markdown_json = safe_load_json(root / "reports" / "latest" / "markdown_inventory.json")
    option_json = safe_load_json(root / "reports" / "latest" / "option_strike_visibility.json")
    model_json = safe_load_json(root / "reports" / "latest" / "model_accuracy_report.json")
    return {
        "reports": reports,
        "blocker_summary": (blocker_json or {}).get("summary") if isinstance(blocker_json, dict) else None,
        "markdown_summary": (markdown_json or {}).get("summary") if isinstance(markdown_json, dict) else None,
        "option_summary": (option_json or {}).get("summary") if isinstance(option_json, dict) else None,
        "model_summary": (model_json or {}).get("summary") if isinstance(model_json, dict) else None,
    }


def detect_forbidden_runtime_change(root: Path) -> List[str]:
    # This runner does not edit source files. This check exists as a safety reminder if someone extends it later.
    touched = []
    latest = root / "reports" / "latest"
    if latest.exists():
        for p in latest.rglob("*"):
            rel = p.relative_to(root).as_posix().lower()
            if any(frag in rel for frag in FORBIDDEN_PATH_FRAGMENTS):
                touched.append(rel)
    return touched


def write_outputs(root: Path, data: Dict[str, Any]) -> None:
    reports = root / "reports" / "latest"
    reports.mkdir(parents=True, exist_ok=True)
    (reports / "system3_control_plane_status.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    lines = [
        "# System3 Global Control Plane Status",
        "",
        f"Generated UTC: `{data['generated_at_utc']}`",
        "",
        "## Overall Verdict",
        "",
        f"`{data['overall_verdict']}`",
        "",
        "## Script Runs",
        "",
        "| Script | Status | Return Code |",
        "|---|---:|---:|",
    ]
    for run in data["script_runs"]:
        lines.append(f"| `{run['path']}` | `{run['status']}` | `{run['returncode']}` |")
    lines.extend(["", "## Expected Reports", "", "| Report | Exists | Size Bytes |", "|---|---:|---:|"])
    for rel, info in data["report_status"]["reports"].items():
        lines.append(f"| `{rel}` | `{info['exists']}` | `{info['size_bytes']}` |")
    lines.extend(["", "## Summaries", ""])
    for key in ["markdown_summary", "option_summary", "model_summary", "blocker_summary"]:
        lines.append(f"### {key}")
        lines.append("")
        summary = data["report_status"].get(key)
        if summary is None:
            lines.append("- Not available")
        else:
            for k, v in summary.items():
                lines.append(f"- **{k}**: `{v}`")
        lines.append("")
    lines.extend(
        [
            "## Safety Statement",
            "",
            "This runner and its child scripts are intended to be read-only verification/reporting tools. They do not enable live trading, do not place orders, and do not touch credentials.",
            "",
            "## Next Rule",
            "",
            "Do not patch runtime logic until this status report, blocker report, option visibility report, and model accuracy report have been reviewed.",
        ]
    )
    (reports / "system3_control_plane_status.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run all System3 control-plane verification scripts")
    parser.add_argument("--root", default=None)
    parser.add_argument("--api-base", default=os.environ.get("SYSTEM3_API_BASE"))
    parser.add_argument("--timeout", type=int, default=60)
    args = parser.parse_args()

    root = Path(args.root).resolve() if args.root else repo_root_from_script()
    runs: List[ScriptRun] = []
    for name, script in SCRIPT_SEQUENCE:
        runs.append(run_script(root, name, script, args.api_base, args.timeout))

    report_status = build_report_status(root)
    forbidden = detect_forbidden_runtime_change(root)
    missing_reports = [rel for rel, info in report_status["reports"].items() if not info["exists"]]
    failed_runs = [r for r in runs if r.status not in {"PASS"}]

    if forbidden:
        verdict = "FAIL_FORBIDDEN_REPORT_PATH"
    elif failed_runs:
        verdict = "FAIL_SCRIPT_RUN"
    elif missing_reports:
        verdict = "FAIL_MISSING_REPORTS"
    else:
        verdict = "PASS_REPORTS_GENERATED_REVIEW_REQUIRED"

    data = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "root": str(root),
        "api_base": args.api_base,
        "overall_verdict": verdict,
        "script_runs": [asdict(r) for r in runs],
        "report_status": report_status,
        "forbidden_report_paths": forbidden,
        "missing_reports": missing_reports,
    }
    write_outputs(root, data)
    print("SYSTEM3_CONTROL_PLANE_RUNNER_COMPLETE")
    print(json.dumps({"overall_verdict": verdict, "missing_reports": missing_reports}, indent=2, ensure_ascii=False))
    return 0 if verdict.startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
