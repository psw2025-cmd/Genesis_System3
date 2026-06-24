"""
Live market scanner — highest % gain CE and PE contracts per index segment.

Uses official chain fields (ltp, previous_close, change_percent) per NSE/Dhan conventions.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

INDEX_SEGMENTS = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def compute_contract_gain_pct(contract: Dict[str, Any]) -> Optional[float]:
    """Return intraday % gain from market fields (NSE/Dhan: LTP vs previous close)."""
    for key in ("change_percent", "pChange", "gain_pct", "pct_change"):
        val = contract.get(key)
        if val is not None:
            try:
                return float(val)
            except (TypeError, ValueError):
                pass

    ltp = contract.get("ltp") or contract.get("last_price") or contract.get("close")
    prev = (
        contract.get("previous_close_price")
        or contract.get("previous_close")
        or contract.get("prev_close")
        or contract.get("close")
    )
    try:
        ltp_f = float(ltp) if ltp is not None else None
        prev_f = float(prev) if prev is not None else None
    except (TypeError, ValueError):
        return None

    if ltp_f is None or prev_f is None or prev_f <= 0:
        return None
    return (ltp_f - prev_f) / prev_f * 100.0


def _contract_row(contract: Dict[str, Any], underlying: str, gain_pct: float) -> Dict[str, Any]:
    opt = str(contract.get("option_type", "")).upper()
    return {
        "underlying": underlying,
        "option_type": opt,
        "strike": contract.get("strike"),
        "trading_symbol": contract.get("trading_symbol") or contract.get("symbol"),
        "expiry_date": contract.get("expiry_date") or contract.get("expiry"),
        "ltp": contract.get("ltp"),
        "previous_close": contract.get("previous_close_price") or contract.get("previous_close"),
        "oi": contract.get("oi"),
        "oi_change": contract.get("oi_change") or contract.get("change_in_oi"),
        "volume": contract.get("volume"),
        "gain_pct": round(gain_pct, 4),
        "security_id": contract.get("security_id"),
        "source": contract.get("source"),
    }


def scan_segment_contracts(
    contracts: List[Dict[str, Any]],
    underlying: str,
    top_n: int = 5,
) -> Dict[str, Any]:
    """Find highest-gain CE and PE contracts for one index segment."""
    scored: List[Dict[str, Any]] = []
    for c in contracts or []:
        opt = str(c.get("option_type", "")).upper()
        if opt not in ("CE", "PE"):
            continue
        gain = compute_contract_gain_pct(c)
        if gain is None:
            continue
        scored.append(_contract_row(c, underlying.upper(), gain))

    ce_rows = sorted([r for r in scored if r["option_type"] == "CE"], key=lambda x: x["gain_pct"], reverse=True)
    pe_rows = sorted([r for r in scored if r["option_type"] == "PE"], key=lambda x: x["gain_pct"], reverse=True)

    return {
        "underlying": underlying.upper(),
        "contracts_scored": len(scored),
        "top_ce": ce_rows[0] if ce_rows else None,
        "top_pe": pe_rows[0] if pe_rows else None,
        "top_ce_list": ce_rows[:top_n],
        "top_pe_list": pe_rows[:top_n],
        "implemented": True,
    }


def scan_all_segments_from_chains(
    chains: Dict[str, Dict[str, Any]],
    top_n: int = 5,
) -> Dict[str, Any]:
    """Scan pre-fetched chain payloads keyed by underlying."""
    segments: Dict[str, Any] = {}
    missing: List[str] = []

    for underlying in INDEX_SEGMENTS:
        chain = chains.get(underlying) or {}
        contracts = chain.get("contracts") or []
        if not contracts:
            missing.append(underlying)
            segments[underlying] = {
                "underlying": underlying,
                "implemented": False,
                "status": chain.get("status", "NO_DATA"),
                "data_source": chain.get("data_source"),
                "message": chain.get("message", "No contracts"),
                "top_ce": None,
                "top_pe": None,
            }
            continue

        seg = scan_segment_contracts(contracts, underlying, top_n=top_n)
        seg["status"] = chain.get("status", "OK")
        seg["data_source"] = chain.get("data_source")
        seg["spot"] = chain.get("spot")
        seg["total_contracts"] = chain.get("total_contracts", len(contracts))
        segments[underlying] = seg

    all_ce = [s["top_ce"] for s in segments.values() if s.get("top_ce")]
    all_pe = [s["top_pe"] for s in segments.values() if s.get("top_pe")]
    market_top_ce = max(all_ce, key=lambda x: x["gain_pct"]) if all_ce else None
    market_top_pe = max(all_pe, key=lambda x: x["gain_pct"]) if all_pe else None

    implemented_count = sum(1 for s in segments.values() if s.get("implemented"))
    return {
        "generated_utc": _utc_now(),
        "segments": INDEX_SEGMENTS,
        "segments_implemented": implemented_count,
        "segments_total": len(INDEX_SEGMENTS),
        "all_segments_live": implemented_count == len(INDEX_SEGMENTS),
        "missing_segments": missing,
        "by_segment": segments,
        "market_wide": {
            "top_ce": market_top_ce,
            "top_pe": market_top_pe,
        },
    }


def fetch_chains_for_segments() -> Dict[str, Dict[str, Any]]:
    """Fetch option chains for all index segments via DataSourceManager."""
    chains: Dict[str, Dict[str, Any]] = {}
    try:
        from core.data.datasource_manager import DataSourceManager
        from dashboard.backend.chain_adapter import fetch_chain_for_api

        dsm = DataSourceManager()
        for underlying in INDEX_SEGMENTS:
            try:
                result = fetch_chain_for_api(dsm, underlying)
                chains[underlying] = result or {"contracts": [], "underlying": underlying}
            except Exception as exc:
                chains[underlying] = {
                    "underlying": underlying,
                    "contracts": [],
                    "error": str(exc)[:200],
                }
    except Exception as exc:
        for underlying in INDEX_SEGMENTS:
            chains.setdefault(underlying, {"contracts": [], "error": str(exc)[:200]})
    return chains


def build_top_contract_gainers_report(top_n: int = 5) -> Dict[str, Any]:
    chains = fetch_chains_for_segments()
    report = scan_all_segments_from_chains(chains, top_n=top_n)
    report["chains_fetched"] = list(chains.keys())
    return report
