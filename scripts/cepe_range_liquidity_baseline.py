"""Frozen CEPE-NEXT-005 candidate ranking; no forward forecast or fill claim."""
from __future__ import annotations

from collections import Counter
import csv
from datetime import date
from hashlib import sha256
from io import StringIO
from math import isfinite
from statistics import mean
from typing import Any

from scripts.cepe_forward_scorecard import _identity
from scripts.cepe_next_open_proof import _rows, compare
from scripts.cepe_session_scope import require_session_alignment

VERSION = "range-liquidity-v1"


def rank(previous: bytes, previous_day: date, following_day: date) -> dict[str, Any]:
    """Rank only prior snapshot fields using the pre-registered fixed rule."""
    if following_day <= previous_day:
        raise ValueError("Following day must follow previous day")
    # Validate exact identities, duplicates and dated observations before ranking.
    _rows(previous, previous_day)
    source_hash = sha256(previous).hexdigest()
    eligible, rejected = [], Counter()
    for row in csv.DictReader(StringIO(previous.decode("utf-8-sig"))):
        if row.get("OptnTp") not in {"CE", "PE"}:
            continue
        if date.fromisoformat(row["XpryDt"]) < following_day:
            rejected["EXPIRED_BEFORE_OUTCOME"] += 1
            continue
        try:
            opening, close, high, low, volume, oi = (
                float(row[name]) for name in
                ("OpnPric", "ClsPric", "HghPric", "LwPric", "TtlTradgVol", "OpnIntrst")
            )
            if not all(isfinite(x) for x in (opening, close, high, low, volume, oi)):
                raise ValueError("Nonfinite field")
        except (KeyError, TypeError, ValueError):
            rejected["MISSING_OR_INVALID_FEATURE"] += 1
            continue
        if not (opening > 0 and high > low >= 0 and low <= opening <= high and low <= close <= high):
            rejected["INVALID_PRICE_RANGE"] += 1
            continue
        if close < 5 or volume < 1000 or oi <= 0:
            rejected["PRIOR_PRICE_VOLUME_OI_FILTER"] += 1
            continue
        key = _identity(dict(symbol=row["TckrSymb"], expiry=row["XpryDt"],
                             strike=row["StrkPric"], type=row["OptnTp"]))
        eligible.append(dict(symbol=key[0], expiry=key[1], strike=key[2], type=key[3],
                             feature=(close-opening)/(high-low), prior_momentum=close/opening,
                             previous_close=close, prior_volume=volume, prior_open_interest=oi))
    eligible.sort(key=lambda item: (-item["feature"], _identity(item)))
    size = len(eligible) // 10
    selected = eligible[:size]
    return dict(version=VERSION, previous_day=previous_day.isoformat(),
                following_day=following_day.isoformat(), source_sha256=source_hash,
                eligible=eligible, selected=selected, rejected=dict(rejected),
                feature_status="RESEARCH_CANDIDATE_NOT_PROVEN", expected_multiple=None,
                expected_range=None, forward_issued=False, orders_allowed=False)


def evaluate(previous: bytes, following: bytes, previous_day: date, following_day: date,
             *, session_calendar: bytes | None = None) -> dict[str, Any]:
    """Retrospective comparison on the same prior-qualified population."""
    ranking = rank(previous, previous_day, following_day)
    comparison = compare(previous, following, previous_day, following_day,
                         min_volume=1, min_previous_close=5, session_calendar=session_calendar)
    require_session_alignment(comparison)
    eligible = {_identity(item) for item in ranking["eligible"]}
    actual = {_identity(row): row["multiple"] for row in comparison["matches"]
              if _identity(row) in eligible}

    def score(items):
        selected = {_identity(item) for item in items}
        multiples = [actual[key] for key in sorted(selected & actual.keys())]
        hits = sum(x >= 3 for x in multiples)
        return dict(selected=len(selected), scoreable=len(multiples),
                    unscoreable=len(selected-actual.keys()), hits=hits,
                    false_picks=len(multiples)-hits,
                    missed_events=sum(x >= 3 for key, x in actual.items() if key not in selected),
                    positive_returns=sum(x > 1 for x in multiples),
                    negative_returns=sum(x < 1 for x in multiples),
                    unchanged_returns=sum(x == 1 for x in multiples),
                    event_precision=hits/len(multiples) if multiples else None,
                    reference_multiples=multiples,
                    gross_reference_mean_return_pct=mean((x-1)*100 for x in multiples) if multiples else None,
                    assumed_cost_stress_mean_return_pct={str(bps):
                        mean((x-1)*100-bps/100 for x in multiples) if multiples else None
                        for bps in (0, 25, 50, 100)})

    momentum = sorted(ranking["eligible"], key=lambda item: (-item["prior_momentum"], _identity(item)))
    return dict(version=VERSION, previous_day=previous_day.isoformat(), following_day=following_day.isoformat(),
                previous_sha256=ranking["source_sha256"], following_sha256=comparison["following_sha256"],
                session_alignment_status=comparison["session_alignment_status"],
                eligible_prior_contracts=len(eligible), matched_eligible_contracts=len(actual),
                rejected=ranking["rejected"], variant=score(ranking["selected"]),
                same_universe_momentum=score(momentum[:len(eligible)//10]),
                uncapped_eligible_multiples=sorted(actual.values()),
                threshold_counts={str(n):sum(x >= n for x in actual.values()) for n in (3,10,20,30)},
                status="RETROSPECTIVE_REFERENCE_ONLY", expected_range=None,
                source_availability_at_issue="NOT_PROVEN", cost_and_fill_proof="NOT_PROVEN",
                forward_issued_predictions=0, orders_allowed=False)
