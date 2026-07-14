#!/usr/bin/env python3
"""Analyzer-only semantic readiness proof for broker and mandatory Dhan chains.

The gate records only sanitized status metadata. It never persists response bodies,
credentials, cookies, holdings, positions, balances, or order data.
"""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BASE = os.getenv("DASHBOARD_BASE_URL", "https://genesis-system3-backend.onrender.com").rstrip("/")
API_KEY = os.getenv("DASHBOARD_API_KEY", "")
OUT = Path("reports/latest/broker_chain_semantic_gate")
REQUIRED = [s.strip().upper() for s in os.getenv(
    "SYSTEM3_REQUIRED_UNDERLYINGS", "NIFTY,BANKNIFTY,FINNIFTY,MIDCPNIFTY"
).split(",") if s.strip()]

AUTH_ERROR = re.compile(r"DH-901|invalid[_ ]authentication|invalid or expired|token.*expired|token.*invalid", re.I)


def fetch_json(path: str, timeout: int = 45) -> tuple[int, Any, str | None]:
    headers = {"Accept": "application/json", "User-Agent": "system3-analyzer-proof/1.0"}
    if API_KEY:
        headers["X-API-Key"] = API_KEY
    req = urllib.request.Request(f"{BASE}{path}", headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            raw = response.read(500_000).decode("utf-8", errors="replace")
            try:
                return int(response.status), json.loads(raw), None
            except json.JSONDecodeError:
                return int(response.status), None, "NON_JSON_RESPONSE"
    except urllib.error.HTTPError as exc:
        return int(exc.code), None, f"HTTP_{exc.code}"
    except Exception as exc:  # sanitized category only
        return 0, None, type(exc).__name__.upper()


def scalar(payload: Any, *keys: str) -> Any:
    if not isinstance(payload, dict):
        return None
    for key in keys:
        if key in payload:
            return payload[key]
    data = payload.get("data")
    if isinstance(data, dict):
        for key in keys:
            if key in data:
                return data[key]
    return None


def broker_semantics(payload: Any) -> tuple[bool, str]:
    connected = scalar(payload, "connected", "is_connected", "authenticated")
    status = str(scalar(payload, "status", "broker_status", "connection_status") or "")
    message = str(scalar(payload, "message", "error", "reason", "blocked_reason") or "")
    combined = f"{status} {message}"
    if AUTH_ERROR.search(combined):
        return False, "TOKEN_EXPIRED_OR_INVALID"
    if connected is True or status.upper() in {"CONNECTED", "OK", "READY"}:
        return True, "CONNECTED"
    return False, "BROKER_NOT_CONNECTED"


def chain_semantics(payload: Any) -> dict[str, Any]:
    source = str(scalar(payload, "data_source", "source") or "").lower()
    priority = str(scalar(payload, "source_priority") or "").lower()
    status = str(scalar(payload, "status") or "").upper()
    stale = scalar(payload, "stale") is True
    contracts_value = scalar(payload, "total_contracts")
    contracts = int(contracts_value or 0) if str(contracts_value or "0").isdigit() else 0
    if not contracts and isinstance(payload, dict) and isinstance(payload.get("contracts"), list):
        contracts = len(payload["contracts"])
    spot_value = scalar(payload, "spot")
    try:
        spot = float(spot_value or 0)
    except (TypeError, ValueError):
        spot = 0.0
    bad_source = bool(re.search(r"csv|fallback|synthetic|bhavcopy|yahoo|fake|mock", f"{source} {priority} {status}", re.I))
    allowed = status in {"OK", "MARKET_OPEN", "MARKET_CLOSED_DHAN_SNAPSHOT", "EOD_SNAPSHOT"}
    ready = source == "dhan" and allowed and not stale and not bad_source and contracts > 0 and spot > 0
    return {
        "ready": ready,
        "source": source or None,
        "priority": priority or None,
        "status": status or None,
        "stale": stale,
        "contracts": contracts,
        "spot_present": spot > 0,
        "reason": None if ready else "NO_CURRENT_VERIFIED_DHAN_CHAIN",
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    blockers: list[str] = []
    transport_failures: list[str] = []

    broker_http, broker_payload, broker_error = fetch_json("/api/broker/dhan/status")
    broker_ok = False
    broker_reason = broker_error or "UNKNOWN"
    if broker_http == 200 and broker_payload is not None:
        broker_ok, broker_reason = broker_semantics(broker_payload)
    else:
        transport_failures.append(f"BROKER_STATUS_HTTP_{broker_http or 0}")
    if not broker_ok:
        blockers.append(f"BROKER:{broker_reason}")

    funds_http, funds_payload, funds_error = fetch_json("/api/broker/funds")
    funds_semantic_ok = funds_http == 200 and funds_payload is not None
    if funds_semantic_ok:
        text = json.dumps(funds_payload, ensure_ascii=True)[:20_000]
        if AUTH_ERROR.search(text):
            funds_semantic_ok = False
            funds_error = "TOKEN_EXPIRED_OR_INVALID"
    if not funds_semantic_ok:
        blockers.append(f"FUNDS:{funds_error or f'HTTP_{funds_http}'}")

    chains: list[dict[str, Any]] = []
    for symbol in REQUIRED:
        http, payload, error = fetch_json(f"/api/chain/{symbol}")
        row = {"symbol": symbol, "http": http, "transport_ok": http == 200, "error": error}
        if http == 200 and payload is not None:
            row.update(chain_semantics(payload))
        else:
            row.update({"ready": False, "source": None, "priority": None, "status": None,
                        "stale": False, "contracts": 0, "spot_present": False,
                        "reason": error or f"HTTP_{http}"})
            transport_failures.append(f"CHAIN_{symbol}_HTTP_{http or 0}")
        if not row["ready"]:
            blockers.append(f"CHAIN:{symbol}:{row['reason']}")
        chains.append(row)

    report = {
        "generated_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "base": BASE,
        "mode": "ANALYZER_ONLY",
        "live_trading_enabled": False,
        "system3_live_trading_allowed": False,
        "order_endpoints_called": False,
        "secrets_written": False,
        "broker": {"http": broker_http, "connected": broker_ok, "reason": broker_reason},
        "funds": {"http": funds_http, "semantic_ok": funds_semantic_ok,
                  "reason": None if funds_semantic_ok else (funds_error or f"HTTP_{funds_http}")},
        "required_chains": chains,
        "required_chain_ready_count": sum(1 for row in chains if row["ready"]),
        "required_chain_total": len(chains),
        "transport_failures": transport_failures,
        "readiness_blockers": blockers,
        "final_verdict": "PASS" if not blockers and not transport_failures else "BLOCKED_NOT_TRADE_READY",
        "production_grade_claim_allowed": False,
    }
    (OUT / "summary.json").write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    lines = [
        "# Broker and Chain Semantic Gate", "",
        f"- Generated UTC: `{report['generated_utc']}`",
        f"- Final verdict: **{report['final_verdict']}**",
        f"- Broker connected: `{broker_ok}` ({broker_reason})",
        f"- Funds semantic proof: `{funds_semantic_ok}`",
        f"- Mandatory chains ready: `{report['required_chain_ready_count']}/{report['required_chain_total']}`",
        "- Analyzer mode: `ON`", "- Live trading: `OFF`", "- Order endpoints called: `false`",
        "- Secrets written: `false`", "", "## Mandatory chains",
    ]
    for row in chains:
        lines.append(f"- {row['symbol']}: {'PASS' if row['ready'] else 'BLOCKED'} http={row['http']} source={row['source']} status={row['status']} contracts={row['contracts']} stale={row['stale']}")
    lines.extend(["", "## Blockers"])
    lines.extend([f"- {item}" for item in blockers] or ["- none"])
    (OUT / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"BROKER_CHAIN_SEMANTIC_GATE verdict={report['final_verdict']} broker_connected={broker_ok} chains={report['required_chain_ready_count']}/{report['required_chain_total']}")
    return 0 if report["final_verdict"] == "PASS" else 2


if __name__ == "__main__":
    sys.exit(main())
