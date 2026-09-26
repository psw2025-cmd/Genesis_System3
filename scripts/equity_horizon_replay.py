"""Research replay for dated NSE equity snapshots at 7/14/365-day horizons.

Picks are derived only from the decision-day snapshot. Outcomes are looked
up separately at the first provided session on/after each target date, with a
maximum calendar lag. Raw closes are NOT corporate-action adjusted, so a
return never counts as verified multibagger performance here.
"""
from __future__ import annotations

import csv
from datetime import date, timedelta
from hashlib import sha256
from io import StringIO
import json
from math import isfinite
from pathlib import Path
from typing import Any


def parse(raw: bytes, day: date) -> dict[str, dict[str, Any]]:
    reader = csv.DictReader(StringIO(raw.decode("utf-8-sig")))
    required = {"TradDt", "ISIN", "TckrSymb", "SctySrs", "ClsPric", "TtlTradgVol"}
    if not required.issubset(reader.fieldnames or []):
        raise ValueError("Unsupported NSE equity CSV schema")
    found = {}
    for row in reader:
        if row["SctySrs"] != "EQ":
            continue
        if row["TradDt"] != day.isoformat():
            raise ValueError("Incorrect trade date")
        isin = row["ISIN"].strip()
        price = float(row["ClsPric"])
        volume = float(row["TtlTradgVol"])
        if not isin or isin in found or not isfinite(price) or price <= 0 or not isfinite(volume) or volume < 0:
            raise ValueError("Invalid or duplicate equity observation")
        found[isin] = dict(symbol=row["TckrSymb"], price=price, volume=volume)
    return found


def replay(snapshots: list[tuple[date, bytes]], *, top_k: int = 20,
           minimum_volume: float = 10000, minimum_price: float = 10,
           horizons: tuple[int, ...] = (7, 14, 365),
           max_outcome_lag_days: int = 4) -> dict[str, Any]:
    if top_k < 1 or not snapshots or [d for d, _ in snapshots] != sorted({d for d, _ in snapshots}):
        raise ValueError("Require sorted unique dated files and top_k >= 1")
    if any(h < 1 for h in horizons):
        raise ValueError("Invalid horizon")
    parsed = [(day, parse(raw, day), sha256(raw).hexdigest()) for day, raw in snapshots]
    decisions = []
    for day, before, source_hash in parsed:
        # The baseline uses only previous-day observable liquidity. Do not
        # train or rank on future returns or future universe membership.
        ranked = sorted(((v["volume"], isin) for isin, v in before.items()
                         if v["volume"] >= minimum_volume and v["price"] >= minimum_price),
                        key=lambda pair: (-pair[0], pair[1]))
        selected = [isin for _, isin in ranked[:top_k]]
        picks_hash = sha256(json.dumps(selected, separators=(",", ":")).encode()).hexdigest()
        outcomes = {}
        for horizon in horizons:
            target = day + timedelta(days=horizon)
            candidate = next(((next_day, after, digest) for next_day, after, digest in parsed
                              if target <= next_day <= target + timedelta(days=max_outcome_lag_days)), None)
            if candidate is None:
                outcomes[str(horizon)] = {"status": "MISSING_TARGET_SESSION", "target_date": target.isoformat()}
                continue
            next_day, after, outcome_hash = candidate
            matched = [(isin, after[isin]["price"] / before[isin]["price"])
                       for isin in selected if isin in after]
            outcomes[str(horizon)] = {
                "status": "UNADJUSTED_RESEARCH_ONLY",
                "target_date": target.isoformat(), "observed_date": next_day.isoformat(),
                "outcome_sha256": outcome_hash, "selected": len(selected),
                "matched": len(matched), "delisted_or_missing": len(selected) - len(matched),
                "at_least_2x": sum(mult >= 2 for _, mult in matched),
                "highest_raw_multiple": max((mult for _, mult in matched), default=None),
            }
        decisions.append({"decision_date": day.isoformat(), "source_sha256": source_hash,
                          "selected_keys_sha256": picks_hash, "selected_count": len(selected),
                          "horizons": outcomes})
    return {"rule": "DECISION_DAY_VOLUME_TOP_K_RESEARCH_BASELINE",
            "instrument_scope": "NSE_EQ_SERIES_MIXED_INSTRUMENTS",
            "company_equity_classification_proven": False,
            "horizon_days": list(horizons), "decisions": decisions,
            "adjusted_return_proven": False, "forecast_accuracy_proven": False,
            "orders_allowed": False}


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("folder", type=Path)
    parser.add_argument("--top-k", type=int, default=20)
    args = parser.parse_args()
    files = sorted((date.fromisoformat(p.name[:4] + "-" + p.name[4:6] + "-" + p.name[6:8]),
                    p.read_bytes()) for p in args.folder.glob("????????_cm_bhavcopy.csv"))
    print(json.dumps(replay(files, top_k=args.top_k), indent=2))


if __name__ == "__main__":
    main()
