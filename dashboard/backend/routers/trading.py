"""
Trading router — paper trades, P&L, positions, signals.
All imports lazy — nothing loaded until endpoint is called.
Memory: ~10MB (file I/O only, no heavy libs at startup).
"""
from __future__ import annotations
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

from fastapi import APIRouter

router = APIRouter(tags=["trading"])

# dashboard/backend/routers/trading.py -> repo/runtime root
ROOT_DIR = Path(__file__).resolve().parents[3]
STATE_DIR = ROOT_DIR / "state"
OUTPUTS_DIR = ROOT_DIR / "src" / "outputs"
PAPER_STATE_FILE = ROOT_DIR / "state" / "paper_trades.json"
PNL_FILE = ROOT_DIR / "state" / "pnl_summary.json"
KILL_SWITCH_FILE = ROOT_DIR / "config" / "kill_switch.json"

FORBIDDEN_PAPER_MARKERS = ("fake", "mock", "fixture", "synthetic", "yahoo", "bhavcopy", "csv_fallback", "paper_simulation_fixture")


def _load_json(path: Path, default=None):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        pass
    return default if default is not None else {}


def _is_live_trading_allowed() -> bool:
    ks = _load_json(KILL_SWITCH_FILE, {})
    env_ok = os.environ.get("LIVE_TRADING_ENABLED", "0") == "1"
    ks_ok = not ks.get("kill_switch_activated", False)
    approved = ks.get("live_trading_approved", False)
    return env_ok and ks_ok and approved


def _load_paper_state() -> tuple[Dict, str]:
    data = _load_json(PAPER_STATE_FILE, {})
    if data:
        return data, str(PAPER_STATE_FILE)
    alt = OUTPUTS_DIR / "paper_state.json"
    data = _load_json(alt, {})
    return data, str(alt)


def _paper_row_source(row: Dict) -> str:
    parts = []
    for key in ("source", "data_source", "quote_source", "price_source", "execution_source", "market_data_source"):
        val = row.get(key)
        if val is not None:
            parts.append(str(val))
    return " ".join(parts).lower()


def _is_rejected_paper_row(row: Dict) -> bool:
    if not isinstance(row, dict):
        return True
    if row.get("is_fixture") is True or row.get("fixture") is True or row.get("synthetic") is True:
        return True
    combined = _paper_row_source(row)
    return any(marker in combined for marker in FORBIDDEN_PAPER_MARKERS)


def _sanitize_rows(rows: List[Dict]) -> tuple[List[Dict], int]:
    clean = []
    rejected = 0
    for row in rows or []:
        if _is_rejected_paper_row(row):
            rejected += 1
            continue
        clean.append(row)
    return clean, rejected


def _truth(source_file: str, rejected_count: int, total_count: int) -> Dict:
    return {
        "source_file": source_file,
        "paper_order_mode": "ANALYZER_PAPER_ONLY",
        "live_trading_allowed": False,
        "broker_order_endpoints_called": False,
        "fake_fixture_rows_rejected": rejected_count,
        "displayed_rows": total_count,
        "truth_rule": "Paper rows are displayed only if they are not marked fake/mock/fixture/synthetic/fallback. Live broker orders remain disabled.",
    }


