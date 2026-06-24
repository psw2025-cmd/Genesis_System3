"""Tests for auto gate evaluator and friction expectancy proof."""

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_gate_evaluator_runs():
    from scripts.system3_gate_evaluator import evaluate_all, load_spearman_days

    days, passing, latest = load_spearman_days(ROOT)
    assert isinstance(days, list)
    payload = evaluate_all(ROOT)
    assert "gates" in payload
    assert payload["gates_total"] >= 5
    assert "ML_SPEARMAN_RHO_GTE_0_70_OVER_5_DAYS" in payload["gates"]
    assert payload["live_trading_enabled"] is False


def test_friction_expectancy_from_fixture():
    from scripts.system3_friction_expectancy_proof import build_report

    report = build_report()
    ev = report["evidence"]
    assert ev["trade_count"] >= 5
    assert ev["net_expectancy_after_costs"] is not None
    assert "pass" in report


def test_auto_gates_service_builds_proof_gates():
    from dashboard.backend.auto_gates_service import build_auto_gates_report

    report = build_auto_gates_report(refresh=True)
    assert report.get("runtime_driven") is True
    assert "proof_gates" in report
    assert report.get("live_trading_enabled") is False


def test_model_to_trade_gap_runs():
    from scripts.system3_model_to_trade_gap_proof import build_report

    report = build_report()
    assert "evidence" in report
    assert "pass" in report
