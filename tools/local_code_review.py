#!/usr/bin/env python3
"""
Local code review — free alternative to Cursor's paid Review / Bugbot.

Runs repo-native static checks, architecture gates, and targeted tests on changed
files. No cloud AI credits required.

Usage (from repo root):
  python tools/local_code_review.py           # quick review (default)
  python tools/local_code_review.py --full    # + pytest + blocker finder
  python tools/local_code_review.py --staged  # review staged files only

Outputs:
  reports/latest/local_code_review/summary.json
  reports/latest/local_code_review/REVIEW.md
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "latest" / "local_code_review"

SKIP_DIRS = {"venv", ".venv", "node_modules", "__pycache__", ".git"}


@dataclass
class StepResult:
    name: str
    status: str  # PASS | FAIL | SKIP | WARN
    detail: str = ""
    findings: List[Dict[str, Any]] = field(default_factory=list)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _run(cmd: Sequence[str], timeout: int = 300) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            list(cmd),
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        out = (proc.stdout or "") + (proc.stderr or "")
        return proc.returncode, out.strip()
    except FileNotFoundError:
        return 127, f"command not found: {cmd[0]}"
    except subprocess.TimeoutExpired:
        return 124, f"timeout after {timeout}s: {' '.join(cmd)}"


def _git_changed_files(staged_only: bool) -> List[str]:
    cmds: List[List[str]] = []
    if staged_only:
        cmds.append(["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"])
    else:
        cmds.extend(
            [
                ["git", "diff", "--name-only", "--diff-filter=ACMR"],
                ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
                ["git", "diff", "--name-only", "origin/main...HEAD"],
                ["git", "diff", "--name-only", "HEAD~1..HEAD"],
            ]
        )
    seen: set[str] = set()
    files: List[str] = []
    for cmd in cmds:
        code, out = _run(cmd, timeout=60)
        if code != 0:
            continue
        for line in out.splitlines():
            path = line.strip().replace("\\", "/")
            if path and path not in seen:
                seen.add(path)
                files.append(path)
    return sorted(files)


def _py_changed(files: Sequence[str]) -> List[Path]:
    out: List[Path] = []
    for f in files:
        if not f.endswith(".py"):
            continue
        p = ROOT / f
        if p.exists() and not any(part in SKIP_DIRS for part in p.parts):
            out.append(p)
    return out


def step_git_summary(changed: Sequence[str]) -> StepResult:
    code, branch_out = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    branch = branch_out if code == 0 else "unknown"
    code2, status_out = _run(["git", "status", "--short"])
    detail = f"branch={branch}, changed_files={len(changed)}"
    return StepResult(
        name="git_summary",
        status="PASS",
        detail=detail,
        findings=[{"branch": branch, "changed": list(changed), "status_short": status_out[:4000]}],
    )


def step_architecture_gate() -> StepResult:
    gate = ROOT / ".github" / "scripts" / "root_architecture_gate.py"
    if not gate.exists():
        return StepResult("architecture_gate", "SKIP", "root_architecture_gate.py missing")
    code, out = _run([sys.executable, str(gate)], timeout=120)
    return StepResult(
        name="architecture_gate",
        status="PASS" if code == 0 else "FAIL",
        detail=out[-2500:],
    )


def step_verify_cursor_bugs() -> StepResult:
    script = ROOT / "tools" / "verify_cursor_agent_bugs.py"
    if not script.exists():
        return StepResult("verify_cursor_agent_bugs", "SKIP", "script missing")
    code, out = _run([sys.executable, str(script)], timeout=120)
    return StepResult(
        name="verify_cursor_agent_bugs",
        status="PASS" if code == 0 else "FAIL",
        detail=out[-2500:],
    )


def step_py_compile(py_files: Sequence[Path]) -> StepResult:
    if not py_files:
        return StepResult("py_compile", "SKIP", "no changed Python files")
    failures: List[Dict[str, str]] = []
    for p in py_files:
        code, out = _run([sys.executable, "-m", "py_compile", str(p)], timeout=30)
        if code != 0:
            failures.append({"file": str(p.relative_to(ROOT)), "error": out})
    return StepResult(
        name="py_compile",
        status="PASS" if not failures else "FAIL",
        detail=f"compiled {len(py_files)} file(s)",
        findings=failures,
    )


def _tool_available(name: str) -> bool:
    code, _ = _run([name, "--version"], timeout=15)
    return code == 0


def step_flake8(py_files: Sequence[Path]) -> StepResult:
    if not py_files:
        return StepResult("flake8", "SKIP", "no changed Python files")
    if not _tool_available("flake8"):
        return StepResult("flake8", "SKIP", "flake8 not installed (pip install flake8)")
    rel = [str(p.relative_to(ROOT)) for p in py_files]
    code, out = _run([sys.executable, "-m", "flake8", *rel], timeout=180)
    findings = [{"line": ln} for ln in out.splitlines()[:50]] if out else []
    return StepResult(
        name="flake8",
        status="PASS" if code == 0 else "FAIL",
        detail=out[-3000:] if out else "no issues",
        findings=findings,
    )


def step_bandit(py_files: Sequence[Path]) -> StepResult:
    if not py_files:
        return StepResult("bandit", "SKIP", "no changed Python files")
    if not _tool_available("bandit"):
        return StepResult("bandit", "SKIP", "bandit not installed (pip install bandit)")
    rel = [str(p.relative_to(ROOT)) for p in py_files]
    code, out = _run(
        [sys.executable, "-m", "bandit", "-q", "-ll", *rel],
        timeout=180,
    )
    # bandit returns 1 when issues found
    status = "PASS" if code == 0 else ("WARN" if code == 1 else "FAIL")
    return StepResult(
        name="bandit",
        status=status,
        detail=out[-3000:] if out else "no issues",
    )


def step_ast_scan(py_files: Sequence[Path]) -> StepResult:
    """Lightweight static scan — no AI credits."""
    if not py_files:
        return StepResult("ast_static_scan", "SKIP", "no changed Python files")
    findings: List[Dict[str, str]] = []
    patterns = [
        (re.compile(r"\bexcept\s*:"), "bare_except"),
        (re.compile(r"api[_-]?key\s*=\s*['\"][^'\"]{8,}", re.I), "hardcoded_api_key"),
        (re.compile(r"password\s*=\s*['\"][^'\"]{4,}", re.I), "hardcoded_password"),
        (re.compile(r"LIVE_TRADING_ENABLED\s*=\s*['\"]?1", re.I), "live_trading_enable"),
    ]
    for p in py_files:
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            findings.append({"file": str(p.relative_to(ROOT)), "issue": f"read_error: {exc}"})
            continue
        for i, line in enumerate(text.splitlines(), 1):
            for rx, label in patterns:
                if rx.search(line) and "Exception" not in line:
                    findings.append(
                        {
                            "file": str(p.relative_to(ROOT)),
                            "line": str(i),
                            "issue": label,
                            "snippet": line.strip()[:120],
                        }
                    )
        try:
            tree = ast.parse(text, filename=str(p))
        except SyntaxError as exc:
            findings.append({"file": str(p.relative_to(ROOT)), "issue": f"syntax_error: {exc}"})
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Attribute) and func.attr in {"placeOrder", "place_order"}:
                    findings.append(
                        {
                            "file": str(p.relative_to(ROOT)),
                            "line": str(getattr(node, "lineno", 0)),
                            "issue": "broker_order_call",
                        }
                    )
    critical = [
        f
        for f in findings
        if f.get("issue") in {"hardcoded_api_key", "hardcoded_password", "live_trading_enable", "syntax_error"}
    ]
    status = "FAIL" if critical else ("WARN" if findings else "PASS")
    return StepResult(
        name="ast_static_scan",
        status=status,
        detail=f"{len(findings)} finding(s)",
        findings=findings[:100],
    )


def _tests_for_changed(py_files: Sequence[Path]) -> List[str]:
    """Map changed modules to likely test files."""
    tests: set[str] = set()
    tests_dir = ROOT / "tests"
    if not tests_dir.exists():
        return []
    for p in py_files:
        stem = p.stem
        if stem.startswith("test_"):
            tests.add(str(p.relative_to(ROOT)).replace("\\", "/"))
            continue
        for candidate in tests_dir.rglob(f"test*{stem}*.py"):
            tests.add(str(candidate.relative_to(ROOT)).replace("\\", "/"))
        for candidate in tests_dir.rglob(f"*{stem}*.py"):
            if candidate.name.startswith("test_"):
                tests.add(str(candidate.relative_to(ROOT)).replace("\\", "/"))
    if not tests and py_files:
        tests.add("tests/")
    return sorted(tests)


def step_pytest(py_files: Sequence[Path], full: bool) -> StepResult:
    if full:
        code, out = _run([sys.executable, "-m", "pytest", "tests/", "-q", "--tb=no"], timeout=600)
        return StepResult(
            name="pytest",
            status="PASS" if code == 0 else "FAIL",
            detail=out[-3000:],
        )
    targets = _tests_for_changed(py_files)
    if not targets:
        return StepResult("pytest", "SKIP", "no mapped tests for changed files")
    code, out = _run([sys.executable, "-m", "pytest", *targets, "-q", "--tb=short"], timeout=300)
    return StepResult(
        name="pytest",
        status="PASS" if code == 0 else "FAIL",
        detail=f"targets={targets}\n{out[-2500:]}",
    )


def step_blocker_finder(full: bool) -> StepResult:
    if not full:
        return StepResult("blocker_finder", "SKIP", "use --full to run")
    script = ROOT / "scripts" / "system3_blocker_finder.py"
    if not script.exists():
        return StepResult("blocker_finder", "SKIP", "script missing")
    code, out = _run([sys.executable, str(script)], timeout=180)
    return StepResult(
        name="blocker_finder",
        status="PASS" if code == 0 else "WARN",
        detail=out[-2500:],
    )


def _render_md(steps: Sequence[StepResult], changed: Sequence[str], verdict: str) -> str:
    lines = [
        "# Local Code Review (Cursor Review alternative)",
        "",
        f"- Generated: `{_utc_now()}`",
        f"- Verdict: **{verdict}**",
        f"- Changed files: **{len(changed)}**",
        "",
        "> Free local review — no Cursor AI credits required.",
        "",
        "## Summary",
        "",
        "| Check | Status |",
        "|---|---|",
    ]
    for s in steps:
        lines.append(f"| {s.name} | {s.status} |")
    lines.extend(["", "## Changed files", ""])
    if changed:
        for f in changed[:80]:
            lines.append(f"- `{f}`")
        if len(changed) > 80:
            lines.append(f"- … and {len(changed) - 80} more")
    else:
        lines.append("- (none — reviewing full repo gates only)")
    lines.extend(["", "## Details", ""])
    for s in steps:
        lines.append(f"### {s.name} — {s.status}")
        if s.detail:
            lines.append("")
            lines.append("```")
            lines.append(s.detail[:4000])
            lines.append("```")
        if s.findings:
            lines.append("")
            lines.append(f"Findings: {len(s.findings)}")
            for fnd in s.findings[:15]:
                lines.append(f"- `{json.dumps(fnd, ensure_ascii=False)}`")
        lines.append("")
    lines.extend(
        [
            "## How to run",
            "",
            "```bat",
            "python tools/local_code_review.py",
            "python tools/local_code_review.py --full",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Local code review (no Cursor credits)")
    parser.add_argument("--full", action="store_true", help="Run full pytest + blocker finder")
    parser.add_argument("--staged", action="store_true", help="Review staged files only")
    args = parser.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    changed = _git_changed_files(staged_only=args.staged)
    py_files = _py_changed(changed)

    steps: List[StepResult] = [
        step_git_summary(changed),
        step_architecture_gate(),
        step_verify_cursor_bugs(),
        step_py_compile(py_files),
        step_ast_scan(py_files),
        step_flake8(py_files),
        step_bandit(py_files),
        step_pytest(py_files, full=args.full),
        step_blocker_finder(args.full),
    ]

    failed = [s for s in steps if s.status == "FAIL"]
    warned = [s for s in steps if s.status == "WARN"]
    if failed:
        verdict = "FAIL"
    elif warned:
        verdict = "PASS_WITH_WARNINGS"
    else:
        verdict = "PASS"

    payload = {
        "generated_utc": _utc_now(),
        "verdict": verdict,
        "cursor_review_alternative": True,
        "changed_files": list(changed),
        "python_changed_count": len(py_files),
        "steps": [asdict(s) for s in steps],
        "failed_steps": [s.name for s in failed],
        "warning_steps": [s.name for s in warned],
    }
    (OUT / "summary.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    (OUT / "REVIEW.md").write_text(_render_md(steps, changed, verdict), encoding="utf-8")

    print(f"Local code review verdict: {verdict}")
    print(f"Report: {OUT / 'REVIEW.md'}")
    for s in steps:
        print(f"  [{s.status}] {s.name}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
