"""
Unified portfolio truth — paper simulation + optional Dhan read-only broker data.

SAFETY: Read-only. Never places orders. Never enables live trading.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.brokers.dhan.nse_option_symbol import enrich_option_row, enrich_option_rows

ROOT = Path(__file__).resolve().parents[2]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _broker_detail_enabled() -> bool:
    """Keep Render web portfolio endpoint lightweight by default.

    Broker status is enough for dashboard health. Holdings/positions can be
    fetched from dedicated broker endpoints, which are separately cached.
    """
    val = os.environ.get("PORTFOLIO_BROKER_DETAILS", "0").strip().lower()
    return val in ("1", "true", "yes", "on")


def _normalize_broker_rows(raw: Any) -> List[Dict[str, Any]]:
    try:
        from core.brokers.dhan.dhan_payload_normalizer import (
            normalize_holding_row,
            normalize_holdings_payload,
            normalize_position_row,
            normalize_positions_payload,
        )
    except ImportError:
        normalize_holdings_payload = normalize_positions_payload = None

    rows: List[Dict[str, Any]] = []
    if raw is None:
        return rows

    if normalize_holdings_payload and isinstance(raw, (list, dict)):
        items = normalize_holdings_payload(raw) or normalize_positions_payload(raw)
        for item in items:
            norm = normalize_holding_row(item)
            rows.append({**norm, "source": "dhan_broker_readonly"})
        if rows:
            return rows

    if isinstance(raw, list):
        items = raw
    elif isinstance(raw, dict):
        items = raw.get("data") or raw.get("holdings") or raw.get("positions") or []
        if isinstance(items, dict):
            items = list(items.values()) if items else []
    else:
        return rows

    for item in items:
        if not isinstance(item, dict):
            continue
        symbol = (
            item.get("tradingSymbol") or item.get("symbol") or item.get("securityId") or item.get("name") or "UNKNOWN"
        )
        qty = item.get("quantity") or item.get("qty") or item.get("netQty") or 0
        rows.append(
            {
                "symbol": symbol,
                "quantity": qty,
                "avg_price": item.get("averagePrice") or item.get("avgPrice") or item.get("costPrice"),
                "ltp": item.get("lastPrice") or item.get("ltp") or item.get("closePrice"),
                "pnl": item.get("pnl") or item.get("realizedProfit") or item.get("unrealizedProfit"),
                "source": "dhan_broker_readonly",
                "raw_keys": list(item.keys())[:12],
            }
        )
    return rows


def _load_paper_summary(outputs_dir: Path) -> Dict[str, Any]:
    for candidate in [outputs_dir / "paper_pnl_summary.json", ROOT / "paper_pnl_summary.json"]:
        if candidate.exists():
            try:
                return json.loads(candidate.read_text(encoding="utf-8"))
            except Exception:
                pass
    return {}


def _load_paper_positions(outputs_dir: Path) -> List[Dict[str, Any]]:
    path = outputs_dir / "positions_live.json"
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return data.get("positions") or []
        if isinstance(data, list):
            return data
    except Exception:
        pass
    return []


def _load_paper_fixture_history() -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
    for candidate in [
        ROOT / "tests" / "fixtures" / "paper_closed_trades_feb2026.json",
        ROOT / "storage" / "paper" / "closed_trades_feb2026.json",
    ]:
        if not candidate.exists():
            continue
        try:
            session = json.loads(candidate.read_text(encoding="utf-8"))
            session_expiry = session.get("session_expiry")
            trades = session.get("trades") or []
            trade_list = trades if isinstance(trades, list) else []
            enriched = enrich_option_rows(trade_list[:100], default_expiry=session_expiry)
            meta = {
                "data_source": session.get("data_source", "paper_simulation"),
                "session": session.get("session", "Paper session"),
                "session_expiry": session_expiry,
                "is_fixture": True,
                "note": session.get("note", "Synthetic paper trades — not broker ledger"),
            }
            return enriched, meta
        except Exception:
            pass
    return [], {"data_source": "none", "session": "", "is_fixture": False}


def _load_trade_history() -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
    try:
        from dashboard.backend.trade_logger import get_all_trades
    except ImportError:
        try:
            from trade_logger import get_all_trades
        except ImportError:
            return _load_paper_fixture_history()
    try:
        trades = get_all_trades()
        if isinstance(trades, list) and trades:
            return enrich_option_rows(trades[-100:]), {
                "data_source": "paper_live",
                "session": "Live paper ledger",
                "is_fixture": False,
                "limited_to_last": 100,
            }
    except Exception:
        pass
    return _load_paper_fixture_history()


def _load_auto_gate_blockers() -> tuple[List[str], List[str]]:
    """Load dynamic blockers from auto gate evaluator if available."""
    path = Path(__file__).resolve().parents[2] / "reports" / "latest" / "system3_auto_gates" / "summary.json"
    if not path.exists():
        return [], []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        blockers = list(data.get("open_blockers") or [])
        blockers.extend(data.get("technical_gates_still_required") or [])
        blockers.append("LIVE_TRADING_DISABLED_BY_DESIGN")
        actions = list(data.get("recommended_auto_actions") or [])
        seen: set[str] = set()
        out_b, out_a = [], []
        for b in blockers:
            if b and b not in seen:
                seen.add(b)
                out_b.append(b)
        for a in actions:
            if a and a not in seen:
                seen.add(a)
                out_a.append(a)
        return out_b, out_a
    except Exception:
        return [], []


def build_unified_portfolio(outputs_dir: Path) -> Dict[str, Any]:
    try:
        from dashboard.backend.human_approval_service import load_human_approval
    except ImportError:
        from human_approval_service import load_human_approval

    human_gate = load_human_approval()
    human_approved = bool(human_gate.get("approved"))

    paper_summary = _load_paper_summary(outputs_dir)
    paper_positions = _load_paper_positions(outputs_dir)
    paper_positions = [enrich_option_row(p) for p in paper_positions[:100]]
    trade_history, trade_history_meta = _load_trade_history()

    broker_holdings: List[Dict[str, Any]] = []
    broker_positions: List[Dict[str, Any]] = []
    broker_connected = False
    broker_error: Optional[str] = None
    broker_details_loaded = False

    try:
        from core.brokers.dhan.dhan_readonly import get_status

        status = get_status()
        broker_connected = bool(status.get("connected"))
        broker_error = status.get("error")

        if broker_connected and _broker_detail_enabled():
            from core.brokers.dhan.dhan_readonly import get_holdings, get_positions

            broker_details_loaded = True
            h = get_holdings()
            p = get_positions()
            if h.get("success"):
                broker_holdings = _normalize_broker_rows(h.get("data"))[:100]
            else:
                broker_error = h.get("error")
            if p.get("success"):
                broker_positions = _normalize_broker_rows(p.get("data"))[:100]
            elif not broker_error:
                broker_error = p.get("error")
    except Exception as exc:
        broker_error = str(exc)[:200]

    paper_source = paper_summary.get("data_source") or trade_history_meta.get("data_source") or "paper_internal"
    has_broker_rows = bool(broker_holdings or broker_positions)
    has_paper_rows = bool(paper_positions or trade_history or paper_summary.get("total_trades"))

    if has_broker_rows and has_paper_rows:
        transparency = "MIXED_PAPER_AND_BROKER_READONLY"
    elif has_broker_rows:
        transparency = "BROKER_READONLY"
    elif has_paper_rows:
        transparency = "PAPER_SIMULATION" if paper_source == "paper_simulation" else "PAPER_INTERNAL"
    else:
        transparency = "NO_PORTFOLIO_DATA"

    dynamic_blockers, dynamic_actions = _load_auto_gate_blockers()
    if not dynamic_blockers:
        dynamic_blockers = [
            "LIVE_TRADING_DISABLED_BY_DESIGN",
            "REAL_PAPER_LIFECYCLE_NOT_PROVEN",
            "POSITIVE_COSTED_EXPECTANCY_NOT_PROVEN",
            "MULTI_DAY_STABILITY_NOT_PROVEN",
        ]
        dynamic_actions = [
            "Run tools/system3_auto_coordinator.py",
            "Accumulate 5+ prediction days with rho>=0.70",
            "Prove positive net expectancy after all costs",
        ]

    return {
        "generated_utc": _utc_now(),
        "live_trading_enabled": False,
        "order_placement_allowed": False,
        "data_transparency": transparency,
        "broker": {
            "connected": broker_connected,
            "holdings_count": len(broker_holdings),
            "positions_count": len(broker_positions),
            "error": broker_error,
            "source": "dhan_readonly",
            "details_loaded": broker_details_loaded,
            "details_mode": "enabled" if broker_details_loaded else "skipped_for_render_memory",
        },
        "paper": {
            "summary": paper_summary,
            "open_positions": paper_positions,
            "open_count": len(paper_positions),
            "trade_history_count": len(trade_history),
            "data_source": paper_source,
        },
        "broker_holdings": broker_holdings,
        "broker_positions": broker_positions,
        "trade_history": trade_history[:100],
        "trade_history_meta": trade_history_meta,
        "production_ready_for_real_money": False,
        "human_approval": human_approved,
        "human_approval_by": human_gate.get("approved_by"),
        "blockers": dynamic_blockers,
        "next_actions": dynamic_actions
        + ([] if human_approved else ["Human approval required before any live enablement"]),
        "auto_gates_report": "reports/latest/system3_auto_gates/summary.json",
    }
