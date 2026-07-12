"""Backend virtual live-market simulation service.

This is deliberately isolated from real live trading:
- no broker calls
- no order routes
- no secrets
- no real live gate credit
- every payload is marked SIMULATION_ONLY
"""
from __future__ import annotations

import math
import time
from datetime import datetime, timezone
from typing import Any, Dict, List

SYMBOLS = [
    {"symbol": "NIFTY", "spot": 24520.0, "step": 50, "lot": 75},
    {"symbol": "BANKNIFTY", "spot": 52240.0, "step": 100, "lot": 30},
    {"symbol": "FINNIFTY", "spot": 23580.0, "step": 50, "lot": 65},
    {"symbol": "MIDCPNIFTY", "spot": 12120.0, "step": 25, "lot": 120},
]


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _wave(seed: float, scale: float = 1.0) -> float:
    now = time.time() / 7.0
    return math.sin(now + seed) * scale + math.cos(now / 2.0 + seed) * scale * 0.35


def _round_strike(spot: float, step: int) -> int:
    return int(round(spot / step) * step)


def build_virtual_live_state(scenario: str = "trend") -> Dict[str, Any]:
    scenario = scenario if scenario in {"trend", "range", "volatile"} else "trend"
    factor = {"trend": 1.0, "range": 0.42, "volatile": 1.85}[scenario]
    rows: List[Dict[str, Any]] = []
    option_chain: List[Dict[str, Any]] = []
    signals: List[Dict[str, Any]] = []
    positions: List[Dict[str, Any]] = []

    for i, item in enumerate(SYMBOLS):
        move = _wave(i + 1, 38.0 * factor)
        spot = round(item["spot"] + move, 2)
        atm = _round_strike(spot, item["step"])
        ce_ltp = round(max(3.0, 82 + move * 0.28 + i * 8), 2)
        pe_ltp = round(max(3.0, 78 - move * 0.24 + i * 7), 2)
        side = "CE" if move >= 0 else "PE"
        ltp = ce_ltp if side == "CE" else pe_ltp
        entry = round(ltp * 0.96, 2)
        qty = item["lot"]
        pnl = round((ltp - entry) * qty, 2)

        rows.append({
            "symbol": item["symbol"],
            "spot": spot,
            "atm_strike": atm,
            "lot_size": qty,
            "virtual_tick_age_sec": 1,
            "source": "BACKEND_VIRTUAL_SIMULATION",
        })
        option_chain.append({
            "symbol": item["symbol"],
            "expiry": "SIM-WEEKLY",
            "strike": atm,
            "ce_ltp": ce_ltp,
            "pe_ltp": pe_ltp,
            "ce_oi": int(100000 + abs(move) * 1200 + i * 5000),
            "pe_oi": int(95000 + abs(move) * 1100 + i * 4200),
            "source": "BACKEND_VIRTUAL_SIMULATION",
        })
        signals.append({
            "symbol": item["symbol"],
            "side": side,
            "strike": atm,
            "expiry": "SIM-WEEKLY",
            "score": round(0.72 + min(abs(move) / 300.0, 0.2), 4),
            "confidence": round(0.68 + min(abs(move) / 350.0, 0.22), 4),
            "reason": f"virtual_{scenario}_tick_chain_signal",
            "source": "BACKEND_VIRTUAL_SIMULATION",
        })
        positions.append({
            "position_id": f"SIM-{i+1:03d}",
            "symbol": item["symbol"],
            "side": side,
            "strike": atm,
            "expiry": "SIM-WEEKLY",
            "qty": qty,
            "entry_price": entry,
            "ltp": ltp,
            "pnl": pnl,
            "status": "OPEN" if i < 3 else "CLOSED",
            "source": "BACKEND_VIRTUAL_SIMULATION",
        })

    total_pnl = round(sum(float(p["pnl"]) for p in positions), 2)
    return {
        "status": "SIMULATION_ONLY",
        "mode": "VIRTUAL_LIVE_MARKET",
        "scenario": scenario,
        "generated_utc": _utc(),
        "market": {"is_open": True, "state": "VIRTUAL_OPEN", "source": "BACKEND_VIRTUAL_SIMULATION"},
        "broker": {
            "connected": True,
            "name": "virtual-broker",
            "status": "SIM_CONNECTED",
            "heartbeat_age_sec": 1,
            "source": "BACKEND_VIRTUAL_SIMULATION",
        },
        "risk": {"live_trading_enabled": False, "order_placement_allowed": False, "real_broker_routes_called": False},
        "universe": rows,
        "option_chain": option_chain,
        "signals": signals,
        "positions": positions,
        "paper": {"orders": positions, "total_pnl": total_pnl, "currency": "INR", "source": "BACKEND_VIRTUAL_SIMULATION"},
        "gates": {
            "virtual_broker_heartbeat": True,
            "virtual_tick_stream": True,
            "virtual_option_chain": True,
            "virtual_signal_generation": True,
            "virtual_paper_lifecycle": True,
            "real_live_gate_credit": False,
        },
        "safety_banner": "SIMULATION ONLY — not live-ready proof, not real broker, not real order execution",
    }
