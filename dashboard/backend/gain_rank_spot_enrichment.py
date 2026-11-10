"""Pure helpers: attach authenticated snapshot spots to gain-rank rows.

Never invent BASE_SPOT / synthetic prices. Only apply spots from caller-supplied
authenticated lookup (live chain or MARKET_CLOSED_DHAN_SNAPSHOT buffers).
"""

from __future__ import annotations

from typing import Any, Dict, List, Mapping, MutableMapping, Optional


_BLOCKED_SOURCES = frozenset(
    {
        "synthetic",
        "base_spot",
        "base_spot_prices",
        "invented",
        "dummy",
    }
)


def _normalize_source(source: Any) -> str:
    return str(source or "").strip().lower()


def is_authenticated_spot_entry(entry: Mapping[str, Any] | None) -> bool:
    if not isinstance(entry, Mapping):
        return False
    try:
        spot = float(entry.get("spot") or 0)
    except (TypeError, ValueError):
        return False
    if spot <= 0:
        return False
    source = _normalize_source(entry.get("source") or entry.get("data_source"))
    if source in _BLOCKED_SOURCES:
        return False
    status = str(entry.get("status") or "").upper()
    # Explicit synthetic markers
    if "SYNTHETIC" in status:
        return False
    return True


def enrich_gain_rank_rows_with_authenticated_spots(
    rows: List[MutableMapping[str, Any]] | List[Dict[str, Any]],
    spot_lookup: Mapping[str, Mapping[str, Any]],
) -> List[Dict[str, Any]]:
    """Copy rows and fill missing spot_price from authenticated lookup only."""
    out: List[Dict[str, Any]] = []
    for row in rows or []:
        if not isinstance(row, dict):
            continue
        enriched = dict(row)
        try:
            existing = float(enriched.get("spot_price") or 0)
        except (TypeError, ValueError):
            existing = 0.0
        if existing > 0:
            out.append(enriched)
            continue
        underlying = str(enriched.get("underlying") or enriched.get("symbol") or "").upper()
        entry = spot_lookup.get(underlying) if underlying else None
        if not is_authenticated_spot_entry(entry):
            out.append(enriched)
            continue
        assert entry is not None
        enriched["spot_price"] = float(entry["spot"])
        enriched["spot_price_source"] = str(
            entry.get("source") or entry.get("data_source") or entry.get("status") or "AUTHENTICATED_SNAPSHOT"
        )
        out.append(enriched)
    return out
