"""One bounded PAPER-only lifecycle tick for Cloud Run Jobs.

This is the production paper execution authority. It deliberately does not run
inside the web service. Each invocation:
1. acquires a fenced Firestore writer lease;
2. restores the last durable paper state;
3. fetches read-only Dhan option chains when the exchange is open;
4. executes one local simulation tick (never a broker order);
5. persists the resulting state + immutable lifecycle events to Firestore.
"""
from __future__ import annotations

import copy
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from dashboard.backend.chain_adapter import fetch_chain_for_api
from dashboard.backend.cloud_paper_engine import CloudPaperEngine
from dashboard.backend.paper_ledger_backend import FirestorePaperLedgerBackend, paper_event_id

ROOT = Path(__file__).resolve().parents[2]
INDEX_UNDERLYINGS = ("NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY")


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _market_context() -> tuple[bool, str]:
    try:
        from utils.market_hours import is_market_open

        is_open, reason = is_market_open()
        return bool(is_open), str(reason or ("OPEN" if is_open else "MARKET_CLOSED"))
    except Exception as exc:
        return False, f"MARKET_CALENDAR_UNAVAILABLE:{type(exc).__name__}"


def _hydrate_engine(engine: CloudPaperEngine, current: Dict[str, Any] | None) -> None:
    current = current or {}
    engine.open_positions = copy.deepcopy(current.get("open_positions") or [])
    engine.closed_positions = copy.deepcopy(current.get("closed_positions") or [])
    engine.seq = int(current.get("seq", 0) or 0)
    engine.session_date = str(current.get("session_date") or "")


def _event_key(row: Dict[str, Any]) -> str:
    return str(row.get("event_id") or paper_event_id(row))


