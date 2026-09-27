"""Chronological evaluation for preregistered CEPE-NEXT-006.

This reuses the exact source, manifest and official-session guards from
CEPE-NEXT-005 while keeping the new candidate and comparator outputs separate.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import date, datetime, timezone
import json
from pathlib import Path
import random
from statistics import mean

from scripts.cepe_chronological_evaluation import (
    distribution,
    pair_session_calendar,
    session_calendar,
    source_scope,
    split_pairs,
    verified,
)
from scripts.cepe_event_liquidity_candidate import evaluate


REGISTRATION_COMMIT = "d706c3c34ce25cd0193abe24808587f31219a4d6"
VERSION = "event-liquidity-expiry-v2"


def run(
    folder: Path,
    start: date,
    end: date,
    phase: str,
    *,
    source_manifest: Path | list[Path] | None = None,
    session_calendar_path: Path | None = None,
    implementation_commit: str | None = None,
) -> dict:
    sessions, calendar_receipt = None, None
    if session_calendar_path is not None:
        sessions, calendar_receipt = session_calendar(session_calendar_path, start, end)
    scope = source_scope(
        folder,
        start,
        end,
        source_manifest,
        official_sessions=sessions,
        calendar_receipt=calendar_receipt,
    )
    pairs, gaps = split_pairs(
        list(folder.glob("????????_fo_bhavcopy.csv")), start, end, sessions
    )
    daily, errors, population = [], [], []
    supplied_pair_calendars = 0
    sample_keys = ("variant", "same_universe_raw_momentum")
    samples = {key: [] for key in sample_keys}
    counts = {key: Counter() for key in sample_keys}
    thresholds = {key: Counter() for key in sample_keys}
    rejected = Counter()
    count_keys = (
        "selected",
        "scoreable",
        "unscoreable",
        "hits",
        "false_picks",
        "missed_events",
        "positive_returns",
        "negative_returns",
        "unchanged_returns",
    )
    for index, (before, previous_path, after, following_path) in enumerate(pairs):
        try:
            pair_calendar = (
                pair_session_calendar(before, after, sessions, calendar_receipt)
                if sessions is not None and calendar_receipt is not None
                else None
            )
            if pair_calendar is not None:
                supplied_pair_calendars += 1
            result = evaluate(
                verified(previous_path),
                verified(following_path),
                before,
                after,
                session_calendar=pair_calendar,
            )
        except (ValueError, KeyError, OSError) as exc:
            errors.append(
                {
                    "previous_day": before.isoformat(),
                    "following_day": after.isoformat(),
                    "error": str(exc),
                    "status": "EXCLUDED_SOURCE_OR_IDENTITY_ERROR",
                }
            )
            continue
        population.extend(result["uncapped_eligible_multiples"])
        result["population_distribution"] = distribution(
            result.pop("uncapped_eligible_multiples")
        )
        rejected.update(result["rejected"])
        for key in sample_keys:
            samples[key].extend(result[key].pop("reference_multiples"))
            counts[key].update({name: result[key][name] for name in count_keys})
            thresholds[key].update(result[key]["threshold_counts"])
        daily.append(result)
        if (index + 1) % 20 == 0:
            print(
                json.dumps({"phase": phase, "evaluated": index + 1, "pairs": len(pairs)}),
                flush=True,
            )

    summary = {}
    for key, values in samples.items():
        size = len(values)
        direction = sum(value > 1 for value in values) / size * 100 if size else None
        precision = sum(value >= 3 for value in values) / size * 100 if size else None
        summary[key] = {
            **dict(counts[key]),
            "threshold_counts": dict(thresholds[key]),
            "distribution": distribution(values),
            "gross_reference_mean_return_pct": (
                mean((value - 1) * 100 for value in values) if size else None
            ),
            "assumed_cost_stress_mean_return_pct": {
                str(bps): (
                    mean((value - 1) * 100 - bps / 100 for value in values)
                    if size else None
                )
                for bps in (0, 25, 50, 100)
            },
            "raw_reference_directional_hit_pct": direction,
            "raw_3x_event_precision_pct": precision,
            "reference_gap_to_65pct_directional_gate": (
                None if direction is None else 65 - direction
            ),
            "reference_gap_to_70pct_3x_precision_gate": (
                None if precision is None else 70 - precision
            ),
        }

    differences = [
        item["variant"]["gross_reference_mean_return_pct"]
        - item["same_universe_raw_momentum"]["gross_reference_mean_return_pct"]
        for item in daily
        if item["variant"]["scoreable"]
        and item["same_universe_raw_momentum"]["scoreable"]
    ]
    rng = random.Random(20260928)
    boot = (
        sorted(mean(rng.choices(differences, k=len(differences))) for _ in range(10000))
        if differences
        else []
    )
    interval = [boot[249], boot[9749]] if boot else None
    uncertainty = {
        "paired_session_mean_excess_pct": mean(differences) if differences else None,
        "paired_day_bootstrap_95pct_interval": interval,
        "positive_excess_days": sum(value > 0 for value in differences),
        "negative_excess_days": sum(value < 0 for value in differences),
        "bootstrap_seed": 20260928,
        "resamples": 10000,
        "limitations": "Day bootstrap does not correct serial dependence. Contract observations are not independent; gross opens are not fills.",
    }
    official_session_count = (
        scope.get("session_calendar", {}).get("session_dates", 0)
        if isinstance(scope.get("session_calendar"), dict)
        else 0
    )
    promotion_checks = {
        "positive_mean_excess": bool(differences and mean(differences) > 0),
        "bootstrap_lower_bound_above_zero": bool(interval and interval[0] > 0),
        "minimum_100_scoreable": summary["variant"].get("scoreable", 0) >= 100,
        "minimum_60_official_sessions": official_session_count >= 60,
        "zero_source_or_identity_errors": not errors,
    }
    validation_promoted = phase == "validation" and all(promotion_checks.values())
    if phase == "validation":
        status = (
            "VALIDATION_PROMOTED_TO_FROZEN_TEST"
            if validation_promoted
            else "VALIDATION_REJECTED_NO_FROZEN_TEST_ACCESS"
        )
    else:
        status = "RETROSPECTIVE_DEVELOPMENT_REFERENCE_ONLY"
    return {
        "task_id": "CEPE-NEXT-006",
        "version": VERSION,
        "phase": phase,
        "start": start.isoformat(),
        "end": end.isoformat(),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "registration_commit": REGISTRATION_COMMIT,
        "strategy_implementation_commit": implementation_commit,
        "evaluated_session_pairs": len(daily),
        "official_sessions": official_session_count,
        "supplied_pair_calendars": supplied_pair_calendars,
        "source_scope": scope,
        "skipped_calendar_gaps": gaps,
        "excluded_errors": errors,
        "rejected_feature_rows": dict(rejected),
        "feature_availability": {
            "archived_bhavcopy_features": "MEASURED",
            "implied_volatility_rows": 0,
            "greeks_rows": 0,
            "missing_iv_or_greeks_action": "EXCLUDED_FROM_SCORE_NOT_IMPUTED",
        },
        "summary": summary,
        "uncertainty": uncertainty,
        "population_distribution": distribution(population),
        "daily": daily,
        "validation_promotion_checks": promotion_checks,
        "validation_promoted": validation_promoted,
        "frozen_test_opened": False,
        "multiple_precision": "Six decimal reference multiples; no capping",
        "negative_forecasts_issued": 0,
        "forward_predictions": 0,
        "forward_outcomes": 0,
        "calibrated_expected_range": None,
        "source_availability_at_historical_issue": "NOT_PROVEN",
        "executable_cost_net_performance": "NOT_PROVEN",
        "project_qualified_oos_trades": 0,
        "project_qualified_oos_days": 0,
        "gap_to_100_qualified_oos_trades": 100,
        "gap_to_60_qualified_oos_days": 60,
        "project_sharpe": "NOT_PROVEN",
        "project_max_drawdown": "NOT_PROVEN",
        "project_deflated_sharpe": "NOT_PROVEN",
        "numeric_reference_metrics_are_project_gate_pass": False,
        "catalyst_ablation": "NO_CATALYST_BASELINE_ONLY",
        "orders_allowed": False,
        "status": status,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("folder", type=Path)
    parser.add_argument("phase", choices=["development", "validation"])
    parser.add_argument("output", type=Path)
    parser.add_argument("--source-manifest", type=Path, action="append")
    parser.add_argument("--session-calendar", type=Path, required=True)
    parser.add_argument("--implementation-commit")
    args = parser.parse_args()
    registry = json.loads(
        Path("research/experiments/cepe_event_liquidity_v2.json").read_text()
    )
    start, end = map(date.fromisoformat, registry["data_plan"][args.phase])
    result = run(
        args.folder,
        start,
        end,
        args.phase,
        source_manifest=args.source_manifest,
        session_calendar_path=args.session_calendar,
        implementation_commit=args.implementation_commit,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(
        json.dumps(
            {key: value for key, value in result.items() if key not in {"daily", "skipped_calendar_gaps"}},
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
