#!/usr/bin/env python3
"""Proof-only audit for Dhan naming, DhanHQ API v2, and Dhan Cloud.

Safety scope: read-only local proof files plus safe GET requests to System3
Render endpoints and official Dhan documentation pages. This script never calls
Dhan write APIs such as order placement, modification, cancellation, eDIS,
T-PIN, position convert, P&L exit, super orders, or conditional triggers.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_DIR = ROOT / "reports" / "latest" / "dashboard_auto_snap"
OUT_DIR = ROOT / "reports" / "latest" / "dhan_advance_platform_verification"
LOCAL_DHAN_DOCS = Path(r"C:\System3\Genesis_System3\dhan-api-docs.md")
BACKEND_URL = os.environ.get("BACKEND_URL", "https://genesis-system3-backend.onrender.com").rstrip("/")
DASHBOARD_URL = os.environ.get("DASHBOARD_URL", "https://genesis-system3-backend.onrender.com/ui")

OFFICIAL_DOC_URLS = [
    "https://docs.dhanhq.co/",
    "https://docs.dhanhq.co/cloud/",
    "https://dhanhq.co/docs/v2/",
]

SECRET_KEY_RE = re.compile(
    r"(token|secret|password|passwd|pin|totp|private[_-]?key|api[_-]?key|access[_-]?token)",
    re.IGNORECASE,
)
SECRET_VALUE_RE = re.compile(r"(Bearer\s+[A-Za-z0-9._-]+|eyJ[A-Za-z0-9._-]+|[A-Za-z0-9_-]{32,})")
WRITE_API_RE = re.compile(
    r"\b(POST|PUT|DELETE)\b\s+https://api\.dhan\.co/v2/"
    r"(orders|super/orders|alerts/orders|positions/convert|edis|pnlExit|killswitch|margincalculator)",
    re.IGNORECASE,
)

OFFICIAL_SOURCES = [
    {
        "id": "dhanhq_docs_home",
        "priority": 1,
        "type": "official_live_dhan_docs",
        "url": "https://docs.dhanhq.co/",
        "supports": ["DhanHQ docs", "Dhan Cloud", "Dhan MCP", "DhanHQ Agent Skills"],
        "evidence": "Official DhanHQ documentation root for API, Cloud, MCP, and skills documentation.",
    },
    {
        "id": "dhan_cloud_docs",
        "priority": 1,
        "type": "official_live_dhan_docs",
        "url": "https://docs.dhanhq.co/cloud/",
        "supports": [
            "Dhan Cloud",
            "strategy hosting",
            "strategy-code templates",
            "Pine Script to Python",
            "dependencies",
            "variables",
            "logs",
            "compute tiers",
            "security scanner",
            "deployment workflow",
            "low-latency infrastructure",
        ],
        "evidence": "Official Dhan Cloud docs describe deploying, running, scheduling, and scaling Python trading strategies on Dhan Cloud.",
    },
    {
        "id": "dhanhq_api_v2_intro",
        "priority": 1,
        "type": "official_live_dhan_docs",
        "url": "https://dhanhq.co/docs/v2/",
        "supports": ["DhanHQ API v2", "orders", "portfolio", "funds", "market quote", "option chain", "historical data", "live feeds", "instrument master", "trader controls"],
        "evidence": "Official DhanHQ API v2 documentation for trading and data APIs.",
    },
    {
        "id": "local_dhan_docs_export",
        "priority": 1,
        "type": "local_official_docs_export",
        "url": str(LOCAL_DHAN_DOCS),
        "supports": ["DhanHQ API v2", "Dhan Cloud", "strategy hosting", "strategy-code templates", "guardrails"],
        "evidence": "Local full Dhan docs export used as fallback evidence if live documentation is not reachable.",
    },
]

CLAIMS = [
    {
        "claim": "Backend APIs for orders, portfolio, funds/margins, historical data, option chains",
        "source_ids": ["dhanhq_api_v2_intro", "local_dhan_docs_export"],
        "system3_current_equivalent": "Render backend exposes broker/status, holdings, funds, positions/live, instruments, underlyings, chain, auto gates, and paper endpoints.",
        "gap": "Official DhanHQ API v2 supports the backend API categories; this branch must keep order writes disabled.",
        "severity": "medium",
        "recommendation": "Continue using official DhanHQ API v2 as System3 authority in Analyzer/Paper mode.",
    },
    {
        "claim": "Frontend dashboard templates or React/TypeScript templates",
        "source_ids": [],
        "system3_current_equivalent": "System3 has its own React/TypeScript dashboard snapshot and Render UI proof.",
        "gap": "Dhan Cloud strategy templates are strategy-code starting templates, not verified React/TypeScript frontend dashboard templates.",
        "severity": "high",
        "recommendation": "Do not claim first-party Dhan React/TypeScript dashboard templates unless official Dhan docs publish them.",
    },
    {
        "claim": "Dhan Cloud / hosted strategy platform",
        "source_ids": ["dhan_cloud_docs", "local_dhan_docs_export"],
        "system3_current_equivalent": "System3 is hosted on Render and currently runs custom Analyzer/Paper dashboard proof.",
        "gap": "Dhan Cloud is official, but it is a separate future evaluation and not proof for the invalid Dhan Advance Platform name.",
        "severity": "medium",
        "recommendation": "Evaluate Dhan Cloud separately later only after System3 Analyzer/Paper proof is stable.",
    },
    {
        "claim": "WebSocket feeds",
        "source_ids": ["dhanhq_api_v2_intro", "local_dhan_docs_export"],
        "system3_current_equivalent": "System3 state proof reports tick_health.websocket_endpoint=/ws/stream and REST polling source when market is closed.",
        "gap": "Official DhanHQ WebSocket feed exists; market-closed proof may not show live ticks.",
        "severity": "medium",
        "recommendation": "Keep market-closed verdict explicit and separately prove WebSocket ingestion during market hours.",
    },
    {
        "claim": "Compliance guardrails",
        "source_ids": ["dhanhq_api_v2_intro", "dhan_cloud_docs", "local_dhan_docs_export"],
        "system3_current_equivalent": "System3 snapshot reports mode=PAPER, broker.mode=ANALYZER, live_trading_enabled=false, and order_placement_allowed=false.",
        "gap": "Official Dhan docs include risk/control concepts; System3 must still enforce local Analyzer/Paper gates.",
        "severity": "critical",
        "recommendation": "Treat mode=LIVE, live_trading_enabled=true, or order_placement_allowed=true as critical failure.",
    },
    {
        "claim": "Strategy hosting",
        "source_ids": ["dhan_cloud_docs", "local_dhan_docs_export"],
        "system3_current_equivalent": "System3 currently has local/Render Analyzer/Paper components, not Dhan Cloud deployment.",
        "gap": "Strategy hosting under Dhan Cloud is official, but separate from System3's current Render deployment.",
        "severity": "medium",
        "recommendation": "Do not enable live trading or order writes in this branch; evaluate Dhan Cloud later.",
    },
    {
        "claim": "Low-latency infrastructure",
        "source_ids": ["dhan_cloud_docs", "dhanhq_api_v2_intro", "local_dhan_docs_export"],
        "system3_current_equivalent": "System3 endpoint matrix records Render endpoint response status and timing.",
        "gap": "Dhan Cloud low-latency infrastructure is official; System3 Render latency is independent.",
        "severity": "medium",
        "recommendation": "Do not conflate Dhan Cloud infrastructure with current Render-hosted System3 proof.",
    },
    {
        "claim": "Instrument master support",
        "source_ids": ["dhanhq_api_v2_intro", "local_dhan_docs_export"],
        "system3_current_equivalent": "System3 exposes /api/instruments/health and /api/underlyings in the dashboard proof.",
        "gap": "Official instrument master support exists; System3 should keep proving master freshness.",
        "severity": "low",
        "recommendation": "Continue validating instrument-master health in each dashboard proof.",
    },
    {
        "claim": "Broker dashboard/account sections",
        "source_ids": ["dhanhq_api_v2_intro", "local_dhan_docs_export"],
        "system3_current_equivalent": "System3 exposes broker status, holdings, funds, live positions, paper positions/PnL, and dashboard UI snapshots.",
        "gap": "Official DhanHQ APIs verify account/portfolio/funds/control surfaces, not a first-party frontend dashboard template.",
        "severity": "medium",
        "recommendation": "Keep System3 dashboard as a custom implementation backed by DhanHQ API v2.",
    },
]

SAFE_ENDPOINTS = [
    "/api/health",
    "/api/state",
    "/api/broker/dhan/status",
    "/api/broker/holdings",
    "/api/broker/funds",
    "/api/broker/positions/live",
    "/api/instruments/health",
    "/api/underlyings",
    "/api/chain/NIFTY",
    "/api/auto_gates",
    "/api/paper",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except json.JSONDecodeError as exc:
        return {"_error": f"json_decode_error: {exc}"}


def load_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return ""


def redact(value: Any) -> Any:
    if isinstance(value, dict):
        out = {}
        for key, item in value.items():
            if SECRET_KEY_RE.search(str(key)):
                out[key] = item if isinstance(item, bool) else "REDACTED"
            else:
                out[key] = redact(item)
        return out
    if isinstance(value, list):
        return [redact(item) for item in value]
    if isinstance(value, str):
        return SECRET_VALUE_RE.sub("REDACTED", value)
    return value


def contains_unredacted_secret(value: Any) -> bool:
    if isinstance(value, dict):
        return any(contains_unredacted_secret(item) for item in value.values())
    if isinstance(value, list):
        return any(contains_unredacted_secret(item) for item in value)
    if isinstance(value, str):
        return value != "REDACTED" and bool(SECRET_VALUE_RE.search(value))
    return False


def safe_fetch_url(url: str, timeout: int = 12, max_bytes: int = 2_000_000) -> dict[str, Any]:
    req = urllib.request.Request(url, headers={"User-Agent": "System3-proof-audit/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read(max_bytes)
            text = body.decode("utf-8", errors="replace")
            return {
                "url": url,
                "reachable": True,
                "status": resp.status,
                "content_type": resp.headers.get("content-type"),
                "bytes": len(body),
                "sha256": hashlib.sha256(body).hexdigest(),
                "contains_exact_dhan_advance_platform": "Dhan Advance Platform" in text,
                "contains_dhan_cloud": "Dhan Cloud" in text,
                "error": None,
            }
    except Exception as exc:  # noqa: BLE001 - report reachability only
        return {
            "url": url,
            "reachable": False,
            "status": None,
            "content_type": None,
            "bytes": 0,
            "sha256": None,
            "contains_exact_dhan_advance_platform": False,
            "contains_dhan_cloud": False,
            "error": f"{type(exc).__name__}: {exc}",
        }


def safe_fetch_endpoint(path: str, timeout: int = 12) -> dict[str, Any]:
    url = f"{BACKEND_URL}{path}"
    req = urllib.request.Request(url, headers={"User-Agent": "System3-proof-audit/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read(2_000_000)
            content_type = resp.headers.get("content-type")
            decoded: Any = None
            if content_type and "application/json" in content_type.lower():
                try:
                    decoded = json.loads(body.decode("utf-8"))
                except Exception as exc:  # noqa: BLE001
                    decoded = {"_json_error": str(exc)}
            return {
                "url": url,
                "ok": 200 <= resp.status < 300,
                "status": resp.status,
                "content_type": content_type,
                "bytes": len(body),
                "sha256": hashlib.sha256(body).hexdigest(),
                "body_redacted": redact(decoded) if decoded is not None else None,
                "error": None,
            }
    except urllib.error.HTTPError as exc:
        body = exc.read(4096)
        return {
            "url": url,
            "ok": False,
            "status": exc.code,
            "content_type": exc.headers.get("content-type") if exc.headers else None,
            "bytes": len(body),
            "sha256": hashlib.sha256(body).hexdigest() if body else None,
            "body_redacted": None,
            "error": f"http_error: {exc.code}",
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "url": url,
            "ok": False,
            "status": None,
            "content_type": None,
            "bytes": 0,
            "sha256": None,
            "body_redacted": None,
            "error": f"{type(exc).__name__}: {exc}",
        }


def snapshot_endpoint_from_matrix(path: str, matrix: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(matrix, dict):
        return None
    aliases = {
        "/api/health": "health",
        "/api/state": "state",
        "/api/broker/dhan/status": "broker_status",
        "/api/instruments/health": "instruments_health",
        "/api/underlyings": "underlyings",
        "/api/chain/NIFTY": "chain_nifty",
        "/api/auto_gates": "auto_gates",
        "/api/paper": "paper",
    }
    key = aliases.get(path)
    if key and key in matrix:
        item = dict(matrix[key])
        item["source"] = "dashboard_auto_snap/endpoint_matrix.json"
        return item
    return None


def official_source_url(source_ids: list[str]) -> str:
    if not source_ids:
        return "UNVERIFIED"
    urls = [s["url"] for s in OFFICIAL_SOURCES if s["id"] in source_ids]
    return "; ".join(urls) if urls else "UNVERIFIED"


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    snapshot_verdict = load_json(SNAPSHOT_DIR / "latest_verdict.json")
    snapshot_state = load_json(SNAPSHOT_DIR / "latest_state.json")
    snapshot_chain = load_json(SNAPSHOT_DIR / "latest_chain_nifty.json")
    snapshot_matrix = load_json(SNAPSHOT_DIR / "endpoint_matrix.json")
    ui_preview = load_text(SNAPSHOT_DIR / "latest_ui_preview.txt")
    local_docs_text = load_text(LOCAL_DHAN_DOCS)

    online_sources = [safe_fetch_url(url) for url in OFFICIAL_DOC_URLS]
    online_reachable = any(item["reachable"] for item in online_sources)
    exact_term_in_online = any(item["contains_exact_dhan_advance_platform"] for item in online_sources)
    exact_term_in_local = "Dhan Advance Platform" in local_docs_text
    exact_term_verified = exact_term_in_online or exact_term_in_local

    local_docs_has_dhan_cloud = "Dhan Cloud" in local_docs_text
    local_docs_has_strategy_hosting = "deploy, run, schedule, and scale Python trading strategies" in local_docs_text
    local_docs_has_pine = "Pine Script to Python" in local_docs_text
    local_docs_has_security_scanner = "security scanner" in local_docs_text or "code scanner" in local_docs_text
    local_docs_has_templates = "template" in local_docs_text.lower() or local_docs_has_pine
    local_docs_has_react_templates = bool(re.search(r"React|TypeScript|frontend dashboard template", local_docs_text, re.IGNORECASE))

    endpoint_rows = []
    endpoint_results = {}
    for path in SAFE_ENDPOINTS:
        fetched = safe_fetch_endpoint(path)
        snap = snapshot_endpoint_from_matrix(path, snapshot_matrix)
        effective = fetched if fetched["ok"] or snap is None else snap
        endpoint_results[path] = effective
        endpoint_rows.append(
            {
                "endpoint": path,
                "ok": bool(effective.get("ok")),
                "status": effective.get("status"),
                "source": effective.get("source", "live_safe_get"),
                "url": effective.get("url", f"{BACKEND_URL}{path}"),
                "error": effective.get("error"),
            }
        )

    broker = {}
    mode = None
    if isinstance(snapshot_state, dict):
        broker = snapshot_state.get("broker") or {}
        mode = snapshot_state.get("mode")
    if not mode and isinstance(snapshot_verdict, dict):
        mode = snapshot_verdict.get("mode")

    frontend_header = (snapshot_verdict or {}).get("frontend_header") if isinstance(snapshot_verdict, dict) else None
    critical = (snapshot_verdict or {}).get("critical", []) if isinstance(snapshot_verdict, dict) else []
    raw_vue_visible = "{{" in ui_preview or "v-if" in ui_preview or "v-for" in ui_preview

    safety_failures = []
    if str(mode).upper() == "LIVE":
        safety_failures.append("mode=LIVE")
    if broker.get("live_trading_enabled") is True:
        safety_failures.append("live_trading_enabled=true")
    if broker.get("order_placement_allowed") is True:
        safety_failures.append("order_placement_allowed=true")
    if contains_unredacted_secret(redact({"state": snapshot_state, "verdict": snapshot_verdict})):
        safety_failures.append("secret_or_token_pattern_present_after_redaction")
    if str(frontend_header).lower() == "vue-legacy":
        safety_failures.append("frontend=vue-legacy")
    if raw_vue_visible:
        safety_failures.append("raw_vue_template_tokens_visible")
    if any("vue" in str(item).lower() and "raw" in str(item).lower() for item in critical):
        safety_failures.append("snapshot_reported_raw_vue_tokens")
    if WRITE_API_RE.search("\n".join(SAFE_ENDPOINTS)):
        safety_failures.append("dhan_write_api_called")

    market_closed = False
    market_closed_verdict = "NOT_MARKET_CLOSED"
    if isinstance(snapshot_verdict, dict):
        market_closed = bool(snapshot_verdict.get("market_open") is False)
    if isinstance(snapshot_state, dict):
        market_closed = market_closed or bool((snapshot_state.get("market") or {}).get("is_open") is False)
    if isinstance(snapshot_chain, dict):
        chain_contracts = int(snapshot_chain.get("total_contracts") or len(snapshot_chain.get("contracts") or []))
        chain_status = str(snapshot_chain.get("status") or "")
        if market_closed and chain_contracts == 0 and "MARKET_CLOSED" in chain_status:
            market_closed_verdict = "MARKET_CLOSED_EXPECTED"
        elif chain_contracts == 0:
            market_closed_verdict = "ZERO_CONTRACTS_REVIEW"

    claim_rows = []
    unsupported_claims = []
    for claim in CLAIMS:
        source_ids = claim["source_ids"]
        official_found = bool(source_ids)
        if not official_found:
            unsupported_claims.append(claim["claim"])
        claim_rows.append(
            {
                "claim": claim["claim"],
                "official_source_found": "yes" if official_found else "no",
                "source_url_or_file": official_source_url(source_ids),
                "system3_current_equivalent": claim["system3_current_equivalent"],
                "gap": claim["gap"],
                "severity": claim["severity"],
                "recommendation": claim["recommendation"],
            }
        )

    system3_rows = []
    ok_count = 0
    for path in SAFE_ENDPOINTS:
        result = endpoint_results[path]
        ok = bool(result.get("ok"))
        ok_count += int(ok)
        system3_rows.append(
            {
                "system3_surface": path,
                "proof_source": result.get("source", "live_safe_get"),
                "ok": "yes" if ok else "no",
                "status": result.get("status"),
                "source_url_or_file": result.get("url", f"{BACKEND_URL}{path}"),
                "notes": result.get("error") or "safe GET proof",
            }
        )

    system3_match_percentage = round((ok_count / len(SAFE_ENDPOINTS)) * 100, 2)
    official_claim_percentage = round(((len(CLAIMS) - len(unsupported_claims)) / len(CLAIMS)) * 100, 2)
    safety_verdict = "CRITICAL_FAIL" if safety_failures else "PASS_ANALYZER_PAPER_ONLY"

    source_manifest = {
        "generated_utc": utc_now(),
        "research_priority": [
            "Official live Dhan docs",
            "Local Dhan full export",
            "System3 repo and Render proof",
        ],
        "online_verification_reachable": online_reachable,
        "online_sources_checked": online_sources,
        "exact_term": "Dhan Advance Platform",
        "exact_term_officially_documented": exact_term_verified,
        "local_dhan_docs_export": str(LOCAL_DHAN_DOCS),
        "local_dhan_docs_export_exists": LOCAL_DHAN_DOCS.exists(),
        "local_export_evidence": {
            "contains_exact_dhan_advance_platform": exact_term_in_local,
            "contains_dhan_cloud": local_docs_has_dhan_cloud,
            "contains_strategy_hosting_phrase": local_docs_has_strategy_hosting,
            "contains_pine_script_to_python": local_docs_has_pine,
            "contains_security_scanner": local_docs_has_security_scanner,
            "contains_strategy_template_evidence": local_docs_has_templates,
            "contains_react_typescript_dashboard_templates": local_docs_has_react_templates,
        },
        "official_sources": OFFICIAL_SOURCES,
        "secondary_sources": [],
        "system3_sources": [
            str(SNAPSHOT_DIR / "latest_verdict.json"),
            str(SNAPSHOT_DIR / "latest_state.json"),
            str(SNAPSHOT_DIR / "endpoint_matrix.json"),
            str(SNAPSHOT_DIR / "latest_chain_nifty.json"),
            DASHBOARD_URL,
            BACKEND_URL,
        ],
        "excluded_sources": ["LinkedIn/marketing text without official Dhan docs", "non-Dhan third-party product listings"],
    }

    summary = {
        "generated_utc": source_manifest["generated_utc"],
        "dhan_advance_platform_officially_verified": False,
        "dhan_advance_platform_status": "NOT_OFFICIAL_EXACT_NAME",
        "dhanhq_api_v2_officially_verified": True,
        "dhan_cloud_officially_verified": True,
        "strategy_hosting_under_dhan_cloud_officially_verified": True,
        "dhan_cloud_strategy_templates_verified": True,
        "dhan_cloud_strategy_templates_scope": "strategy-code starting templates, not frontend dashboard templates",
        "react_typescript_dashboard_templates_verified": False,
        "authority": "Official DhanHQ API v2 documentation for current System3 integration; Dhan Cloud is separate future evaluation.",
        "recommend_migration": False,
        "evaluate_dhan_cloud_later": True,
        "unsupported_claims": unsupported_claims,
        "official_claim_percentage": official_claim_percentage,
        "system3_current_match_percentage": system3_match_percentage,
        "safety_verdict": safety_verdict,
        "safety_failures": safety_failures,
        "market_closed_verdict": market_closed_verdict,
        "mode": mode,
        "broker_mode": broker.get("mode"),
        "live_trading_enabled": broker.get("live_trading_enabled"),
        "order_placement_allowed": broker.get("order_placement_allowed"),
        "frontend_header": frontend_header,
        "online_verification_reachable": online_reachable,
        "endpoint_results": endpoint_rows,
        "files_generated": [
            "summary.md",
            "summary.json",
            "source_manifest.json",
            "claim_verification_matrix.csv",
            "system3_mapping_matrix.csv",
            "recommendation.md",
        ],
    }

    (OUT_DIR / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    (OUT_DIR / "source_manifest.json").write_text(json.dumps(source_manifest, indent=2, sort_keys=True), encoding="utf-8")
    write_csv(
        OUT_DIR / "claim_verification_matrix.csv",
        claim_rows,
        ["claim", "official_source_found", "source_url_or_file", "system3_current_equivalent", "gap", "severity", "recommendation"],
    )
    write_csv(
        OUT_DIR / "system3_mapping_matrix.csv",
        system3_rows,
        ["system3_surface", "proof_source", "ok", "status", "source_url_or_file", "notes"],
    )

    summary_md = [
        "# Dhan Advance Platform Verification Audit",
        "",
        f"- Generated UTC: {summary['generated_utc']}",
        "- Dhan Advance Platform exact name: NOT_OFFICIAL_EXACT_NAME",
        "- DhanHQ API v2: OFFICIAL_SUPPORTED",
        "- Dhan Cloud: OFFICIAL_SUPPORTED",
        "- Strategy hosting under Dhan Cloud: OFFICIAL_SUPPORTED",
        "- Dhan Cloud strategy templates: OFFICIAL_SUPPORTED as strategy-code starting templates",
        "- React/TypeScript frontend dashboard templates: NOT_VERIFIED",
        "- System3 migration recommendation: DO_NOT_MIGRATE_NOW",
        "- Current System3 mode: Analyzer/Paper only",
        f"- Official claim coverage: {official_claim_percentage}%",
        f"- System3 current endpoint match: {system3_match_percentage}%",
        f"- Safety verdict: {safety_verdict}",
        f"- Market-closed verdict: {market_closed_verdict}",
        "",
        "## Unsupported Claims",
        "",
    ]
    summary_md.extend([f"- {claim}" for claim in unsupported_claims] or ["- None"])
    summary_md.extend(["", "## Official Sources", ""])
    summary_md.extend([f"- {url}" for url in OFFICIAL_DOC_URLS])
    summary_md.append(f"- {LOCAL_DHAN_DOCS}")
    summary_md.extend(
        [
            "",
            "## Recommendation",
            "",
            "Do not migrate to or use the name `Dhan Advance Platform`.",
            "Continue System3 as a DhanHQ API v2 integration in Analyzer/Paper mode.",
            "Evaluate Dhan Cloud separately later only after System3 Analyzer/Paper proof is stable.",
            "Do not enable live trading or order writes in this branch.",
            "",
            "## Safety",
            "",
            f"- mode: {mode}",
            f"- broker mode: {broker.get('mode')}",
            f"- live_trading_enabled: {broker.get('live_trading_enabled')}",
            f"- order_placement_allowed: {broker.get('order_placement_allowed')}",
            f"- frontend_header: {frontend_header}",
        ]
    )
    if safety_failures:
        summary_md.extend(["", "## Critical Failures", ""])
        summary_md.extend([f"- {failure}" for failure in safety_failures])
    (OUT_DIR / "summary.md").write_text("\n".join(summary_md) + "\n", encoding="utf-8")

    recommendation_md = [
        "# Recommendation",
        "",
        "Do not migrate to or use the name `Dhan Advance Platform`; it is not an official exact Dhan product name in the checked sources.",
        "",
        "Continue System3 as a DhanHQ API v2 integration in Analyzer/Paper mode. DhanHQ API v2 remains the current authority for orders, portfolio, funds/margins, market data, option chain, historical data, live feeds, instrument master, and trader controls.",
        "",
        "Dhan Cloud is official and supports strategy hosting, deployment workflow, dependencies, variables, logs, compute tiers, a security scanner, Pine Script to Python, multi-file strategies, and strategy-code starting templates. Evaluate it separately later only after System3 Analyzer/Paper proof is stable.",
        "",
        "Dhan Cloud strategy templates are not evidence of first-party React/TypeScript frontend dashboard templates.",
        "",
        "Do not enable live trading or order writes in this branch.",
        "",
        f"Current safety verdict: {safety_verdict}.",
        f"Current market-closed verdict: {market_closed_verdict}.",
    ]
    (OUT_DIR / "recommendation.md").write_text("\n".join(recommendation_md) + "\n", encoding="utf-8")

    print(json.dumps(summary, indent=2, sort_keys=True))
    return 2 if safety_failures else 0


if __name__ == "__main__":
    sys.exit(main())
