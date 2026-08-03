"""
Live market scanner — highest % gain CE and PE contracts (index + equity FO).

Uses LTP vs previous_close from Dhan option-chain rows (official fields).
Produces a market-wide ranked table similar to broker Top Gainers boards.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
import time
from typing import Any, Dict, List, Optional, Tuple

INDEX_SEGMENTS = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _ist_now_str() -> str:
    # Asia/Kolkata = UTC+5:30
    ist = timezone(timedelta(hours=5, minutes=30))
    return datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S")


def compute_contract_gain(contract: Dict[str, Any]) -> Tuple[Optional[float], Optional[float], Optional[float], Optional[float]]:
    """Return (ltp, previous_close, change_rs, gain_pct)."""
    try:
        ltp = float(contract.get("ltp") or contract.get("last_price") or contract.get("close") or 0)
    except (TypeError, ValueError):
        ltp = 0.0
    try:
        prev = float(
            contract.get("previous_close_price")
            or contract.get("previous_close")
            or contract.get("prev_close")
            or 0
        )
    except (TypeError, ValueError):
        prev = 0.0

    change_rs = None
    gain_pct = None
    if ltp > 0 and prev > 0:
        change_rs = round(ltp - prev, 4)
        gain_pct = round((ltp - prev) / prev * 100.0, 4)
    else:
        # Only trust explicit percent when prev close is unavailable.
        for key in ("change_percent", "pChange", "gain_pct", "pct_change"):
            val = contract.get(key)
            if val is None:
                continue
            try:
                pct = float(val)
            except (TypeError, ValueError):
                continue
            if abs(pct) > 1e-9:
                gain_pct = round(pct, 4)
                break
    return (ltp if ltp > 0 else None, prev if prev > 0 else None, change_rs, gain_pct)


def compute_contract_gain_pct(contract: Dict[str, Any]) -> Optional[float]:
    """Backward-compatible gain % helper used by unit tests and callers."""
    return compute_contract_gain(contract)[3]


def _contract_row(contract: Dict[str, Any], underlying: str, gain_pct: float, change_rs: Optional[float], ltp: float, prev: Optional[float]) -> Dict[str, Any]:
    opt = str(contract.get("option_type", "")).upper()
    return {
        "underlying": underlying.upper(),
        "symbol": underlying.upper(),
        "option_type": opt,
        "strike": contract.get("strike"),
        "trading_symbol": contract.get("trading_symbol") or contract.get("symbol"),
        "expiry_date": contract.get("expiry_date") or contract.get("expiry"),
        "ltp": ltp,
        "previous_close": prev,
        "change": change_rs,
        "change_rs": change_rs,
        "oi": contract.get("oi"),
        "oi_change": contract.get("oi_change") or contract.get("change_in_oi"),
        "volume": contract.get("volume"),
        "gain_pct": gain_pct,
        "security_id": contract.get("security_id"),
        "source": contract.get("source") or "dhan",
        "data_provenance": "DHAN_OPTION_CHAIN_LIVE",
        "market_match_note": f"LIVE DHAN GAINER (+{gain_pct:.2f}%)",
    }


def scan_segment_contracts(
    contracts: List[Dict[str, Any]],
    underlying: str,
    top_n: int = 5,
    min_ltp: float = 1.0,
    min_volume: int = 0,
    default_expiry: Optional[str] = None,
) -> Dict[str, Any]:
    """Find highest-gain CE and PE contracts for one underlying."""
    scored: List[Dict[str, Any]] = []
    for c in contracts or []:
        opt = str(c.get("option_type", "")).upper()
        if opt not in ("CE", "PE"):
            continue
        ltp, prev, change_rs, gain = compute_contract_gain(c)
        if gain is None or ltp is None or ltp < min_ltp:
            continue
        vol = int(c.get("volume") or 0)
        if vol < min_volume:
            continue
        row = _contract_row(c, underlying.upper(), gain, change_rs, ltp, prev)
        if not row.get("expiry_date") and default_expiry:
            row["expiry_date"] = default_expiry
        scored.append(row)

    ce_rows = sorted([r for r in scored if r["option_type"] == "CE"], key=lambda x: x["gain_pct"], reverse=True)
    pe_rows = sorted([r for r in scored if r["option_type"] == "PE"], key=lambda x: x["gain_pct"], reverse=True)

    return {
        "underlying": underlying.upper(),
        "contracts_scored": len(scored),
        "top_ce": ce_rows[0] if ce_rows else None,
        "top_pe": pe_rows[0] if pe_rows else None,
        "top_ce_list": ce_rows[:top_n],
        "top_pe_list": pe_rows[:top_n],
        "all_scored": scored,
        "implemented": True,
    }


def _rank_table(rows: List[Dict[str, Any]], top_n: int, refreshed_at: str) -> List[Dict[str, Any]]:
    out = []
    for i, row in enumerate(rows[:top_n], start=1):
        item = dict(row)
        item["rank"] = i
        item["refreshed_at"] = refreshed_at
        out.append(item)
    return out


def scan_all_segments_from_chains(
    chains: Dict[str, Dict[str, Any]],
    top_n: int = 5,
    market_top_n: int = 25,
) -> Dict[str, Any]:
    """Scan pre-fetched chain payloads keyed by underlying."""
    segments: Dict[str, Any] = {}
    missing: List[str] = []
    all_scored: List[Dict[str, Any]] = []
    refreshed_at = _ist_now_str()

    underlyings = list(chains.keys()) or list(INDEX_SEGMENTS)
    for underlying in underlyings:
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

        seg = scan_segment_contracts(
            contracts,
            underlying,
            top_n=top_n,
            default_expiry=chain.get("expiry_date") or chain.get("expiry"),
        )
        seg["status"] = chain.get("status", "OK")
        seg["data_source"] = chain.get("data_source")
        seg["spot"] = chain.get("spot")
        seg["total_contracts"] = chain.get("total_contracts", len(contracts))
        segments[underlying] = {k: v for k, v in seg.items() if k != "all_scored"}
        all_scored.extend(seg.get("all_scored") or [])

    ce_all = sorted([r for r in all_scored if r["option_type"] == "CE"], key=lambda x: x["gain_pct"], reverse=True)
    pe_all = sorted([r for r in all_scored if r["option_type"] == "PE"], key=lambda x: x["gain_pct"], reverse=True)
    # Board must show both CE and PE (broker Top Gainers style), not CE-only domination.
    pe_slots = min(10, max(5, market_top_n // 3), len(pe_all))
    ce_slots = max(0, market_top_n - pe_slots)
    mixed = list(ce_all[:ce_slots]) + list(pe_all[:pe_slots])
    mixed = sorted(mixed, key=lambda x: x["gain_pct"], reverse=True)
    combined = mixed if mixed else sorted(all_scored, key=lambda x: x["gain_pct"], reverse=True)

    index_keys = set(INDEX_SEGMENTS)
    implemented_index = sum(1 for u in INDEX_SEGMENTS if segments.get(u, {}).get("implemented"))
    return {
        "generated_utc": _utc_now(),
        "refreshed_at": refreshed_at,
        "segments": INDEX_SEGMENTS,
        "segments_implemented": implemented_index,
        "segments_total": len(INDEX_SEGMENTS),
        "underlyings_scanned": len([u for u, s in segments.items() if s.get("implemented")]),
        "all_segments_live": implemented_index == len(INDEX_SEGMENTS),
        "missing_segments": [u for u in INDEX_SEGMENTS if u in missing],
        "by_segment": {k: v for k, v in segments.items() if k in index_keys},
        "by_underlying": segments,
        "market_wide": {
            "top_ce": ce_all[0] if ce_all else None,
            "top_pe": pe_all[0] if pe_all else None,
            "top_ce_list": _rank_table(ce_all, market_top_n, refreshed_at),
            "top_pe_list": _rank_table(pe_all, market_top_n, refreshed_at),
            "top_combined_list": _rank_table(combined, market_top_n, refreshed_at),
        },
        "market_top_table": _rank_table(combined, market_top_n, refreshed_at),
        "contracts_scored_total": len(all_scored),
    }


def _equity_scan_universe(limit: int = 12) -> List[str]:
    try:
        from core.brokers.dhan.equity_fo_universe import PRIORITY_EQUITY_FO, load_equity_fo_universe

        universe = load_equity_fo_universe()
        priority = list(universe.get("priority_underlyings") or PRIORITY_EQUITY_FO)
        return priority[: max(3, min(limit, 20))]
    except Exception:
        return ["RELIANCE", "HDFCBANK", "TCS", "INFY", "ICICIBANK", "SBIN", "ITC", "BAJFINANCE"]


def fetch_chains_for_market(
    include_equity: bool = True,
    equity_limit: int = 8,
    overall_timeout_s: float = 75.0,
) -> Dict[str, Dict[str, Any]]:
    """Fetch option chains for index + priority equity FO names.

    Equity fetches are best-effort under a time budget so Cloud Run does not 503.
    """
    chains: Dict[str, Dict[str, Any]] = {}
    symbols = list(INDEX_SEGMENTS)
    if include_equity:
        for sym in _equity_scan_universe(equity_limit):
            if sym not in symbols:
                symbols.append(sym)
    try:
        from core.data.datasource_manager import DataSourceManager
        from dashboard.backend.chain_adapter import fetch_chain_for_api

        dsm = DataSourceManager()
        started = time.monotonic()

        def _fetch_one(underlying: str):
            ch = fetch_chain_for_api(dsm, underlying)
            return underlying, ch or {"contracts": [], "underlying": underlying}

        # Indices first (required), then equity fill-in under remaining budget.
        index_syms = [u for u in symbols if u in INDEX_SEGMENTS]
        equity_syms = [u for u in symbols if u not in INDEX_SEGMENTS]

        with ThreadPoolExecutor(max_workers=min(4, max(1, len(index_syms)))) as pool:
            futs = {pool.submit(_fetch_one, u): u for u in index_syms}
            for fut in as_completed(futs, timeout=max(20.0, overall_timeout_s * 0.55)):
                underlying, ch = fut.result()
                chains[underlying] = ch

        remaining = overall_timeout_s - (time.monotonic() - started)
        if equity_syms and remaining > 12.0:
            with ThreadPoolExecutor(max_workers=min(4, len(equity_syms))) as pool:
                futs = {pool.submit(_fetch_one, u): u for u in equity_syms}
                try:
                    for fut in as_completed(futs, timeout=max(8.0, remaining - 2.0)):
                        underlying, ch = fut.result()
                        chains[underlying] = ch
                        if (time.monotonic() - started) >= overall_timeout_s:
                            break
                except Exception:
                    # Partial equity is acceptable — return what we have.
                    pass
                for fut, underlying in futs.items():
                    if not fut.done():
                        fut.cancel()
                        chains.setdefault(
                            underlying,
                            {"contracts": [], "underlying": underlying, "status": "SKIPPED_TIMEOUT"},
                        )
    except Exception as exc:
        for underlying in symbols:
            chains.setdefault(underlying, {"contracts": [], "error": str(exc)[:200]})
    return chains


def fetch_chains_for_segments() -> Dict[str, Dict[str, Any]]:
    """Backward-compatible index-only fetch."""
    return fetch_chains_for_market(include_equity=False)


def build_top_contract_gainers_report(
    top_n: int = 5,
    market_top_n: int = 25,
    include_equity: bool = True,
) -> Dict[str, Any]:
    chains = fetch_chains_for_market(
        include_equity=include_equity,
        equity_limit=4 if include_equity else 0,
        overall_timeout_s=55.0 if include_equity else 45.0,
    )
    report = scan_all_segments_from_chains(chains, top_n=top_n, market_top_n=market_top_n)
    report["chains_fetched"] = list(chains.keys())
    report["include_equity"] = include_equity
    report["status"] = "ok" if report.get("contracts_scored_total", 0) > 0 else "no_data"
    return report
