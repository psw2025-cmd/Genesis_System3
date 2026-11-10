"""Fail-closed backtest results API.

The previous implementation returned hardcoded winning trades, a fabricated
equity curve, fixed metrics and cloud provenance as a current PASS. Such
fixtures are not evidence of a verified historical replay or a real strategy.
Do not publish positive performance metrics without independent reconciliation.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

BACKTEST_STRATEGIES: List[Dict[str, Any]] = []


def get_backtest_results() -> Dict[str, Any]:
    """Keep the dashboard response shape, but never certify missing evidence."""
    return {
        "status": "NOT_VERIFIED",
        "passed": False,
        "data_mode": "NO_VERIFIED_BACKTEST",
        "verification_status": "NOT_VERIFIED",
        "reason_if_unverified": (
            "No independently reconciled historical market replay, immutable "
            "dataset provenance, costed fills, or walk-forward result is available."
        ),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "run_id": None,
        "git_sha": None,
        "summary": {
            "total_trades": None,
            "winning_trades": None,
            "losing_trades": None,
            "win_rate": None,
            "profit_factor": None,
            "net_pnl": None,
            "initial_capital": None,
            "cagr_pct": None,
            "max_drawdown_pct": None,
            "sharpe_ratio": None,
            "calmar_ratio": None,
            "avg_trade_expectancy": None,
            "passed": False,
        },
        "strategy": None,
        "equity_curve": [],
        "recent_trades": [],
        "cloud_artifacts": None,
        "governance": {
            "mode": "ANALYZER_PAPER_EVIDENCE",
            "live_trading_enabled": False,
            "order_placement_allowed": False,
        },
    }
