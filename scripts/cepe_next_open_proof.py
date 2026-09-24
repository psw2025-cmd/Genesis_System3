"""Read-only next-opening option premium audit from two NSE F&O bhavcopies.

This measures historical moves, not predictive performance or executable fills.
"""
from __future__ import annotations

import csv
from datetime import date
from hashlib import sha256
from io import StringIO
from pathlib import Path


def _rows(raw: bytes, trade_date: date) -> dict[tuple[str, str, str, str], dict]:
    table = {}
    text = raw.decode("utf-8-sig")
    reader = csv.DictReader(StringIO(text))
    names = set(reader.fieldnames or ())
    modern = {"TckrSymb", "XpryDt", "OptnTp", "StrkPric", "OpnPric", "ClsPric", "TradDt"}
    old = {"SYMBOL", "EXPIRY_DT", "OPTION_TYP", "STRIKE_PR", "OPEN", "CLOSE", "TIMESTAMP"}
    if modern <= names:
        cols = ("TckrSymb", "XpryDt", "OptnTp", "StrkPric", "OpnPric", "ClsPric", "TradDt")
    elif old <= names:
        cols = ("SYMBOL", "EXPIRY_DT", "OPTION_TYP", "STRIKE_PR", "OPEN", "CLOSE", "TIMESTAMP")
    else:
        raise ValueError("Unsupported bhavcopy schema")
    sym, expiry, kind, strike, opening, closing, dated = cols
    for row in reader:
        if row[kind] not in {"CE", "PE"}:
            continue
        observed = _date(row[dated])
        if observed != trade_date:
            raise ValueError("Trade date differs from requested date")
        expiry_day = _date(row[expiry])
        if expiry_day < trade_date:
            continue
        key = (row[sym].strip().upper(), expiry_day.isoformat(),
               format(float(row[strike]), ".4f"), row[kind])
        if key in table:
            raise ValueError("Duplicate contract row")
        table[key] = {"open": float(row[opening]), "close": float(row[closing])}
    return table


def _date(value: str) -> date:
    from datetime import datetime
    for fmt in ("%Y-%m-%d", "%d-%b-%Y", "%d-%b-%y", "%d/%m/%Y"):
        try:
            return datetime.strptime(value.strip(), fmt).date()
        except ValueError:
            pass
    raise ValueError("Unknown date format")


def compare(previous: bytes, following: bytes, previous_day: date, following_day: date) -> dict:
    if following_day <= previous_day or (following_day - previous_day).days > 5:
        raise ValueError("Dates are not adjacent trading sessions")
    before, after = _rows(previous, previous_day), _rows(following, following_day)
    matches = []
    for key in sorted(before.keys() & after.keys()):
        close, opening = before[key]["close"], after[key]["open"]
        if close <= 0 or opening <= 0:
            continue
        matches.append({"symbol": key[0], "expiry": key[1], "strike": key[2],
                        "type": key[3], "previous_close": close, "next_open": opening,
                        "multiple": round(opening / close, 6)})
    return {"previous_day": previous_day.isoformat(), "following_day": following_day.isoformat(),
            "previous_sha256": sha256(previous).hexdigest(),
            "following_sha256": sha256(following).hexdigest(),
            "matched_contracts": len(matches),
            "counts": {str(n): sum(x["multiple"] >= n for x in matches) for n in (3, 10, 20, 30)},
            "matches": matches, "status": "HISTORICAL_MOVES_ONLY",
            "prediction_accuracy_proven": False, "orders_allowed": False}


if __name__ == "__main__":
    import argparse
    import json
    parser = argparse.ArgumentParser()
    parser.add_argument("previous_csv", type=Path)
    parser.add_argument("following_csv", type=Path)
    parser.add_argument("previous_day", type=date.fromisoformat)
    parser.add_argument("following_day", type=date.fromisoformat)
    args = parser.parse_args()
    print(json.dumps(compare(args.previous_csv.read_bytes(), args.following_csv.read_bytes(),
                             args.previous_day, args.following_day), indent=2))
