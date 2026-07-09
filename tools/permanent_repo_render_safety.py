#!/usr/bin/env python3
"""Permanent repo + Render safety audit for System3.

Read-only repo/config audit. It checks safety invariants, workflow coverage,
frontend no-fake posture, Render analyzer-only settings, and key docs/reports.
It does not call broker order endpoints and does not mutate runtime state.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports" / "latest" / "permanent_repo_render_safety"
TEXT_EXT = {".py", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".yml", ".yaml", ".md", ".json", ".txt", ".toml", ".ini"}
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", ".pytest_cache", "dist", "build"}
SECRET_VALUE_RE = re.compile(r"(?i)(access-token|authorization|api[_-]?key|deploy[_-]?hook|client[_-]?secret|password|totp|pin)\s*[:=]\s*['\"]?([A-Za-z0-9_./?=&:-]{12,})")
LIVE_BAD_RE = re.compile(r"(?i)(LIVE_TRADING_ENABLED\s*[:=]\s*['\"]?1|SYSTEM3_LIVE_TRADING_ALLOWED\s*[:=]\s*['\"]?1)")
FRONTEND_BAD_RE = re.compile(r"(?i)(csv_fallback|STALE_CSV_FALLBACK|STALE_LAST_GOOD|keepLastGood|INTERNAL_UNVERIFIED|bhavcopy|yahoo|Math\.random|hardcoded\s*0|\.\.\.3741|cached read-only)")
ORDER_RE = re.compile(r"(?i)\b(place_order|modify_order|cancel_order|route_order|order_placement_allowed)\b")
ALLOW_ORDER_PATHS = {
    "core/brokers/dhan/broker_legacy.py",
    "core/ultra/phase52_multi_broker.py",
    "dashboard/backend/routers/broker.py",
    "tools/cloud_runtime_check.py",
    "tools/local_code_review.py",
    "scripts/verify_dhan_readonly.py",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def iter_text_files() -> Iterable[Path]:
    for p in ROOT.rglob("*"):
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if p.is_file() and p.suffix.lower() in TEXT_EXT:
            yield p


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def add(result: Dict[str, Any], level: str, key: str, message: str, path: str = "") -> None:
    row = {"level": level, "key": key, "message": message}
    if path:
        row["path"] = path
    target = "alerts" if level == "CRITICAL" else "warnings" if level == "WARNING" else "passed"
    result[target].append(row)


def check_required_files(result: Dict[str, Any]) -> None:
    required = [
        "Procfile",
        "render.yaml",
        "README.md",
        ".github/workflows/dashboard-live-proof.yml",
        ".github/workflows/cloud-runtime-check.yml",
        ".github/workflows/actions-truth-autopsy.yml",
        ".github/workflows/system3-full-auto-truth.yml",
        "tools/frontend_no_fake_guard.mjs",
        "tools/dashboard_live_ui_proof.mjs",
        "tools/permanent_live_log_watch.mjs",
        "tools/actions_truth_autopsy.py",
        "dashboard/frontend/src/components/SystemTruthControl.tsx",
        "core/data/datasource_manager.py",
    ]
    for item in required:
        if (ROOT / item).exists():
            add(result, "PASS", f"required_file_{item}", "present", item)
        else:
            add(result, "CRITICAL", f"missing_required_file_{item}", "required safety/proof file missing", item)


def check_render_yaml(result: Dict[str, Any]) -> None:
    p = ROOT / "render.yaml"
    text = read(p)
    if not text:
        add(result, "CRITICAL", "render_yaml_missing", "render.yaml missing or unreadable", "render.yaml")
        return
    required_pairs = [
        "SYSTEM3_MODE", "analyzer",
        "ANALYZE_MODE", "1",
        "LIVE_TRADING_ENABLED", "0",
        "SYSTEM3_LIVE_TRADING_ALLOWED", "0",
        "SYSTEM3_REAL_ONLY", "1",
        "DHAN_CLIENT_ID", "sync: false",
        "DHAN_ACCESS_TOKEN", "sync: false",
    ]
    for i in range(0, len(required_pairs), 2):
        key, value = required_pairs[i], required_pairs[i + 1]
        if key in text and value in text:
            add(result, "PASS", f"render_{key}", f"{key} includes {value}", "render.yaml")
        else:
            add(result, "CRITICAL", f"render_{key}_bad", f"{key} / {value} not proven in render.yaml", "render.yaml")
    if LIVE_BAD_RE.search(text):
        add(result, "CRITICAL", "render_live_flag_enabled", "render.yaml appears to enable live trading", "render.yaml")


def check_procfile(result: Dict[str, Any]) -> None:
    p = ROOT / "Procfile"
    text = read(p)
    if "uvicorn dashboard.backend.app:app" in text:
        add(result, "PASS", "procfile_backend_entrypoint", "FastAPI backend entrypoint present", "Procfile")
    else:
        add(result, "CRITICAL", "procfile_backend_entrypoint_missing", "Expected backend entrypoint not found", "Procfile")


def scan_secrets_and_live_flags(result: Dict[str, Any]) -> None:
    for p in iter_text_files():
        r = rel(p)
        if r.startswith("reports/latest/"):
            continue
        text = read(p)
        for m in SECRET_VALUE_RE.finditer(text):
            # allow references to GitHub secrets syntax and docs without values
            snippet = m.group(0)
            if "${{ secrets." in snippet or "[REDACTED]" in snippet or "sync: false" in snippet:
                continue
            add(result, "CRITICAL", "possible_secret_literal", "possible secret-like literal in repo", r)
            break
        if LIVE_BAD_RE.search(text):
            add(result, "CRITICAL", "live_flag_enabled_in_repo", "live trading flag appears enabled in repo text", r)


def scan_frontend_bad_markers(result: Dict[str, Any]) -> None:
    root = ROOT / "dashboard" / "frontend" / "src"
    found = []
    for p in root.rglob("*") if root.exists() else []:
        if p.is_file() and p.suffix.lower() in {".ts", ".tsx", ".js", ".jsx"}:
            text = read(p)
            if FRONTEND_BAD_RE.search(text):
                found.append(rel(p))
    if found:
        for f in found[:20]:
            add(result, "CRITICAL", "frontend_bad_marker", "frontend contains banned stale/fake/hardcoded marker", f)
    else:
        add(result, "PASS", "frontend_no_fake_guard_static", "no banned frontend stale/fake/hardcoded markers found")


def scan_order_paths(result: Dict[str, Any]) -> None:
    suspects = []
    for p in iter_text_files():
        r = rel(p)
        if r.startswith("reports/latest/") or r in ALLOW_ORDER_PATHS:
            continue
        text = read(p)
        if ORDER_RE.search(text):
            suspects.append(r)
    if suspects:
        for s in suspects[:40]:
            add(result, "WARNING", "order_word_usage_review", "order-placement keyword found outside allowlist; manual review required", s)
    else:
        add(result, "PASS", "order_keywords_allowlisted", "order placement keywords only found in allowlisted/disabled/proof paths")


def inventory_docs(result: Dict[str, Any]) -> None:
    docs = []
    for base in [ROOT / "docs", ROOT / "reports" / "latest", ROOT / ".github" / "workflows"]:
        if base.exists():
            for p in base.rglob("*"):
                if p.is_file() and p.suffix.lower() in {".md", ".json", ".yml", ".yaml"}:
                    docs.append(rel(p))
    result["document_inventory"] = sorted(docs)[:500]
    add(result, "PASS", "document_inventory_created", f"indexed {len(docs)} docs/workflow/report files")


def run_frontend_guard(result: Dict[str, Any]) -> None:
    script = ROOT / "tools" / "frontend_no_fake_guard.mjs"
    if not script.exists():
        add(result, "CRITICAL", "frontend_guard_missing", "frontend guard script missing")
        return
    try:
        proc = subprocess.run(["node", str(script)], cwd=ROOT, text=True, capture_output=True, timeout=60)
        result["frontend_guard_stdout"] = proc.stdout[-4000:]
        result["frontend_guard_stderr"] = proc.stderr[-4000:]
        if proc.returncode == 0:
            add(result, "PASS", "frontend_guard_runtime_pass", "frontend_no_fake_guard.mjs passed")
        else:
            add(result, "CRITICAL", "frontend_guard_runtime_fail", "frontend_no_fake_guard.mjs failed")
    except Exception as exc:
        add(result, "WARNING", "frontend_guard_runtime_error", f"could not run frontend guard: {exc}")


def final_verdict(result: Dict[str, Any]) -> str:
    if result["alerts"]:
        return "FAIL"
    if result["warnings"]:
        return "WARN"
    return "PASS"


def write_report(result: Dict[str, Any]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    result["generated_utc"] = utc_now()
    result["verdict"] = final_verdict(result)
    (REPORT_DIR / "summary.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    lines = [
        "# Permanent Repo + Render Safety",
        "",
        f"- Generated UTC: `{result['generated_utc']}`",
        f"- Verdict: **{result['verdict']}**",
        f"- Critical alerts: `{len(result['alerts'])}`",
        f"- Warnings: `{len(result['warnings'])}`",
        f"- Pass checks: `{len(result['passed'])}`",
        f"- Documents indexed: `{len(result.get('document_inventory', []))}`",
        "",
        "## Critical alerts",
    ]
    if result["alerts"]:
        for a in result["alerts"]:
            lines.append(f"- `{a['key']}` {a.get('path','')} — {a['message']}")
    else:
        lines.append("- None")
    lines.append("")
    lines.append("## Warnings")
    if result["warnings"]:
        for w in result["warnings"][:80]:
            lines.append(f"- `{w['key']}` {w.get('path','')} — {w['message']}")
    else:
        lines.append("- None")
    lines.append("")
    lines.append("## Safety statement")
    lines.append("- This audit is repo/config/read-only runtime proof automation.")
    lines.append("- It does not enable live trading and does not call broker order endpoints.")
    lines.append("- Live-money use remains blocked unless System Truth Control and proof artifacts show all required layers PASS.")
    (REPORT_DIR / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    result: Dict[str, Any] = {"alerts": [], "warnings": [], "passed": [], "document_inventory": []}
    check_required_files(result)
    check_render_yaml(result)
    check_procfile(result)
    scan_secrets_and_live_flags(result)
    scan_frontend_bad_markers(result)
    scan_order_paths(result)
    inventory_docs(result)
    run_frontend_guard(result)
    write_report(result)
    print((REPORT_DIR / "summary.md").read_text(encoding="utf-8"))
    return 1 if result["alerts"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
