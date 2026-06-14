#!/usr/bin/env python3
"""
Claude Full Repo Scan - Genesis_System3
READ-ONLY audit except writing proof reports under reports/latest/claude_full_repo_scan/.
"""

from __future__ import annotations

import ast
import csv
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import zipfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.cwd()
OUT = ROOT / "reports" / "latest" / "claude_full_repo_scan"
OUT.mkdir(parents=True, exist_ok=True)

EXCLUDE_DIRS = {
    ".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache",
    ".mypy_cache", ".ruff_cache", "dist", "build"
}

TEXT_EXTS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".json", ".yml", ".yaml", ".toml",
    ".md", ".txt", ".sh", ".ps1", ".bat", ".ini", ".cfg", ".env", ".example",
    ".csv"
}

SECRET_RE = re.compile(
    r"(?i)(api[_-]?key|secret[_-]?key|client[_-]?secret|access[_-]?token|"
    r"refresh[_-]?token|totp|otp|pin|password|passwd|bearer)[\s\"']*[:=][\s\"']*([^\"'\s,}]+)"
)

LIVE_RE = re.compile(r"(?i)(LIVE_TRADING_ENABLED|USE_LIVE_EXECUTION_ENGINE|live[_-]?trading|place_order|real order|broker order)")
TODO_RE = re.compile(r"(?i)(TODO|FIXME|HACK|XXX|NotImplementedError)")
LOCALHOST_RE = re.compile(r"(?i)(localhost|127\.0\.0\.1|0\.0\.0\.0)")

def run(cmd, timeout=120):
    p = subprocess.run(cmd, cwd=ROOT, shell=True, text=True, capture_output=True, timeout=timeout)
    return {"cmd": cmd, "rc": p.returncode, "stdout": p.stdout, "stderr": p.stderr}

def is_excluded(p: Path) -> bool:
    parts = set(p.parts)
    return bool(parts & EXCLUDE_DIRS)

def is_text_file(p: Path) -> bool:
    if p.suffix.lower() in TEXT_EXTS:
        return True
    if p.name in {"Dockerfile", "render.yaml", ".gitignore", ".dockerignore"}:
        return True
    return False

def safe_read(p: Path, max_bytes=2_000_000) -> str:
    try:
        if p.stat().st_size > max_bytes:
            return ""
        return p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    try:
        with p.open("rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return ""

def rel(p: Path) -> str:
    return str(p.relative_to(ROOT)).replace("\\", "/")

def write(path: str, content: str):
    (OUT / path).write_text(content, encoding="utf-8", errors="replace")

def write_json(path: str, obj):
    (OUT / path).write_text(json.dumps(obj, indent=2, default=str), encoding="utf-8")

def write_csv(path: str, rows, fieldnames):
    with (OUT / path).open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fieldnames})

started = datetime.now(timezone.utc)
issues = []
commands = {}

# Git / repo state
for name, cmd in {
    "git_branch": "git branch --show-current",
    "git_head": "git rev-parse HEAD",
    "git_status": "git status --short --untracked-files=all",
    "git_recent": "git log --oneline -10",
    "git_file_count": "git ls-files | wc -l",
}.items():
    try:
        commands[name] = run(cmd, timeout=60)
    except Exception as e:
        commands[name] = {"cmd": cmd, "rc": 999, "stdout": "", "stderr": str(e)}

# File inventory
tracked_raw = commands["git_file_count"]["stdout"].strip()
all_files = []
tracked_files = []

try:
    tracked_list = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True).splitlines()
    tracked_files = [ROOT / x for x in tracked_list]
except Exception:
    tracked_files = []

for p in ROOT.rglob("*"):
    if p.is_file() and not is_excluded(p):
        all_files.append(p)

inventory_rows = []
basename_groups = defaultdict(list)
sha_groups = defaultdict(list)
suffix_counter = Counter()

