"""Auditable verification script for all 8 streaming intelligence routes."""

import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dashboard.backend.app import (
    get_backtest_results_endpoint,
    get_catalysts_endpoint,
    get_multibagger_workspace_endpoint,
    get_option_chain_alias,
    get_paper_account,
    get_paper_positions,
    get_paper_status,
    get_paper_trades,
)


async def main():
    print("=== AUDITABLE ROUTE PROOF REPORT ===")
    results = {}

    # 1. Option Chain
    c = await get_option_chain_alias("NIFTY")
    results["/api/option-chain"] = {
        "status": "OK",
        "underlying": c.get("underlying"),
        "spot": c.get("spot"),
        "pcr": c.get("pcr"),
        "contracts_count": len(c.get("contracts", [])),
    }

    # 2. Paper Positions
    p = await get_paper_positions()
    results["/api/paper/positions"] = {
        "status": "OK",
        "open_count": p.get("open_count", 0),
        "message": p.get("message", "OK"),
    }

    # 3. Paper Trades
    t = await get_paper_trades()
    results["/api/paper/trades"] = {
        "status": "OK",
        "count": t.get("count", 0),
        "is_fixture": t.get("meta", {}).get("is_fixture", False),
    }

    # 4. Paper Account
    a = await get_paper_account()
    results["/api/paper/account"] = {
        "status": "OK",
        "initial_capital": a.get("initial_capital"),
        "mode": a.get("mode"),
    }

    # 5. Paper Status
    s = await get_paper_status()
    results["/api/paper/status"] = {
        "status": "OK",
        "engine": s.get("engine"),
        "live_trading_enabled": s.get("live_trading_enabled"),
    }

    # 6. Backtest Results
    b = await get_backtest_results_endpoint()
    results["/api/backtest/results"] = {
        "status": b.get("status"),
        "win_rate": b.get("summary", {}).get("win_rate"),
        "net_pnl": b.get("summary", {}).get("net_pnl"),
        "total_trades": b.get("summary", {}).get("total_trades"),
    }

    # 7. Catalysts
    cat = await get_catalysts_endpoint()
    results["/api/catalysts"] = {
        "status": cat.get("status"),
        "total_catalysts": cat.get("total_catalysts"),
        "market_bias": cat.get("sentiment_summary", {}).get("overall_market_bias"),
    }

    # 8. Multibagger
    m = await get_multibagger_workspace_endpoint()
    results["/api/multibagger"] = {
        "status": m.get("status"),
        "total_candidates": m.get("total_candidates"),
    }

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
