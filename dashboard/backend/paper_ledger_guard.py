"""Reject synthetic paper-ledger fixtures that are not Dhan option fills.

The Sept-12 EQ strike-100 CUSTOM_* rows produced a fake ₹70,400 / 100% win-rate
tape. Paper UI must not treat those as realized P&L.
"""

from __future__ import annotations

from typing import Any, Dict, List, Mapping, Sequence

_FIXTURE_STRATEGIES = frozenset({"CUSTOM_MOMENTUM", "CUSTOM_SHORT_ALPHA"})
_INDEX_OR_EQ_UNDERLYINGS = frozenset(
    {"NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX", "BANKEX"}
)


def is_synthetic_eq_fixture_row(row: Mapping[str, Any] | None) -> bool:
    if not isinstance(row, Mapping):
        return False
    opt = str(row.get("option_type") or row.get("opt_type") or "").strip().upper()
    und = str(row.get("underlying") or row.get("symbol") or "").strip().upper()
    strat = str(row.get("strategy") or "").strip().upper()
    if strat in _FIXTURE_STRATEGIES:
        return True
    if opt == "EQ" and und not in _INDEX_OR_EQ_UNDERLYINGS and not und:
        return True
    try:
        strike = float(row.get("strike") or 0)
    except (TypeError, ValueError):
        strike = 0.0
    if opt == "EQ" and strike == 100.0 and und not in _INDEX_OR_EQ_UNDERLYINGS:
        return True
    return False


def filter_paper_trade_rows(rows: Sequence[Mapping[str, Any]] | None) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for row in rows or []:
        if is_synthetic_eq_fixture_row(row):
            continue
        out.append(dict(row))
    return out


def _open_position_count(summary: Mapping[str, Any] | None) -> int:
    if not isinstance(summary, Mapping):
        return 0
    ops = summary.get("open_positions")
    if isinstance(ops, list):
        return len(ops)
    try:
        if int(summary.get("open_count") or 0) > 0:
            return int(summary.get("open_count") or 0)
    except (TypeError, ValueError):
        pass
    try:
        if not isinstance(ops, list):
            return int(ops or 0)
    except (TypeError, ValueError):
        return 0
    return 0


def is_unproven_paper_summary(_summary: Mapping[str, Any] | None, real_trade_count: int) -> bool:
    """True when a persisted pnl_live summary must not be shown as realized P&L.

    Open CE/PE engine fills are proven paper activity even before a CLOSE row
    exists. Only a zero-close AND zero-open ledger is unproven.
    """
    if real_trade_count > 0:
        return False
    return _open_position_count(_summary) <= 0


def empty_paper_summary() -> Dict[str, Any]:
    return {
        "total_trades": 0,
        "winning_trades": 0,
        "losing_trades": 0,
        "win_rate": None,
        "total_realized_pnl": None,
        "total_unrealized_pnl": None,
        "total_pnl": None,
        "open_positions": 0,
        "source": "NO_VERIFIED_PAPER_FILLS",
        "live_trading_enabled": False,
    }