for p in sorted(all_files, key=lambda x: rel(x)):
    rp = rel(p)
    try:
        st = p.stat()
        suffix = p.suffix.lower()
        suffix_counter[suffix or "[no_ext]"] += 1
        sh = sha256_file(p) if st.st_size <= 10_000_000 else ""
        inventory_rows.append({
            "path": rp,
            "size_bytes": st.st_size,
            "suffix": suffix,
            "sha256": sh,
            "tracked": "YES" if p in tracked_files else "NO",
        })
        basename_groups[p.name].append(rp)
        if sh:
            sha_groups[sh].append(rp)
    except Exception as e:
        issues.append({"severity": "LOW", "category": "file_inventory", "file": rp, "issue": f"Could not stat/hash file: {e}"})

write_csv("file_inventory.csv", inventory_rows, ["path", "size_bytes", "suffix", "sha256", "tracked"])

dup_rows = []
for name, paths in basename_groups.items():
    if len(paths) > 1:
        dup_rows.append({"type": "same_basename", "key": name, "count": len(paths), "paths": " | ".join(paths[:50])})
for sh, paths in sha_groups.items():
    if len(paths) > 1:
        dup_rows.append({"type": "same_sha256", "key": sh, "count": len(paths), "paths": " | ".join(paths[:50])})
write_csv("duplicate_candidates.csv", dup_rows, ["type", "key", "count", "paths"])

if dup_rows:
    issues.append({"severity": "MEDIUM", "category": "repo_cleanup", "file": "", "issue": f"Duplicate/same-name candidates found: {len(dup_rows)}. Requires runtime authority before delete/archive."})

# Secret-style scan
secret_lines = []
secret_count = 0
for p in sorted(all_files, key=lambda x: rel(x)):
    if not is_text_file(p):
        continue
    txt = safe_read(p)
    if not txt:
        continue
    for i, line in enumerate(txt.splitlines(), 1):
        if SECRET_RE.search(line):
            secret_count += 1
            redacted = SECRET_RE.sub(lambda m: f"{m.group(1)}=***REDACTED***", line.strip())
            secret_lines.append(f"{rel(p)}:{i}: {redacted[:500]}")

write("secret_style_findings_redacted.txt", "\n".join(secret_lines) + ("\n" if secret_lines else ""))
if secret_count:
    issues.append({"severity": "CRITICAL", "category": "safety_secrets", "file": "", "issue": f"Secret-style patterns found: {secret_count}. Review redacted report; rotate any real exposed credential."})

# TODO / FIXME / localhost / live scan
todo_lines = []
localhost_live_lines = []
for p in sorted(all_files, key=lambda x: rel(x)):
    if not is_text_file(p):
        continue
    txt = safe_read(p)
    if not txt:
        continue
    for i, line in enumerate(txt.splitlines(), 1):
        s = line.strip()
        if TODO_RE.search(s):
            todo_lines.append(f"{rel(p)}:{i}: {s[:500]}")
        if LOCALHOST_RE.search(s) or LIVE_RE.search(s):
            localhost_live_lines.append(f"{rel(p)}:{i}: {s[:500]}")

write("todo_fixme_scan.txt", "\n".join(todo_lines[:5000]) + ("\n" if todo_lines else ""))
write("localhost_live_mode_scan.txt", "\n".join(localhost_live_lines[:8000]) + ("\n" if localhost_live_lines else ""))

if todo_lines:
    issues.append({"severity": "LOW", "category": "code_debt", "file": "", "issue": f"TODO/FIXME/HACK markers found: {len(todo_lines)}."})
if localhost_live_lines:
    issues.append({"severity": "MEDIUM", "category": "config_runtime", "file": "", "issue": f"localhost/live-mode references found: {len(localhost_live_lines)}. Review for dashboard/deploy/runtime leakage."})

# Python syntax compile + import edges
py_files = [p for p in all_files if p.suffix == ".py"]
compile_failures = []
compile_pass = 0
dependency_edges = []
import_static_findings = []

import py_compile as _pyc
for p in sorted(py_files, key=lambda x: rel(x)):
    rp = rel(p)
    try:
        _pyc.compile(str(p), doraise=True)
        compile_pass += 1
    except Exception as e:
        compile_failures.append({"file": rp, "error": str(e)})
        issues.append({"severity": "HIGH", "category": "python_compile", "file": rp, "issue": str(e)})

    txt = safe_read(p)
    if not txt:
        continue
    try:
        tree = ast.parse(txt, filename=rp)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    dependency_edges.append({"file": rp, "import": a.name, "type": "import"})
            elif isinstance(node, ast.ImportFrom) and node.module:
                dependency_edges.append({"file": rp, "import": node.module, "type": "from"})
    except Exception as e:
        import_static_findings.append({"file": rp, "error": str(e)})

