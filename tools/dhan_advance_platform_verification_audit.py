#!/usr/bin/env python3
"""Proof-only audit for Dhan Advance Platform claims.

This script does not place, modify, cancel, or simulate live broker orders. It
only reads local proof files and performs safe GET checks against System3
dashboard endpoints when available.
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
BACKEND_URL = os.environ.get("BACKEND_URL", "https://genesis-system3-backend.onrender.com").rstrip("/")
DASHBOARD_URL = os.environ.get("DASHBOARD_URL", "https://genesis-system3-backend.onrender.com/ui")

SECRET_KEY_RE = re.compile(
    r"(token|secret|password|passwd|pin|totp|private[_-]?key|api[_-]?key|access[_-]?token)",
    re.IGNORECASE,
)
SECRET_VALUE_RE = re.compile(r"(Bearer\s+[A-Za-z0-9._-]+|eyJ[A-Za-z0-9._-]+|[A-Za-z0-9_-]{32,})")


OFFICIAL_SOURCES = [
    {
        "id": "dhanhq_api_v2_intro",
        "priority": 1,
        "type": "official_dhanhq_docs",
        "url": "https://dhanhq.co/docs/v2/",
        "supports": ["DhanHQ API v2", "REST APIs", "trading strategies", "portfolio", "live market data"],
        "evidence": "DhanHQ API v2 documents REST-like trading/data APIs for trading services and strategies.",
    },
    {
        "id": "dhanhq_orders",
        "priority": 1,
        "type": "official_dhanhq_docs",
        "url": "https://dhanhq.co/docs/v2/orders/",
        "supports": ["orders", "order book", "trades", "static IP whitelisting"],
        "evidence": "Official Orders page documents place/modify/cancel plus read-only order/trade book endpoints and static IP whitelisting requirement for write APIs.",
    },
    {
        "id": "dhanhq_portfolio",
        "priority": 1,
        "type": "official_dhanhq_docs",
        "url": "https://dhanhq.co/docs/v2/portfolio/",
        "supports": ["holdings", "positions", "portfolio"],
        "evidence": "Official Portfolio and Positions page documents holdings and positions APIs.",
    },
    {
        "id": "dhanhq_funds",
        "priority": 1,
        "type": "official_dhanhq_docs",
        "url": "https://dhanhq.co/docs/v2/funds/",
        "supports": ["funds", "margin", "fund limit"],
        "evidence": "Official Funds & Margin page documents margin calculator and fund limit APIs.",
    },
    {
        "id": "dhanhq_historical",
        "priority": 1,
        "type": "official_dhanhq_docs",
        "url": "https://dhanhq.co/docs/v2/historical-data/",
        "supports": ["historical data"],
        "evidence": "Official Historical Data page is listed under DhanHQ API v2 Data APIs.",
    },
    {
        "id": "dhanhq_option_chain",
        "priority": 1,
        "type": "official_dhanhq_docs",
        "url": "https://dhanhq.co/docs/v2/option-chain/",
        "supports": ["option chain", "expiry list", "OI", "greeks", "bid ask"],
        "evidence": "Official Option Chain page documents real-time option chain and expiry list APIs.",
    },
    {
        "id": "dhanhq_live_market_feed",
        "priority": 1,
        "type": "official_dhanhq_docs",
        "url": "https://dhanhq.co/docs/v2/live-market-feed/",
        "supports": ["WebSocket feeds", "real-time market data", "low-latency feed"],
        "evidence": "Official Live Market Feed page documents WebSocket market feeds and feed speed characteristics.",
    },
    {
        "id": "dhanhq_instruments",
        "priority": 1,
        "type": "official_dhanhq_docs",
        "url": "https://dhanhq.co/docs/v2/instruments/",
        "supports": ["instrument master", "security id", "CSV master"],
        "evidence": "Official Instrument List page documents compact/detailed CSV masters and segmentwise instrument fetch.",
    },
    {
        "id": "dhanhq_traders_control",
        "priority": 1,
        "type": "official_dhanhq_docs",
        "url": "https://dhanhq.co/docs/v2/traders-control/",
        "supports": ["kill switch", "P&L based exit", "risk controls", "compliance guardrails"],
        "evidence": "Official Trader's Control page documents kill switch and P&L based exit APIs.",
    },
]


CLAIMS = [
    {
        "claim": "Backend APIs for orders, portfolio, funds/margins, historical data, option chains",
        "source_ids": [
            "dhanhq_orders",
            "dhanhq_portfolio",
            "dhanhq_funds",
            "dhanhq_historical",
            "dhanhq_option_chain",
        ],
        "system3_current_equivalent": "Render backend exposes broker/status, holdings, funds, positions/live, instruments, underlyings, chain, auto gates, and paper endpoints; local broker adapters map to Dhan read-only surfaces.",
        "gap": "Official DhanHQ API v2 supports the backend API categories, but System3 must keep order write APIs disabled in Analyzer/Paper mode.",
        "severity": "medium",
        "recommendation": "Continue using official DhanHQ API v2 docs as the authority; do not enable order writes for this proof branch.",
    },
    {
        "claim": "Frontend dashboard templates or React/TypeScript templates",
        "source_ids": [],
        "system3_current_equivalent": "System3 has its own React/TypeScript dashboard snapshot and Render UI proof.",
        "gap": "No official DhanHQ source found for a Dhan-provided React/TypeScript dashboard template.",
        "severity": "high",
        "recommendation": "Do not claim official Dhan frontend templates unless Dhan publishes documentation or a first-party repository.",
    },
    {
        "claim": "Dhan Cloud / hosted strategy platform",
        "source_ids": [],
        "system3_current_equivalent": "System3 is hosted on Render and runs its own backend/dashboard proof.",
        "gap": "No official DhanHQ source found for a product named Dhan Cloud or a hosted strategy platform under the exact Dhan Advance Platform claim.",
        "severity": "high",
        "recommendation": "Do not recommend migration to Dhan Cloud without official Dhan documentation.",
    },
    {
        "claim": "WebSocket feeds",
        "source_ids": ["dhanhq_live_market_feed"],
        "system3_current_equivalent": "System3 state proof reports tick_health.websocket_endpoint=/ws/stream and REST polling source when market is closed.",
        "gap": "Official DhanHQ WebSocket feed exists; System3 proof did not demonstrate a live Dhan WebSocket tick during market closed.",
        "severity": "medium",
        "recommendation": "Retain REST/paper proof for market-closed audits and separately prove Dhan WebSocket ingestion during market hours.",
    },
    {
        "claim": "Compliance guardrails",
        "source_ids": ["dhanhq_orders", "dhanhq_traders_control", "dhanhq_funds", "dhanhq_instruments"],
        "system3_current_equivalent": "System3 snapshot reports mode=PAPER, broker.mode=ANALYZER, live_trading_enabled=false, order_placement_allowed=false, and risk limits PASS.",
        "gap": "Official DhanHQ documents several risk controls, rate limits, write-API whitelisting, and instrument flags; System3 also needs local gates to keep order writes disabled.",
        "severity": "critical",
        "recommendation": "Keep local Analyzer/Paper gates mandatory and treat any live/order-enabled proof as critical failure.",
    },
    {
        "claim": "Strategy hosting",
        "source_ids": [],
        "system3_current_equivalent": "System3 has local/Render analyzer and paper components, but no official Dhan-hosted strategy runtime was verified.",
        "gap": "DhanHQ docs support building trading strategies via APIs, but no official strategy hosting platform was verified.",
        "severity": "high",
        "recommendation": "Do not represent API strategy building as official Dhan strategy hosting.",
    },
    {
        "claim": "Low-latency infrastructure",
        "source_ids": ["dhanhq_api_v2_intro", "dhanhq_live_market_feed"],
        "system3_current_equivalent": "System3 endpoint matrix records sub-second Render responses in the latest snapshot.",
        "gap": "Official DhanHQ docs describe fast APIs/WebSocket feed behavior; System3's Render latency is independent infrastructure, not Dhan-hosted infrastructure.",
        "severity": "medium",
        "recommendation": "State this as official DhanHQ API/feed capability, not proof of Dhan Advance Platform hosting.",
    },
    {
        "claim": "Instrument master support",
        "source_ids": ["dhanhq_instruments"],
        "system3_current_equivalent": "System3 exposes /api/instruments/health and /api/underlyings in the dashboard proof.",
        "gap": "Official instrument master support exists; System3 proof should keep showing master freshness and source status.",
        "severity": "low",
        "recommendation": "Continue validating instrument-master health in each dashboard proof.",
    },
    {
        "claim": "Broker dashboard/account sections",
        "source_ids": ["dhanhq_portfolio", "dhanhq_funds", "dhanhq_traders_control"],
        "system3_current_equivalent": "System3 exposes broker status, holdings, funds, live positions, paper positions/PnL, and dashboard UI snapshots.",
        "gap": "Official DhanHQ sources verify account/portfolio/funds/control APIs, but not a first-party dashboard template for System3.",
        "severity": "medium",
        "recommendation": "Keep System3 dashboard as a custom implementation backed by official DhanHQ API v2.",
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


def redact(value: Any) -> Any:
    if isinstance(value, dict):
        out = {}
        for key, item in value.items():
            if SECRET_KEY_RE.search(str(key)):
                if isinstance(item, bool):
                    out[key] = item
                else:
                    out[key] = "REDACTED"
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
        if value == "REDACTED":
            return False
        return bool(SECRET_VALUE_RE.search(value))
    return False


def safe_fetch(path: str, timeout: int = 12) -> dict[str, Any]:
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
                except Exception as exc:  # noqa: BLE001 - report only
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
    except Exception as exc:  # noqa: BLE001 - proof script must not crash on network
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


def endpoint_key(path: str) -> str:
    return path.strip("/").replace("/", "_").replace("-", "_")


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

    endpoint_rows = []
    endpoint_results = {}
    for path in SAFE_ENDPOINTS:
        fetched = safe_fetch(path)
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

    safety_failures = []
    if str(mode).upper() == "LIVE":
        safety_failures.append("mode=LIVE")
    if broker.get("live_trading_enabled") is True:
        safety_failures.append("live_trading_enabled=true")
    if broker.get("order_placement_allowed") is True:
        safety_failures.append("order_placement_allowed=true")
    if contains_unredacted_secret(redact({"state": snapshot_state, "verdict": snapshot_verdict})):
        safety_failures.append("secret_or_token_pattern_present_after_redaction")

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
    exact_term_verified = False
    safety_verdict = "CRITICAL_FAIL" if safety_failures else "PASS_ANALYZER_PAPER_ONLY"

    source_manifest = {
        "generated_utc": utc_now(),
        "research_priority": [
            "Official Dhan website / DhanHQ docs only",
            "DhanHQ Agent Skill repo only as secondary reference",
            "System3 repo and Render proof",
        ],
        "exact_term": "Dhan Advance Platform",
        "exact_term_officially_documented": exact_term_verified,
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
        "excluded_sources": ["LinkedIn/marketing text without official Dhan docs"],
    }

    summary = {
        "generated_utc": source_manifest["generated_utc"],
        "dhan_advance_platform_officially_verified": exact_term_verified,
        "authority": "Official DhanHQ API v2 documentation",
        "recommend_migration": False,
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
        [
            "claim",
            "official_source_found",
            "source_url_or_file",
            "system3_current_equivalent",
            "gap",
            "severity",
            "recommendation",
        ],
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
        f"- Exact term officially documented: {'yes' if exact_term_verified else 'no'}",
        "- Verdict: UNVERIFIED for the exact term `Dhan Advance Platform`",
        "- Migration recommendation: do not migrate based on the unverified umbrella term",
        "- Authority: continue using official DhanHQ API v2 documentation",
        f"- Official claim coverage: {official_claim_percentage}%",
        f"- System3 current endpoint match: {system3_match_percentage}%",
        f"- Safety verdict: {safety_verdict}",
        f"- Market-closed verdict: {market_closed_verdict}",
        "",
        "## Unsupported Claims",
        "",
    ]
    summary_md.extend([f"- {claim}" for claim in unsupported_claims] or ["- None"])
    summary_md.extend(
        [
            "",
            "## Official Sources Found",
            "",
        ]
    )
    summary_md.extend([f"- {src['url']} ({src['id']})" for src in OFFICIAL_SOURCES])
    summary_md.extend(
        [
            "",
            "## Safety",
            "",
            f"- mode: {mode}",
            f"- broker mode: {broker.get('mode')}",
            f"- live_trading_enabled: {broker.get('live_trading_enabled')}",
            f"- order_placement_allowed: {broker.get('order_placement_allowed')}",
        ]
    )
    if safety_failures:
        summary_md.extend(["", "## Critical Failures", ""])
        summary_md.extend([f"- {failure}" for failure in safety_failures])
    (OUT_DIR / "summary.md").write_text("\n".join(summary_md) + "\n", encoding="utf-8")

    recommendation_md = [
        "# Recommendation",
        "",
        "Do not recommend migration to a platform named `Dhan Advance Platform` because the exact term was not verified in official Dhan/DhanHQ documentation.",
        "",
        "Continue treating official DhanHQ API v2 documentation as the authority for orders, portfolio, funds/margins, historical data, option chains, WebSocket feeds, instrument master support, and trader risk controls.",
        "",
        "System3 should remain in Analyzer/Paper mode for this branch. Any proof that reports `mode=LIVE`, `live_trading_enabled=true`, or `order_placement_allowed=true` is a critical failure.",
        "",
        f"Current safety verdict: {safety_verdict}.",
        f"Current market-closed verdict: {market_closed_verdict}.",
    ]
    (OUT_DIR / "recommendation.md").write_text("\n".join(recommendation_md) + "\n", encoding="utf-8")

    print(json.dumps(summary, indent=2, sort_keys=True))
    return 2 if safety_failures else 0


if __name__ == "__main__":
    sys.exit(main())

