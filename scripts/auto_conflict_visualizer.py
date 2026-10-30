#!/usr/bin/env python3
"""
Genesis_System3 — Automated Repo & Live Cloud Conflict Visual Generator
Save to: C:\Genesis_System3\scripts\auto_conflict_visualizer.py
Run:     python scripts\auto_conflict_visualizer.py --open

Automatically inspects:
  1. Local repository code (scripts/run_paper_validation.py, dashboard/backend/routers/ml.py)
  2. Local validation directories (state/market_validations, state/paper_validations)
  3. Git working tree & commit SHA (git rev-parse HEAD, git status)
  4. Live Cloud Run endpoints (/api/deploy/info, /api/health, /api/scheduler/health,
     /api/broker/dhan/status, /api/chain/NIFTY..MIDCPNIFTY)
Generates a self-contained visual HTML report at reports/latest/conflict_visual_dashboard.html
highlighting every cross-layer contradiction in red.
"""

from __future__ import annotations
import argparse
import datetime as dt
import json
import pathlib
import re
import subprocess
import urllib.request
import webbrowser

BASE_URL = "https://genesis-system3-web-doq2wplepa-el.a.run.app"
REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT_DIR = REPO_ROOT / "reports" / "latest"


def fetch_json(path: str, timeout: int = 15) -> dict:
    url = f"{BASE_URL}{path}"
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8", errors="replace"))
    except Exception as exc:
        return {"_error": str(exc), "_url": url}


def git_cmd(*args: str) -> str:
    try:
        res = subprocess.run(
            ["git", *args], cwd=REPO_ROOT, capture_output=True, text=True, timeout=10, check=False
        )
        return res.stdout.strip()
    except Exception as exc:
        return f"ERROR: {exc}"


def scan_repo_code() -> dict:
    paper_script = REPO_ROOT / "scripts" / "run_paper_validation.py"
    ml_router = REPO_ROOT / "dashboard" / "backend" / "routers" / "ml.py"
    recovery_tab = REPO_ROOT / "dashboard" / "frontend" / "src" / "components" / "RecoveryProgressTab.tsx"

    paper_text = paper_script.read_text(encoding="utf-8", errors="replace") if paper_script.exists() else ""
    ml_text = ml_router.read_text(encoding="utf-8", errors="replace") if ml_router.exists() else ""

    return {
        "f001_hardcoded_rho": bool(re.search(r"0\.78|COSTED_WALK_FORWARD_PASS", paper_text)),
        "f002_synthetic_ids": "PAPER_TR_" in paper_text,
        "f005_local_val_dir_only": "_validations_checklist" in ml_text and "VAL_DIR" in ml_text,
        "f011_prompts_synthetic_script": "run_paper_validation.py" in ml_text,
        "recovery_tab_file_exists": recovery_tab.exists(),
    }