def _new_lifecycle_events(
    before_open: List[Dict[str, Any]],
    before_closed: List[Dict[str, Any]],
    after_open: List[Dict[str, Any]],
    after_closed: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    before_open_ids = {str(row.get("position_id") or "") for row in before_open}
    before_closed_keys = {
        (str(row.get("position_id") or ""), str(row.get("time_ist") or ""), str(row.get("exit_reason") or ""))
        for row in before_closed
    }
    events: List[Dict[str, Any]] = []
    for row in after_open:
        if str(row.get("position_id") or "") not in before_open_ids:
            event = {**copy.deepcopy(row), "action": "OPEN", "broker_order_endpoints_called": False, "live_trading_enabled": False}
            event["event_id"] = _event_key(event)
            events.append(event)
    for row in after_closed:
        key = (str(row.get("position_id") or ""), str(row.get("time_ist") or ""), str(row.get("exit_reason") or ""))
        if key not in before_closed_keys:
            event = {**copy.deepcopy(row), "action": "CLOSE", "broker_order_endpoints_called": False, "live_trading_enabled": False}
            event["event_id"] = _event_key(event)
            events.append(event)
    return events


def _merge_recent(existing: List[Dict[str, Any]], new_events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    ordered: List[Dict[str, Any]] = []
    seen = set()
    for row in [*(existing or []), *new_events]:
        if not isinstance(row, dict):
            continue
        event = copy.deepcopy(row)
        event["event_id"] = _event_key(event)
        if event["event_id"] in seen:
            continue
        seen.add(event["event_id"])
        ordered.append(event)
    return ordered[-FirestorePaperLedgerBackend.MAX_RECENT_EVENTS :]


def _snapshot(
    engine: CloudPaperEngine,
    current: Dict[str, Any] | None,
    *,
    recent_events: List[Dict[str, Any]],
    chains: List[Dict[str, Any]],
    market_open: bool,
    market_reason: str,
    execution: str,
) -> Dict[str, Any]:
    current = current or {}
    totals = dict(current.get("history_totals") or {})
    prior_ids = {str(row.get("event_id") or "") for row in (current.get("recent_events") or []) if isinstance(row, dict)}
    newly_visible = [row for row in recent_events if str(row.get("event_id") or "") not in prior_ids]
    totals["open_events"] = int(totals.get("open_events", 0) or 0) + sum(1 for row in newly_visible if str(row.get("action") or "").upper() == "OPEN")
    totals["close_events"] = int(totals.get("close_events", 0) or 0) + sum(1 for row in newly_visible if str(row.get("action") or "").upper() == "CLOSE")
    totals["events"] = int(totals.get("open_events", 0) or 0) + int(totals.get("close_events", 0) or 0)
    real_chains = [row for row in chains if str(row.get("data_source") or "").lower() == "dhan" and row.get("contracts")]
    if market_open and real_chains:
        data_source = "DHAN_LIVE_MARK_TO_MARKET"
    elif market_open:
        data_source = "NO_DHAN_CHAIN"
    else:
        data_source = "MARKET_CLOSED_DURABLE_LEDGER"
    return {
        "schema_version": 1,
        "mode": "PAPER",
        "session_date": engine.session_date,
        "seq": int(engine.seq),
        "open_positions": copy.deepcopy(engine.open_positions),
        "closed_positions": copy.deepcopy(engine.closed_positions),
        "recent_events": recent_events,
        "history_totals": totals,
        "data_source": data_source,
        "market_open": market_open,
        "market_reason": market_reason,
        "chain_underlyings_ready": [str(row.get("underlying") or "") for row in real_chains],
        "chain_count": len(real_chains),
        "updated_at_utc": _utc_iso(),
        "job_execution": execution,
        "deploy_git_sha": os.environ.get("DEPLOY_GIT_SHA") or os.environ.get("GITHUB_SHA"),
        "broker_order_endpoints_called": False,
        "live_trading_enabled": False,
    }


def run_durable_paper_once(*, backend: FirestorePaperLedgerBackend | None = None) -> Dict[str, Any]:
    # Redundant safety locks: the generic worker also enforces these before calling us.
    os.environ["LIVE_TRADING_ENABLED"] = "0"
    os.environ["SYSTEM3_LIVE_TRADING_ALLOWED"] = "0"
    os.environ["AUTO_EXECUTE_TRADES"] = "0"
    os.environ["ANALYZE_MODE"] = "1"

    execution = (
        os.environ.get("CLOUD_RUN_EXECUTION")
        or os.environ.get("SYSTEM3_PAPER_EXECUTION_ID")
        or f"manual-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    )
    backend = backend or FirestorePaperLedgerBackend()
    lease = backend.acquire_lease(execution, 55)
    if not lease.get("acquired"):
        return {
            "status": "SKIPPED_LEASE_HELD",
            "lease_owner": lease.get("owner"),
            "mode": "PAPER",
            "live_trading_enabled": False,
            "broker_order_endpoints_called": False,
        }

    current = backend.load_current()
    mirror_dir = Path(os.environ.get("SYSTEM3_PAPER_LOCAL_MIRROR_DIR") or (ROOT / "outputs"))
    mirror_dir.mkdir(parents=True, exist_ok=True)
    engine = CloudPaperEngine(mirror_dir)
    _hydrate_engine(engine, current)
    before_open = copy.deepcopy(engine.open_positions)
    before_closed = copy.deepcopy(engine.closed_positions)

    market_open, market_reason = _market_context()
    chains: List[Dict[str, Any]] = []
    if market_open:
        from core.data.datasource_manager import DataSourceManager

        dsm = DataSourceManager()
        for symbol in INDEX_UNDERLYINGS:
            try:
                payload = fetch_chain_for_api(dsm, symbol)
            except Exception:
                payload = None
            if payload and str(payload.get("data_source") or "").lower() == "dhan" and payload.get("contracts"):
                chains.append(payload)
        if chains:
            engine.step(chains, max_open=max(1, int(os.environ.get("SYSTEM3_PAPER_MAX_OPEN", "3") or 3)))
        else:
            # Preserve durable state rather than inventing a trade from fallback/synthetic data.
            engine._reset_if_new_day()
    else:
        engine._reset_if_new_day()

    events = _new_lifecycle_events(before_open, before_closed, engine.open_positions, engine.closed_positions)
    recent = _merge_recent((current or {}).get("recent_events") or [], events)
    state = _snapshot(
        engine,
        current,
        recent_events=recent,
        chains=chains,
        market_open=market_open,
        market_reason=market_reason,
        execution=execution,
    )
    stored = backend.publish(state, owner=execution, fence=int(lease["fence"]), events=events)
    public = backend.public_snapshot()
    return {
        "status": "PASS" if (not market_open or chains) else "PENDING_NO_DHAN_CHAIN",
        "market_open": market_open,
        "market_reason": market_reason,
        "chain_count": len(chains),
        "new_event_count": len(events),
        "ledger_version": stored.get("ledger_version"),
        "open_count": len(engine.open_positions),
        "closed_count": len(engine.closed_positions),
        "history_event_count": ((stored.get("history_totals") or {}).get("events")),
        "public_status": public.get("status"),
        "positions_source": public.get("positions_source"),
        "mode": "PAPER",
        "live_trading_enabled": False,
        "broker_order_endpoints_called": False,
    }
