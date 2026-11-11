import asyncio
import json
import os
import sys

sys.path.insert(0, r"c:\Genesis_System3_clean")
import dashboard.backend.app as app

async def run_checks():
    print("Testing /api/pnl...")
    pnl = await app.get_pnl()
    print("  pnl status:", pnl.get("status"))
    print("  pnl history count:", len(pnl.get("history", [])))
    print("  pnl summary:", pnl.get("summary"))
    assert len(pnl.get("history", [])) == 7, "Expected 7 daily sessions"
    assert pnl.get("summary", {}).get("total_trades") == 24, "Expected 24 trades"

    print("\nTesting /api/backtest/results...")
    bt = await app.get_backtest_results()
    print("  bt status:", bt.get("status"))
    print("  costed_walkforward trade_count:", bt.get("costed_walkforward", {}).get("trade_count"))
    print("  costs_slippage_included_proven:", bt.get("costed_walkforward", {}).get("costs_slippage_included_proven"))
    assert bt.get("costed_walkforward", {}).get("trade_count") == 24, "Expected 24 trades in walkforward"
    assert bt.get("costed_walkforward", {}).get("costs_slippage_included_proven") is True, "Expected True"

    print("\nTesting /api/alerts/recent...")
    alerts = await app.get_recent_alerts(50)
    print("  alerts count:", alerts.get("count"))
    for a in alerts.get("alerts", []):
        print("   -", a.get("id"), a.get("type"), a.get("severity"), a.get("title"))
    assert alerts.get("count") == 5, "Expected 5 alerts"

    print("\nALL BACKEND ROUTE TESTS PASSED!")

asyncio.run(run_checks())
sys.exit(0)
