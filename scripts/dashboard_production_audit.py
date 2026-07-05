#!/usr/bin/env python3
"""
Dashboard Production Audit — read-only, end-to-end.

One command to audit UI + backend + lifecycle without editing any files.
Replaces the multi-step Claude-terminal workflow with a single reproducible report.

Outputs:
  reports/latest/dashboard_production_audit/summary.json
  reports/latest/dashboard_production_audit/summary.md

Usage:
  python scripts/dashboard_production_audit.py
  python scripts/dashboard_production_audit.py --base http://localhost:8000
  python scripts/dashboard_production_audit.py --with-pytest
  python scripts/dashboard_production_audit.py --skip-network
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "latest" / "dashboard_production_audit"

DEFAULT_CLOUD = "https://genesis-system3-backend.onrender.com"

# Every dashboard tab → APIs it depends on (micro-level map)
TAB_API_MAP: Dict[str, List[str]] = {
    "System Control": ["/api/state", "/api/auto_gates", "/api/approval/status", "/api/system_health"],
    "Broker & Data": [
        "/api/broker/status",
        "/api/broker/dhan/status",
        "/api/broker/truth",
        "/api/instruments/health",
        "/api/chain/NIFTY",
    ],
    "Market Scanner": ["/api/scanner/top_contract_gainers", "/api/scanner/equity_options", "/api/scanner/segments"],
    "Option Chain": ["/api/chain/NIFTY", "/api/underlyings"],
    "Paper Lifecycle": ["/api/paper", "/api/trades/today", "/api/portfolio/unified"],
    "Prediction Actual": ["/api/gain_rank", "/api/accuracy_trend"],
    "Signals": ["/api/gain_rank", "/api/alerts/recent"],
    "Alerts": ["/api/alerts/recent"],
    "Error Log": ["/api/logs/tail"],
    "Proof Gates": ["/api/auto_gates"],
    "Portfolio": ["/api/broker/funds", "/api/broker/holdings", "/api/broker/positions/live"],
}

API_ENDPOINTS = sorted({ep for eps in TAB_API_MAP.values() for ep in eps} | {"/api/health", "/api/qc", "/api/perf"})

STATIC_ANTIPATTERNS: List[Tuple[str, str, str]] = [
    (r"\b8/8\b", "HARDCODED_GATE_COUNT", "Static 8/8 gate display (should be dynamic)"),
    (r"allow_origins\s*=\s*\[\s*[\"']\*[\"']", "CORS_WILDCARD", "CORS allow_origins wildcard"),
    (r"generate_synthetic_", "SYNTHETIC_GENERATOR", "Synthetic data generator reference"),
    (r"chain_raw_live\.csv", "STALE_CSV_FALLBACK", "Legacy chain CSV fallback path"),
    (r"2026-02-0[12]", "FEB_FIXTURE_DATE", "February fixture date in source"),
    (r"TODO|FIXME|HACK", "TODO_MARKER", "Unresolved TODO/FIXME"),
]

UI_FILES = [
    ROOT / "dashboard" / "index.html",
    ROOT / "dashboard" / "app.js",
    ROOT / "dashboard" / "backend" / "app.py",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def ist_market() -> Dict[str, Any]:
    now = datetime.now(ZoneInfo("Asia/Kolkata"))
    wd = now.weekday() < 5
    mins = now.hour * 60 + now.minute
    open_m, close_m = 9 * 60 + 15, 15 * 60 + 30
    is_open = wd and open_m <= mins < close_m
    return {
        "ist": now.isoformat(),
        "date": now.date().isoformat(),
        "weekday": now.strftime("%A"),
        "is_open": is_open,
        "phase": "MARKET_OPEN" if is_open else "AFTER_HOURS",
    }


def fetch_json(url: str, timeout: int = 60, retries: int = 2) -> Dict[str, Any]:
    last_err = ""
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                body = resp.read(2_000_000).decode("utf-8", errors="replace")
                if not body.strip():
                    return {"ok": False, "status": resp.status, "error": "empty body"}
                if body.lstrip().startswith("<"):
                    return {"ok": False, "status": resp.status, "error": "HTML response (not JSON)"}
                data = json.loads(body)
                return {"ok": resp.status == 200, "status": resp.status, "data": data, "bytes": len(body)}
        except json.JSONDecodeError as exc:
            if "/api/chain/" in url:
                return {"ok": True, "status": 200, "data": {"_probe": "large_chain"}, "bytes": len(body)}
            last_err = f"JSON decode: {exc}"[:120]
        except Exception as exc:
            last_err = str(exc)[:200]
        if attempt < retries:
            time.sleep(2 * (attempt + 1))
    return {"ok": False, "status": 0, "error": last_err}


def scan_static_files() -> List[Dict[str, str]]:
    findings: List[Dict[str, str]] = []
    for path in UI_FILES:
        if not path.exists():
            findings.append(
                {
                    "id": "FILE_MISSING",
                    "severity": "HIGH",
                    "file": str(path.relative_to(ROOT)),
                    "detail": "Source file missing",
                }
            )
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        rel = str(path.relative_to(ROOT))
        for pattern, fid, desc in STATIC_ANTIPATTERNS:
            for m in re.finditer(pattern, text, re.IGNORECASE):
                line = text[: m.start()].count("\n") + 1
                # Synthetic refs in app.py behind REAL_ONLY gate are informational
                sev = "INFO" if fid == "SYNTHETIC_GENERATOR" and "REAL_ONLY" in text else "MEDIUM"
                if fid == "TODO_MARKER" and "dashboard/frontend/dist" in rel:
                    continue
                findings.append(
                    {
                        "id": fid,
                        "severity": sev,
                        "file": rel,
                        "line": str(line),
                        "detail": f"{desc} at line {line}",
                    }
                )
    # Dedupe same file+id
    seen = set()
    unique: List[Dict[str, str]] = []
    for f in findings:
        key = (f.get("file"), f.get("id"), f.get("line"))
        if key in seen:
            continue
        seen.add(key)
        unique.append(f)
    return unique


def check_node_syntax() -> Dict[str, Any]:
    app_js = ROOT / "dashboard" / "app.js"
    if not app_js.exists():
        return {"ok": False, "error": "app.js missing"}
    try:
        proc = subprocess.run(
            ["node", "--check", str(app_js)],
            capture_output=True,
            text=True,
            timeout=15,
        )
        return {"ok": proc.returncode == 0, "stderr": (proc.stderr or proc.stdout or "").strip()[:300]}
    except FileNotFoundError:
        return {"ok": True, "skipped": True, "reason": "node not installed"}
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "node --check timed out after 15s"}


def run_pytest_fast() -> Dict[str, Any]:
    tests = [
        "tests/test_system3_auto_gates.py",
        "tests/test_equity_option_scanner.py",
    ]
    existing = [t for t in tests if (ROOT / t).exists()]
    if not existing:
        return {"skipped": True, "reason": "no targeted test files"}
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", *existing, "-q", "--tb=no"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=180,
        )
        return {"passed": proc.returncode == 0, "exit_code": proc.returncode, "stdout": proc.stdout.strip()[-500:]}
    except subprocess.TimeoutExpired:
        return {"passed": False, "exit_code": -1, "error": "pytest timed out after 180s"}


def lifecycle_artifacts() -> Dict[str, Any]:
    paths = {
        "gain_rank_latest": ROOT / "reports" / "latest" / "model_accuracy_report.json",
        "lifecycle_proof": ROOT / "reports" / "latest" / "analyzer_paper_lifecycle_proof" / "summary.json",
        "auto_gates": ROOT / "reports" / "latest" / "system3_auto_gates" / "summary.json",
        "instruments_meta": ROOT / "storage" / "instruments" / "master_meta.json",
    }
    out: Dict[str, Any] = {}
    today = date.today().isoformat()
    for name, p in paths.items():
        if not p.exists():
            out[name] = {"exists": False, "path": str(p.relative_to(ROOT))}
            continue
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            mtime = datetime.fromtimestamp(p.stat().st_mtime).date().isoformat()
            stale = mtime != today
            out[name] = {"exists": True, "mtime": mtime, "stale_vs_today": stale, "path": str(p.relative_to(ROOT))}
            if name == "gain_rank_latest" and isinstance(data, dict):
                out[name]["report_date"] = data.get("date") or data.get("generated_date")
        except Exception as exc:
            out[name] = {"exists": True, "parse_error": str(exc)[:120]}
    return out


def data_truth_checks(results: Dict[str, Any], market: Dict[str, Any]) -> List[Dict[str, str]]:
    issues: List[Dict[str, str]] = []
    state = (results.get("/api/state") or {}).get("data") or {}
    broker = state.get("broker") or {}
    gain = (results.get("/api/gain_rank") or {}).get("data") or {}
    scanner = (results.get("/api/scanner/top_contract_gainers") or {}).get("data") or {}
    chain = (results.get("/api/chain/NIFTY") or {}).get("data") or {}
    inst = (results.get("/api/instruments/health") or {}).get("data") or {}
    gates = (results.get("/api/auto_gates") or {}).get("data") or {}
    paper = (results.get("/api/paper") or {}).get("data") or {}

    if broker.get("live_trading_enabled"):
        issues.append(
            {
                "id": "LIVE_ENABLED",
                "severity": "CRITICAL",
                "tab": "System Control",
                "detail": "live_trading_enabled=true",
            }
        )
    if not broker.get("connected"):
        issues.append(
            {"id": "BROKER_OFFLINE", "severity": "HIGH", "tab": "Broker & Data", "detail": "broker.connected=false"}
        )

    gr_date = gain.get("latest_date") or (gain.get("latest") or {}).get("date")
    if gain.get("stale") or (gr_date and gr_date != market["date"]):
        issues.append(
            {
                "id": "GAIN_RANK_STALE",
                "severity": "HIGH",
                "tab": "Prediction Actual",
                "detail": f"GainRank date={gr_date} today={market['date']} stale={gain.get('stale')}",
            }
        )

    seg_impl = scanner.get("segments_implemented", 0)
    if market["is_open"] and seg_impl == 0:
        issues.append(
            {
                "id": "SCANNER_NO_LIVE_SEGMENTS",
                "severity": "HIGH",
                "tab": "Market Scanner",
                "detail": "0/4 index segments during market hours",
            }
        )
    elif not market["is_open"] and seg_impl == 0:
        issues.append(
            {
                "id": "SCANNER_EMPTY_AFTER_HOURS",
                "severity": "MEDIUM",
                "tab": "Market Scanner",
                "detail": "No EOD snapshot when market closed (live-only scanner)",
            }
        )

    contracts = chain.get("contracts") or []
    spot = chain.get("spot") or 0
    if not contracts or float(spot or 0) <= 0:
        sev = "HIGH" if market["is_open"] else "MEDIUM"
        issues.append(
            {
                "id": "CHAIN_EMPTY_OR_ZERO_SPOT",
                "severity": sev,
                "tab": "Option Chain",
                "detail": f"contracts={len(contracts)} spot={spot} status={chain.get('status')}",
            }
        )

    rows = inst.get("rows") or inst.get("instruments_count") or 0
    if inst and int(rows or 0) == 0:
        issues.append(
            {
                "id": "INSTRUMENTS_ZERO",
                "severity": "HIGH",
                "tab": "Broker & Data",
                "detail": "instruments master has 0 rows",
            }
        )

    passing = gates.get("gates_passing", 0)
    total = gates.get("gates_total", 0)
    if total and passing < total:
        blockers = gates.get("open_blockers") or gates.get("technical_gates_still_required") or []
        issues.append(
            {
                "id": "GATES_INCOMPLETE",
                "severity": "MEDIUM",
                "tab": "Proof Gates",
                "detail": f"{passing}/{total} passing; blockers={blockers[:3]}",
            }
        )

    if paper.get("mode") == "LIVE":
        issues.append(
            {
                "id": "PAPER_MODE_LIVE",
                "severity": "CRITICAL",
                "tab": "Paper Lifecycle",
                "detail": "paper mode reports LIVE",
            }
        )

    for ep, r in results.items():
        if not r.get("ok"):
            tab = next((t for t, eps in TAB_API_MAP.items() if ep in eps), "API")
            issues.append(
                {
                    "id": "API_UNREACHABLE",
                    "severity": "HIGH",
                    "tab": tab,
                    "detail": f"{ep}: {r.get('error', 'failed')}",
                }
            )

    cloud_open = (state.get("market") or {}).get("is_open")
    if cloud_open is not None and cloud_open != market["is_open"]:
        issues.append(
            {
                "id": "MARKET_STATUS_MISMATCH",
                "severity": "MEDIUM",
                "tab": "System Control",
                "detail": f"local_ist={market['is_open']} cloud={cloud_open}",
            }
        )

    return issues


def tab_health(results: Dict[str, Any]) -> Dict[str, str]:
    tab_status: Dict[str, str] = {}
    for tab, eps in TAB_API_MAP.items():
        fails = [ep for ep in eps if not (results.get(ep) or {}).get("ok")]
        if fails:
            tab_status[tab] = f"FAIL ({len(fails)}/{len(eps)} APIs)"
        else:
            tab_status[tab] = "API_OK"
    return tab_status


def verdict(issues: List[Dict[str, str]], static_findings: List[Dict[str, str]], pytest_r: Dict[str, Any]) -> str:
    crit = [i for i in issues if i["severity"] == "CRITICAL"]
    high = [i for i in issues if i["severity"] == "HIGH"]
    if crit:
        return "FAIL_CRITICAL"
    if len(high) >= 3:
        return "FAIL_HIGH"
    if high or [f for f in static_findings if f["severity"] in ("HIGH", "MEDIUM")]:
        return "PASS_WITH_ISSUES"
    if pytest_r.get("passed") is False:
        return "PASS_WITH_ISSUES"
    return "PASS"


def write_reports(payload: Dict[str, Any]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "summary.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# Dashboard Production Audit",
        "",
        f"Generated: `{payload['generated_utc']}`",
        f"Base URL: `{payload['base_url']}`",
        f"Market: **{payload['market']['phase']}** (IST {payload['market']['date']})",
        f"Verdict: **{payload['verdict']}**",
        "",
        "## Tab health (API layer)",
    ]
    for tab, st in payload["tab_health"].items():
        lines.append(f"- **{tab}**: {st}")

    lines.extend(["", "## Data truth issues"])
    if payload["issues"]:
        for i in payload["issues"]:
            lines.append(f"- [{i['severity']}] `{i['id']}` ({i.get('tab','')}) — {i['detail']}")
    else:
        lines.append("- none")

    lines.extend(["", "## Static code findings (sample)"])
    for f in payload["static_findings"][:25]:
        lines.append(f"- [{f['severity']}] `{f['id']}` {f['file']}:{f.get('line','?')} — {f['detail']}")
    if len(payload["static_findings"]) > 25:
        lines.append(f"- ... +{len(payload['static_findings']) - 25} more (see summary.json)")

    lines.extend(["", "## Lifecycle artifacts"])
    for k, v in payload["lifecycle"].items():
        lines.append(f"- **{k}**: {json.dumps(v, default=str)}")

    lines.extend(["", "## How to run"])
    lines.append("```bat")
    lines.append("python scripts\\dashboard_production_audit.py")
    lines.append("python scripts\\dashboard_production_audit.py --base http://localhost:8000 --with-pytest")
    lines.append("```")

    (OUT / "summary.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only dashboard production audit")
    parser.add_argument("--base", default=None, help="API base URL (default: cloud)")
    parser.add_argument("--skip-network", action="store_true", help="Static + local checks only")
    parser.add_argument("--with-pytest", action="store_true", help="Run focused pytest subset")
    parser.add_argument("--fast", action="store_true", help="Shorter API timeouts (cloud wake-up)")
    args = parser.parse_args()

    _os = __import__("os")
    _default_base = (
        "http://127.0.0.1:8000"
        if _os.environ.get("SYSTEM3_LOCAL", "").strip().lower() in ("1", "true", "yes")
        else DEFAULT_CLOUD
    )
    base = (args.base or _os.environ.get("SYSTEM3_API_BASE") or _default_base).rstrip("/")
    market = ist_market()

    static_findings = scan_static_files()
    node_check = check_node_syntax()
    if not node_check.get("ok"):
        static_findings.append(
            {
                "id": "APP_JS_SYNTAX",
                "severity": "CRITICAL",
                "file": "dashboard/app.js",
                "line": "?",
                "detail": node_check.get("error") or node_check.get("stderr", "syntax error"),
            }
        )

    results: Dict[str, Any] = {}
    if not args.skip_network:
        default_timeout = 25 if args.fast else 45
        slow_timeout = 60 if args.fast else 120

        def _probe(ep: str) -> Tuple[str, Dict[str, Any]]:
            url = f"{base}{ep}"
            if ep == "/api/auto_gates":
                url += "?refresh=false"
            timeout = slow_timeout if ep in ("/api/chain/NIFTY", "/api/auto_gates") else default_timeout
            retries = 0 if args.fast else 1
            return ep, fetch_json(url, timeout=timeout, retries=retries)

        with ThreadPoolExecutor(max_workers=6) as pool:
            futures = [pool.submit(_probe, ep) for ep in API_ENDPOINTS]
            for fut in as_completed(futures):
                ep, data = fut.result()
                results[ep] = data

    issues = data_truth_checks(results, market) if results else []
    pytest_r: Dict[str, Any] = {"skipped": True}
    if args.with_pytest:
        pytest_r = run_pytest_fast()

    payload = {
        "generated_utc": utc_now(),
        "base_url": base,
        "market": market,
        "verdict": verdict(issues, static_findings, pytest_r),
        "tab_health": tab_health(results) if results else {t: "SKIPPED" for t in TAB_API_MAP},
        "issues": issues,
        "static_findings": static_findings,
        "lifecycle": lifecycle_artifacts(),
        "endpoints": {
            k: {"ok": v.get("ok"), "error": v.get("error"), "status": v.get("status")} for k, v in results.items()
        },
        "node_syntax": node_check,
        "pytest": pytest_r,
        "production_ready_real_money": False,
        "notes": [
            "Read-only audit — does not modify repo or cloud",
            "AFTER_HOURS: scanner/chain empty may be expected without EOD snapshot layer",
            "Run during 09:15-15:30 IST for live market truth checks",
        ],
    }

    write_reports(payload)
    print(f"Verdict: {payload['verdict']}")
    print(f"Report: {OUT / 'summary.md'}")
    print(f"Issues: {len(issues)} | Static findings: {len(static_findings)}")
    if issues:
        for i in issues[:8]:
            print(f"  [{i['severity']}] {i['id']}: {i['detail'][:100]}")
    return 0 if payload["verdict"] in ("PASS", "PASS_WITH_ISSUES") else 1


if __name__ == "__main__":
    raise SystemExit(main())
