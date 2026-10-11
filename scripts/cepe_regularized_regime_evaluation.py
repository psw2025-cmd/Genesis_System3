"""One-shot frozen Q2 replay for preregistered CEPE-NEXT-007.

The registry and implementation commit must exist before this script is run.
It retains both preregistered heads and the identical-universe comparator, uses
official-session/source guards, and never places an order.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import date, datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import random
from statistics import mean, median
from typing import Any

from scripts.cepe_chronological_evaluation import (
    distribution,
    pair_session_calendar,
    session_calendar,
    source_scope,
    split_pairs,
    verified,
)
from scripts.cepe_next_open_proof import compare
from scripts.cepe_regularized_regime_candidate import (
    FEATURE_ORDER,
    HEADS,
    SELECTION_COUNT,
    VERSION,
    _identity,
    rank,
)
from scripts.cepe_session_scope import require_session_alignment


TASK_ID = "CEPE-NEXT-007"


def _score(
    selected_items: list[dict[str, Any]],
    actual: dict[tuple[str, str, str, str], float],
) -> dict[str, Any]:
    selected = {_identity(item) for item in selected_items}
    values = [actual[key] for key in sorted(selected & actual.keys())]
    thresholds = {
        str(level): sum(value >= level for value in values)
        for level in (3, 10, 20, 30)
    }
    return {
        "selected": len(selected),
        "scoreable": len(values),
        "unscoreable": len(selected - actual.keys()),
        "positive": sum(value > 1 for value in values),
        "negative": sum(value < 1 for value in values),
        "unchanged": sum(value == 1 for value in values),
        "threshold_counts": thresholds,
        "directional_pct": (
            sum(value > 1 for value in values) / len(values) * 100
            if values else None
        ),
        "event_precision_pct": (
            thresholds["3"] / len(values) * 100 if values else None
        ),
        "gross_reference_mean_return_pct": (
            mean((value - 1) * 100 for value in values) if values else None
        ),
        "gross_reference_median_return_pct": (
            median((value - 1) * 100 for value in values) if values else None
        ),
        "stress_100bps_mean_return_pct": (
            mean((value - 1) * 100 - 1 for value in values) if values else None
        ),
        "reference_multiples": values,
    }


def _bootstrap(differences: list[float], seed: int) -> dict[str, Any]:
    if not differences:
        return {
            "paired_session_mean_excess_pct": None,
            "paired_session_bootstrap_95pct": None,
            "positive_excess_sessions": 0,
            "negative_excess_sessions": 0,
        }
    rng = random.Random(seed)
    draws = sorted(
        mean(rng.choices(differences, k=len(differences))) for _ in range(10000)
    )
    return {
        "paired_session_mean_excess_pct": mean(differences),
        "paired_session_bootstrap_95pct": [draws[249], draws[9749]],
        "positive_excess_sessions": sum(value > 0 for value in differences),
        "negative_excess_sessions": sum(value < 0 for value in differences),
        "bootstrap_seed": seed,
        "resamples": 10000,
    }


def run(
    folder: Path,
    calendar_path: Path,
    manifests: list[Path],
    registration_commit: str,
) -> dict[str, Any]:
    start, end = date(2026, 4, 1), date(2026, 6, 30)
    registry_path = Path("research/experiments/cepe_regularized_regime_v3.json")
    registry_raw = registry_path.read_bytes()
    registry = json.loads(registry_raw)
    if registry["status"] != "PREREGISTERED_BEFORE_FROZEN_Q2":
        raise ValueError("Registry is not frozen for Q2")
    if tuple(registry["feature_order"]) != FEATURE_ORDER:
        raise ValueError("Feature order differs from registry")
    if registry["frozen_heads"] != HEADS:
        raise ValueError("Frozen head coefficients differ from registry")
    if registry["selection_count_per_session"] != SELECTION_COUNT:
        raise ValueError("Selection count differs from registry")
    if not registration_commit or len(registration_commit) != 40:
        raise ValueError("Exact preregistration commit is required")

    sessions, calendar_receipt = session_calendar(calendar_path, start, end)
    scope = source_scope(
        folder,
        start,
        end,
        manifests,
        official_sessions=sessions,
        calendar_receipt=calendar_receipt,
    )
    pairs, gaps = split_pairs(
        list(folder.glob("????????_fo_bhavcopy.csv")), start, end, sessions
    )
    all_paths = {
        datetime.strptime(path.name[:8], "%Y%m%d").date(): path
        for path in folder.glob("????????_fo_bhavcopy.csv")
    }
    all_dates = sorted(all_paths)
    prior_for = {
        current: all_dates[index - 1]
        for index, current in enumerate(all_dates)
        if index and current in sessions
    }

    keys = ("directional", "rare_tail", "raw_momentum")
    samples = {key: [] for key in keys}
    totals = {key: Counter() for key in keys}
    threshold_totals = {key: Counter() for key in keys}
    daily: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    missingness = Counter()
    count_fields = ("selected", "scoreable", "unscoreable", "positive", "negative", "unchanged")

    for before, current_path, after, following_path in pairs:
        try:
            prior_day = prior_for[before]
            prior_path = all_paths[prior_day]
            prior = verified(prior_path)
            current = verified(current_path)
            following = verified(following_path)
            ranked = rank(prior, current, prior_day, before, after)
            pair_calendar = pair_session_calendar(
                before, after, sessions, calendar_receipt
            )
            comparison = compare(
                current,
                following,
                before,
                after,
                min_volume=1,
                min_previous_close=5,
                session_calendar=pair_calendar,
            )
            require_session_alignment(comparison)
            eligible = {_identity(item) for item in ranked["eligible"]}
            actual = {
                _identity(item): item["multiple"]
                for item in comparison["matches"]
                if _identity(item) in eligible
            }
            raw_momentum = sorted(
                ranked["eligible"],
                key=lambda item: (
                    -item["feature_percentiles"]["intraday_momentum"],
                    _identity(item),
                ),
            )[:SELECTION_COUNT]
            results = {
                "directional": _score(ranked["selected"]["directional"], actual),
                "rare_tail": _score(ranked["selected"]["rare_tail"], actual),
                "raw_momentum": _score(raw_momentum, actual),
            }
            for item in ranked["eligible"]:
                missingness.update(
                    field for field, absent in item["feature_missingness"].items()
                    if absent
                )
            for key in keys:
                samples[key].extend(results[key].pop("reference_multiples"))
                totals[key].update(
                    {field: results[key][field] for field in count_fields}
                )
                threshold_totals[key].update(results[key]["threshold_counts"])
            daily.append(
                {
                    "prior_day": prior_day.isoformat(),
                    "previous_day": before.isoformat(),
                    "following_day": after.isoformat(),
                    "prior_sha256": ranked["prior_sha256"],
                    "previous_sha256": ranked["current_sha256"],
                    "following_sha256": comparison["following_sha256"],
                    "calendar_sha256": comparison["session_calendar_sha256"],
                    "eligible": len(eligible),
                    **results,
                }
            )
        except (KeyError, OSError, ValueError) as exc:
            errors.append(
                {
                    "previous_day": before.isoformat(),
                    "following_day": after.isoformat(),
                    "error": str(exc),
                    "status": "EXCLUDED_SOURCE_OR_IDENTITY_ERROR",
                }
            )

    summary: dict[str, Any] = {}
    for key, values in samples.items():
        summary[key] = {
            **dict(totals[key]),
            "threshold_counts": dict(threshold_totals[key]),
            "distribution": distribution(values),
            "directional_pct": (
                sum(value > 1 for value in values) / len(values) * 100
                if values else None
            ),
            "event_precision_pct": (
                sum(value >= 3 for value in values) / len(values) * 100
                if values else None
            ),
            "gross_reference_mean_return_pct": (
                mean((value - 1) * 100 for value in values) if values else None
            ),
            "gross_reference_median_return_pct": (
                median((value - 1) * 100 for value in values) if values else None
            ),
            "stress_100bps_mean_return_pct": (
                mean((value - 1) * 100 - 1 for value in values)
                if values else None
            ),
        }

    uncertainty = {}
    for offset, head in enumerate(("directional", "rare_tail")):
        differences = [
            item[head]["gross_reference_mean_return_pct"]
            - item["raw_momentum"]["gross_reference_mean_return_pct"]
            for item in daily
            if item[head]["scoreable"] and item["raw_momentum"]["scoreable"]
        ]
        uncertainty[head] = _bootstrap(differences, 20260930 + offset)

    official_sessions = calendar_receipt["session_dates"]
    direction = summary["directional"]
    tail = summary["rare_tail"]
    comparator = summary["raw_momentum"]
    directional_checks = {
        "minimum_100_scoreable": direction.get("scoreable", 0) >= 100,
        "minimum_60_official_sessions": official_sessions >= 60,
        "directional_at_least_65pct": (direction.get("directional_pct") or 0) >= 65,
        "positive_median": (direction.get("gross_reference_median_return_pct") or 0) > 0,
        "positive_paired_mean_excess": (
            (uncertainty["directional"]["paired_session_mean_excess_pct"] or 0) > 0
        ),
        "zero_source_or_identity_errors": not errors,
    }
    tail_checks = {
        "minimum_100_scoreable": tail.get("scoreable", 0) >= 100,
        "minimum_60_official_sessions": official_sessions >= 60,
        "event_precision_above_raw_momentum": (
            (tail.get("event_precision_pct") or 0)
            > (comparator.get("event_precision_pct") or 0)
        ),
        "positive_paired_mean_excess": (
            (uncertainty["rare_tail"]["paired_session_mean_excess_pct"] or 0) > 0
        ),
        "zero_source_or_identity_errors": not errors,
    }
    return {
        "task_id": TASK_ID,
        "version": VERSION,
        "phase": "frozen_retrospective_test",
        "start": start.isoformat(),
        "end": end.isoformat(),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "registration_commit": registration_commit,
        "registry_sha256": sha256(registry_raw).hexdigest(),
        "evaluated_session_pairs": len(daily),
        "official_sessions": official_sessions,
        "source_scope": scope,
        "skipped_calendar_gaps": gaps,
        "excluded_errors": errors,
        "feature_missingness": dict(missingness),
        "summary": summary,
        "uncertainty": uncertainty,
        "daily": daily,
        "directional_research_success_checks": directional_checks,
        "rare_tail_research_success_checks": tail_checks,
        "directional_research_success": all(directional_checks.values()),
        "rare_tail_research_success": all(tail_checks.values()),
        "familywise_alpha": 0.05,
        "per_head_alpha_bonferroni": 0.025,
        "retuning_allowed": False,
        "forward_predictions": 0,
        "forward_outcomes": 0,
        "opening_fill_proven": False,
        "actual_cost_net_performance": "NOT_PROVEN",
        "project_sharpe": "NOT_PROVEN",
        "project_max_drawdown": "NOT_PROVEN",
        "project_deflated_sharpe": "NOT_PROVEN",
        "orders_allowed": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("folder", type=Path)
    parser.add_argument("calendar", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--source-manifest", type=Path, action="append", required=True)
    parser.add_argument("--registration-commit", required=True)
    args = parser.parse_args()
    result = run(
        args.folder,
        args.calendar,
        args.source_manifest,
        args.registration_commit,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(
        json.dumps(
            {
                key: value
                for key, value in result.items()
                if key not in {"daily", "skipped_calendar_gaps"}
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
