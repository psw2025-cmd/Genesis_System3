#!/usr/bin/env python3
"""System3 cloud dashboard proof checker.

Read-only by design. It only performs HTTP GET requests and writes proof files.
It fails only for hard safety/runtime blockers:
- API unreachable
- live trading enabled
- order placement allowed
- state.mode=LIVE
- instrument master missing evidence
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

BASE_URL = os.environ.get("SYSTEM3_CLOUD_BASE", "https://genesis-system3-backend.onrender.com").rstrip("/")
OUT_DIR = Path(os.environ.get("SYSTEM3_PROOF_DIR", "reports/latest/cloud_live_ui_paper_prediction_check"))
API_DIR = OUT_DIR / "api"
ENDPOINTS = [
    "/api/state",
    "/api/status",
    "/api/health",
    "/api/paper",
    "/api/trades/today",
    "/api/trades/history",
    "/api/gain_rank",
    "/api/accuracy_trend",
    "/api/auto_gates",
    "/api/broker/status",
    "/api/broker/dhan/status",
    "/api/broker/positions/live",
    "/api/broker/funds",
    "/api/portfolio/unified",
    "/api/broker/truth",
    "/api/trader/requirements",
    "/api/debug/state_source",
]
UI_PATHS = ["/ui", "/ui/app.js", "/ui/style.css"]
INSTRUMENT_PATHS = [
    "storage/instruments/OpenAPIScripMaster.json",
    "src/storage/instruments/OpenAPIScripMaster.json",
    "dashboard/backend/storage/instruments/OpenAPIScripMaster.json",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def safe_name(path: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", path.strip("/").replace("/", "_") or "root")


def fetch_path(path: str, timeout: int = 25) -> Dict[str, Any]:
    url = BASE_URL + path
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "System3-cloud-proof/1.2-read-only",
            "Accept": "application/json,text/html,text/plain,*/*",
            "Cache-Control": "no-cache",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # nosec: configured cloud proof URL only
            body = resp.read().decode("utf-8", errors="replace")
            status = int(resp.status)
            headers = {k.lower(): v for k, v in resp.headers.items()}
            parsed = _parse_json(body)
            return {
                "endpoint": path,
                "url": url,
                "status": status,
                "ok": 200 <= status < 300,
                "content_type": headers.get("content-type"),
                "bytes": len(body.encode("utf-8")),
                "data": parsed,
                "text_preview": body[:3000] if parsed is None else None,
                "error": None,
            }
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
        return {"endpoint": path, "url": url, "status": int(exc.code), "ok": False, "data": _parse_json(body), "text_preview": body[:3000], "error": f"HTTPError: {exc}"}
    except Exception as exc:  # noqa: BLE001
        return {"endpoint": path, "url": url, "status": None, "ok": False, "data": None, "text_preview": None, "error": f"{type(exc).__name__}: {exc}"}


def _parse_json(text: str) -> Any:
    try:
        return json.loads(text)
    except Exception:
        return None


def walk(obj: Any, prefix: str = "") -> Iterable[Tuple[str, Any]]:
    if isinstance(obj, dict):
        for key, val in obj.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            yield path, val
            yield from walk(val, path)
    elif isinstance(obj, list):
        for idx, val in enumerate(obj):
            path = f"{prefix}[{idx}]"
            yield path, val
            yield from walk(val, path)


def true_hits(payloads: Dict[str, Any], key_name: str) -> List[Dict[str, Any]]:
    hits: List[Dict[str, Any]] = []
    for endpoint, payload in payloads.items():
        for path, val in walk(payload):
            if path.split(".")[-1] == key_name and val is True:
                hits.append({"endpoint": endpoint, "path": path, "value": val})
    return hits


def get_nested(data: Any, *keys: str, default: Any = None) -> Any:
    cur = data
    for key in keys:
        if isinstance(cur, dict) and key in cur:
            cur = cur[key]
        else:
            return default
    return cur


def count_trades(today_payload: Any, history_payload: Any) -> Dict[str, Any]:
    out: Dict[str, Any] = {"today_count": None, "history_count": None, "source": None}
    if isinstance(today_payload, dict):
        for key in ("count", "total_trades", "trade_count"):
            if isinstance(today_payload.get(key), int):
                out["today_count"] = today_payload[key]
                out["source"] = f"/api/trades/today.{key}"
                break
        if out["today_count"] is None:
            rows = today_payload.get("entries") or today_payload.get("trades") or today_payload.get("orders")
            if isinstance(rows, list):
                out["today_count"] = len(rows)
                out["source"] = "/api/trades/today list length"
    if isinstance(history_payload, dict):
        if isinstance(history_payload.get("count"), int):
            out["history_count"] = history_payload["count"]
        elif isinstance(history_payload.get("trades"), list):
            out["history_count"] = len(history_payload["trades"])
    return out


def prediction_summary(gain_rank: Any, accuracy: Any) -> Dict[str, Any]:
    out: Dict[str, Any] = {"available": False, "prediction_count": 0, "top_prediction": None, "days_available": None, "latest_rho": None, "avg_rho": None, "stale": None, "is_today": None}
    if isinstance(gain_rank, dict):
        latest = gain_rank.get("latest") or {}
        preds = latest.get("predictions") if isinstance(latest, dict) else None
        if isinstance(preds, list):
            out["available"] = bool(preds)
            out["prediction_count"] = len(preds)
            out["top_prediction"] = preds[0] if preds else None
        out["stale"] = gain_rank.get("stale")
        out["is_today"] = gain_rank.get("is_today")
    if isinstance(accuracy, dict):
        out["days_available"] = accuracy.get("days_available")
        out["avg_rho"] = accuracy.get("avg_rho")
        trend = accuracy.get("trend")
        if isinstance(trend, list) and trend and isinstance(trend[-1], dict):
            out["latest_rho"] = trend[-1].get("rho")
    return out


def instrument_repo_check() -> Dict[str, Any]:
    checked = []
    found = []
    for rel in INSTRUMENT_PATHS:
        p = Path(rel)
        exists = p.exists()
        size = p.stat().st_size if exists else 0
        checked.append({"path": rel, "exists": exists, "size_bytes": size})
        if exists and size > 0:
            found.append(rel)
    return {
        "status": "PASS" if found else "FAIL",
        "found": found,
        "checked": checked,
        "blocker_if_missing": "OpenAPIScripMaster.json missing. Render logs show TokenManager cannot find /app/storage/instruments/OpenAPIScripMaster.json.",
    }


def ui_static_check() -> Dict[str, Any]:
    result: Dict[str, Any] = {"paths": {}, "checks": {}, "screenshot": None, "errors": []}
    combined = ""
    for path in UI_PATHS:
        res = fetch_path(path)
        result["paths"][path] = {k: v for k, v in res.items() if k != "data"}
        text = res.get("text_preview") or ""
        if res.get("data") is not None:
            text = json.dumps(res.get("data"))
        (OUT_DIR / f"ui_{safe_name(path)}.txt").write_text(text, encoding="utf-8")
        combined += "\n" + text
    result["checks"] = {
        "shows_analyzer_paper": "ANALYZER / PAPER" in combined or "PAPER ONLY" in combined,
        "shows_live_disabled": "LIVE DISABLED" in combined or "LIVE TRADING" in combined,
        "shows_order_blocked": "ORDER PLACEMENT" in combined and "BLOCKED" in combined,
        "has_auto_gates_fetch": "/api/auto_gates" in combined,
        "has_paper_endpoint_fetch": "/api/paper" in combined,
        "has_gain_rank_fetch": "/api/gain_rank" in combined,
    }
    if os.environ.get("SYSTEM3_PLAYWRIGHT_SCREENSHOT", "0").lower() in {"1", "true", "yes"}:
        try:
            from playwright.sync_api import sync_playwright  # type: ignore
            shot = OUT_DIR / "dashboard_ui_screenshot.png"
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page(viewport={"width": 1440, "height": 1400})
                page.goto(BASE_URL + "/ui", wait_until="networkidle", timeout=60000)
                page.screenshot(path=str(shot), full_page=True)
                browser.close()
            result["screenshot"] = str(shot)
        except Exception as exc:  # noqa: BLE001
            result["errors"].append(f"screenshot_failed: {type(exc).__name__}: {exc}")
    return result


def market_reference() -> Dict[str, Any]:
    refs = {"source": "Yahoo Finance chart API, best-effort only", "symbols": {}, "errors": []}
    for label, encoded in {"NIFTY50": "%5ENSEI", "SENSEX": "%5EBSESN"}.items():
        url_path = f"https://query1.finance.yahoo.com/v8/finance/chart/{encoded}?range=1d&interval=5m"
        try:
            req = urllib.request.Request(url_path, headers={"User-Agent": "System3-cloud-proof/1.2"})
            with urllib.request.urlopen(req, timeout=20) as resp:  # nosec: public market reference only
                body = resp.read().decode("utf-8", errors="replace")
            (OUT_DIR / f"market_{label.lower()}.json").write_text(body, encoding="utf-8")
            data = json.loads(body)["chart"]["result"][0]
            meta = data.get("meta", {})
            price = meta.get("regularMarketPrice")
            prev = meta.get("chartPreviousClose") or meta.get("previousClose")
            pct = round(((price - prev) / prev) * 100, 4) if isinstance(price, (int, float)) and isinstance(prev, (int, float)) and prev else None
            refs["symbols"][label] = {"regularMarketPrice": price, "previousClose": prev, "pct_change": pct, "exchangeName": meta.get("exchangeName"), "timezone": meta.get("timezone")}
        except Exception as exc:  # noqa: BLE001
            refs["errors"].append({"symbol": label, "error": f"{type(exc).__name__}: {exc}"})
    return refs


def build_markdown(summary: Dict[str, Any]) -> str:
    verdict = summary["verdict"]
    lines = [
        "# Cloud Live UI / Paper / Prediction Proof",
        "",
        f"- Generated UTC: `{summary['generated_utc']}`",
        f"- Base URL: `{summary['base_url']}`",
        f"- Overall: `{verdict['overall']}`",
        f"- Live trading enabled: `{verdict['live_trading_enabled']}`",
        f"- Order placement allowed: `{verdict['order_placement_allowed']}`",
        f"- Paper trade today count: `{summary['paper_trade_check'].get('today_count')}`",
        f"- Prediction available: `{summary['prediction_check'].get('available')}`",
        f"- Instrument master status: `{summary['instrument_repo_check'].get('status')}`",
        "",
        "## Blockers",
    ]
    lines += [f"- `{b}`" for b in verdict["blockers"]] or ["- None"]
    lines += ["", "## Warnings"]
    lines += [f"- `{w}`" for w in verdict["warnings"]] or ["- None"]
    lines += ["", "## Endpoint status"]
    for ep, item in summary["endpoints"].items():
        lines.append(f"- `{ep}`: status=`{item.get('status')}`, ok=`{item.get('ok')}`, error=`{item.get('error')}`")
    lines += ["", "## Safety note", "This check is read-only. It does not place, modify, cancel, or authorize orders."]
    return "\n".join(lines) + "\n"


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    API_DIR.mkdir(parents=True, exist_ok=True)
    payloads: Dict[str, Any] = {}
    endpoint_status: Dict[str, Any] = {}
    for ep in ENDPOINTS:
        res = fetch_path(ep)
        endpoint_status[ep] = {k: v for k, v in res.items() if k != "data"}
        data = res.get("data")
        suffix = "json" if data is not None else "txt"
        (API_DIR / f"{safe_name(ep)}.{suffix}").write_text(json.dumps(data, indent=2, ensure_ascii=False) if data is not None else (res.get("text_preview") or ""), encoding="utf-8")
        if data is not None:
            payloads[ep] = data
        print(f"[{'OK' if res.get('ok') else 'FAIL'}] {ep} status={res.get('status')}")
        time.sleep(0.15)

    inst = instrument_repo_check()
    (OUT_DIR / "instrument_master_repo_check.json").write_text(json.dumps(inst, indent=2), encoding="utf-8")
    ui = ui_static_check()
    market = market_reference()

    live_hits = true_hits(payloads, "live_trading_enabled")
    order_hits = true_hits(payloads, "order_placement_allowed")
    state = payloads.get("/api/state") if isinstance(payloads.get("/api/state"), dict) else {}
    mode = get_nested(state, "mode")
    data_source = get_nested(state, "data_source")
    broker_connected = get_nested(state, "broker", "connected")
    paper = count_trades(payloads.get("/api/trades/today"), payloads.get("/api/trades/history"))
    pred = prediction_summary(payloads.get("/api/gain_rank"), payloads.get("/api/accuracy_trend"))

    blockers: List[str] = []
    warnings: List[str] = []
    if not endpoint_status.get("/api/state", {}).get("ok"):
        blockers.append("API_STATE_NOT_REACHABLE")
    if live_hits:
        blockers.append("LIVE_TRADING_ENABLED_TRUE_IN_API")
    if order_hits:
        blockers.append("ORDER_PLACEMENT_ALLOWED_TRUE_IN_API")
    if str(mode).upper() == "LIVE":
        blockers.append("STATE_MODE_LIVE")
    if inst.get("status") != "PASS":
        blockers.append("INSTRUMENT_MASTER_MISSING_IN_REPO_PROOF")
    if paper.get("today_count") in (None, 0):
        warnings.append("NO_PAPER_TRADE_TODAY_PROVEN")
    if not pred.get("available"):
        warnings.append("NO_TODAY_PREDICTION_OUTPUT_PROVEN")
    if pred.get("stale") is True or pred.get("is_today") is False:
        warnings.append("PREDICTION_OUTPUT_STALE_OR_NOT_TODAY")
    if str(data_source).upper() in {"SYNTHETIC", "NOT_READY", "NONE", "NULL"}:
        warnings.append(f"DATA_SOURCE_NOT_REAL_OR_READY:{data_source}")
    if broker_connected is not True:
        warnings.append("BROKER_NOT_CONNECTED_OR_NOT_PROVEN")
    if not ui.get("screenshot"):
        warnings.append("BROWSER_SCREENSHOT_NOT_PRODUCED")

    overall = "FAIL" if blockers else ("PASS_WITH_WARNINGS" if warnings else "PASS")
    summary = {
        "generated_utc": utc_now(),
        "base_url": BASE_URL,
        "mode": mode,
        "data_source": data_source,
        "broker_connected": broker_connected,
        "endpoints": endpoint_status,
        "paper_trade_check": paper,
        "prediction_check": pred,
        "ui_check": ui,
        "market_reference": market,
        "instrument_repo_check": inst,
        "safety_hits": {"live_trading_enabled_true": live_hits, "order_placement_allowed_true": order_hits},
        "verdict": {"overall": overall, "blockers": blockers, "warnings": warnings, "live_trading_enabled": bool(live_hits), "order_placement_allowed": bool(order_hits), "trade_ready": False, "real_money_ready": False},
    }
    (OUT_DIR / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    (OUT_DIR / "summary.md").write_text(build_markdown(summary), encoding="utf-8")
    print(json.dumps(summary["verdict"], indent=2))
    return 2 if blockers else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001
        print(f"fatal: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise
