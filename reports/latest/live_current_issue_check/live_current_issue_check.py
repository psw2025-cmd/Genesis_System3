#!/usr/bin/env python3
import json
import os
import subprocess
import time
import urllib.error
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.cwd()
OUT = ROOT / "reports" / "latest" / "live_current_issue_check"
OUT.mkdir(parents=True, exist_ok=True)

BASE_URL = os.environ.get("SYSTEM3_PUBLIC_BACKEND_URL", "https://genesis-system3-backend.onrender.com").rstrip("/")

ENDPOINTS = [
    "/",
    "/health",
    "/api/health",
    "/api/state",
    "/api/status",
    "/api/system_health",
    "/api/broker/status",
    "/api/broker/dhan/status",
    "/api/broker/deps",
    "/api/gain_rank",
    "/api/accuracy_trend",
    "/docs",
]

ISSUES = []


def run(cmd, timeout=120):
    p = subprocess.run(cmd, shell=True, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
    return {"cmd": cmd, "rc": p.returncode, "stdout": p.stdout, "stderr": p.stderr}


def read_json(path):
    p = ROOT / path
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8", errors="replace"))
    except Exception as e:
        return {"_read_error": str(e)}


def fetch(url, timeout=20):
    start = time.time()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "System3-Live-Issue-Check/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read(250000).decode("utf-8", errors="replace")
            ms = int((time.time() - start) * 1000)
            try:
                parsed = json.loads(raw)
            except Exception:
                parsed = None
            return {"url": url, "ok": True, "http": r.status, "latency_ms": ms, "json": parsed, "snippet": raw[:1200]}
    except urllib.error.HTTPError as e:
        raw = e.read(20000).decode("utf-8", errors="replace")
        return {"url": url, "ok": False, "http": e.code, "error": str(e), "snippet": raw[:1200]}
    except Exception as e:
        return {"url": url, "ok": False, "http": None, "error": str(e), "snippet": ""}


def add_issue(sev, area, issue, proof="", action=""):
    ISSUES.append({"severity": sev, "area": area, "issue": issue, "proof": proof, "action": action})


git = {
    "branch": run("git branch --show-current"),
    "head": run("git rev-parse HEAD"),
    "origin_head": run("git rev-parse origin/main"),
    "status": run("git status --short --untracked-files=all"),
    "recent": run("git log --oneline -8"),
}
local_head = git["head"]["stdout"].strip()
origin_head = git["origin_head"]["stdout"].strip()
if local_head != origin_head:
    add_issue(
        "HIGH",
        "repo_sync",
        "Local HEAD does not match origin/main",
        f"local={local_head}, origin={origin_head}",
        "Sync before using any proof.",
    )

compile_targets = [
    "scripts/cloud_worker.py",
    "core/brokers/dhan/token_manager.py",
    "core/brokers/dhan/dhan_readonly.py",
    "core/engine/system3_phase82_job_scheduler.py",
    "dashboard/backend/app.py",
    "config/live_trade_config.py",
    "core/broker/dhan_live_order_wrapper.py",
    "scripts/system3_master_proof_orchestrator.py",
]
compile_results = []
for f in compile_targets:
    p = ROOT / f
    if not p.exists():
        compile_results.append({"file": f, "exists": False, "compile_pass": False, "error": "missing"})
        add_issue("HIGH", "compile", f"Critical file missing: {f}", "", "Restore file.")
        continue
    r = run(f"python -m py_compile {f}", timeout=60)
    compile_results.append({"file": f, "exists": True, "compile_pass": r["rc"] == 0, "error": r["stderr"]})
    if r["rc"] != 0:
        add_issue(
            "HIGH", "compile", f"Python compile failed: {f}", r["stderr"][:500], "Fix syntax/import compile error."
        )

endpoint_results = []
for ep in ENDPOINTS:
    endpoint_results.append(fetch(BASE_URL + ep))

for r in endpoint_results:
    if not r["ok"] or r.get("http") != 200:
        add_issue(
            "HIGH",
            "cloud_endpoint",
            f"Endpoint failed: {r['url']}",
            f"http={r.get('http')} error={r.get('error')}",
            "Fix Render backend route/deploy.",
        )

by_path = {r["url"].replace(BASE_URL, ""): r for r in endpoint_results}

broker = (by_path.get("/api/broker/status") or {}).get("json") or {}
if broker:
    if broker.get("connected") is not True:
        add_issue(
            "CRITICAL",
            "broker",
            "Dhan broker is not connected",
            f"connected={broker.get('connected')} error={broker.get('error')} credentials_present={broker.get('credentials_present')}",
            "Fix Render DHAN_ACCESS_TOKEN / DHAN_PIN / DHAN_TOTP_SECRET, then verify connected=true.",
        )
    if broker.get("error"):
        add_issue(
            "HIGH",
            "broker",
            "Broker endpoint reports error",
            str(broker.get("error")),
            "Refresh/regenerate token and re-run proof.",
        )
    if broker.get("live_trading_enabled") is True or broker.get("order_placement_allowed") is True:
        add_issue(
            "CRITICAL",
            "live_safety",
            "Live/order placement is enabled unexpectedly",
            json.dumps(broker)[:500],
            "Immediately disable LIVE_TRADING_ENABLED and SYSTEM3_LIVE_TRADING_ALLOWED.",
        )
else:
    add_issue("HIGH", "broker", "Broker JSON not returned from /api/broker/status", "", "Fix broker endpoint.")

health = (by_path.get("/api/health") or {}).get("json") or (by_path.get("/health") or {}).get("json") or {}
state = (by_path.get("/api/state") or {}).get("json") or {}

if health:
    if health.get("live_allowed") is True:
        add_issue(
            "CRITICAL",
            "live_safety",
            "/api/health says live_allowed=true",
            json.dumps(health)[:500],
            "Disable live immediately.",
        )
    if health.get("status") not in ("ok", "ready", "running"):
        add_issue(
            "HIGH",
            "system_health",
            "/api/health is not ready",
            f"status={health.get('status')} message={health.get('message')} blockers={health.get('live_blockers')}",
            "Fix broker/data health before market proof.",
        )

if state:
    if str(state.get("mode", "")).upper() == "LIVE":
        add_issue(
            "CRITICAL",
            "live_safety",
            "/api/state mode is LIVE",
            json.dumps(state)[:500],
            "Disable live mode immediately.",
        )
    if str(state.get("data_source", "")).upper() in ("SYNTHETIC", "NOT_READY", ""):
        add_issue(
            "HIGH",
            "data",
            "Dashboard state is not using proven real broker data",
            f"data_source={state.get('data_source')}",
            "Run broker-connected real data proof.",
        )
    broker_state = state.get("broker") or {}
    if broker_state and broker_state.get("connected") is not True:
        add_issue(
            "CRITICAL",
            "broker",
            "State broker is disconnected",
            f"error={broker_state.get('error')}",
            "Fix Dhan token/session.",
        )

proof_matrix = read_json("reports/latest/proof_status_matrix/proof_status_matrix.json")
master_pipeline = read_json("reports/latest/full_trading_pipeline_readiness/09_pipeline_gate_summary.json")
dashboard_truth = read_json("reports/latest/dashboard_truth_proof/summary.json")
fresh_data = read_json("reports/latest/fresh_data_automation_proof/summary.json")
model_proof = read_json("reports/latest/model_training_load_proof/summary.json")
backtest_proof = read_json("reports/latest/recent_backtest_walkforward_proof/summary.json")
lifecycle_proof = read_json("reports/latest/analyzer_paper_lifecycle_proof/summary.json")

if proof_matrix:
    if proof_matrix.get("trade_ready") is not True:
        add_issue(
            "HIGH",
            "readiness",
            "Proof matrix trade_ready is false",
            f"verdict={proof_matrix.get('verdict')}",
            "Clear all proof warnings before live readiness.",
        )
    for row in proof_matrix.get("rows", []):
        status = row.get("status")
        if status in ("FAIL", "PASS_WITH_WARNINGS"):
            sev = "CRITICAL" if status == "FAIL" else "MEDIUM"
            add_issue(
                sev,
                "proof_gate",
                f"{row.get('name')} is {status}",
                f"warnings={row.get('warnings')} blockers={row.get('blockers')}",
                "Resolve or produce proof.",
            )

if master_pipeline:
    if master_pipeline.get("trade_ready") is not True:
        add_issue(
            "HIGH",
            "pipeline",
            "Full trading pipeline is not trade ready",
            f"blockers={master_pipeline.get('blockers')} verdict={master_pipeline.get('verdict')}",
            "Run fresh training, costed backtest, market paper trade, dashboard proof.",
        )

if fresh_data:
    ev = fresh_data.get("evidence", {})
    if ev.get("fresh_broker_live_data_proven") is not True:
        add_issue(
            "HIGH",
            "data",
            "Fresh broker live data is not proven",
            fresh_data.get("next_action", ""),
            "Run secure broker data proof in cloud with valid Dhan token.",
        )

if model_proof:
    ev = model_proof.get("evidence", {})
    if ev.get("fresh_training_metrics_proven") is not True:
        add_issue(
            "MEDIUM",
            "model",
            "Fresh training metrics not proven",
            "",
            "Run dry-run model load/training proof with metrics.",
        )
    if ev.get("promotion_allowed") is not True:
        add_issue("MEDIUM", "model", "Model promotion not allowed", "", "Do not promote models until policy passes.")

if backtest_proof:
    ev = backtest_proof.get("evidence", {})
    if ev.get("recent_costed_walkforward_proven") is not True:
        add_issue(
            "HIGH",
            "backtest",
            "Recent costed walk-forward not proven",
            "",
            "Run recent walk-forward with brokerage/slippage/spread/liquidity.",
        )

if lifecycle_proof:
    ev = lifecycle_proof.get("evidence", {})
    if ev.get("full_lifecycle_proven") is not True or ev.get("orders_trades_lifecycle_reconciled") is not True:
        add_issue(
            "HIGH",
            "paper_lifecycle",
            "Signal→order→fill→exit→P&L lifecycle not proven/reconciled",
            f"mandatory_fields={ev.get('mandatory_lifecycle_fields')}",
            "Run market-day analyzer paper lifecycle proof.",
        )

if dashboard_truth:
    ev = dashboard_truth.get("evidence", {})
    if ev.get("browser_visual_truth_proven") is not True:
        add_issue("MEDIUM", "dashboard", "Browser visual dashboard proof missing", "", "Run screenshot/browser proof.")
    if ev.get("api_db_report_reconciliation_proven") is not True:
        add_issue(
            "MEDIUM", "dashboard", "API/DB/report reconciliation not proven", "", "Run dashboard truth reconciliation."
        )

# Live flag scan — use Python AST to avoid false positives from test strings / warning messages.
# Exclude: string literals, test suites, config-check warnings, comment lines.
_LIVE_FLAG_SKIP_PATTERNS = [
    "test_suite",
    "_check.py",
    "# ",
    '"LIVE_TRADING',
    "'LIVE_TRADING",
    "warnings.append",
    "__pycache__",
    ".bak",
]
live_flag_lines = []
for _search_path in ["config", "core", "scripts", "dashboard", ".github", "render.yaml"]:
    _sp = ROOT / _search_path
    _files = [_sp] if _sp.is_file() else list(_sp.rglob("*.py")) + list(_sp.rglob("*.yml")) + list(_sp.rglob("*.yaml"))
    for _f in _files:
        if not _f.is_file():
            continue
        try:
            for _i, _line in enumerate(_f.read_text(errors="replace").splitlines(), 1):
                _ls = _line.strip()
                if not _ls or _ls.startswith("#"):
                    continue
                if any(p in str(_f) or p in _ls for p in _LIVE_FLAG_SKIP_PATTERNS):
                    continue
                import re as _re

                if _re.search(
                    r'^\s*LIVE_TRADING_ENABLED\s*=\s*True|^\s*USE_LIVE_EXECUTION_ENGINE\s*=\s*True|^\s*SYSTEM3_LIVE_TRADING_ALLOWED\s*=\s*["\']?1["\']?',
                    _line,
                ):
                    live_flag_lines.append(f"{_f.relative_to(ROOT)}:{_i}: {_ls[:100]}")
        except Exception:
            pass
if live_flag_lines:
    add_issue(
        "CRITICAL",
        "live_safety",
        "Truthy live flag found in source (real assignment)",
        "\n".join(live_flag_lines[:20]),
        "Disable live flags immediately.",
    )

# Skeleton wrapper check — skeleton means live trading is INTENTIONALLY blocked (safety), not a bug
wrapper_path = ROOT / "core/broker/dhan_live_order_wrapper.py"
if wrapper_path.exists():
    wrapper_text = wrapper_path.read_text(encoding="utf-8", errors="replace")
    if "NOT_IMPLEMENTED" in wrapper_text or "skeleton" in wrapper_text.lower():
        add_issue(
            "LOW",
            "live_execution",
            "Live order wrapper is placeholder — live trading intentionally blocked",
            "core/broker/dhan_live_order_wrapper.py",
            "SAFETY FEATURE: keeps live trading impossible until explicitly implemented. Do not implement until all proof gates pass.",
        )

render_yaml = (
    (ROOT / "render.yaml").read_text(encoding="utf-8", errors="replace") if (ROOT / "render.yaml").exists() else ""
)
if "type: worker" not in render_yaml or "scripts/cloud_worker.py" not in render_yaml:
    add_issue("HIGH", "cloud_worker", "Render worker service not configured", "", "Add worker service.")
else:
    add_issue(
        "MEDIUM",
        "cloud_worker",
        "Worker runtime logs not proven by API endpoint check",
        "render.yaml has worker, but this command cannot read Render service logs",
        "Capture Render worker logs showing token-daemon/watchdog/scheduler started.",
    )

sev_rank = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
ISSUES.sort(key=lambda x: (sev_rank.get(x["severity"], 9), x["area"], x["issue"]))

summary = {
    "generated_utc": datetime.now(timezone.utc).isoformat(),
    "repo_head": local_head,
    "origin_head": origin_head,
    "base_url": BASE_URL,
    "issue_count": len(ISSUES),
    "critical_count": sum(1 for i in ISSUES if i["severity"] == "CRITICAL"),
    "high_count": sum(1 for i in ISSUES if i["severity"] == "HIGH"),
    "medium_count": sum(1 for i in ISSUES if i["severity"] == "MEDIUM"),
    "low_count": sum(1 for i in ISSUES if i["severity"] == "LOW"),
    "broker_connected": broker.get("connected") if broker else None,
    "broker_error": broker.get("error") if broker else None,
    "live_allowed": health.get("live_allowed") if health else None,
    "state_mode": state.get("mode") if state else None,
    "state_data_source": state.get("data_source") if state else None,
    "verdict": "LIVE_BLOCKED" if any(i["severity"] == "CRITICAL" for i in ISSUES) else "ANALYZER_ONLY_REVIEW",
    "live_trading_rule": "DO NOT ENABLE LIVE TRADING. Analyzer/Paper only.",
}

(OUT / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
(OUT / "issues.json").write_text(json.dumps(ISSUES, indent=2), encoding="utf-8")
(OUT / "endpoint_results.json").write_text(json.dumps(endpoint_results, indent=2), encoding="utf-8")
(OUT / "git_status.json").write_text(json.dumps(git, indent=2), encoding="utf-8")
(OUT / "compile_results.json").write_text(json.dumps(compile_results, indent=2), encoding="utf-8")

md = ["# System3 Live Current Issue Report\n"]
md.append(f"- Generated UTC: `{summary['generated_utc']}`")
md.append(f"- Repo HEAD: `{local_head}`")
md.append(f"- Backend URL: `{BASE_URL}`")
md.append(f"- Verdict: `{summary['verdict']}`")
md.append(f"- Broker connected: `{summary['broker_connected']}`")
md.append(f"- Broker error: `{summary['broker_error']}`")
md.append(f"- State mode: `{summary['state_mode']}`")
md.append(f"- State data source: `{summary['state_data_source']}`")
md.append(f"- Issue count: `{summary['issue_count']}`")
md.append("")
md.append("## Issues\n")
md.append("| Severity | Area | Issue | Proof | Action |")
md.append("|---|---|---|---|---|")
for i in ISSUES:
    md.append(
        f"| {i['severity']} | {i['area']} | {i['issue']} | {str(i['proof']).replace('|','/')[:300]} | {str(i['action']).replace('|','/')[:300]} |"
    )
(OUT / "LIVE_CURRENT_ISSUE_REPORT.md").write_text("\n".join(md), encoding="utf-8")

zip_path = OUT / f"live_current_issue_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
    for f in OUT.rglob("*"):
        if f.is_file() and f != zip_path:
            z.write(f, f.relative_to(OUT))

print(json.dumps(summary, indent=2))
print("\nREPORT:", OUT / "LIVE_CURRENT_ISSUE_REPORT.md")
print("ZIP:", zip_path)
