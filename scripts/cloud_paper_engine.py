#!/usr/bin/env python3
"""Fail-closed Cloud Run PAPER execution loop.

This process deliberately has no broker order-placement dependency. It consumes
only the local System3 read APIs and feeds explicit TRADE signals into the
simulation-only ``PaperExecutor``. LIVE order authority remains impossible while
``LIVE_TRADING_ENABLED`` and ``SYSTEM3_LIVE_TRADING_ALLOWED`` are both false.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import pytz

from src.trading.paper_executor import PaperExecutor

IST = pytz.timezone("Asia/Kolkata")
ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = ROOT / "outputs"
STATUS_PATH = OUTPUTS / "cloud_paper_engine_status.json"
TRADES_PATH = OUTPUTS / "paper_trades_live.csv"
POSITIONS_PATH = OUTPUTS / "positions_live.json"
POLL_S = max(3, int(os.getenv("SYSTEM3_PAPER_POLL_S", "5")))
PORT = int(os.getenv("PORT", "8080"))
BASE = os.getenv("SYSTEM3_LOCAL_API_BASE", f"http://127.0.0.1:{PORT}").rstrip("/")


def _enabled(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def paper_runtime_contract() -> dict[str, Any]:
    return {
        "analyze_mode": os.getenv("ANALYZE_MODE", "1"),
        "system3_mode": os.getenv("SYSTEM3_MODE", "ANALYZER").upper(),
        "cloud_paper_engine": _enabled(os.getenv("CLOUD_PAPER_ENGINE", "0")),
        "auto_execute_trades": _enabled(os.getenv("AUTO_EXECUTE_TRADES", "0")),
        "live_trading_enabled": _enabled(os.getenv("LIVE_TRADING_ENABLED", "0")),
        "system3_live_trading_allowed": _enabled(os.getenv("SYSTEM3_LIVE_TRADING_ALLOWED", "0")),
    }


def assert_paper_only_contract() -> dict[str, Any]:
    contract = paper_runtime_contract()
    problems: list[str] = []
    if contract["analyze_mode"] != "0":
        problems.append("ANALYZE_MODE_MUST_BE_0")
    if contract["system3_mode"] != "PAPER":
        problems.append("SYSTEM3_MODE_MUST_BE_PAPER")
    if not contract["cloud_paper_engine"]:
        problems.append("CLOUD_PAPER_ENGINE_MUST_BE_1")
    if not contract["auto_execute_trades"]:
        problems.append("AUTO_EXECUTE_TRADES_MUST_BE_1")
    if contract["live_trading_enabled"]:
        problems.append("LIVE_TRADING_ENABLED_MUST_BE_0")
    if contract["system3_live_trading_allowed"]:
        problems.append("SYSTEM3_LIVE_TRADING_ALLOWED_MUST_BE_0")
    if problems:
        raise RuntimeError("paper_runtime_contract_invalid:" + ",".join(problems))
    return contract


def _get_json(path: str, timeout: float = 12.0) -> Any:
    req = urllib.request.Request(
        BASE + path,
        headers={"Accept": "application/json", "User-Agent": "system3-cloud-paper-engine/1"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        if response.status != 200:
            raise RuntimeError(f"HTTP_{response.status}:{path}")
        return json.loads(response.read().decode("utf-8"))


def _write_status(state: str, **extra: Any) -> None:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    payload = {
        "state": state,
        "observed_at_ist": datetime.now(IST).isoformat(),
        "paper_only": True,
        "broker_orders_called": False,
        "live_trading_enabled": False,
        "system3_live_trading_allowed": False,
        **extra,
    }
    STATUS_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print("[cloud-paper] " + json.dumps(payload, sort_keys=True), flush=True)


def _signal_candidates(payload: Any) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            action = str(value.get("action") or "").upper()
            if action == "TRADE":
                found.append(value)
            for child in value.values():
                if isinstance(child, (dict, list)):
                    walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)

    walk(payload)
    return found


def _fingerprint(signal: dict[str, Any]) -> str:
    stable = {
        key: signal.get(key)
        for key in ("signal_id", "underlying", "strategy", "tokens", "strikes", "timestamp", "observed_at")
    }
    return hashlib.sha256(json.dumps(stable, sort_keys=True, default=str).encode()).hexdigest()


def _contracts(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [row for row in payload if isinstance(row, dict)]
    if not isinstance(payload, dict):
        return []
    for key in ("contracts", "chain", "data", "rows"):
        rows = payload.get(key)
        if isinstance(rows, list):
            return [row for row in rows if isinstance(row, dict)]
    return []


def _normalize_contracts(rows: list[dict[str, Any]]) -> pd.DataFrame:
    normalized: list[dict[str, Any]] = []
    for row in rows:
        item = dict(row)
        item.setdefault("token", item.get("security_id") or item.get("securityId") or item.get("security_id_s"))
        item.setdefault("symbol", item.get("trading_symbol") or item.get("tradingSymbol") or item.get("display_name") or "")
        item.setdefault("option_type", item.get("type") or item.get("optionType") or item.get("right") or "")
        item.setdefault("ltp", item.get("last_price") or item.get("lastPrice") or 0)
        item.setdefault("mid_price", item.get("ltp") or 0)
        item.setdefault("bidPrice", item.get("bid_price") or item.get("top_bid_price") or item.get("ltp") or 0)
        item.setdefault("offerPrice", item.get("ask_price") or item.get("top_ask_price") or item.get("ltp") or 0)
        item.setdefault("lotSize", item.get("lot_size") or item.get("lot") or 1)
        normalized.append(item)
    return pd.DataFrame(normalized)


def _persist(executor: PaperExecutor) -> None:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    open_positions = [dict(p) for p in executor.positions.values() if p.get("status") == "OPEN"]
    POSITIONS_PATH.write_text(
        json.dumps({"open_positions": open_positions, "count": len(open_positions)}, indent=2, default=str),
        encoding="utf-8",
    )
    if executor.trade_history:
        pd.DataFrame(executor.trade_history).to_csv(TRADES_PATH, index=False)


def run_forever() -> None:
    contract = assert_paper_only_contract()
    executor = PaperExecutor()
    seen: set[str] = set()
    _write_status("STARTING", contract=contract)

    while True:
        try:
            health = _get_json("/api/health")
            if not isinstance(health, dict):
                raise RuntimeError("health_not_object")
            market = health.get("market") if isinstance(health.get("market"), dict) else {}
            market_open = bool(market.get("is_open", health.get("market_status") == "open"))
            broker = health.get("broker") if isinstance(health.get("broker"), dict) else {}
            broker_connected = bool(broker.get("connected", health.get("broker_status") == "connected"))
            qc_status = str(health.get("qc_status") or (health.get("qc") or {}).get("status") or "NOT_READY").upper()

            # The engine is fail-closed: no paper fill unless current production truth
            # proves an open market, connected broker, and usable QC.
            if not market_open or not broker_connected or qc_status not in {"PASS", "READY"}:
                _write_status(
                    "IDLE_NOT_READY",
                    market_open=market_open,
                    broker_connected=broker_connected,
                    qc_status=qc_status,
                    open_positions=len(executor.positions),
                )
                time.sleep(POLL_S)
                continue

            signal_payload = _get_json("/api/signals")
            candidates = _signal_candidates(signal_payload)
            executed = 0
            chain_cache: dict[str, pd.DataFrame] = {}

            for signal in candidates:
                fp = _fingerprint(signal)
                if fp in seen:
                    continue
                underlying = str(signal.get("underlying") or "").strip().upper()
                if not underlying:
                    continue
                if underlying not in chain_cache:
                    chain_cache[underlying] = _normalize_contracts(_contracts(_get_json(f"/api/chain/{underlying}")))
                frame = chain_cache[underlying]
                if frame.empty:
                    continue
                position = executor.execute_trade(signal, frame, datetime.now(IST).isoformat())
                if position is not None:
                    seen.add(fp)
                    executed += 1

            if executor.positions:
                needed = {str(p.get("underlying") or "").upper() for p in executor.positions.values()}
                for underlying in sorted(filter(None, needed)):
                    if underlying not in chain_cache:
                        chain_cache[underlying] = _normalize_contracts(_contracts(_get_json(f"/api/chain/{underlying}")))
                executor.update_positions(chain_cache, datetime.now(IST).isoformat())

            _persist(executor)
            _write_status(
                "RUNNING",
                market_open=True,
                broker_connected=True,
                qc_status=qc_status,
                candidate_signals=len(candidates),
                paper_trades_executed_this_cycle=executed,
                open_positions=len(executor.positions),
                broker_orders_called=False,
            )
        except (urllib.error.URLError, TimeoutError, RuntimeError, ValueError, KeyError) as exc:
            _write_status("DEGRADED_FAIL_CLOSED", error_type=type(exc).__name__, message=str(exc)[:200])
        except Exception as exc:  # keep supervisor alive, but never trade through an unproven state
            _write_status("DEGRADED_FAIL_CLOSED", error_type=type(exc).__name__, message=str(exc)[:200])
        time.sleep(POLL_S)


if __name__ == "__main__":
    run_forever()
