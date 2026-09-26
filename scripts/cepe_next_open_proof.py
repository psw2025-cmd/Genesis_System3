"""Read-only next-opening option premium audit from two NSE F&O bhavcopies.

This measures historical moves, not predictive performance or executable fills.
Opening prices are reference observations and are never claimed as fills.
"""
from __future__ import annotations

import csv
from datetime import date, datetime
from hashlib import sha256
from io import StringIO
from math import isfinite
from pathlib import Path
from typing import Any

from scripts.cepe_session_scope import session_scope


def _number(value: Any, field: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid {field}") from exc
    if not isfinite(number) or number < 0:
        raise ValueError(f"Invalid {field}")
    return number


def _rows(
    raw: bytes,
    trade_date: date,
) -> dict[tuple[str, str, str, str], dict[str, float]]:
    table: dict[tuple[str, str, str, str], dict[str, float]] = {}
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError("Bhavcopy is not UTF-8 CSV") from exc
    reader = csv.DictReader(StringIO(text))
    names = set(reader.fieldnames or ())
    modern = {
        "TckrSymb",
        "XpryDt",
        "OptnTp",
        "StrkPric",
        "OpnPric",
        "ClsPric",
        "TradDt",
        "TtlTradgVol",
    }
    old = {
        "SYMBOL",
        "EXPIRY_DT",
        "OPTION_TYP",
        "STRIKE_PR",
        "OPEN",
        "CLOSE",
        "TIMESTAMP",
        "CONTRACTS",
    }
    if modern <= names:
        cols = (
            "TckrSymb",
            "XpryDt",
            "OptnTp",
            "StrkPric",
            "OpnPric",
            "ClsPric",
            "TradDt",
            "TtlTradgVol",
        )
    elif old <= names:
        cols = (
            "SYMBOL",
            "EXPIRY_DT",
            "OPTION_TYP",
            "STRIKE_PR",
            "OPEN",
            "CLOSE",
            "TIMESTAMP",
            "CONTRACTS",
        )
    else:
        raise ValueError("Unsupported bhavcopy schema")

    sym, expiry, kind, strike, opening, closing, dated, volume = cols
    for row in reader:
        option_type = str(row.get(kind, "")).strip().upper()
        if option_type not in {"CE", "PE"}:
            continue
        observed = _date(row[dated])
        if observed != trade_date:
            raise ValueError("Trade date differs from requested date")
        expiry_day = _date(row[expiry])
        if expiry_day < trade_date:
            continue
        symbol = str(row.get(sym, "")).strip().upper()
        if not symbol:
            raise ValueError("Missing contract symbol")
        key = (
            symbol,
            expiry_day.isoformat(),
            format(_number(row.get(strike), "strike"), ".4f"),
            option_type,
        )
        if key in table:
            raise ValueError("Duplicate contract row")
        table[key] = {
            "open": _number(row.get(opening), "opening price"),
            "close": _number(row.get(closing), "closing price"),
            "volume": _number(row.get(volume), "traded volume"),
        }
    return table


def _date(value: str) -> date:
    for fmt in ("%Y-%m-%d", "%d-%b-%Y", "%d-%b-%y", "%d/%m/%Y"):
        try:
            return datetime.strptime(value.strip(), fmt).date()
        except ValueError:
            pass
    raise ValueError("Unknown date format")


def compare(
    previous: bytes,
    following: bytes,
    previous_day: date,
    following_day: date,
    *,
    min_volume: float = 100,
    min_previous_close: float = 1,
    session_calendar: bytes | None = None,
) -> dict[str, Any]:
    """Return the full gross reference distribution for liquid matched contracts."""
    minimum_volume = _number(min_volume, "minimum volume")
    minimum_close = _number(min_previous_close, "minimum previous close")
    before = _rows(previous, previous_day)
    after = _rows(following, following_day)
    scope = session_scope(previous_day, following_day, session_calendar)
    aligned = scope["session_alignment_status"] != "NOT_PROVEN"
    matches = []
    excluded_illiquid = 0
    for key in sorted(before.keys() & after.keys()):
        close = before[key]["close"]
        opening = after[key]["open"]
        liquid = (
            close > 0 and close >= minimum_close
            and opening > 0
            and min(before[key]["volume"], after[key]["volume"])
            >= minimum_volume
        )
        if not liquid:
            excluded_illiquid += 1
            continue
        multiple = round(opening / close, 6)
        matches.append(
            {
                "symbol": key[0],
                "expiry": key[1],
                "strike": key[2],
                "type": key[3],
                "previous_close": close,
                "next_open": opening if aligned else None,
                "observed_open": opening,
                "multiple": multiple,
                "gross_reference_multiple": multiple,
                "opening_fill_proven": False,
                "cost_adjusted": False,
            }
        )

    multiples = [row["multiple"] for row in matches]
    ordered = sorted(matches, key=lambda row: row["multiple"], reverse=True)
    return {
        **scope,
        "previous_day": previous_day.isoformat(),
        "following_day": following_day.isoformat(),
        "previous_sha256": sha256(previous).hexdigest(),
        "following_sha256": sha256(following).hexdigest(),
        "matched_contracts": len(matches),
        "excluded_illiquid_contracts": excluded_illiquid,
        "minimum_volume_each_day": minimum_volume,
        "minimum_previous_close": minimum_close,
        "highest_multiple": max(multiples, default=None),
        "top_moves": ordered[:20],
        "example_threshold_counts": {
            str(threshold): sum(value >= threshold for value in multiples)
            for threshold in (3, 10, 20, 30)
        },
        "matches": matches,
        "distribution_scope": "FULL_MATCHED_CONTRACT_SET_UNCAPPED",
        "metric_basis": ("GROSS_NEXT_OPEN_OVER_PREVIOUS_CLOSE_REFERENCE" if aligned
                         else "GROSS_LATER_OPEN_OVER_PREVIOUS_CLOSE_REFERENCE"),
        "fees_slippage_status": "NOT_APPLIED",
        "opening_fill_proven": False,
        "status": "HISTORICAL_MOVES_ONLY" if aligned else "HISTORICAL_INTERVAL_ONLY",
        "prediction_accuracy_proven": False,
        "orders_allowed": False,
    }


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser()
    parser.add_argument("previous_csv", type=Path)
    parser.add_argument("following_csv", type=Path)
    parser.add_argument("previous_day", type=date.fromisoformat)
    parser.add_argument("following_day", type=date.fromisoformat)
    parser.add_argument("--min-volume", type=float, default=100)
    parser.add_argument("--min-previous-close", type=float, default=1)
    parser.add_argument("--session-calendar", type=Path)
    args = parser.parse_args()
    print(
        json.dumps(
            compare(
                args.previous_csv.read_bytes(),
                args.following_csv.read_bytes(),
                args.previous_day,
                args.following_day,
                min_volume=args.min_volume,
                min_previous_close=args.min_previous_close,
                session_calendar=args.session_calendar.read_bytes() if args.session_calendar else None,
            ),
            indent=2,
        )
    )
