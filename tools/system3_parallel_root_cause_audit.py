#!/usr/bin/env python3
"""
System3 Parallel Root-Cause Audit

Runs one focused audit track at a time. GitHub Actions runs tracks in parallel.
This tool is proof-first: it reports PASS/BLOCKED/FAIL, never claims production-grade.
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "latest" / "parallel_root_cause_audit"

TRACKS = {
    "backend_routes": "Active backend route truth and duplicate/inactive-router risk",
    "render_truth": "Render deploy/public truth freshness",
    "broker_auth": "Dhan broker auth and connected-vs-token contradiction",
    "chain_scanner": "Option-chain, scanner, ranker dependency chain",
    "paper_lifecycle": "Paper trade lifecycle and provenance",
    "ml_training": "CE/PE ML training proof and score visibility",
    "visual_proof": "Dashboard screenshot/visible-text proof",
    "final_truth": "Final truth aggregation and stale verdict risk",
}


def read(path: str) -> str:
    p = ROOT / path
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8", errors="replace")


def exists(path: str) -> bool:
    return (ROOT / path).exists()


def line_has(text: str, *patterns: str) -> bool:
    low = text.lower()
    return all(p.lower() in low for p in patterns)


def report(track: str, status: str, blockers: List[str], findings: List[str], fixes: List[str]) -> Dict:
    OUT.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "track": track,
        "description": TRACKS.get(track, track),
        "status": status,
        "blocker_count": len(blockers),
        "blockers": blockers,
        "findings": findings,
        "required_fixes": fixes,
        "live_trading_enabled": False,
        "production_grade_claim_allowed": False,
    }
    (OUT / f"{track}.json").write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    md = [f"# Parallel Audit — {track}", "", f"- Status: **{status}**", f"- Blockers: `{len(blockers)}`", "", "## Findings"]
    md += [f"- {x}" for x in findings] or ["- none"]
    md += ["", "## Blockers"]
    md += [f"- {x}" for x in blockers] or ["- none"]
    md += ["", "## Required fixes"]
    md += [f"- {x}" for x in fixes] or ["- none"]
    (OUT / f"{track}.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return payload


def audit_backend_routes() -> Dict:
    app = read("dashboard/backend/app.py")
    findings, blockers, fixes = [], [], []
    if "app.include_router(broker_router.router)" in app and "# app.include_router(broker_router.router)" in app:
        blockers.append("Modular routers are imported but disabled; fixes in dashboard/backend/routers may not affect production routes.")
        fixes.append("Move critical fixed logic into active dashboard/backend/app.py routes or safely complete router migration without duplicate routes.")
    if "@app.get(\"/api/broker/funds\")" in app:
        findings.append("Active broker funds route is implemented in app.py.")
    if "@app.get(\"/api/broker/positions/live\")" in app:
        findings.append("Active broker live positions route is implemented in app.py.")
    if "synthetic_data_generator" in app:
        blockers.append("Synthetic data generator import still exists in backend; verify REAL_ONLY blocks it from displayed trading truth.")
        fixes.append("Add proof that synthetic generator is never used for live scanner/chain/model/paper truth.")
    status = "BLOCKED" if blockers else "PASS"
    return report("backend_routes", status, blockers, findings, fixes)


def audit_render_truth() -> Dict:
    idx = read("reports/latest/system3_public_truth/index.md")
    findings, blockers, fixes = [], [], []
    if not idx:
        blockers.append("Public truth index is missing.")
        fixes.append("Regenerate system3_public_truth after latest commit and Render deploy.")
    else:
        findings.append("Public truth index exists.")
        m = re.search(r"Commit: `([^`]+)`", idx)
        if m:
            findings.append(f"Public truth commit: {m.group(1)}")
        if "Final verdict: **FAIL**" in idx:
            blockers.append("Public truth final verdict is FAIL.")
        if "dashboard_live_ui_proof` present=`True` verdict=`PASS`" in idx:
            findings.append("Dashboard live UI proof summary was present and PASS in stale public truth.")
        blockers.append("Need compare public truth commit with latest repository head and Render deploy info; static repo audit cannot prove Render freshness.")
        fixes.append("Run Render deploy verification and publish fresh public truth from latest head.")
    return report("render_truth", "BLOCKED" if blockers else "PASS", blockers, findings, fixes)


def audit_broker_auth() -> Dict:
    app = read("dashboard/backend/app.py")
    panel = read("dashboard/frontend/src/components/BrokerPanel.tsx")
    findings, blockers, fixes = [], [], []
    if "brokerTruthConnected" in panel and "brokerTokenBad" in panel:
        findings.append("Broker UI has token-aware connected logic.")
    else:
        blockers.append("Broker UI may still show CONNECTED while token/funds proof fails.")
        fixes.append("Use brokerTruthConnected=false whenever token/funds/status proof fails.")
    if "@app.get(\"/api/broker/diagnose\")" in app:
        findings.append("Backend has broker diagnose endpoint for env/token probe.")
    else:
        blockers.append("Backend broker diagnose endpoint missing.")
    if "DHAN_ACCESS_TOKEN" in app and "DHAN_CLIENT_ID" in app:
        findings.append("Backend checks Dhan env presence in diagnose route.")
    blockers.append("Actual Dhan auth cannot be proven by static repo; needs Render API probe and user refreshed token if invalid.")
    fixes.append("User must refresh/update Dhan read-only token securely if Render probe shows invalid/expired.")
    fixes.append("Visual proof must show Broker panel BLOCKED/TOKEN ERROR or valid broker proof; no misleading CONNECTED.")
    return report("broker_auth", "BLOCKED", blockers, findings, fixes)


def audit_chain_scanner() -> Dict:
    findings, blockers, fixes = [], [], []
    dm = read("core/data/datasource_manager.py")
    scanner = read("dashboard/backend/contract_gain_scanner.py")
    if "Dhan" in dm or "dhan" in dm:
        findings.append("Datasource manager contains Dhan chain path.")
    if "NIFTY" in scanner and "BANKNIFTY" in scanner:
        findings.append("Scanner includes index segment targets.")
    blockers.append("Option-chain/scanner cannot pass until Dhan auth and live/closed-market Dhan chain rows are proven.")
    blockers.append("Current user visual proof showed scanner segments 0/4 and enabled universe 0/4.")
    fixes.append("After broker auth proof, verify /api/chain/NIFTY/BANKNIFTY/FINNIFTY/MIDCPNIFTY with Dhan rows and spot > 0.")
    fixes.append("Then verify /api/scanner/top_contract_gainers has real segment rows and CE/PE candidates.")
    return report("chain_scanner", "BLOCKED", blockers, findings, fixes)


def audit_paper_lifecycle() -> Dict:
    paper_ui = read("dashboard/frontend/src/components/PaperTrading.tsx")
    trade_router = read("dashboard/backend/routers/trading.py")
    findings, blockers, fixes = [], [], []
    if "Paper Truth Provenance" in paper_ui:
        findings.append("Paper UI now has provenance panel.")
    else:
        blockers.append("Paper UI does not visibly expose provenance panel.")
    if "fake_fixture_rows_rejected" in trade_router:
        findings.append("Inactive/route trading module contains fake fixture rejection logic.")
        blockers.append("Trading router may be inactive if app.py duplicate routes are authoritative.")
    blockers.append("Paper lifecycle needs real candidate -> paper entry -> exit -> PnL proof, not only UI panel.")
    fixes.append("Move paper provenance logic into active app.py route or confirm active endpoint response includes paper_truth.")
    fixes.append("Run paper lifecycle proof with actual Dhan-derived candidate after scanner/ranker pass.")
    return report("paper_lifecycle", "BLOCKED", blockers, findings, fixes)


def audit_ml_training() -> Dict:
    findings, blockers, fixes = [], [], []
    if exists("scripts/options_ce_pe_history_pipeline.py"):
        findings.append("CE/PE historical options training pipeline exists.")
    else:
        blockers.append("CE/PE historical options training pipeline missing.")
    if exists("scripts/build_options_history_contracts.py"):
        findings.append("CE/PE contract builder exists.")
    else:
        blockers.append("CE/PE contract builder missing.")
    if exists("reports/latest/options_ml_training/summary.json"):
        findings.append("Options ML training summary exists.")
    else:
        blockers.append("Options ML training summary is missing/not published.")
    blockers.append("Actual high model score is not proven until dataset rows, train/test rows, accuracy/AUC, and model artifact are visible.")
    fixes.append("Run options-ml-training-proof workflow with valid Dhan historical data or licensed CSV import.")
    fixes.append("ML tab must show score fields from proof JSON, not hardcoded text.")
    return report("ml_training", "BLOCKED" if blockers else "PASS", blockers, findings, fixes)


def audit_visual_proof() -> Dict:
    findings, blockers, fixes = [], [], []
    summary = read("reports/latest/dashboard_visual_production_proof/summary.json")
    proof = read("tools/dashboard_live_ui_proof.mjs")
    if summary:
        findings.append("Dashboard visual proof summary exists.")
    else:
        blockers.append("Dashboard visual proof summary missing.")
    if "hasOwner" in proof and "hasPaperTruthText" in proof and "hasMlProofText" in proof:
        findings.append("Visual proof checks visible text for owner, paper truth, and ML proof.")
    else:
        blockers.append("Visual proof does not verify all required visible text.")
    blockers.append("Need fresh screenshot after latest commits; older screenshots do not prove current UI.")
    fixes.append("Run dashboard visual proof after Render deploy; verify owner, proof bar, ML, paper, broker, and truth text.")
    return report("visual_proof", "BLOCKED" if blockers else "PASS", blockers, findings, fixes)


def audit_final_truth() -> Dict:
    findings, blockers, fixes = [], [], []
    idx = read("reports/latest/system3_public_truth/index.md")
    if "Final verdict: **FAIL**" in idx:
        blockers.append("Final public truth is FAIL.")
    if "Generated UTC" in idx:
        findings.append("Final public truth exists but must be checked for freshness.")
    blockers.append("Final truth must aggregate latest Render, integration, visual, broker, chain, scanner, paper, ML proof.")
    fixes.append("Patch truth publisher to fail if any latest proof is missing/stale or not matching current commit.")
    return report("final_truth", "BLOCKED", blockers, findings, fixes)


def aggregate() -> Dict:
    OUT.mkdir(parents=True, exist_ok=True)
    items = []
    for track in TRACKS:
        path = OUT / f"{track}.json"
        if path.exists():
            items.append(json.loads(path.read_text(encoding="utf-8")))
    blockers = [b for item in items for b in item.get("blockers", [])]
    payload = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "tracks_total": len(TRACKS),
        "tracks_reported": len(items),
        "status": "PASS" if items and not blockers and len(items) == len(TRACKS) else "BLOCKED",
        "blocker_count": len(blockers),
        "blockers": blockers,
        "production_grade_claim_allowed": False,
    }
    (OUT / "summary.json").write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    md = ["# System3 Parallel Root-Cause Audit Summary", "", f"- Status: **{payload['status']}**", f"- Tracks reported: `{payload['tracks_reported']}/{payload['tracks_total']}`", f"- Blockers: `{payload['blocker_count']}`", "", "## Blockers"]
    md += [f"- {x}" for x in blockers] or ["- none"]
    (OUT / "summary.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--track", choices=list(TRACKS) + ["all", "aggregate"], required=True)
    args = ap.parse_args()
    fn = {
        "backend_routes": audit_backend_routes,
        "render_truth": audit_render_truth,
        "broker_auth": audit_broker_auth,
        "chain_scanner": audit_chain_scanner,
        "paper_lifecycle": audit_paper_lifecycle,
        "ml_training": audit_ml_training,
        "visual_proof": audit_visual_proof,
        "final_truth": audit_final_truth,
    }
    if args.track == "aggregate":
        payload = aggregate()
    elif args.track == "all":
        for f in fn.values():
            f()
        payload = aggregate()
    else:
        payload = fn[args.track]()
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