def evaluate_conflicts(code_scan: dict, api_data: dict, git_info: dict) -> list[dict]:
    conflicts = []

    # CF-01: Synthetic Paper Validation vs Real Ledger
    conflicts.append({
        "id": "CF-01",
        "title": "Synthetic Paper Validation (rho=0.78 / 24 fake IDs) vs. Fail-Closed Ledger",
        "claim": "scripts/run_paper_validation.py or UI claims COSTED_WALK_FORWARD_PASS / ready_for_live=true",
        "truth": f"Hardcoded rho=0.78 present={code_scan['f001_hardcoded_rho']}, Fake PAPER_TR_ IDs={code_scan['f002_synthetic_ids']}",
        "status": "CONFLICT" if (code_scan["f001_hardcoded_rho"] or code_scan["f002_synthetic_ids"]) else "RESOLVED",
    })

    # CF-02: Broker AUTH_OK vs 0/4 Option Chains
    broker_ok = api_data.get("broker", {}).get("connected") is True
    chains = api_data.get("chains", {})
    ready_chains = sum(1 for c in chains.values() if (c.get("total_contracts") or 0) > 0 and not c.get("blocked", True))
    conflicts.append({
        "id": "CF-02",
        "title": "Dhan Broker Connected (AUTH_OK) vs. Option Chain Coverage",
        "claim": f"Broker connected={broker_ok} ({api_data.get('broker', {}).get('auth_classification')})",
        "truth": f"Verified non-empty Dhan option chains = {ready_chains}/4",
        "status": "CONFLICT" if (broker_ok and ready_chains < 4) else ("RESOLVED" if ready_chains == 4 else "BLOCKED"),
    })

    # CF-03: Split-brain storage in ml.py
    conflicts.append({
        "id": "CF-03",
        "title": "Split-Brain Validation Storage (Firestore vs Local Container Disk)",
        "claim": "Cloud Run validation job succeeded (1/1) and writes to cloud state",
        "truth": f"ml.py _validations_checklist checks local disk VAL_DIR={code_scan['f005_local_val_dir_only']}",
        "status": "CONFLICT" if code_scan["f005_local_val_dir_only"] else "RESOLVED",
    })

    # CF-04: Local Git HEAD vs Deployed Cloud Run SHA
    local_sha = git_info.get("head", "")[:7]
    deploy_sha = str(api_data.get("deploy", {}).get("git_sha", ""))[:7]
    conflicts.append({
        "id": "CF-04",
        "title": "Local Repository HEAD vs. Deployed Cloud Run Revision",
        "claim": f"Local Git HEAD = {local_sha} (dirty files: {git_info.get('dirty_count', 0)})",
        "truth": f"Cloud Run /api/deploy/info git_sha = {deploy_sha}",
        "status": "CONFLICT" if (local_sha != deploy_sha or git_info.get("dirty_count", 0) > 0) else "RESOLVED",
    })

    return conflicts


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate visual conflict report from repo + live APIs")
    parser.add_argument("--open", action="store_true", help="Open generated HTML report in browser")
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    now_utc = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    code_scan = scan_repo_code()
    git_status = git_cmd("status", "-s")
    git_info = {
        "head": git_cmd("rev-parse", "HEAD"),
        "dirty_count": len([line for line in git_status.splitlines() if line.strip()]),
    }
    api_data = {
        "deploy": fetch_json("/api/deploy/info"),
        "health": fetch_json("/api/health"),
        "scheduler": fetch_json("/api/scheduler/health"),
        "broker": fetch_json("/api/broker/dhan/status"),
        "chains": {sym: fetch_json(f"/api/chain/{sym}") for sym in ("NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY")},
    }

    conflicts = evaluate_conflicts(code_scan, api_data, git_info)
    receipt_path = OUT_DIR / "conflict_receipt.json"
    receipt_path.write_text(
        json.dumps({"generated_at": now_utc, "git": git_info, "code_scan": code_scan, "conflicts": conflicts}, indent=2),
        encoding="utf-8",
    )

    cards_html = "".join(
        f"<div style='border:2px solid {'#f43f5e' if c['status']=='CONFLICT' else '#10b981'};border-radius:12px;padding:16px;margin-bottom:12px;background:#111827'>"
        f"<div style='display:flex;justify-content:space-between'><strong>{c['id']}: {c['title']}</strong>"
        f"<span style='color:{'#fda4af' if c['status']=='CONFLICT' else '#6ee7b7'};font-family:monospace'>{c['status']}</span></div>"
        f"<p style='color:#9ca3af;font-size:13px;margin:8px 0 4px'><b>Surface Claim:</b> {c['claim']}</p>"
        f"<p style='color:#f87171;font-size:13px;margin:0'><b>Repo/API Truth:</b> {c['truth']}</p></div>"
        for c in conflicts
    )

    html_path = OUT_DIR / "conflict_visual_dashboard.html"
    html_path.write_text(
        f"<!doctype html><html><head><meta charset='utf-8'><title>Genesis System3 Conflict Visual</title></head>"
        f"<body style='background:#0b0f19;color:#f3f4f6;font-family:system-ui;padding:24px;max-width:960px;margin:0 auto'>"
        f"<h1>Genesis_System3 — Auto-Generated Conflict Report</h1><p style='color:#9ca3af'>Generated: {now_utc}</p>"
        f"{cards_html}</body></html>",
        encoding="utf-8",
    )
    print(f"[OK] Wrote {html_path} and {receipt_path}")
    if args.open:
        webbrowser.open(html_path.as_uri())


if __name__ == "__main__":
    main()