write_json("python_compile_report.json", {
    "total_py_files": len(py_files),
    "compile_pass": compile_pass,
    "compile_fail_count": len(compile_failures),
    "failures": compile_failures,
})
write_json("import_static_scan.json", {
    "dependency_edge_count": len(dependency_edges),
    "parse_issue_count": len(import_static_findings),
    "parse_issues": import_static_findings,
})
write_csv("dependency_edges.csv", dependency_edges, ["file", "import", "type"])

# Runtime entrypoints
entry_keywords = [
    'if __name__ == "__main__"', "uvicorn", "FastAPI(", "Flask(",
    "argparse.ArgumentParser", "schedule", "cron", "postStartCommand", "render.yaml",
]
runtime_hits = []
dashboard_hits = []
safety_hits = []

for p in sorted(all_files, key=lambda x: rel(x)):
    rp = rel(p)
    if not is_text_file(p):
        continue
    txt = safe_read(p)
    if not txt:
        continue
    low_rp = rp.lower()
    if any(k in txt for k in entry_keywords) or rp in {"render.yaml", ".devcontainer/devcontainer.json"}:
        runtime_hits.append(rp)
    if "dashboard" in low_rp or "api/" in txt or "FastAPI(" in txt or "Flask(" in txt:
        dashboard_hits.append(rp)
    if "LIVE_TRADING_ENABLED" in txt or "USE_LIVE_EXECUTION_ENGINE" in txt or "kill" in txt.lower() or "risk" in low_rp or "safety" in low_rp:
        safety_hits.append(rp)

write("runtime_entrypoints.md", "# Runtime Entrypoint Candidates\n\n" + "\n".join(f"- `{x}`" for x in runtime_hits) + "\n")
write("dashboard_api_map.md", "# Dashboard/API Candidate Map\n\n" + "\n".join(f"- `{x}`" for x in dashboard_hits[:1000]) + "\n")
write("trading_safety_map.md", "# Trading Safety / Live Mode Candidate Map\n\n" + "\n".join(f"- `{x}`" for x in safety_hits[:1000]) + "\n")

# Existing proof reports
proof_paths = [
    "docs/project_control/SYSTEM3_MASTER_STATUS.md",
    "reports/latest/full_repo_verification/summary.json",
    "reports/latest/safety_and_secrets/summary.json",
    "reports/latest/full_trading_pipeline_readiness/09_pipeline_gate_summary.json",
    "reports/latest/proof_status_matrix/proof_status_matrix.json",
    "reports/latest/fresh_data_automation_proof/summary.json",
    "reports/latest/model_training_load_proof/summary.json",
    "reports/latest/recent_backtest_walkforward_proof/summary.json",
    "reports/latest/analyzer_paper_lifecycle_proof/summary.json",
    "reports/latest/dashboard_truth_proof/summary.json",
]
proof_md = ["# Existing Proof Report Snapshot", ""]
for pp in proof_paths:
    p = ROOT / pp
    proof_md.append(f"## `{pp}`")
    if not p.exists():
        proof_md.append("- MISSING")
        issues.append({"severity": "HIGH", "category": "proof_reports", "file": pp, "issue": "Expected proof report missing."})
        continue
    txt = safe_read(p)
    proof_md.append("```")
    proof_md.append(txt[:5000])
    proof_md.append("```")
write("open_issues_from_reports.md", "\n".join(proof_md))

open_issue_notes = []
for p in sorted(all_files, key=lambda x: rel(x)):
    if not is_text_file(p):
        continue
    txt = safe_read(p)
    if not txt:
        continue
    if "TRADE_READY_BLOCKED" in txt or "NOT_TRADE_READY" in txt or "PASS_WITH_WARNINGS" in txt or "FAIL" in txt:
        open_issue_notes.append(rel(p))
write("proof_warning_files.txt", "\n".join(open_issue_notes[:2000]) + "\n")

# Repo map
top_dirs = Counter()
for row in inventory_rows:
    top = row["path"].split("/", 1)[0]
    top_dirs[top] += 1

