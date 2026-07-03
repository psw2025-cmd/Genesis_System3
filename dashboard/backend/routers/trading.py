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
from typing import Any, Dict, List, Optional

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(tags=["trading"])

ROOT_DIR = Path(__file__).resolve().parents[2]
STATE_DIR = ROOT_DIR / "state"
OUTPUTS_DIR = ROOT_DIR / "src" / "outputs"
PAPER_STATE_FILE = ROOT_DIR / "state" / "paper_trades.json"
PNL_FILE = ROOT_DIR / "state" / "pnl_summary.json"
KILL_SWITCH_FILE = ROOT_DIR / "config" / "kill_switch.json"


def _load_json(path: Path, default=None):
    try:
        if path.exists():
            return json.loads(path.read_text())
    except Exception:
        pass
    return default if default is not None else {}


def _is_live_trading_allowed() -> bool:
    ks = _load_json(KILL_SWITCH_FILE, {})
    env_ok = os.environ.get("LIVE_TRADING_ENABLED", "0") == "1"
    ks_ok = not ks.get("kill_switch_activated", False)
    approved = ks.get("live_trading_approved", False)
    return env_ok and ks_ok and approved


@router.get("/api/paper")
async def get_paper_state():
    """Paper trading state — positions, P&L summary."""
    data = _load_json(PAPER_STATE_FILE, {})
    if not data:
        # Try SSOT outputs
        alt = OUTPUTS_DIR / "paper_state.json"
        data = _load_json(alt, {})
    return {
        "mode": "PAPER",
        "live_trading_allowed": False,
        "positions": data.get("positions", []),
        "summary": data.get("summary", {
            "total_pnl": 0, "win_rate": 0,
            "total_trades": 0, "open_count": 0,
        }),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/api/pnl")
async def get_pnl():
    """P&L summary — realized + unrealized."""
    data = _load_json(PNL_FILE, {})
    if not data:
        alt = OUTPUTS_DIR / "pnl_summary.json"
        data = _load_json(alt, {})
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
        "history": data.get("history", []),
        "last_updated": data.get("last_updated", "never"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/api/positions")
async def get_positions():
    """Open paper positions."""
    data = _load_json(PAPER_STATE_FILE, {})
    return {
        "positions": data.get("positions", []),
        "open_count": len([p for p in data.get("positions", [])
                          if p.get("status") == "open"]),
        "mode": "PAPER",
        "live_trading": False,
    }


@router.get("/api/positions/live")
async def get_live_positions():
    """
    Live positions from Dhan — read-only.
    Only returns data when market open and token valid.
    """
    try:
        from dhanhq import DhanHQ
        client_id = os.environ.get("DHAN_CLIENT_ID", "")
        token = os.environ.get("DHAN_ACCESS_TOKEN", "")
        if not client_id or not token:
            return {"positions": [], "error": "Dhan credentials not set"}
        dhan = DhanHQ(client_id=client_id, access_token=token)
        resp = dhan.get_positions()
        positions = resp.get("data", []) if isinstance(resp, dict) else []
        return {
            "positions": positions,
            "count": len(positions),
            "source": "dhan_live",
        }
    except Exception as e:
        return {"positions": [], "error": str(e)[:100]}


@router.get("/api/signals")
async def get_signals():
    """Latest trading signals — read from gain_rank file."""
    gain_file = ROOT_DIR / "state" / "gain_rank_history.json"
    data = _load_json(gain_file, [])
    if not data:
        return {"signals": [], "status": "no_data",
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
    """Unified portfolio view — paper + real holdings."""
    pnl = await get_pnl()
    positions = await get_positions()
    return {
        "mode": "PAPER",
        "pnl": pnl["summary"],
        "positions": positions["positions"],
        "live_trading_enabled": False,
        "max_daily_loss": 5000,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/api/trades")
async def get_trades():
    """Trade history."""
    data = _load_json(PAPER_STATE_FILE, {})
    trades = data.get("trades", data.get("history", []))
    return {
        "trades": trades[-50:],  # Last 50 trades
        "total": len(trades),
        "mode": "PAPER",
    }


@router.get("/api/trades/today")
async def get_today_trades():
    """Today's trades only."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    data = _load_json(PAPER_STATE_FILE, {})
    trades = data.get("trades", [])
    today_trades = [t for t in trades if t.get("date", "").startswith(today)]
    return {
        "trades": today_trades,
        "count": len(today_trades),
        "date": today,
        "mode": "PAPER",
    }


@router.get("/api/pnl/today")
async def get_today_pnl():
    """Today's P&L only."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    data = _load_json(PNL_FILE, {})
    history = data.get("history", [])
    today_entry = next((h for h in reversed(history)
                        if h.get("date", "").startswith(today)), None)
    return {
        "date": today,
        "pnl": today_entry.get("pnl", 0) if today_entry else 0,
        "trades": today_entry.get("trades", 0) if today_entry else 0,
        "mode": "PAPER",
    }
