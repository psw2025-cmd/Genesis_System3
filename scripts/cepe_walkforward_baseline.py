"""Walk-forward CE/PE baseline over a directory of dated F&O CSV snapshots.

Research-only fixed rule: rank prior-day close/open momentum, select top K
eligible prior-day contracts, then score next-open outcomes. Retrospective
volume filters in compare() define the scoreable population and should not
be interpreted as knowable at issuance. No same-day outcome enters selection.

Usage: python -m scripts.cepe_walkforward_baseline /data/fo --top-k 100
Files: YYYYMMDD_fo_bhavcopy.csv. The final adjacent pair is the holdout.
"""
from __future__ import annotations

import argparse
from datetime import date
from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from scripts.cepe_next_open_proof import _rows, compare


def run(files: list[tuple[date, bytes]], *, top_k: int = 100,
        target_multiple: float = 3, min_volume: float = 100,
        min_close: float = 1) -> dict[str, Any]:
    if top_k <= 0 or len(files) < 2:
        raise ValueError("Need positive top_k and at least two dated snapshots")
    if [day for day, _ in files] != sorted({day for day, _ in files}):
        raise ValueError("Snapshot dates must be unique and sorted")
    output = []
    for (day, raw), (next_day, subsequent) in zip(files, files[1:]):
        if (next_day - day).days > 5:
            # Don't imply a missing market day is an adjacent session.
            raise ValueError("Gap exceeds five days: confirm intervening sessions")
        prior = _rows(raw, day)
        observed = compare(raw, subsequent, day, next_day, min_volume=min_volume,
                           min_previous_close=min_close)
        ranked = sorted(
            ((prices["close"] / prices["open"], key) for key, prices in prior.items()
             if prices["open"] > 0 and prices["close"] >= min_close
             and prices["volume"] >= min_volume),
            key=lambda item: (-item[0], item[1])
        )
        selected = {key for _, key in ranked[:top_k]}
        selected_digest = sha256(json.dumps(sorted(selected), separators=(",", ":")).encode()).hexdigest()
        actual = {(row["symbol"], row["expiry"], row["strike"], row["type"]): row
                  for row in observed["matches"]}
        hits = sum(actual[key]["multiple"] >= target_multiple
                   for key in selected & actual.keys())
        winners = sum(row["multiple"] >= target_multiple for row in actual.values())
        output.append({
            "previous_day": day.isoformat(), "next_day": next_day.isoformat(),
            "previous_sha256": sha256(raw).hexdigest(),
            "following_sha256": sha256(subsequent).hexdigest(),
            "selected": len(selected), "selected_keys_sha256": selected_digest, "scorable_selected": len(selected & actual.keys()),
            "unscorable_selected": len(selected - actual.keys()),
            "matched_contracts": len(actual), "winners": winners, "hits": hits,
            "false_picks": len(selected & actual.keys()) - hits,
            "missed_winners": winners - hits,
            "precision_scorable": hits / len(selected & actual.keys())
                if selected & actual.keys() else None,
            "recall": hits / winners if winners else None,
            "data_scope": "CACHED_SOURCE_UNVERIFIED",
        })
    holdout = output[-1]
    return {
        "rule": "PRIOR_DAY_CLOSE_DIVIDED_BY_OPEN_TOP_K",
        "top_k": top_k, "target_multiple": target_multiple,
        "train_pairs": output[:-1], "holdout_pair": holdout,
        "holdout_hits": holdout["hits"], "holdout_winners": holdout["winners"],
        "holdout_precision_scorable": holdout["precision_scorable"],
        "forward_issued_predictions": 0, "orders_allowed": False,
        "warning": "Historical proxy. No independent advance issuance, official source recheck, execution costs or opening fill proof.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("folder", type=Path)
    parser.add_argument("--top-k", type=int, default=100)
    parser.add_argument("--target-multiple", type=float, default=3)
    args = parser.parse_args()
    files = sorted((date.fromisoformat(p.name[:4] + "-" + p.name[4:6] + "-" + p.name[6:8]),
                    p.read_bytes()) for p in args.folder.glob("????????_fo_bhavcopy.csv"))
    print(json.dumps(run(files, top_k=args.top_k, target_multiple=args.target_multiple),
                     indent=2))


if __name__ == "__main__":
    main()