repo_map = [
    "# Claude Full Repo Map", "",
    f"- Generated UTC: `{started.isoformat()}`",
    f"- Root: `{ROOT}`",
    f"- Git branch: `{commands['git_branch']['stdout'].strip()}`",
    f"- Git HEAD: `{commands['git_head']['stdout'].strip()}`",
    f"- Git status lines: `{len(commands['git_status']['stdout'].splitlines())}`",
    f"- Tracked file count from git: `{tracked_raw}`",
    f"- Files scanned excluding heavy dirs: `{len(all_files)}`",
    f"- Python files scanned: `{len(py_files)}`",
    f"- Python compile failures: `{len(compile_failures)}`",
    f"- Secret-style findings: `{secret_count}`",
    f"- TODO/FIXME findings: `{len(todo_lines)}`",
    f"- Localhost/live-mode findings: `{len(localhost_live_lines)}`",
    f"- Runtime entrypoint candidates: `{len(runtime_hits)}`",
    f"- Dashboard/API candidates: `{len(dashboard_hits)}`",
    f"- Safety/live-mode candidates: `{len(safety_hits)}`",
    "", "## Top-level file counts", "",
]
for k, v in sorted(top_dirs.items()):
    repo_map.append(f"- `{k}`: {v}")
repo_map += [
    "", "## Git status", "```",
    commands["git_status"]["stdout"][:10000],
    "```", "", "## Recent commits", "```",
    commands["git_recent"]["stdout"],
    "```",
]
write("repo_map.md", "\n".join(repo_map))

# Issue register
severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
issues_sorted = sorted(issues, key=lambda x: (severity_order.get(x["severity"], 9), x.get("category",""), x.get("file","")))

issue_md = [
    "# Claude Full Repo Issue Register", "",
    f"- Generated UTC: `{started.isoformat()}`",
    f"- Total issues/findings: `{len(issues_sorted)}`",
    "", "| Severity | Category | File | Issue |", "|---|---|---|---|",
]
for it in issues_sorted:
    issue_md.append(f"| {it.get('severity','')} | {it.get('category','')} | `{it.get('file','')}` | {str(it.get('issue','')).replace('|','/')} |")
write("issue_register.md", "\n".join(issue_md))
write_json("issue_register.json", issues_sorted)

summary = {
    "generated_utc": started.isoformat(),
    "git_branch": commands["git_branch"]["stdout"].strip(),
    "git_head": commands["git_head"]["stdout"].strip(),
    "git_status_line_count": len(commands["git_status"]["stdout"].splitlines()),
    "tracked_file_count_git": tracked_raw,
    "files_scanned": len(all_files),
    "python_files_scanned": len(py_files),
    "python_compile_fail_count": len(compile_failures),
    "secret_style_finding_count": secret_count,
    "todo_fixme_count": len(todo_lines),
    "localhost_live_mode_count": len(localhost_live_lines),
    "duplicate_candidate_count": len(dup_rows),
    "runtime_entrypoint_candidate_count": len(runtime_hits),
    "dashboard_api_candidate_count": len(dashboard_hits),
    "trading_safety_candidate_count": len(safety_hits),
    "issue_count_total": len(issues_sorted),
    "issue_count_by_severity": dict(Counter(i["severity"] for i in issues_sorted)),
    "verdict": (
        "BLOCKED_CRITICAL_FINDINGS" if any(i["severity"] == "CRITICAL" for i in issues_sorted)
        else "NEEDS_REVIEW"
    ),
    "live_trading_rule": "DO_NOT_ENABLE_LIVE_TRADING_FROM_THIS_SCAN. Analyzer/Paper only until gates pass.",
}
write_json("summary.json", summary)
write_json("command_outputs.json", commands)

zip_name = OUT / f"claude_full_repo_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
with zipfile.ZipFile(zip_name, "w", compression=zipfile.ZIP_DEFLATED) as z:
    for f in OUT.rglob("*"):
        if f.is_file() and f != zip_name:
            z.write(f, f.relative_to(OUT))

print(json.dumps({"ok": True, "out_dir": str(OUT), "zip": str(zip_name), "summary": summary}, indent=2))
