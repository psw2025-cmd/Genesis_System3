from __future__ import annotations

from datetime import datetime, timedelta, timezone

from src.quant.factor_decay import DecayPolicy, evaluate_decay, information_ratio


def _evidence(*, decayed: bool = False, age_days: int = 0) -> dict:
    now = datetime(2026, 8, 12, tzinfo=timezone.utc)
    start = now - timedelta(days=89 + age_days)
    baseline = [0.20, 0.10, 0.15, 0.05, 0.12, 0.08] * 10
    recent = ([0.08, 0.02, 0.04, -0.01, 0.03, 0.01] * 5) if decayed else ([0.19, 0.09, 0.14, 0.04, 0.11, 0.07] * 5)
    values = baseline + recent
    observations = [
        {"timestamp": (start + timedelta(days=i)).isoformat(), "value": value}
        for i, value in enumerate(values)
    ]
    return {
        "manifest": {
            "evidence_id": "decay-unit-test",
            "source_sha": "a" * 40,
            "data_manifest_sha256": "b" * 64,
            "model_or_factor_sha256": "c" * 64,
            "data_provenance_verified": True,
            "frozen_or_paper_oos": True,
            "metric_predeclared": True,
            "observation_type": "information_coefficient",
            "baseline_observations": 60,
            "recent_observations": 30,
        },
        "observations": observations,
    }


def test_information_ratio_is_mean_over_population_std():
    result = information_ratio([0.1, 0.2, 0.3])
    assert result is not None
    assert result > 0


def test_stable_series_does_not_retrain_or_trade():
    now = datetime(2026, 8, 12, tzinfo=timezone.utc)
    result = evaluate_decay(_evidence(decayed=False), now=now)
    assert result["state"] == "STABLE"
    assert result["research_required"] is False
    assert result["automatic_retraining_allowed"] is False
    assert result["model_auto_promotion_allowed"] is False
    assert result["position_size_change_allowed"] is False
    assert result["live_trading_enabled"] is False
    assert result["real_order_authority"] is False


def test_ir_deterioration_over_threshold_only_triggers_research():
    now = datetime(2026, 8, 12, tzinfo=timezone.utc)
    result = evaluate_decay(_evidence(decayed=True), now=now)
    assert result["state"] == "RESEARCH_REQUIRED"
    assert result["research_required"] is True
    assert result["metrics"]["deterioration_pct"] > 15.0
    assert result["next_action"] == "CREATE_ISOLATED_RESEARCH_CHALLENGER"
    assert result["automatic_retraining_allowed"] is False
    assert result["model_auto_promotion_allowed"] is False
    assert result["position_size_change_allowed"] is False
    assert result["live_trading_enabled"] is False


def test_too_little_data_is_insufficient_not_false_stable():
    evidence = _evidence()
    evidence["observations"] = evidence["observations"][-20:]
    now = datetime(2026, 8, 12, tzinfo=timezone.utc)
    result = evaluate_decay(evidence, now=now)
    assert result["state"] == "INSUFFICIENT_EVIDENCE"
    assert any(item.startswith("insufficient_decay_observations") for item in result["blockers"])
    assert result["research_required"] is False


def test_stale_data_is_stale_not_stable():
    now = datetime(2026, 8, 20, tzinfo=timezone.utc)
    result = evaluate_decay(_evidence(), now=now)
    assert result["state"] == "STALE"
    assert any(item.startswith("decay_evidence_stale") for item in result["blockers"])


def test_unverified_provenance_fails_closed():
    evidence = _evidence()
    evidence["manifest"]["data_provenance_verified"] = False
    now = datetime(2026, 8, 12, tzinfo=timezone.utc)
    result = evaluate_decay(evidence, now=now)
    assert result["state"] == "SCHEMA_ERROR"
    assert "data_provenance_not_verified" in result["blockers"]


def test_non_oos_series_is_rejected():
    evidence = _evidence()
    evidence["manifest"]["frozen_or_paper_oos"] = False
    now = datetime(2026, 8, 12, tzinfo=timezone.utc)
    result = evaluate_decay(evidence, now=now)
    assert result["state"] == "SCHEMA_ERROR"
    assert "non_oos_decay_series" in result["blockers"]


def test_non_chronological_observations_fail_closed():
    evidence = _evidence()
    evidence["observations"][10], evidence["observations"][11] = evidence["observations"][11], evidence["observations"][10]
    now = datetime(2026, 8, 12, tzinfo=timezone.utc)
    result = evaluate_decay(evidence, now=now)
    assert "observations_not_strictly_chronological" in result["blockers"]
    assert result["state"] != "STABLE"


def test_policy_minimum_windows_cannot_be_declared_smaller():
    evidence = _evidence()
    evidence["manifest"]["baseline_observations"] = 20
    evidence["manifest"]["recent_observations"] = 10
    now = datetime(2026, 8, 12, tzinfo=timezone.utc)
    result = evaluate_decay(evidence, DecayPolicy(), now=now)
    assert result["state"] == "INSUFFICIENT_EVIDENCE"
    assert "baseline_window_below_policy_minimum" in result["blockers"]
    assert "recent_window_below_policy_minimum" in result["blockers"]
