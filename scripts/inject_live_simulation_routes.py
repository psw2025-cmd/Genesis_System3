#!/usr/bin/env python3
"""Inject backend virtual live simulation routes into active dashboard/backend/app.py.

The repo currently keeps modular routers disabled because of duplicate route risk. This script
adds only isolated /api/simulation/live/* endpoints to the active app.py file.

Safety:
- no live order route
- no broker route
- no secrets
- no real live gate credit
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "dashboard" / "backend" / "app.py"
MARKER = "# SYSTEM3_BACKEND_VIRTUAL_LIVE_SIMULATION_ROUTES"
BLOCK = f'''

{MARKER}
@app.get("/api/simulation/live/state")
async def get_virtual_live_simulation_state(scenario: str = "trend"):
    """Backend virtual live-market simulation feed. No real broker/orders."""
    try:
        from dashboard.backend.live_simulation_service import build_virtual_live_state
    except ImportError:
        from live_simulation_service import build_virtual_live_state
    payload = build_virtual_live_state(scenario=scenario)
    payload["api_route"] = "/api/simulation/live/state"
    payload["live_trading_enabled"] = False
    payload["order_placement_allowed"] = False
    payload["real_broker_routes_called"] = False
    return payload


@app.get("/api/simulation/live/chain")
async def get_virtual_live_simulation_chain(scenario: str = "trend"):
    """Virtual option chain shaped like a backend feed; simulation only."""
    try:
        from dashboard.backend.live_simulation_service import build_virtual_live_state
    except ImportError:
        from live_simulation_service import build_virtual_live_state
    payload = build_virtual_live_state(scenario=scenario)
    return {
        "status": "SIMULATION_ONLY",
        "api_route": "/api/simulation/live/chain",
        "scenario": payload.get("scenario"),
        "generated_utc": payload.get("generated_utc"),
        "rows": payload.get("option_chain") or [],
        "row_count": len(payload.get("option_chain") or []),
        "live_trading_enabled": False,
        "order_placement_allowed": False,
        "real_broker_routes_called": False,
    }


@app.get("/api/simulation/live/signals")
async def get_virtual_live_simulation_signals(scenario: str = "trend"):
    """Virtual CE/PE signal feed; simulation only."""
    try:
        from dashboard.backend.live_simulation_service import build_virtual_live_state
    except ImportError:
        from live_simulation_service import build_virtual_live_state
    payload = build_virtual_live_state(scenario=scenario)
    return {
        "status": "SIMULATION_ONLY",
        "api_route": "/api/simulation/live/signals",
        "scenario": payload.get("scenario"),
        "generated_utc": payload.get("generated_utc"),
        "rows": payload.get("signals") or [],
        "row_count": len(payload.get("signals") or []),
        "live_trading_enabled": False,
        "order_placement_allowed": False,
        "real_broker_routes_called": False,
    }


@app.get("/api/simulation/live/paper")
async def get_virtual_live_simulation_paper(scenario: str = "trend"):
    """Virtual paper lifecycle tape; simulation only."""
    try:
        from dashboard.backend.live_simulation_service import build_virtual_live_state
    except ImportError:
        from live_simulation_service import build_virtual_live_state
    payload = build_virtual_live_state(scenario=scenario)
    paper = payload.get("paper") or {}
    return {
        "status": "SIMULATION_ONLY",
        "api_route": "/api/simulation/live/paper",
        "scenario": payload.get("scenario"),
        "generated_utc": payload.get("generated_utc"),
        "orders": paper.get("orders") or [],
        "total_pnl": paper.get("total_pnl"),
        "currency": "INR",
        "live_trading_enabled": False,
        "order_placement_allowed": False,
        "real_broker_routes_called": False,
    }
'''


def main() -> int:
    text = APP.read_text(encoding="utf-8")
    if MARKER in text:
        print("simulation routes already present")
        return 0
    APP.write_text(text.rstrip() + BLOCK + "\n", encoding="utf-8")
    print("injected simulation routes into dashboard/backend/app.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
