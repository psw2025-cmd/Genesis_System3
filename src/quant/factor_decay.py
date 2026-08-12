"""Fail-closed factor/model decay detection for Genesis System3 research.

The monitor consumes a versioned chronological series of *predeclared* research
quality observations such as daily active returns or daily information
coefficients.  It compares an earlier baseline window with a later monitoring
window using Information Ratio (mean / standard deviation).

A deterioration beyond the configured threshold may only trigger
``RESEARCH_REQUIRED``.  It never retrains, promotes, sizes, or trades.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import statistics
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Mapping, Sequence

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$", re.IGNORECASE)
_GIT_SHA_RE = re.compile(r"^[0-9a-f]{40}$", re.IGNORECASE)


@dataclass(frozen=True)
class DecayPolicy:
    deterioration_trigger_pct: float = 15.0
    min_baseline_observations: int = 60
    min_recent_observations: int = 30
    min_positive_baseline_ir: float = 0.05
    max_observation_age_days: int = 7


def _number(value: Any) -> float | None:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def _parse_time(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(str(value).strip().replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def information_ratio(values: Sequence[float]) -> float | None:
    """Mean divided by population standard deviation for a predeclared series.

    For active returns this is the non-annualized Information Ratio per input
    period. For information coefficients it is the usual IC information ratio.
    The caller must declare the observation type in the evidence manifest.
    """
    if len(values) < 2:
        return None
    std = statistics.pstdev(values)
    if std <= 0:
        return None
    return statistics.fmean(values) / std


def _chronological_rows(evidence: Mapping[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    raw = evidence.get("observations")
    if not isinstance(raw, list):
        return [], ["observations_missing"]
    rows: list[dict[str, Any]] = []
    blockers: list[str] = []
    previous: datetime | None = None
    for index, row in enumerate(raw):
        if not isinstance(row, Mapping):
            blockers.append(f"observation_not_object:{index}")
            continue
        ts = _parse_time(row.get("timestamp"))
        value = _number(row.get("value"))
        if ts is None or value is None:
            blockers.append(f"observation_invalid:{index}")
            continue
        if previous is not None and ts <= previous:
            blockers.append("observations_not_strictly_chronological")
        previous = ts
        rows.append({"timestamp": ts, "value": value})
    return rows, blockers


def _manifest_blockers(manifest: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    if not _GIT_SHA_RE.fullmatch(str(manifest.get("source_sha") or "")):
        blockers.append("source_sha_missing_or_invalid")
    for key in ("data_manifest_sha256", "model_or_factor_sha256"):
        if not _SHA256_RE.fullmatch(str(manifest.get(key) or "")):
            blockers.append(f"{key}_missing_or_invalid")
    if not str(manifest.get("evidence_id") or "").strip():
        blockers.append("evidence_id_missing")
    if manifest.get("data_provenance_verified") is not True:
        blockers.append("data_provenance_not_verified")
    if manifest.get("frozen_or_paper_oos") is not True:
        blockers.append("non_oos_decay_series")
    if manifest.get("metric_predeclared") is not True:
        blockers.append("decay_metric_not_predeclared")
    observation_type = str(manifest.get("observation_type") or "")
    if observation_type not in {"active_return", "information_coefficient"}:
        blockers.append("unsupported_observation_type")
    return blockers


def evaluate_decay(
    evidence: Mapping[str, Any],
    policy: DecayPolicy | None = None,
    *,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Return typed decay truth without performing any remediation action."""
    policy = policy or DecayPolicy()
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    manifest = evidence.get("manifest") if isinstance(evidence.get("manifest"), Mapping) else {}
    blockers = _manifest_blockers(manifest)
    rows, row_blockers = _chronological_rows(evidence)
    blockers.extend(row_blockers)

    baseline_count = int(manifest.get("baseline_observations") or policy.min_baseline_observations)
    recent_count = int(manifest.get("recent_observations") or policy.min_recent_observations)
    if baseline_count < policy.min_baseline_observations:
        blockers.append("baseline_window_below_policy_minimum")
    if recent_count < policy.min_recent_observations:
        blockers.append("recent_window_below_policy_minimum")
    if len(rows) < baseline_count + recent_count:
        blockers.append(
            f"insufficient_decay_observations:{len(rows)}<{baseline_count + recent_count}"
        )

    latest_age_days: float | None = None
    if rows:
        latest_age_days = max(0.0, (now - rows[-1]["timestamp"]).total_seconds() / 86400.0)
        if latest_age_days > policy.max_observation_age_days:
            blockers.append(
                f"decay_evidence_stale:{latest_age_days:.2f}>{policy.max_observation_age_days}"
            )

    baseline_values: list[float] = []
    recent_values: list[float] = []
    if len(rows) >= baseline_count + recent_count:
        # Non-overlapping windows: baseline immediately precedes the recent
        # monitor window. This prevents a recent observation from contributing
        # to both numerator regimes and understating change.
        baseline_values = [row["value"] for row in rows[-(baseline_count + recent_count):-recent_count]]
        recent_values = [row["value"] for row in rows[-recent_count:]]

    baseline_ir = information_ratio(baseline_values)
    recent_ir = information_ratio(recent_values)
    deterioration_pct: float | None = None
    trigger = False
    if baseline_ir is None or recent_ir is None:
        blockers.append("information_ratio_unavailable")
    elif baseline_ir < policy.min_positive_baseline_ir:
        blockers.append(
            f"baseline_ir_not_positive_enough:{baseline_ir:.6f}<{policy.min_positive_baseline_ir}"
        )
    else:
        deterioration_pct = 100.0 * (baseline_ir - recent_ir) / abs(baseline_ir)
        trigger = deterioration_pct > policy.deterioration_trigger_pct

    blockers = sorted(set(blockers))
    schema_problem = any(
        item.startswith(("source_sha_", "data_manifest_", "model_or_factor_", "evidence_id_", "unsupported_", "observation_not_", "observation_invalid"))
        for item in blockers
    )
    stale = any(item.startswith("decay_evidence_stale") for item in blockers)
    insufficient = any(
        item.startswith(("insufficient_", "baseline_window_", "recent_window_", "information_ratio_unavailable", "baseline_ir_not_"))
        for item in blockers
    )
    if schema_problem or "data_provenance_not_verified" in blockers or "decay_metric_not_predeclared" in blockers or "non_oos_decay_series" in blockers:
        state = "SCHEMA_ERROR"
    elif stale:
        state = "STALE"
    elif insufficient:
        state = "INSUFFICIENT_EVIDENCE"
    elif trigger:
        state = "RESEARCH_REQUIRED"
    else:
        state = "STABLE"

    canonical = json.dumps(evidence, sort_keys=True, separators=(",", ":"), default=str).encode()
    return {
        "schema_version": 1,
        "state": state,
        "evidence_id": manifest.get("evidence_id"),
        "evidence_sha256": hashlib.sha256(canonical).hexdigest(),
        "observation_type": manifest.get("observation_type"),
        "policy": asdict(policy),
        "sample": {
            "total_observations": len(rows),
            "baseline_observations": len(baseline_values),
            "recent_observations": len(recent_values),
            "latest_age_days": latest_age_days,
        },
        "metrics": {
            "baseline_information_ratio": baseline_ir,
            "recent_information_ratio": recent_ir,
            "deterioration_pct": deterioration_pct,
        },
        "blockers": blockers,
        "research_required": state == "RESEARCH_REQUIRED",
        "automatic_retraining_allowed": False,
        "model_auto_promotion_allowed": False,
        "position_size_change_allowed": False,
        "live_trading_enabled": False,
        "real_order_authority": False,
        "next_action": (
            "CREATE_ISOLATED_RESEARCH_CHALLENGER"
            if state == "RESEARCH_REQUIRED"
            else "NO_AUTOMATIC_MODEL_ACTION"
        ),
        "note": (
            "Decay detection is a research trigger only. A challenger must preserve trial history, "
            "use train/validation tuning, and pass frozen AlphaTruth evidence before research-candidate status."
        ),
    }
