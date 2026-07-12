#!/usr/bin/env python3
"""
System3 Render 100-Agent Swarm

Runs one independent deterministic audit agent per matrix job.
Purpose: speed up Render/UI/backend/frontend/workflow/root-cause discovery.
No secret printing. No live orders. Analyzer/read-only only.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "latest" / "render_100_agent_swarm"
BASE = os.environ.get("DASHBOARD_BASE_URL", "https://genesis-system3-backend.onrender.com").rstrip("/")

FOCUS_AREAS = [
    "render_health",
    "deploy_freshness",
    "frontend_ui_load",
    "backend_api_smoke",
    "broker_truth",
    "option_chain",
    "scanner_signals",
    "paper_lifecycle",
    "ml_training",
    "public_truth",
    "workflow_failures",
    "visible_ui_issues",
    "todo_status",
    "root_cause_matrix",
    "install_dependencies",
    "security_live_off",
    "stale_fake_synthetic",
    "route_conflicts",
    "proof_files",
    "mobile_responsive",
]

API_ENDPOINTS = [
    "/api/health",
    "/api/state",
    "/api/deploy/info",
    "/api/broker/diagnose",
    "/api/broker/funds",
    "/api/broker/holdings",
    "/api/broker/positions/live",
    "/api/scanner/top_contract_gainers",
    "/api/paper",
    "/api/ml/performance",
]

LOCAL_FILES = [
    "dashboard/backend/app.py",
    "dashboard/frontend/src/App.tsx",
    "dashboard/frontend/src/components/SystemTruthControl.tsx",
    "dashboard/frontend/src/components/BrokerPanel.tsx",
    "dashboard/frontend/src/components/PaperTrading.tsx",
    "tools/dashboard_visible_issue_tracker.mjs",
    "tools/system3_autopilot_proof_board.py",
    "reports/latest/system3_public_truth/index.md",
    "docs/SYSTEM3_360_ROOT_CAUSE_BLOCKERS.md",
]

RED_WORDS = ["ERROR", "FAIL", "FAILED", "BLOCKED", "PENDING", "NOT READY", "NOT PROVEN", "MISSING", "STALE", "TIMEOUT", "INVALID", "EXPIRED", "0/4", "NO TRADE", "NO SIGNAL"]


def url_get(path_or_url: str, timeout: int = 25) -> Dict[str, Any]:
    url = path_or_url if path_or_url.startswith("http") else BASE + path_or_url
    t0 = time.time()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "system3-render-100-agent-swarm"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read(300000).decode("utf-8", errors="replace")
            return {"url": url, "ok": 200 <= resp.status < 400, "status_code": resp.status, "latency_ms": int((time.time() - t0) * 1000), "body_sample": body[:4000]}
    except urllib.error.HTTPError as exc:
        body = exc.read(20000).decode("utf-8", errors="replace") if hasattr(exc, "read") else ""
        return {"url": url, "ok": False, "status_code": exc.code, "latency_ms": int((time.time() - t0) * 1000), "error": body[:1000]}
    except Exception as exc:
        return {"url": url, "ok": False, "status_code": 0, "latency_ms": int((time.time() - t0) * 1000), "error": f"{type(exc).__name__}: {str(exc)[:500]}"}


def read(rel: str) -> str:
    p = ROOT / rel
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8", errors="replace")


def json_load(rel: str) -> Dict[str, Any]:
    txt = read(rel)
    if not txt:
        return {}
    try:
        return json.loads(txt)
    except Exception as exc:
        return {"_json_error": str(exc)}


def add_issue(issues: List[str], text: str):
    if text and text not in issues:
        issues.append(text[:500])


def audit_agent(agent_id: int) -> Dict[str, Any]:
    focus = FOCUS_AREAS[(agent_id - 1) % len(FOCUS_AREAS)]
    pass_num = ((agent_id - 1) // len(FOCUS_AREAS)) + 1
    issues: List[str] = []
    findings: List[str] = []
    evidence: Dict[str, Any] = {}

    findings.append(f"agent_id={agent_id:03d}")
    findings.append(f"focus={focus}")
    findings.append(f"pass={pass_num}")

    if focus == "render_health":
        for ep in ["/", "/ui/", "/api/health"]:
            r = url_get(ep)
            evidence[ep] = {k: r.get(k) for k in ("ok", "status_code", "latency_ms", "error")}
            if not r.get("ok"):
                add_issue(issues, f"Render health failed {ep}: status={r.get('status_code')} error={r.get('error')}")

    elif focus == "deploy_freshness":
        r = url_get("/api/deploy/info")
        evidence["/api/deploy/info"] = r
        if not r.get("ok"):
            add_issue(issues, "Deploy info endpoint missing/failing; cannot prove Render deployed latest commit.")
        elif "commit" not in str(r.get("body_sample", "")).lower():
            add_issue(issues, "Deploy info response does not visibly expose commit; stale Render risk remains.")

    elif focus == "frontend_ui_load":
        r = url_get("/ui/", timeout=35)
        body = r.get("body_sample", "")
        evidence["ui"] = {"ok": r.get("ok"), "status_code": r.get("status_code"), "latency_ms": r.get("latency_ms"), "sample": body[:500]}
        if not r.get("ok"):
            add_issue(issues, "UI route failed to load.")
        if r.get("ok") and not any(x in body.lower() for x in ["root", "script", "system3", "genesis"]):
            add_issue(issues, "UI HTML loaded but expected app markers not found.")

    elif focus == "backend_api_smoke":
        for ep in API_ENDPOINTS[:5]:
            r = url_get(ep)
            evidence[ep] = {"ok": r.get("ok"), "status_code": r.get("status_code"), "latency_ms": r.get("latency_ms"), "error": r.get("error")}
            if r.get("status_code") >= 500 or r.get("status_code") == 0:
                add_issue(issues, f"Backend API smoke failed {ep}: status={r.get('status_code')}")

    elif focus == "broker_truth":
        for ep in ["/api/broker/diagnose", "/api/broker/funds", "/api/broker/holdings", "/api/broker/positions/live"]:
            r = url_get(ep)
            sample = str(r.get("body_sample") or r.get("error") or "")
            evidence[ep] = {"ok": r.get("ok"), "status_code": r.get("status_code"), "sample": sample[:800]}
            if any(w in sample.lower() for w in ["invalid", "expired", "unauthorized", "auth required", "token"]):
                add_issue(issues, f"Broker/auth issue visible at {ep}: {sample[:220]}")
            if r.get("status_code") >= 500:
                add_issue(issues, f"Broker endpoint server error: {ep}")

    elif focus == "option_chain":
        for sym in ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"]:
            ep = f"/api/chain/{sym}"
            r = url_get(ep, timeout=35)
            sample = str(r.get("body_sample") or r.get("error") or "")
            evidence[ep] = {"ok": r.get("ok"), "status_code": r.get("status_code"), "sample": sample[:800]}
            if not r.get("ok") or any(w in sample.lower() for w in ["blocked", "error", "missing", "invalid", "expired"]):
                add_issue(issues, f"Option-chain proof blocked for {sym}: status={r.get('status_code')} sample={sample[:220]}")

    elif focus == "scanner_signals":
        for ep in ["/api/scanner/top_contract_gainers", "/api/state"]:
            r = url_get(ep, timeout=45)
            sample = str(r.get("body_sample") or r.get("error") or "")
            evidence[ep] = {"ok": r.get("ok"), "status_code": r.get("status_code"), "sample": sample[:1000]}
            if any(x in sample for x in ["0/4", "NO TRADE", "No trade", "blocked", "BLOCKED"]):
                add_issue(issues, f"Scanner/signals issue at {ep}: {sample[:260]}")
            if r.get("status_code") >= 500:
                add_issue(issues, f"Scanner/signals endpoint server error: {ep}")

    elif focus == "paper_lifecycle":
        r = url_get("/api/paper", timeout=30)
        sample = str(r.get("body_sample") or r.get("error") or "")
        evidence["/api/paper"] = {"ok": r.get("ok"), "status_code": r.get("status_code"), "sample": sample[:1200]}
        if any(w in sample.lower() for w in ["blocked", "no today", "missing", "fixture", "fake"]):
            add_issue(issues, f"Paper lifecycle/provenance issue visible: {sample[:260]}")

    elif focus == "ml_training":
        for ep in ["/api/ml/performance", "/api/ml/status"]:
            r = url_get(ep, timeout=25)
            sample = str(r.get("body_sample") or r.get("error") or "")
            evidence[ep] = {"ok": r.get("ok"), "status_code": r.get("status_code"), "sample": sample[:1000]}
            if any(w in sample.lower() for w in ["pending", "blocked", "missing", "not_ready", "not ready"]):
                add_issue(issues, f"ML proof issue at {ep}: {sample[:250]}")

    elif focus == "public_truth":
        txt = read("reports/latest/system3_public_truth/index.md")
        evidence["exists"] = bool(txt)
        evidence["sample"] = txt[:1000]
        if not txt:
            add_issue(issues, "Public truth file missing.")
        elif "Final verdict: **FAIL**" in txt:
            add_issue(issues, "Public truth final verdict is FAIL.")
        elif "Generated UTC" not in txt:
            add_issue(issues, "Public truth has no generated timestamp.")

    elif focus == "workflow_failures":
        data = json_load("reports/latest/workflow_failure_tracker/summary.json")
        evidence["workflow_failure_tracker"] = data
        if not data:
            add_issue(issues, "Workflow failure tracker summary missing.")
        if data.get("failed_count", 0):
            add_issue(issues, f"Workflow failures present: failed_count={data.get('failed_count')}")
        if data.get("status") not in ["PASS", None] and data:
            add_issue(issues, f"Workflow failure tracker status={data.get('status')}")

    elif focus == "visible_ui_issues":
        data = json_load("reports/latest/dashboard_visible_issue_tracker/summary.json")
        evidence["visible_ui_issues"] = data
        if not data:
            add_issue(issues, "Dashboard visible issue tracker summary missing.")
        if data.get("visible_issue_count", 0):
            add_issue(issues, f"Visible dashboard issues present: {data.get('visible_issue_count')}")
        if data.get("status") not in ["PASS", None] and data:
            add_issue(issues, f"Dashboard visible issue tracker status={data.get('status')}")

    elif focus == "todo_status":
        data = json_load("reports/latest/todo_status_update/summary.json")
        evidence["todo_status"] = data
        if not data:
            add_issue(issues, "1000+ TODO status summary missing.")
        if data.get("status") not in ["DONE", "PASS", None] and data:
            add_issue(issues, f"TODO status is not complete: {data.get('status')} counts={data.get('counts')}")

    elif focus == "root_cause_matrix":
        data = json_load("reports/latest/parallel_root_cause_audit/summary.json")
        txt = read("docs/SYSTEM3_360_ROOT_CAUSE_BLOCKERS.md")
        evidence["parallel_summary"] = data
        evidence["matrix_exists"] = bool(txt)
        if not txt:
            add_issue(issues, "360 root-cause matrix missing.")
        if data.get("blocker_count", 0):
            add_issue(issues, f"Parallel root-cause blockers remain: {data.get('blocker_count')}")

    elif focus == "install_dependencies":
        data = json_load("reports/latest/secure_install_credential_audit/summary.json")
        evidence["secure_install_credential_audit"] = data
        if not data:
            add_issue(issues, "Secure install/credential audit summary missing.")
        if data.get("status") not in ["PASS", None] and data:
            add_issue(issues, f"Install/credential audit blocked: {data.get('blocker_count')} blockers")

    elif focus == "security_live_off":
        combined = "\n".join(read(f) for f in LOCAL_FILES)
        evidence["live_flags"] = {"env_live": os.environ.get("LIVE_TRADING_ENABLED", "0"), "env_allowed": os.environ.get("SYSTEM3_LIVE_TRADING_ALLOWED", "0")}
        if os.environ.get("LIVE_TRADING_ENABLED", "0") not in ["0", "false", "False", ""]:
            add_issue(issues, "LIVE_TRADING_ENABLED not OFF in workflow env.")
        if "order_placement_allowed" not in combined:
            add_issue(issues, "Could not find order_placement_allowed safety marker in inspected files.")

    elif focus == "stale_fake_synthetic":
        hits = []
        for rel in LOCAL_FILES:
            txt = read(rel)
            for w in ["synthetic", "fake", "fixture", "mock", "yahoo", "bhavcopy"]:
                if w in txt.lower():
                    hits.append({"file": rel, "word": w})
        evidence["hits"] = hits[:80]
        if hits:
            add_issue(issues, f"Fake/stale/source-risk words found: {hits[:12]}")

    elif focus == "route_conflicts":
        app = read("dashboard/backend/app.py")
        evidence["router_disabled"] = "# app.include_router" in app
        if "# app.include_router(broker_router.router)" in app:
            add_issue(issues, "Modular broker router disabled; patches in router may not affect active app route.")
        routes = re.findall(r"@app\.(?:get|post|put|delete)\(\"([^\"]+)\"", app)
        dup = sorted({r for r in routes if routes.count(r) > 1})
        evidence["duplicate_routes"] = dup
        if dup:
            add_issue(issues, f"Duplicate app routes found: {dup[:20]}")

    elif focus == "proof_files":
        required = [
            "reports/latest/autopilot_proof_board/summary.json",
            "reports/latest/dashboard_visible_issue_tracker/summary.json",
            "reports/latest/workflow_failure_tracker/summary.json",
            "reports/latest/todo_status_update/summary.json",
            "reports/latest/system3_public_truth/index.md",
        ]
        missing = [p for p in required if not (ROOT / p).exists()]
        evidence["missing"] = missing
        if missing:
            add_issue(issues, f"Required proof files missing: {missing}")

    elif focus == "mobile_responsive":
        # Static proof that mobile screenshot/check exists in visual tooling.
        tracker = read("tools/dashboard_live_ui_proof.mjs") + read("tools/dashboard_visible_issue_tracker.mjs")
        evidence["has_mobile_390x844"] = "390" in tracker and "844" in tracker
        if not evidence["has_mobile_390x844"]:
            add_issue(issues, "Mobile 390x844 visual proof not found in visual tooling.")

    status = "PASS" if not issues else "BLOCKED"
    return {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "agent_id": f"{agent_id:03d}",
        "focus": focus,
        "pass": pass_num,
        "status": status,
        "issue_count": len(issues),
        "issues": issues,
        "findings": findings,
        "evidence": evidence,
        "live_trading_enabled": False,
        "order_routes_called": False,
        "secrets_printed": False,
        "production_grade_claim_allowed": False,
    }


def aggregate() -> Dict[str, Any]:
    OUT.mkdir(parents=True, exist_ok=True)
    agents = []
    for p in sorted(OUT.glob("agent_*.json")):
        try:
            agents.append(json.loads(p.read_text(encoding="utf-8")))
        except Exception:
            pass
    issues = []
    by_focus: Dict[str, Dict[str, Any]] = {}
    for a in agents:
        f = a.get("focus", "unknown")
        by_focus.setdefault(f, {"agents": 0, "blocked": 0, "issues": 0})
        by_focus[f]["agents"] += 1
        by_focus[f]["issues"] += int(a.get("issue_count") or 0)
        if a.get("status") != "PASS":
            by_focus[f]["blocked"] += 1
        for i in a.get("issues", []):
            issues.append(f"agent_{a.get('agent_id')}:{f}: {i}")
    payload = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if agents and not issues and len(agents) >= 100 else "BLOCKED",
        "agents_reported": len(agents),
        "expected_agents": 100,
        "issue_count": len(issues),
        "issues": issues[:1000],
        "by_focus": by_focus,
        "live_trading_enabled": False,
        "order_routes_called": False,
        "secrets_printed": False,
        "production_grade_claim_allowed": False,
    }
    (OUT / "summary.json").write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    md = [
        "# System3 Render 100-Agent Swarm Summary",
        "",
        f"Generated UTC: `{payload['generated_utc']}`",
        f"Status: **{payload['status']}**",
        f"Agents reported: `{payload['agents_reported']}/{payload['expected_agents']}`",
        f"Issue count: `{payload['issue_count']}`",
        "",
        "## Focus summary",
        "",
        "| Focus | Agents | Blocked | Issues |",
        "|---|---:|---:|---:|",
    ]
    for f, row in sorted(by_focus.items()):
        md.append(f"| {f} | {row['agents']} | {row['blocked']} | {row['issues']} |")
    md += ["", "## Issues", ""]
    md += [f"- [ ] {x}" for x in payload["issues"]] or ["- [x] None"]
    (OUT / "summary.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--agent-id", type=int, default=0)
    ap.add_argument("--aggregate", action="store_true")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if args.aggregate:
        payload = aggregate()
    else:
        if not (1 <= args.agent_id <= 100):
            raise SystemExit("--agent-id must be 1..100")
        payload = audit_agent(args.agent_id)
        p = OUT / f"agent_{args.agent_id:03d}.json"
        p.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        md = [f"# Render Swarm Agent {args.agent_id:03d}", "", f"Focus: `{payload['focus']}`", f"Status: **{payload['status']}**", f"Issues: `{payload['issue_count']}`", "", "## Issues"]
        md += [f"- [ ] {x}" for x in payload["issues"]] or ["- [x] None"]
        (OUT / f"agent_{args.agent_id:03d}.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2)[:12000])
    return 0 if payload.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
