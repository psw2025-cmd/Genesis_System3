"""Fail-closed MARKET -> SIGNAL -> PAPER feed admission.

The dashboard may *display* a stale Dhan chain, but no automated PAPER action
may use it. This is an ingress/transport freshness guard, NOT an independent
exchange quote or market-outcome verifier. Never sends broker requests.
"""
from __future__ import annotations

import math
from typing import Any, Mapping


FRESH_MAX_AGE_S = 90.0
_BLOCKED_SOURCE_TOKENS = (
    "synthetic", "replay", "fixture", "sample", "demo", "mock",
    "csv", "fallback", "snapshot", "moneycontrol", "yahoo",
    "market_closed", "last_good", "stale",
)


def _number(value: Any, *, positive: bool = False) -> float | None:
    if isinstance(value, bool) or value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    if not math.isfinite(number) or (positive and number <= 0):
        return None
    return number


def _valid_contract(contract: Any) -> bool:
    if not isinstance(contract, Mapping):
        return False
    if str(contract.get("option_type") or "").upper() not in ("CE", "PE"):
        return False
    if _number(contract.get("strike"), positive=True) is None:
        return False
    quote = contract.get("ltp") or contract.get("mid_price")
    if _number(quote, positive=True) is None:
        return False
    # CloudPaperEngine converts these values to float when selecting signals.
    # Reject a whole corrupt contract rather than crashing a trading tick.
    for field in (
        "previous_close_price", "previous_close", "prev_close", "gain_pct",
        "dOI", "oi_change", "change_in_oi", "volume",
    ):
        if contract.get(field) is not None and _number(contract[field]) is None:
            return False
    return True


def admit_paper_chains(
    chains: list[Any], *, max_age_seconds: float = FRESH_MAX_AGE_S
) -> tuple[list[dict], list[dict]]:
    """Return admitted chains and metadata-only rejection receipts.

    Requires an explicitly LIVE, not-stale Dhan push/micro-loop snapshot with
    measured transport age. This **does not** independently verify the Dhan
    exchange quote timestamp or authenticate a worker; those are upstream tasks.
    """
    if (_number(max_age_seconds, positive=True) is None
            or max_age_seconds > FRESH_MAX_AGE_S):
        raise ValueError("PAPER_FEED_MAX_AGE_INVALID")
    admitted: list[dict] = []
    rejected: list[dict] = []
    for index, chain in enumerate(chains):
        reason = None
        symbol = str(chain.get("underlying") or "")[:30] if isinstance(chain, dict) else ""
        if not isinstance(chain, dict):
            reason = "INVALID_CHAIN"
        elif chain.get("live") is not True or chain.get("stale") is not False:
            reason = "CHAIN_NOT_FRESH_LIVE"
        else:
            age = _number(chain.get("snapshot_age_seconds"))
            if age is None or not 0 <= age <= max_age_seconds:
                reason = "MISSING_OR_STALE_TRANSPORT_TIMESTAMP"
            else:
                source = str(chain.get("data_source") or "").lower()
                provenance = " ".join(
                    str(chain.get(key) or "").lower()
                    for key in ("data_source", "source", "status", "market_data_source", "quote_source")
                )
                if "dhan" not in source or any(
                    token in provenance for token in _BLOCKED_SOURCE_TOKENS
                ):
                    reason = "SOURCE_NOT_DHAN_LIVE"
                elif _number(chain.get("spot") or chain.get("spot_price"), positive=True) is None:
                    reason = "INVALID_SPOT"
        if reason is None:
            all_contracts = chain.get("contracts")
            if not isinstance(all_contracts, list):
                reason = "INVALID_CONTRACTS"
            else:
                contracts = [dict(c) for c in all_contracts if _valid_contract(c)]
                if not contracts:
                    reason = "NO_USABLE_OPTION_QUOTES"
        if reason:
            rejected.append({"index": index, "underlying": symbol, "reason": reason})
        else:
            admitted.append({**chain, "contracts": contracts})
    return admitted, rejected


def missing_open_position_quotes(
    positions: list[Any], admitted_chains: list[dict]
) -> list[str]:
    """Stop *the entire tick* if any OPEN trade cannot be freshly marked.

    Legacy paper engine otherwise falls back to entry_price and can fabricate
    an EOD simulated exit using that old number. No quote => no fill.
    """
    quotes = set()
    for chain in admitted_chains:
        symbol = str(chain.get("underlying") or "").upper()
        for row in chain.get("contracts") or []:
            quotes.add((symbol, float(row["strike"]), str(row["option_type"]).upper()))
    missing: list[str] = []
    for position in positions:
        if not isinstance(position, Mapping):
            missing.append("INVALID_POSITION")
            continue
        symbol = str(position.get("underlying") or "").upper()
        strike = _number(position.get("strike"), positive=True)
        side = str(position.get("option_type") or "").upper()
        if strike is None or (symbol, strike, side) not in quotes:
            # Do not print confidential IDs, account information or prices.
            missing.append("MISSING_CURRENT_QUOTE")
    return missing
