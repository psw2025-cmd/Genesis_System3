"""Fail-closed quantitative research evaluation for Genesis System3.

AlphaTruth is an evaluation authority, not a trading engine.  It accepts a
versioned evidence bundle produced by an isolated research/backtest job and
answers one question: is there enough clean out-of-sample evidence to call the
candidate a *research* candidate?

It never places orders, never enables LIVE trading and never promotes a model
into a broker execution path.  Missing provenance, leakage controls, benchmark
alignment, sample size or required metrics fail closed.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import statistics
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Iterable, Mapping, Sequence

_GIT_SHA_RE = re.compile(r"^[0-9a-f]{40}$", re.IGNORECASE)
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$", re.IGNORECASE)


@dataclass(frozen=True)
class AlphaTargets:
    """System3 research acceptance targets.

    These are project goals supplied by the user.  They are not statements
    about current model performance.
    """

    min_oos_directional_accuracy_pct: float = 65.0
    min_top_decile_precision_pct: float = 70.0
    min_sharpe: float = 2.5
    min_sortino: float = 3.5
    max_drawdown_pct: float = 10.0
    min_win_loss_ratio: float = 2.0
    max_is_oos_accuracy_gap_pct_points: float = 15.0
    min_oos_trades: int = 100
    min_oos_days: int = 60
    top_fraction: float = 0.10
    periods_per_year: int = 252
    min_deflated_sharpe_probability: float = 0.95


@dataclass(frozen=True)
class Gate:
    name: str
    passed: bool
    actual: Any
    target: Any
    reason: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def _float(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _parse_time(value: Any) -> datetime | None:
    if not value:
        return None
    text = str(value).strip().replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def _same_sign(predicted_direction: float, actual_return: float) -> bool:
    if predicted_direction == 0 or actual_return == 0:
        return False
    return (predicted_direction > 0 and actual_return > 0) or (
        predicted_direction < 0 and actual_return < 0
    )


def directional_accuracy(observations: Sequence[Mapping[str, Any]]) -> float | None:
    rows: list[tuple[float, float]] = []
    for row in observations:
        pred = _float(row.get("predicted_direction"))
        actual = _float(row.get("actual_return"))
        if pred is None or actual is None:
            continue
        rows.append((pred, actual))
    if not rows:
        return None
    return 100.0 * sum(_same_sign(pred, actual) for pred, actual in rows) / len(rows)


def precision_at_top_fraction(
    observations: Sequence[Mapping[str, Any]], fraction: float
) -> tuple[float | None, int]:
    """Return directional precision among the highest-confidence signals.

    `confidence` must be a non-negative score where larger means the model was
    more confident.  Precision is defined here as the fraction of selected
    signals whose predicted direction matched the sign of the realized return.
    """
    rows: list[tuple[float, float, float]] = []
    for row in observations:
        confidence = _float(row.get("confidence"))
        pred = _float(row.get("predicted_direction"))
        actual = _float(row.get("actual_return"))
        if confidence is None or pred is None or actual is None:
            continue
        rows.append((confidence, pred, actual))
    if not rows or fraction <= 0 or fraction > 1:
        return None, 0
    rows.sort(key=lambda item: item[0], reverse=True)
    k = max(1, math.ceil(len(rows) * fraction))
    selected = rows[:k]
    precision = 100.0 * sum(_same_sign(pred, actual) for _, pred, actual in selected) / k
    return precision, k


def _clean_returns(values: Iterable[Any]) -> list[float]:
    result: list[float] = []
    for value in values:
        number = _float(value)
        if number is not None and number > -1.0:
            result.append(number)
    return result


def annualized_sharpe(returns: Sequence[float], periods_per_year: int) -> float | None:
    if len(returns) < 2:
        return None
    std = statistics.pstdev(returns)
    if std <= 0:
        return None
    return statistics.fmean(returns) / std * math.sqrt(periods_per_year)


def annualized_sortino(returns: Sequence[float], periods_per_year: int) -> float | None:
    if len(returns) < 2:
        return None
    downside = [min(0.0, value) for value in returns]
    downside_deviation = math.sqrt(sum(value * value for value in downside) / len(downside))
    if downside_deviation <= 0:
        return None
    return statistics.fmean(returns) / downside_deviation * math.sqrt(periods_per_year)


def compounded_return(returns: Sequence[float]) -> float | None:
    if not returns:
        return None
    equity = 1.0
    for value in returns:
        equity *= 1.0 + value
    return equity - 1.0


def maximum_drawdown_pct(returns: Sequence[float]) -> float | None:
    if not returns:
        return None
    equity = 1.0
    peak = 1.0
    worst = 0.0
    for value in returns:
        equity *= 1.0 + value
        peak = max(peak, equity)
        if peak > 0:
            worst = max(worst, (peak - equity) / peak)
    return 100.0 * worst


def trade_statistics(pnl_values: Iterable[Any]) -> dict[str, float | int | None]:
    pnl = [number for value in pnl_values if (number := _float(value)) is not None]
    wins = [value for value in pnl if value > 0]
    losses = [value for value in pnl if value < 0]
    avg_win = statistics.fmean(wins) if wins else None
    avg_loss_abs = abs(statistics.fmean(losses)) if losses else None
    win_loss_ratio = (
        avg_win / avg_loss_abs
        if avg_win is not None and avg_loss_abs is not None and avg_loss_abs > 0
        else None
    )
    gross_profit = sum(wins)
    gross_loss = abs(sum(losses))
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else None
    return {
        "trade_count": len(pnl),
        "win_count": len(wins),
        "loss_count": len(losses),
        "win_rate_pct": (100.0 * len(wins) / len(pnl)) if pnl else None,
        "avg_win": avg_win,
        "avg_loss_abs": avg_loss_abs,
        "win_loss_ratio": win_loss_ratio,
        "profit_factor": profit_factor,
        "net_pnl": sum(pnl),
    }


def _provenance_blockers(manifest: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    if not _GIT_SHA_RE.fullmatch(str(manifest.get("source_sha") or "")):
        blockers.append("source_sha_missing_or_invalid")
    for key in ("data_manifest_sha256", "feature_schema_sha256", "model_artifact_sha256"):
        if not _SHA256_RE.fullmatch(str(manifest.get(key) or "")):
            blockers.append(f"{key}_missing_or_invalid")
    if not str(manifest.get("evidence_id") or "").strip():
        blockers.append("evidence_id_missing")
    if manifest.get("data_provenance_verified") is not True:
        blockers.append("data_provenance_not_verified")
    return blockers


def _leakage_blockers(manifest: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    if manifest.get("is_out_of_sample") is not True:
        blockers.append("test_not_declared_out_of_sample")
    if manifest.get("test_is_frozen") is not True:
        blockers.append("frozen_holdout_not_enforced")
    if manifest.get("tuned_on_frozen_holdout") is not False:
        blockers.append("frozen_holdout_tuning_not_explicitly_false")
    if manifest.get("target_leakage_checks_passed") is not True:
        blockers.append("target_leakage_checks_not_proven")
    if manifest.get("feature_scaling_fit_on_train_only") is not True:
        blockers.append("train_only_feature_fit_not_proven")

    train_end = _parse_time(manifest.get("train_end"))
    validation_start = _parse_time(manifest.get("validation_start"))
    validation_end = _parse_time(manifest.get("validation_end"))
    test_start = _parse_time(manifest.get("test_start"))
    test_end = _parse_time(manifest.get("test_end"))
    if not all((train_end, validation_start, validation_end, test_start, test_end)):
        blockers.append("chronological_split_timestamps_incomplete")
    elif not (train_end < validation_start <= validation_end < test_start <= test_end):
        blockers.append("chronological_split_overlap_or_order_error")

    horizon = int(manifest.get("label_horizon_bars") or 0)
    purge_gap = int(manifest.get("purge_gap_bars") or 0)
    if horizon <= 0:
        blockers.append("label_horizon_not_declared")
    if purge_gap < horizon:
        blockers.append("purge_gap_shorter_than_label_horizon")
    return blockers


def _gate(name: str, actual: Any, target: Any, passed: bool, reason: str) -> Gate:
    return Gate(name=name, passed=bool(passed), actual=actual, target=target, reason=reason)


def _metric_gate(
    name: str,
    actual: float | None,
    target: float,
    *,
    comparison: str,
) -> Gate:
    if actual is None:
        return _gate(name, None, target, False, "metric_unavailable")
    if comparison == ">":
        passed = actual > target
    elif comparison == ">=":
        passed = actual >= target
    elif comparison == "<=":
        passed = actual <= target
    else:
        raise ValueError(f"unsupported comparison: {comparison}")
    return _gate(name, round(actual, 6), target, passed, f"required {comparison} {target}")


def evaluate_alpha_evidence(
    evidence: Mapping[str, Any], targets: AlphaTargets | None = None
) -> dict[str, Any]:
    """Evaluate an AlphaTruth evidence bundle.

    A PROVEN result means the supplied *research evidence* meets the configured
    thresholds.  It never means LIVE trading is authorized.
    """
    targets = targets or AlphaTargets()
    manifest = evidence.get("manifest") if isinstance(evidence.get("manifest"), Mapping) else {}
    observations = evidence.get("observations") if isinstance(evidence.get("observations"), list) else []
    daily_returns = _clean_returns(evidence.get("daily_net_returns") or [])
    benchmark_returns = _clean_returns(evidence.get("benchmark_daily_returns") or [])
    trade_pnl = evidence.get("trade_net_pnl") if isinstance(evidence.get("trade_net_pnl"), list) else []

    provenance_blockers = _provenance_blockers(manifest)
    leakage_blockers = _leakage_blockers(manifest)
    blockers = list(provenance_blockers) + list(leakage_blockers)

    accuracy = directional_accuracy(observations)
    top_precision, top_k = precision_at_top_fraction(observations, targets.top_fraction)
    sharpe = annualized_sharpe(daily_returns, targets.periods_per_year)
    sortino = annualized_sortino(daily_returns, targets.periods_per_year)
    max_dd = maximum_drawdown_pct(daily_returns)
    total_return = compounded_return(daily_returns)
    benchmark_return = compounded_return(benchmark_returns)
    stats = trade_statistics(trade_pnl)

    in_sample_accuracy = _float(evidence.get("in_sample_directional_accuracy_pct"))
    is_oos_gap = (
        abs(in_sample_accuracy - accuracy)
        if in_sample_accuracy is not None and accuracy is not None
        else None
    )

    oos_days = int(evidence.get("oos_days") or len(daily_returns))
    trade_count = int(stats["trade_count"] or 0)
    observation_count = len(observations)

    if observation_count < targets.min_oos_trades:
        blockers.append(
            f"insufficient_oos_observations:{observation_count}<{targets.min_oos_trades}"
        )
    if trade_count < targets.min_oos_trades:
        blockers.append(f"insufficient_oos_trades:{trade_count}<{targets.min_oos_trades}")
    if oos_days < targets.min_oos_days:
        blockers.append(f"insufficient_oos_days:{oos_days}<{targets.min_oos_days}")
    if len(daily_returns) != oos_days:
        blockers.append("oos_day_count_does_not_match_daily_return_count")
    if len(benchmark_returns) != len(daily_returns) or not daily_returns:
        blockers.append("benchmark_returns_not_aligned_with_oos_returns")
    if manifest.get("benchmark_aligned") is not True:
        blockers.append("benchmark_alignment_not_proven")
    if not str(manifest.get("benchmark_name") or "").strip():
        blockers.append("benchmark_name_missing")

    gates: list[Gate] = [
        _metric_gate(
            "oos_directional_accuracy_pct",
            accuracy,
            targets.min_oos_directional_accuracy_pct,
            comparison=">",
        ),
        _metric_gate(
            "top_decile_precision_pct",
            top_precision,
            targets.min_top_decile_precision_pct,
            comparison=">",
        ),
        _metric_gate("annualized_sharpe", sharpe, targets.min_sharpe, comparison=">="),
        _metric_gate("annualized_sortino", sortino, targets.min_sortino, comparison=">="),
        _metric_gate(
            "max_drawdown_pct", max_dd, targets.max_drawdown_pct, comparison="<="
        ),
        _metric_gate(
            "win_loss_ratio",
            _float(stats.get("win_loss_ratio")),
            targets.min_win_loss_ratio,
            comparison=">",
        ),
        _metric_gate(
            "is_oos_accuracy_gap_pct_points",
            is_oos_gap,
            targets.max_is_oos_accuracy_gap_pct_points,
            comparison="<=",
        ),
    ]

    benchmark_gate_pass = (
        total_return is not None
        and benchmark_return is not None
        and total_return > benchmark_return
    )
    gates.append(
        _gate(
            "benchmark_outperformance",
            {
                "candidate_total_return_pct": None
                if total_return is None
                else round(total_return * 100.0, 6),
                "benchmark_total_return_pct": None
                if benchmark_return is None
                else round(benchmark_return * 100.0, 6),
            },
            "candidate_total_return > aligned benchmark_total_return",
            benchmark_gate_pass,
            "same-window compounded net return after costs",
        )
    )

    strategy_trials = int(manifest.get("strategy_trials") or 0)
    dsr_probability = _float((evidence.get("selection_bias") or {}).get("deflated_sharpe_probability"))
    if strategy_trials <= 0:
        blockers.append("strategy_trial_count_missing")
        selection_gate = _gate(
            "selection_bias_control", None, "strategy_trials >= 1", False, "trial count not recorded"
        )
    elif strategy_trials == 1:
        selection_gate = _gate(
            "selection_bias_control",
            {"strategy_trials": 1, "deflated_sharpe_probability": dsr_probability},
            "trial count recorded; DSR required when trials > 1",
            True,
            "single declared strategy trial",
        )
    else:
        selection_gate = _metric_gate(
            "deflated_sharpe_probability",
            dsr_probability,
            targets.min_deflated_sharpe_probability,
            comparison=">=",
        )
        if dsr_probability is None:
            blockers.append("multiple_testing_adjustment_missing")
    gates.append(selection_gate)

    failed_gates = [gate.name for gate in gates if not gate.passed]
    blockers.extend(f"target_gate_failed:{name}" for name in failed_gates)
    blockers = sorted(set(blockers))

    has_schema_or_provenance_error = bool(provenance_blockers)
    has_leakage_error = bool(leakage_blockers)
    insufficient = any(item.startswith("insufficient_") for item in blockers)
    if has_schema_or_provenance_error:
        state = "SCHEMA_ERROR"
    elif has_leakage_error:
        state = "LEAKAGE_BLOCKED"
    elif insufficient:
        state = "INSUFFICIENT_EVIDENCE"
    elif failed_gates or blockers:
        state = "TARGET_FAIL"
    else:
        state = "PROVEN"

    canonical_evidence = json.dumps(evidence, sort_keys=True, separators=(",", ":"), default=str).encode()
    evidence_sha256 = hashlib.sha256(canonical_evidence).hexdigest()

    return {
        "schema_version": 1,
        "state": state,
        "evidence_id": manifest.get("evidence_id"),
        "evidence_sha256": evidence_sha256,
        "targets": asdict(targets),
        "sample": {
            "oos_observations": observation_count,
            "oos_trades": trade_count,
            "oos_days": oos_days,
            "top_k": top_k,
            "strategy_trials": strategy_trials,
        },
        "metrics": {
            "oos_directional_accuracy_pct": accuracy,
            "top_decile_precision_pct": top_precision,
            "annualized_sharpe": sharpe,
            "annualized_sortino": sortino,
            "max_drawdown_pct": max_dd,
            "candidate_total_return_pct": None if total_return is None else total_return * 100.0,
            "benchmark_total_return_pct": None if benchmark_return is None else benchmark_return * 100.0,
            "is_oos_accuracy_gap_pct_points": is_oos_gap,
            **stats,
        },
        "gates": [gate.as_dict() for gate in gates],
        "blockers": blockers,
        "research_candidate_allowed": state == "PROVEN",
        "model_auto_promotion_allowed": False,
        "live_trading_enabled": False,
        "real_order_authority": False,
        "frozen_holdout_can_be_tuned_against": False,
        "note": (
            "PROVEN is research-evidence status only. It never authorizes LIVE trading, "
            "broker orders, or automatic model promotion."
        ),
    }


def evaluate_legacy_costed_walkforward(
    proof: Mapping[str, Any], targets: AlphaTargets | None = None
) -> dict[str, Any]:
    """Classify the legacy five-day costed proof without rewriting its meaning."""
    targets = targets or AlphaTargets()
    trade_count = int(proof.get("trade_count") or 0)
    days = proof.get("bhavcopy_days_used") if isinstance(proof.get("bhavcopy_days_used"), list) else []
    net_pnl = _float(proof.get("total_net_pnl"))
    return {
        "schema_version": 1,
        "state": "INSUFFICIENT_EVIDENCE",
        "source_type": "legacy_costed_walkforward_mechanics_proof",
        "legacy_proof_id": proof.get("proof_id"),
        "legacy_mechanics_pass": proof.get("pass") is True,
        "performance_target_proven": False,
        "sample": {"oos_trades": trade_count, "oos_days": len(days)},
        "observed": {
            "win_rate_pct": _float(proof.get("win_rate_pct")),
            "total_net_pnl": net_pnl,
            "costs_slippage_included": proof.get("costs_slippage_included_proven") is True,
        },
        "targets": asdict(targets),
        "blockers": sorted(
            {
                f"insufficient_oos_trades:{trade_count}<{targets.min_oos_trades}",
                f"insufficient_oos_days:{len(days)}<{targets.min_oos_days}",
                "directional_accuracy_not_measured",
                "top_decile_precision_not_measured",
                "daily_return_series_not_supplied",
                "benchmark_not_supplied",
                "frozen_holdout_manifest_not_supplied",
                "selection_bias_adjustment_not_supplied",
                *( ["negative_net_pnl"] if net_pnl is not None and net_pnl < 0 else [] ),
            }
        ),
        "research_candidate_allowed": False,
        "model_auto_promotion_allowed": False,
        "live_trading_enabled": False,
        "real_order_authority": False,
        "note": "Legacy PASS proves the costed walk-forward mechanism executed; it is not AlphaTruth performance proof.",
    }
