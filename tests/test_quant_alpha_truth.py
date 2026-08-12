from __future__ import annotations

from copy import deepcopy

from src.quant.alpha_truth import AlphaTargets, evaluate_alpha_evidence, evaluate_legacy_costed_walkforward


def _valid_evidence() -> dict:
    observations = []
    for i in range(120):
        correct = i < 84  # 70% OOS directional accuracy
        observations.append(
            {
                "predicted_direction": 1,
                "actual_return": 0.01 if correct else -0.01,
                "confidence": 120 - i,
            }
        )
    daily = [0.003] * 55 + [-0.001] * 5
    benchmark = [0.001] * 60
    trade_pnl = [2.5] * 75 + [-1.0] * 25
    return {
        "manifest": {
            "evidence_id": "unit-test-frozen-oos",
            "source_sha": "a" * 40,
            "data_manifest_sha256": "b" * 64,
            "feature_schema_sha256": "c" * 64,
            "model_artifact_sha256": "d" * 64,
            "data_provenance_verified": True,
            "is_out_of_sample": True,
            "test_is_frozen": True,
            "tuned_on_frozen_holdout": False,
            "target_leakage_checks_passed": True,
            "feature_scaling_fit_on_train_only": True,
            "train_end": "2025-06-30T00:00:00+00:00",
            "validation_start": "2025-07-02T00:00:00+00:00",
            "validation_end": "2025-09-30T00:00:00+00:00",
            "test_start": "2025-10-02T00:00:00+00:00",
            "test_end": "2026-03-31T00:00:00+00:00",
            "label_horizon_bars": 1,
            "purge_gap_bars": 2,
            "benchmark_aligned": True,
            "benchmark_name": "NIFTY50",
            "strategy_trials": 1,
        },
        "observations": observations,
        "daily_net_returns": daily,
        "benchmark_daily_returns": benchmark,
        "trade_net_pnl": trade_pnl,
        "oos_days": 60,
        "in_sample_directional_accuracy_pct": 72.0,
        "selection_bias": {},
    }


def test_strong_synthetic_fixture_can_reach_research_proven_without_live_authority():
    result = evaluate_alpha_evidence(_valid_evidence())
    assert result["state"] == "PROVEN"
    assert result["metrics"]["oos_directional_accuracy_pct"] == 70.0
    assert result["metrics"]["top_decile_precision_pct"] == 100.0
    assert result["research_candidate_allowed"] is True
    assert result["model_auto_promotion_allowed"] is False
    assert result["live_trading_enabled"] is False
    assert result["real_order_authority"] is False
    assert result["frozen_holdout_can_be_tuned_against"] is False


def test_tiny_legacy_walkforward_is_mechanics_only_not_alpha_proof():
    legacy = {
        "proof_id": "legacy",
        "pass": True,
        "trade_count": 8,
        "win_rate_pct": 50.0,
        "total_net_pnl": -102636.35,
        "bhavcopy_days_used": ["1", "2", "3", "4", "5"],
        "costs_slippage_included_proven": True,
    }
    result = evaluate_legacy_costed_walkforward(legacy)
    assert result["state"] == "INSUFFICIENT_EVIDENCE"
    assert result["legacy_mechanics_pass"] is True
    assert result["performance_target_proven"] is False
    assert "negative_net_pnl" in result["blockers"]
    assert any(item.startswith("insufficient_oos_trades") for item in result["blockers"])
    assert result["research_candidate_allowed"] is False


def test_frozen_holdout_tuning_is_hard_blocked_even_with_good_metrics():
    evidence = _valid_evidence()
    evidence["manifest"]["tuned_on_frozen_holdout"] = True
    result = evaluate_alpha_evidence(evidence)
    assert result["state"] == "LEAKAGE_BLOCKED"
    assert "frozen_holdout_tuning_not_explicitly_false" in result["blockers"]
    assert result["research_candidate_allowed"] is False


def test_chronological_overlap_is_hard_blocked():
    evidence = _valid_evidence()
    evidence["manifest"]["test_start"] = "2025-09-15T00:00:00+00:00"
    result = evaluate_alpha_evidence(evidence)
    assert result["state"] == "LEAKAGE_BLOCKED"
    assert "chronological_split_overlap_or_order_error" in result["blockers"]


def test_multiple_strategy_trials_require_selection_bias_adjustment():
    evidence = _valid_evidence()
    evidence["manifest"]["strategy_trials"] = 25
    result = evaluate_alpha_evidence(evidence)
    assert result["state"] == "TARGET_FAIL"
    assert "multiple_testing_adjustment_missing" in result["blockers"]
    assert any(gate["name"] == "deflated_sharpe_probability" and not gate["passed"] for gate in result["gates"])


def test_deflated_sharpe_probability_gate_can_pass_when_supplied():
    evidence = _valid_evidence()
    evidence["manifest"]["strategy_trials"] = 25
    evidence["selection_bias"] = {"deflated_sharpe_probability": 0.97}
    result = evaluate_alpha_evidence(evidence)
    assert result["state"] == "PROVEN"


def test_target_failure_does_not_get_relabelled_as_proven():
    evidence = _valid_evidence()
    for row in evidence["observations"]:
        row["actual_return"] = -0.01
    result = evaluate_alpha_evidence(evidence)
    assert result["state"] == "TARGET_FAIL"
    assert result["metrics"]["oos_directional_accuracy_pct"] == 0.0
    assert result["research_candidate_allowed"] is False


def test_minimum_evidence_targets_are_configurable_but_fail_closed():
    evidence = _valid_evidence()
    evidence["trade_net_pnl"] = evidence["trade_net_pnl"][:8]
    targets = AlphaTargets(min_oos_trades=100)
    result = evaluate_alpha_evidence(evidence, targets)
    assert result["state"] == "INSUFFICIENT_EVIDENCE"
    assert "insufficient_oos_trades:8<100" in result["blockers"]