@router.get("/api/paper")
async def get_paper_state():
    """Paper trading state — positions, P&L summary with provenance."""
    data, source_file = _load_paper_state()
    positions, rejected_positions = _sanitize_rows(data.get("positions", []))
    trades, rejected_trades = _sanitize_rows(data.get("trades", data.get("history", [])))
    total_rejected = rejected_positions + rejected_trades
    return {
        "mode": "PAPER",
        "live_trading_allowed": False,
        "positions": positions,
        "trades": trades[-50:],
        "summary": data.get("summary", {
            "total_pnl": 0, "win_rate": 0,
            "total_trades": len(trades), "open_count": len([p for p in positions if p.get("status") == "open"]),
        }),
        "paper_truth": _truth(source_file, total_rejected, len(positions) + len(trades)),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/api/pnl")
async def get_pnl():
    """P&L summary — realized + unrealized, read-only paper truth."""
    data = _load_json(PNL_FILE, {})
    source_file = str(PNL_FILE)
    if not data:
        alt = OUTPUTS_DIR / "pnl_summary.json"
        data = _load_json(alt, {})
        source_file = str(alt)
    history, rejected = _sanitize_rows(data.get("history", []))
    return {
        "summary": {
            "total_pnl": data.get("total_pnl", 0),
            "realized_pnl": data.get("realized_pnl", 0),
            "unrealized_pnl": data.get("unrealized_pnl", 0),
            "win_rate": data.get("win_rate", 0.0),
            "total_trades": data.get("total_trades", 0),
            "winning_trades": data.get("winning_trades", 0),
            "losing_trades": data.get("losing_trades", 0),
        },
        "history": history,
        "paper_truth": _truth(source_file, rejected, len(history)),
        "last_updated": data.get("last_updated", "never"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/api/positions")
async def get_positions():
    """Open paper positions."""
    data, source_file = _load_paper_state()
    positions, rejected = _sanitize_rows(data.get("positions", []))
    return {
        "positions": positions,
        "open_count": len([p for p in positions if p.get("status") == "open"]),
        "mode": "PAPER",
        "live_trading": False,
        "paper_truth": _truth(source_file, rejected, len(positions)),
    }


@router.get("/api/positions/live")
async def get_live_positions():
    """
    Live positions from Dhan — read-only.
    Only returns data when token is valid. No live order action.
    """
    try:
        from dhanhq import DhanHQ
        client_id = os.environ.get("DHAN_CLIENT_ID", "")
        token = os.environ.get("DHAN_ACCESS_TOKEN", "")
        if not client_id or not token:
            return {"positions": [], "error": "Dhan credentials not set", "source": "dhan_live_readonly"}
        dhan = DhanHQ(client_id=client_id, access_token=token)
        resp = dhan.get_positions()
        positions = resp.get("data", []) if isinstance(resp, dict) else []
        return {
            "positions": positions,
            "count": len(positions),
            "source": "dhan_live_readonly",
            "order_endpoints_called": False,
        }
    except Exception as e:
        return {"positions": [], "error": str(e)[:100], "source": "dhan_live_readonly"}


@router.get("/api/signals")
async def get_signals():
    """Latest trading signals — read from gain_rank file."""
    gain_file = ROOT_DIR / "state" / "gain_rank_history.json"
    data = _load_json(gain_file, [])
    if not data:
        return {"signals": [], "status": "no_data", "source_file": str(gain_file),
                "message": "No signals yet — worker runs at 09:15 IST"}
    latest = data[-1] if data else {}
    predictions = latest.get("predictions", [])
    signals = []
    for p in predictions:
        score = p.get("gain_score", 0)
        signals.append({
            "underlying": p.get("underlying", "NIFTY"),
            "score": score,
            "direction": "BUY" if score > 0 else "SELL" if score < 0 else "NO_TRADE",
            "confidence": min(abs(score) / 100, 1.0),
            "date": latest.get("date", ""),
            "source_file": str(gain_file),
        })
    return {
        "signals": signals,
        "count": len(signals),
        "date": latest.get("date", ""),
        "status": "ok" if signals else "empty",
        "market_note": "Signals generated at 09:15 IST — stale after market close",
    }


@router.get("/api/signal/top")
async def get_top_signal():
    """Top signal for TopBar display."""
    resp = await get_signals()
    signals = resp.get("signals", [])
    if not signals:
        return {"signal": None, "status": "no_data"}
    top = max(signals, key=lambda x: abs(x.get("score", 0)))
    return {"signal": top, "status": "ok", "date": resp.get("date", "")}


@router.get("/api/portfolio")
async def get_portfolio():
    """Unified portfolio view — paper + read-only provenance."""
    pnl = await get_pnl()
    positions = await get_positions()
    return {
        "mode": "PAPER",
        "pnl": pnl["summary"],
        "positions": positions["positions"],
        "live_trading_enabled": False,
        "max_daily_loss": 5000,
        "paper_truth": positions.get("paper_truth", {}),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/api/trades")
async def get_trades():
    """Trade history, excluding fake/fixture rows."""
    data, source_file = _load_paper_state()
    trades_raw = data.get("trades", data.get("history", []))
    trades, rejected = _sanitize_rows(trades_raw)
    return {
        "trades": trades[-50:],
        "total": len(trades),
        "mode": "PAPER",
        "paper_truth": _truth(source_file, rejected, len(trades)),
    }


@router.get("/api/trades/today")
async def get_today_trades():
    """Today's paper trades only, excluding fake/fixture rows."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    data, source_file = _load_paper_state()
    trades_raw = data.get("trades", [])
    trades, rejected = _sanitize_rows(trades_raw)
    today_trades = [t for t in trades if str(t.get("date", t.get("timestamp", ""))).startswith(today)]
    return {
        "trades": today_trades,
        "count": len(today_trades),
        "date": today,
        "mode": "PAPER",
        "paper_truth": _truth(source_file, rejected, len(today_trades)),
    }


@router.get("/api/pnl/today")
async def get_today_pnl():
    """Today's P&L only, excluding fake/fixture history rows."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    data = _load_json(PNL_FILE, {})
    history, rejected = _sanitize_rows(data.get("history", []))
    today_entry = next((h for h in reversed(history)
                        if str(h.get("date", "")).startswith(today)), None)
    return {
        "date": today,
        "pnl": today_entry.get("pnl", 0) if today_entry else 0,
        "trades": today_entry.get("trades", 0) if today_entry else 0,
        "mode": "PAPER",
        "paper_truth": _truth(str(PNL_FILE), rejected, 1 if today_entry else 0),
    }
