"""Pure, read-only scheduling policy for paced equity F&O option chains.

A per-symbol cache miss must never monopolize the single existing Dhan
option-chain worker. This module makes NO broker calls and cannot trade.
"""


def _names(values):
    seen = set()
    out = []
    for value in values or []:
        name = str(value or "").strip().upper()
        if name and name not in seen:
            seen.add(name)
            out.append(name)
    return out


def choose_equity_gainer_symbol(cursor, underlyings, priorities):
    """Visit the entire verified universe with ~25% priority slots.

    The existing market micro-loop owns rate limiting and invokes this policy
    once per paced equity turn. Missing/failed symbols do not cause retries of
    the same first symbol forever. If the master is unavailable, only priority
    hints are attempted and no full-universe coverage is claimed.
    """
    if not isinstance(cursor, int) or cursor < 0:
        raise ValueError("INVALID_EQUITY_ROTATION_CURSOR")
    universe = _names(underlyings)
    priority = _names(priorities)
    if universe:
        allowed = set(universe)
        priority = [name for name in priority if name in allowed]
    if not universe:
        return priority[cursor % len(priority)] if priority else None
    if priority and cursor % 4 == 0:
        return priority[(cursor // 4) % len(priority)]
    # Every non-priority slot must advance by one (3 per four calls).
    full_index = (cursor // 4) * 3 + (cursor % 4) - 1 if priority else cursor
    return universe[full_index % len(universe)]
