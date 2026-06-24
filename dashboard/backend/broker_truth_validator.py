"""
Multi-validation broker truth for trader dashboard fields.

Validates: broker auth → API success → payload shape → field presence → numeric sanity.
Never enables live trading. Read-only Dhan calls only.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from core.brokers.dhan.dhan_payload_normalizer import (
    normalize_funds_payload,
    normalize_funds_row,
    normalize_holding_row,
    normalize_holdings_payload,
    normalize_position_row,
    normalize_positions_payload,
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _field_status(
    *,
    broker_connected: bool,
    api_success: bool,
    value: Any,
    required_type: type = str,
    allow_zero: bool = True,
) -> Dict[str, Any]:
    if not broker_connected:
        return {"status": "BROKER_OFFLINE", "valid": False, "value": None}
    if not api_success:
        return {"status": "API_FAILED", "valid": False, "value": None}
    if value is None:
        return {"status": "NOT_FOUND", "valid": False, "value": None}
    if required_type in (int, float):
        try:
            num = float(value)
            if not allow_zero and num == 0:
                return {"status": "EMPTY_ZERO", "valid": False, "value": num}
            return {"status": "VALID", "valid": True, "value": num}
        except (TypeError, ValueError):
            return {"status": "INVALID_TYPE", "valid": False, "value": value}
    if isinstance(value, str) and not value.strip():
        return {"status": "EMPTY", "valid": False, "value": value}
    if required_type is list and not value:
        return {"status": "EMPTY_LIST", "valid": True, "value": value}
    return {"status": "VALID", "valid": True, "value": value}


def build_broker_truth_report() -> Dict[str, Any]:
    from core.brokers.dhan.dhan_readonly import (
        get_funds,
        get_holdings,
        get_positions,
        get_status,
    )

    status = get_status()
    broker_connected = bool(status.get("connected"))
    holdings_resp = get_holdings()
    positions_resp = get_positions()
    funds_resp = get_funds()

    holdings_raw = normalize_holdings_payload(holdings_resp.get("data"))
    positions_raw = normalize_positions_payload(positions_resp.get("data"))
    funds_raw = normalize_funds_payload(funds_resp.get("data"))
    funds_norm = normalize_funds_row(funds_raw)

    holdings_norm = [normalize_holding_row(h) for h in holdings_raw]
    positions_norm = [normalize_position_row(p) for p in positions_raw]

    total_holdings_value = sum(h.get("current_value") or 0 for h in holdings_norm)
    total_unrealized = sum(p.get("unrealized_pnl") or 0 for p in positions_norm)
    total_realized_pos = sum(p.get("realized_pnl") or 0 for p in positions_norm)

    trader_fields = {
        "cash_available": _field_status(
            broker_connected=broker_connected,
            api_success=bool(funds_resp.get("success")),
            value=funds_norm.get("available_balance"),
            required_type=float,
            allow_zero=True,
        ),
        "utilized_margin": _field_status(
            broker_connected=broker_connected,
            api_success=bool(funds_resp.get("success")),
            value=funds_norm.get("utilized_amount"),
            required_type=float,
            allow_zero=True,
        ),
        "total_limit": _field_status(
            broker_connected=broker_connected,
            api_success=bool(funds_resp.get("success")),
            value=funds_norm.get("total_limit"),
            required_type=float,
            allow_zero=True,
        ),
        "holdings_count": _field_status(
            broker_connected=broker_connected,
            api_success=bool(holdings_resp.get("success")),
            value=len(holdings_norm),
            required_type=float,
            allow_zero=True,
        ),
        "positions_count": _field_status(
            broker_connected=broker_connected,
            api_success=bool(positions_resp.get("success")),
            value=len(positions_norm),
            required_type=float,
            allow_zero=True,
        ),
        "holdings_total_value": _field_status(
            broker_connected=broker_connected,
            api_success=bool(holdings_resp.get("success")),
            value=round(total_holdings_value, 2) if holdings_norm else (0 if holdings_resp.get("success") else None),
            required_type=float,
            allow_zero=True,
        ),
        "positions_unrealized_pnl": _field_status(
            broker_connected=broker_connected,
            api_success=bool(positions_resp.get("success")),
            value=round(total_unrealized, 2) if positions_resp.get("success") else None,
            required_type=float,
            allow_zero=True,
        ),
        "positions_realized_pnl": _field_status(
            broker_connected=broker_connected,
            api_success=bool(positions_resp.get("success")),
            value=round(total_realized_pos, 2) if positions_resp.get("success") else None,
            required_type=float,
            allow_zero=True,
        ),
    }

    # Per-row sample validation (first holding/position if any)
    if holdings_norm:
        h0 = holdings_norm[0]
        trader_fields["holding_symbol_sample"] = _field_status(
            broker_connected=broker_connected,
            api_success=True,
            value=h0.get("symbol"),
        )
        trader_fields["holding_ltp_sample"] = _field_status(
            broker_connected=broker_connected,
            api_success=True,
            value=h0.get("ltp"),
            required_type=float,
        )
    if positions_norm:
        p0 = positions_norm[0]
        trader_fields["position_symbol_sample"] = _field_status(
            broker_connected=broker_connected,
            api_success=True,
            value=p0.get("symbol"),
        )

    valid_count = sum(1 for f in trader_fields.values() if f.get("valid"))
    total_count = len(trader_fields)
    all_apis_ok = (
        all(r.get("success") for r in (holdings_resp, positions_resp, funds_resp)) if broker_connected else False
    )

    if not broker_connected:
        overall = "BROKER_OFFLINE"
        pct = 0
    elif all_apis_ok and valid_count == total_count:
        overall = "VALID"
        pct = 100
    elif valid_count >= total_count * 0.7:
        overall = "PASS_WITH_WARNINGS"
        pct = int(valid_count / total_count * 100) if total_count else 0
    else:
        overall = "NOT_VALID"
        pct = int(valid_count / total_count * 100) if total_count else 0

    return {
        "generated_utc": _utc_now(),
        "live_trading_enabled": False,
        "order_placement_allowed": False,
        "broker": status,
        "broker_connected": broker_connected,
        "validation": {
            "overall": overall,
            "valid_pct": pct,
            "valid_count": valid_count,
            "total_fields": total_count,
            "all_apis_success": all_apis_ok,
        },
        "trader_fields": trader_fields,
        "funds": {
            "success": bool(funds_resp.get("success")),
            "source": funds_resp.get("source"),
            "error": funds_resp.get("error"),
            "normalized": funds_norm,
            "raw_count": 1 if funds_raw else 0,
        },
        "holdings": {
            "success": bool(holdings_resp.get("success")),
            "source": holdings_resp.get("source"),
            "error": holdings_resp.get("error"),
            "count": len(holdings_norm),
            "rows": holdings_norm,
            "raw_rows": holdings_raw,
        },
        "positions": {
            "success": bool(positions_resp.get("success")),
            "source": positions_resp.get("source"),
            "error": positions_resp.get("error"),
            "count": len(positions_norm),
            "rows": positions_norm,
            "raw_rows": positions_raw,
        },
        "data_source": (
            "DHAN_BROKER_READONLY"
            if broker_connected and all_apis_ok
            else ("BROKER_PARTIAL" if broker_connected else "BROKER_OFFLINE")
        ),
    }
