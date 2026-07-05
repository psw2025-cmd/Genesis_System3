#!/usr/bin/env python3
"""Runtime QC/anomaly proof audit.

Read-only proof script. It calls safe Render GET endpoints only and writes proof
artifacts under reports/latest/qc_forensic_anomaly_audit/.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BACKEND_URL = os.getenv("BACKEND_URL", "https://genesis-system3-backend.onrender.com").rstrip("/")
DASHBOARD_URL = os.getenv("DASHBOARD_URL", "https://genesis-system3-backend.onrender.com/ui").rstrip("/")
OUT_DIR = Path("reports/latest/qc_forensic_anomaly_audit")
SNAP_DIR = Path("reports/latest/dashboard_auto_snap")
TIMEOUT_S = int(os.getenv("QC_RUNTIME_AUDIT_TIMEOUT_S", "25") or "25")

ENDPOINTS = {
    "health": "/api/health",
    "state": "/api/state",
    "qc": "/api/qc",
    "qc_runtime": "/api/qc/runtime",
    "chain_nifty": "/api/chain/NIFTY",
    "chain_banknifty": "/api/chain/BANKNIFTY",
    "chain_finnifty": "/api/chain/FINNIFTY",
    "chain_midcpnifty": "/api/chain/MIDCPNIFTY",
}

REDACT_KEY_RE = re.compile(r"(token|secret|password|pin|totp|otp|cookie|authorization|api[_-]?key|access[_-]?token|private[_-]?key)", re.I)
SECRET_VALUE_RE = re.compile(r"(Bearer\s+[A-Za-z0-9._-]+|eyJ[A-Za-z0-9._-]+|[A-Za-z0-9_-]{32,})")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def redact(obj: Any) -> Any:
    if isinstance(obj, dict):
        out = {}
        for key, value in obj.items():
            if REDACT_KEY_RE.search(str(key)):
                out[key] = value if isinstance(value, bool) or value in (None, "", False) else "<redacted>"
            else:
                out[key] = redact(value)
        return out
    if isinstance(obj, list):
        return [redact(item) for item in obj]
    if isinstance(obj, str):
        return SECRET_VALUE_RE.sub("<redacted>", obj)
    return obj


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def load_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(redact(data), indent=2, sort_keys=True), encoding="utf-8")


def fetch_json(name: str, endpoint: str) -> dict[str, Any]:
    url = f"{BACKEND_URL}{endpoint}"
    req = urllib.request.Request(url, headers={"User-Agent": "System3-qc-runtime-anomaly-audit/1.0"}, method="GET")
    started = time.time()
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
            raw = resp.read(2_000_000)
            text = raw.decode("utf-8", errors="replace")
            data = None
            try:
                data = json.loads(text)
            except Exception:
                pass
            return {
                "name": name,
                "endpoint": endpoint,
                "url": url,
                "ok": 200 <= int(resp.status) < 300,
                "status": int(resp.status),
                "elapsed_s": round(time.time() - started, 3),
                "content_type": resp.headers.get("content-type"),
                "bytes": len(raw),
                "sha256": hashlib.sha256(raw).hexdigest(),
                "data": redact(data),
                "text_preview": None if data is not None else text[:500],
                "error": None,
            }
    except urllib.error.HTTPError as exc:
        body = exc.read(4096)
        return {
            "name": name,
            "endpoint": endpoint,
            "url": url,
            "ok": False,
            "status": int(exc.code),
            "elapsed_s": round(time.time() - started, 3),
            "content_type": exc.headers.get("content-type") if exc.headers else None,
            "bytes": len(body),
            "sha256": hashlib.sha256(body).hexdigest() if body else None,
            "data": None,
            "text_preview": body.decode("utf-8", errors="replace")[:500] if body else "",
            "error": f"http_error:{exc.code}",
        }
    except Exception as exc:  # noqa: BLE001 - report only
        return {
            "name": name,
            "endpoint": endpoint,
            "url": url,
            "ok": False,
            "status": None,
            "elapsed_s": round(time.time() - started, 3),
            "content_type": None,
            "bytes": 0,
            "sha256": None,
            "data": None,
            "text_preview": "",
            "error": f"{type(exc).__name__}: {exc}",
        }


def walk_values(obj: Any):
    if isinstance(obj, dict):
        for key, value in obj.items():
            yield key, value
            yield from walk_values(value)
    elif isinstance(obj, list):
        for item in obj:
            yield from walk_values(item)


def is_market_closed_zero_expected(data: Any) -> bool:
    if not isinstance(data, dict):
        return False
    status = str(data.get("status") or "").upper()
    contracts = int(data.get("total_contracts") or 0)
    return bool(contracts == 0 and (data.get("skipped") is True or status in {"MARKET_CLOSED", "MARKET_CLOSED_EXPECTED"}))


def synthetic_marked_trade_ready(data: Any) -> bool:
    if not isinstance(data, dict):
        return False
    source = str(data.get("data_source") or data.get("source") or "").lower()
    status = str(data.get("status") or "").upper()
    ready = bool(data.get("trade_ready") or data.get("tradeable") or data.get("ready_for_trade"))
    return ("synthetic" in source or "fake" in source) and (ready or status in {"MARKET_OPEN", "LIVE", "TRADE_READY"})


def chain_anomalies(name: str, data: Any) -> list[dict[str, Any]]:
    rows = []
    if not isinstance(data, dict):
        return rows
    contracts = data.get("contracts") or []
    if not contracts:
        if not is_market_closed_zero_expected(data):
            rows.append({"surface": name, "severity": "warning", "check": "zero_contracts", "detail": str(data.get("status"))})
        return rows
    source = str(data.get("data_source") or data.get("source") or "")
    if synthetic_marked_trade_ready(data):
        rows.append({"surface": name, "severity": "critical", "check": "synthetic_trade_ready", "detail": source})
    for idx, contract in enumerate(contracts[:1000]):
        bid = contract.get("bidPrice", contract.get("top_bid_price", contract.get("bid")))
        ask = contract.get("offerPrice", contract.get("top_ask_price", contract.get("ask")))
        try:
            if bid is not None and ask is not None and float(ask) < float(bid):
                rows.append({"surface": name, "severity": "critical", "check": "ask_lt_bid", "detail": f"row={idx}"})
        except Exception:
            pass
        try:
            if contract.get("ltp") is not None and float(contract.get("ltp")) < 0:
                rows.append({"surface": name, "severity": "critical", "check": "negative_ltp", "detail": f"row={idx}"})
        except Exception:
            pass
        try:
            if contract.get("iv") is not None and (float(contract.get("iv")) < 0 or float(contract.get("iv")) > 3):
                rows.append({"surface": name, "severity": "high", "check": "invalid_iv", "detail": f"row={idx}"})
        except Exception:
            pass
    return rows


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    endpoint_results = {name: fetch_json(name, endpoint) for name, endpoint in ENDPOINTS.items()}

    snapshot_verdict = load_json(SNAP_DIR / "latest_verdict.json") or {}
    ui_preview = load_text(SNAP_DIR / "latest_ui_preview.txt")
    frontend_header = str(snapshot_verdict.get("frontend_header") or "").lower()
    raw_vue_visible = "{{" in ui_preview or "v-if" in ui_preview or "v-for" in ui_preview

    critical = []
    warnings = []
    anomaly_rows = []

    for result in endpoint_results.values():
        data = result.get("data")
        if not result.get("ok"):
            warnings.append(f"{result['name']}: endpoint not ok ({result.get('status') or result.get('error')})")
        if isinstance(data, dict):
            for key, value in walk_values(data):
                key_l = str(key).lower()
                if key_l == "mode" and str(value).upper() == "LIVE":
                    critical.append(f"{result['name']}: mode=LIVE")
                if key_l == "live_trading_enabled" and value is True:
                    critical.append(f"{result['name']}: live_trading_enabled=true")
                if key_l == "order_placement_allowed" and value is True:
                    critical.append(f"{result['name']}: order_placement_allowed=true")
            if synthetic_marked_trade_ready(data):
                critical.append(f"{result['name']}: synthetic data marked trade-ready")

    if frontend_header == "vue-legacy":
        critical.append("frontend is vue-legacy")
    if raw_vue_visible:
        critical.append("raw Vue template tokens are visible")

    for name in ["chain_nifty", "chain_banknifty", "chain_finnifty", "chain_midcpnifty"]:
        anomaly_rows.extend(chain_anomalies(name, endpoint_results[name].get("data")))
    runtime_data = endpoint_results["qc_runtime"].get("data")
    if isinstance(runtime_data, dict):
        for item in runtime_data.get("critical_failures") or []:
            critical.append(f"qc_runtime: {item}")
        for item in runtime_data.get("warnings") or []:
            warnings.append(f"qc_runtime: {item}")

    critical.extend([f"{r['surface']}: {r['check']} {r['detail']}" for r in anomaly_rows if r["severity"] == "critical"])
    warnings.extend([f"{r['surface']}: {r['check']} {r['detail']}" for r in anomaly_rows if r["severity"] != "critical"])

    safety_verdict = {
        "generated_utc": utc_now(),
        "safety_verdict": "CRITICAL_FAIL" if critical else "PASS_ANALYZER_PAPER_ONLY",
        "critical_failures": sorted(set(critical)),
        "warnings": sorted(set(warnings)),
        "live_trading_enabled": False,
        "order_placement_allowed": False,
    }
    summary = {
        "generated_utc": safety_verdict["generated_utc"],
        "backend_url": BACKEND_URL,
        "dashboard_url": DASHBOARD_URL,
        "status": "FAIL" if critical else ("WARN" if warnings else "PASS"),
        "anomaly_audit_verdict": safety_verdict["safety_verdict"],
        "market_closed_zero_contract_policy": "zero contracts accepted when status is MARKET_CLOSED/MARKET_CLOSED_EXPECTED or skipped=true",
        "endpoint_count": len(endpoint_results),
        "endpoint_ok_count": sum(1 for result in endpoint_results.values() if result.get("ok")),
        "runtime_qc_available": bool(endpoint_results["qc_runtime"].get("ok")),
        "safety_verdict": safety_verdict["safety_verdict"],
        "critical_failures": safety_verdict["critical_failures"],
        "warnings": safety_verdict["warnings"],
        "files_generated": [
            "summary.md",
            "summary.json",
            "endpoint_matrix.json",
            "runtime_qc.json",
            "chain_matrix.json",
            "anomaly_matrix.csv",
            "safety_verdict.json",
        ],
    }

    chain_matrix = {name: endpoint_results[name] for name in ["chain_nifty", "chain_banknifty", "chain_finnifty", "chain_midcpnifty"]}
    write_json(OUT_DIR / "summary.json", summary)
    write_json(OUT_DIR / "endpoint_matrix.json", endpoint_results)
    write_json(OUT_DIR / "runtime_qc.json", endpoint_results["qc_runtime"])
    write_json(OUT_DIR / "chain_matrix.json", chain_matrix)
    write_json(OUT_DIR / "safety_verdict.json", safety_verdict)

    with (OUT_DIR / "anomaly_matrix.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["surface", "severity", "check", "detail"])
        writer.writeheader()
        for row in anomaly_rows:
            writer.writerow(row)

    lines = [
        "# Runtime QC Anomaly Audit",
        "",
        f"- Generated UTC: {summary['generated_utc']}",
        f"- Backend URL: {BACKEND_URL}",
        f"- Status: {summary['status']}",
        f"- Anomaly audit verdict: {summary['anomaly_audit_verdict']}",
        f"- Runtime QC available: {summary['runtime_qc_available']}",
        f"- Endpoint OK: {summary['endpoint_ok_count']}/{summary['endpoint_count']}",
        "- Market closed zero-contract policy: expected skip, not failure",
        "- Live trading enabled: false",
        "- Order placement allowed: false",
        "",
        "## Critical Failures",
        "",
    ]
    lines.extend([f"- {item}" for item in summary["critical_failures"]] or ["- None"])
    lines.extend(["", "## Warnings", ""])
    lines.extend([f"- {item}" for item in summary["warnings"]] or ["- None"])
    (OUT_DIR / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps(summary, indent=2, sort_keys=True))
    return 2 if critical else 0


if __name__ == "__main__":
    sys.exit(main())
