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
    # Moneycontrol-style: pure % gain ranking across CE+PE (no forced CE/PE slot mix).
    # Index domination is handled by separate equity_focus board when requested.
    combined = sorted(all_scored, key=lambda x: x["gain_pct"], reverse=True)

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
        "ranking_mode": "pure_gain_pct",
    }


_SHARD_STATE: Dict[str, Any] = {"cursor": 0, "last_syms": []}


def _equity_scan_universe(limit: int = 12, rotate: bool = True) -> List[str]:
    """Return equity FO names for this scan tick.

    Momentum + priority first; optional cursor rotation walks the full OPTSTK
    universe in shards so Cloud Run never fans out all ~211 chains in one request.
    """
    try:
        from core.brokers.dhan.equity_fo_universe import (
            HIGH_MOMENTUM_EQUITY_FO,
            PRIORITY_EQUITY_FO,
            load_equity_fo_universe,
        )

        universe = load_equity_fo_universe()
        priority = list(universe.get("priority_underlyings") or [])
        if not priority:
            priority = [s for s in (HIGH_MOMENTUM_EQUITY_FO + PRIORITY_EQUITY_FO) if True]
        all_names = list(universe.get("underlyings") or [])
        limit = max(3, min(int(limit or 12), 40))

        # Always include head of momentum/priority so today's MC names are eligible.
        selected: List[str] = []
        for name in priority:
            if name not in selected:
                selected.append(name)
            if len(selected) >= max(8, limit // 2):
                break

        if rotate and all_names:
            cursor = int(_SHARD_STATE.get("cursor") or 0) % max(1, len(all_names))
            shard = []
            for i in range(len(all_names)):
                name = all_names[(cursor + i) % len(all_names)]
                if name in selected:
                    continue
                shard.append(name)
                if len(selected) + len(shard) >= limit:
                    break
            selected.extend(shard)
            _SHARD_STATE["cursor"] = (cursor + max(1, limit // 2)) % max(1, len(all_names))
        else:
            selected = selected[:limit]

        _SHARD_STATE["last_syms"] = selected[:limit]
        return selected[:limit]
    except Exception:
        return ["DIVISLAB", "LTM", "PAYTM", "JUBLFOOD", "RELIANCE", "HDFCBANK", "TCS", "INFY"][: max(3, min(limit, 20))]


def fetch_chains_for_market(
    include_equity: bool = True,
    equity_limit: int = 8,
    overall_timeout_s: float = 75.0,
    rotate_equity: bool = True,
) -> Dict[str, Dict[str, Any]]:
    """Fetch option chains for index + priority/rotated equity FO names.

    Equity fetches are best-effort under a time budget so Cloud Run does not 503.
    """
    chains: Dict[str, Dict[str, Any]] = {}
    symbols = list(INDEX_SEGMENTS)
    if include_equity:
        for sym in _equity_scan_universe(equity_limit, rotate=rotate_equity):
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
            # Dhan option-chain rate limit ≈ 1 unique request / 3s. Parallel fan-out
            # for equities returns empty and Market Top never sees DIVISLAB/LTM/etc.
            for underlying in equity_syms:
                if (time.monotonic() - started) >= overall_timeout_s - 3.0:
                    chains.setdefault(
                        underlying,
                        {"contracts": [], "underlying": underlying, "status": "SKIPPED_TIMEOUT"},
                    )
                    continue
                try:
                    time.sleep(3.15)
                    underlying2, ch = _fetch_one(underlying)
                    chains[underlying2] = ch
                except Exception as eq_exc:
                    chains[underlying] = {
                        "contracts": [],
                        "underlying": underlying,
                        "status": "ERROR",
                        "error": str(eq_exc)[:160],
                    }
    except Exception as exc:
        for underlying in symbols:
            chains.setdefault(underlying, {"contracts": [], "error": str(exc)[:200]})
    return chains


def fetch_chains_for_segments() -> Dict[str, Dict[str, Any]]:
    """Backward-compatible index-only fetch."""
    return fetch_chains_for_market(include_equity=False)


def merge_market_top_reports(base: Dict[str, Any], incoming: Dict[str, Any], market_top_n: int = 25) -> Dict[str, Any]:
    """Merge two scanner reports by pure gain_pct (keeps rolling shard memory)."""
    if not base:
        return incoming or {}
    if not incoming:
        return base
    by_key: Dict[str, Dict[str, Any]] = {}
    for report in (base, incoming):
        for row in report.get("market_top_table") or []:
            if not isinstance(row, dict):
                continue
            key = (
                f"{row.get('underlying')}|{row.get('option_type')}|{row.get('strike')}|"
                f"{row.get('expiry_date') or row.get('expiry')}"
            )
            prev = by_key.get(key)
            if prev is None or float(row.get("gain_pct") or -1e18) >= float(prev.get("gain_pct") or -1e18):
                by_key[key] = dict(row)
    combined = sorted(by_key.values(), key=lambda x: float(x.get("gain_pct") or 0), reverse=True)
    refreshed_at = incoming.get("refreshed_at") or base.get("refreshed_at") or _ist_now_str()
    out = dict(incoming)
    out["market_top_table"] = _rank_table(combined, market_top_n, refreshed_at)
    out["market_wide"] = dict(incoming.get("market_wide") or {})
    out["market_wide"]["top_combined_list"] = out["market_top_table"]
    out["contracts_scored_total"] = max(
        int(base.get("contracts_scored_total") or 0),
        int(incoming.get("contracts_scored_total") or 0),
        len(combined),
    )
    scanned = set(base.get("chains_fetched") or []) | set(incoming.get("chains_fetched") or [])
    out["chains_fetched"] = sorted(scanned)
    out["underlyings_scanned"] = len(scanned)
    out["ranking_mode"] = "pure_gain_pct_merged"
    out["shard_cursor"] = _SHARD_STATE.get("cursor")
    out["shard_last_syms"] = list(_SHARD_STATE.get("last_syms") or [])
    return out


def build_top_contract_gainers_report(
    top_n: int = 5,
    market_top_n: int = 25,
    include_equity: bool = True,
    equity_limit: Optional[int] = None,
    overall_timeout_s: Optional[float] = None,
    rotate_equity: bool = True,
    equity_only_board: bool = False,
) -> Dict[str, Any]:
    eq_limit = 16 if include_equity else 0
    if equity_limit is not None:
        eq_limit = int(equity_limit)
    timeout = 70.0 if include_equity else 45.0
    if overall_timeout_s is not None:
        timeout = float(overall_timeout_s)
    chains = fetch_chains_for_market(
        include_equity=include_equity,
        equity_limit=eq_limit,
        overall_timeout_s=timeout,
        rotate_equity=rotate_equity,
    )
    if equity_only_board:
        chains = {k: v for k, v in chains.items() if k not in INDEX_SEGMENTS}
    report = scan_all_segments_from_chains(chains, top_n=top_n, market_top_n=market_top_n)
    report["chains_fetched"] = list(chains.keys())
    report["include_equity"] = include_equity
    report["equity_limit"] = eq_limit
    report["equity_only_board"] = equity_only_board
    report["shard_cursor"] = _SHARD_STATE.get("cursor")
    report["shard_last_syms"] = list(_SHARD_STATE.get("last_syms") or [])
    report["status"] = "ok" if report.get("contracts_scored_total", 0) > 0 else "no_data"
    report["diagnose"] = {
        "why_not_moneycontrol_parity": (
            "Dhan Market Top scans a rotating equity FO shard + indices; "
            "Moneycontrol ranks essentially all NSE option contracts. "
            "Use /api/scanner/moneycontrol_gainers for LIVE_SCRAPED reference."
        ),
        "equity_limit": eq_limit,
        "shard_last_syms": list(_SHARD_STATE.get("last_syms") or []),
        "live_trading_enabled": False,
    }
    return report


def diagnose_market_top_gap(expected_symbols: Optional[List[str]] = None) -> Dict[str, Any]:
    """Auto-diagnose why Moneycontrol high-risers may be missing from Dhan Market Top."""
    expected = [
        s.upper()
        for s in (
            expected_symbols
            or [
                "DIVISLAB",
                "LTM",
                "PAYTM",
                "JUBLFOOD",
                "TVSMOTOR",
                "SIEMENS",
                "APLAPOLLO",
                "BAJAJFINSV",
            ]
        )
    ]
    try:
        from core.brokers.dhan.equity_fo_universe import load_equity_fo_universe

        universe = load_equity_fo_universe()
        names = set(universe.get("underlyings") or [])
        priority = list(universe.get("priority_underlyings") or [])
    except Exception as exc:
        return {"status": "ERROR", "error": str(exc)[:200]}

    in_master = [s for s in expected if s in names]
    missing_master = [s for s in expected if s not in names]
    in_priority = [s for s in expected if s in priority]
    not_in_priority_head = [s for s in expected if s in names and s not in priority[:16]]
    return {
        "status": "ok",
        "expected": expected,
        "in_fo_master": in_master,
        "missing_from_fo_master": missing_master,
        "in_scan_priority": in_priority,
        "not_in_priority_head16": not_in_priority_head,
        "fo_underlying_count": len(names),
        "shard_cursor": _SHARD_STATE.get("cursor"),
        "shard_last_syms": list(_SHARD_STATE.get("last_syms") or []),
        "root_cause_if_absent_on_board": (
            "Symbol may be in FO master but not yet reached by rotating equity shard, "
            "or Dhan chain returned no LTP/prev_close for gain calc, or index contracts "
            "outranked it on pure gain_pct. Moneycontrol scrape board is separate LIVE_SCRAPED truth."
        ),
        "remediation": [
            "Keep market_top_micro_loop running so shards rotate through OPTSTK",
            "Compare /api/scanner/moneycontrol_gainers (LIVE_SCRAPED) vs Dhan market_top_table",
            "Paper may seed from high-rise rows; live money stays OFF until gates pass",
        ],
        "live_trading_enabled": False,
    }
