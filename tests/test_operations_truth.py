from __future__ import annotations

import json
from pathlib import Path

from src.ops.operations_truth import REQUIRED_INVENTORY_CATEGORIES, evaluate_operations_truth

ROOT = Path(__file__).resolve().parents[1]
TARGETS = json.loads((ROOT / "config" / "system3_sre_targets.json").read_text(encoding="utf-8"))


def _inventory_record(items=None):
    values = [] if items is None else items
    return {
        "state": "PROVEN" if values else "PROVEN_EMPTY",
        "items": values,
        "source": "gcloud read-only inventory",
        "observed_at": "2026-08-12T00:00:00+00:00",
    }


def _complete_inventory():
    return {category: _inventory_record([]) for category in REQUIRED_INVENTORY_CATEGORIES}


def _metric(value, observations):
    return {
        "value": value,
        "observations": observations,
        "source": "cloud-monitoring-test-fixture",
        "observed_at": "2026-08-12T00:00:00+00:00",
    }


def _passing_scorecard():
    return {
        "availability_pct": _metric(99.99, 2000),
        "api_success_latency_p95_ms": _metric(250.0, 2000),
        "broker_read_success_pct": _metric(99.95, 200),
        "token_rotation_success_pct": _metric(100.0, 20),
        "synthetic_success_pct": _metric(99.95, 2000),
    }


def test_empty_inventory_is_proven_empty_not_unknown():
    result = evaluate_operations_truth({"inventory": _complete_inventory()}, TARGETS)
    assert result["inventory_state"] == "PROVEN"
    assert all(item["state"] == "PROVEN_EMPTY" for item in result["inventory"].values())
    assert result["scorecard_state"] == "INSUFFICIENT_EVIDENCE"
    assert result["full_sre_program_closed"] is False


def test_missing_inventory_remains_partial_and_never_defaults_green():
    result = evaluate_operations_truth({}, TARGETS)
    assert result["inventory_state"] == "PARTIAL"
    assert result["state"] == "PARTIAL_EVIDENCE"
    assert any(item["state"] == "SCHEMA_ERROR" for item in result["inventory"].values()) is False
    assert all(item["state"] == "UNKNOWN" for item in result["inventory"].values())


def test_secret_payload_fields_are_rejected_even_when_query_claims_proven():
    inventory = _complete_inventory()
    inventory["secret_manager_secrets"] = _inventory_record([{"name": "safe-secret-name", "payload": "forbidden"}])
    result = evaluate_operations_truth({"inventory": inventory}, TARGETS)
    secret_truth = result["inventory"]["secret_manager_secrets"]
    assert secret_truth["state"] == "SCHEMA_ERROR"
    assert "secret_payload_field_forbidden" in secret_truth["reason"]
    assert result["state"] == "PARTIAL_EVIDENCE"


def test_scorecard_requires_sample_size_before_target_pass():
    inventory = _complete_inventory()
    scorecard = _passing_scorecard()
    scorecard["availability_pct"] = _metric(100.0, 10)
    result = evaluate_operations_truth({"inventory": inventory, "scorecard": scorecard}, TARGETS)
    assert result["scorecard"]["availability_pct"]["state"] == "NOT_PROVEN"
    assert result["scorecard_state"] == "INSUFFICIENT_EVIDENCE"


def test_scorecard_fails_real_target_miss():
    inventory = _complete_inventory()
    scorecard = _passing_scorecard()
    scorecard["api_success_latency_p95_ms"] = _metric(450.0, 2000)
    result = evaluate_operations_truth({"inventory": inventory, "scorecard": scorecard}, TARGETS)
    assert result["scorecard"]["api_success_latency_p95_ms"]["state"] == "FAIL"
    assert result["scorecard_state"] == "TARGET_FAIL"


def test_all_baseline_targets_pass_but_full_nine_phase_program_does_not_auto_close():
    result = evaluate_operations_truth(
        {"inventory": _complete_inventory(), "scorecard": _passing_scorecard()},
        TARGETS,
    )
    assert result["inventory_state"] == "PROVEN"
    assert result["scorecard_state"] == "PROVEN"
    assert result["state"] == "BASELINE_PROVEN_NOT_FULL_SRE_CLOSURE"
    assert result["full_sre_program_closed"] is False
    assert result["live_trading_enabled"] is False
    assert result["real_orders_attempted"] == 0


def test_trends_need_incident_history_and_preserve_directionality():
    evidence = {
        "inventory": _complete_inventory(),
        "trends": {
            "mttr_minutes": {"baseline": 30, "current": 20, "incidents": 5},
            "false_alert_rate_pct": {"baseline": 8, "current": 5, "incidents": 5},
            "automated_recovery_rate_pct": {"baseline": 40, "current": 60, "incidents": 5},
        },
    }
    result = evaluate_operations_truth(evidence, TARGETS)
    assert all(item["state"] == "IMPROVING" for item in result["trends"].values())


def test_target_config_forbids_order_probe_pr_mutation_and_hidden_token_fallback():
    governance = TARGETS["governance"]
    assert governance["live_trading_enabled"] is False
    assert governance["order_probe_allowed"] is False
    assert governance["pull_request_production_mutation_allowed"] is False
    assert governance["secret_payload_inventory_allowed"] is False
    assert governance["hidden_token_fallback_allowed"] is False
    assert governance["canonical_token_authority"] == "gcp-secret-manager-dynamic"
    assert governance["candidate_initial_traffic_pct"] == 0
    assert governance["rollback_by_traffic_reassignment"] is True
    assert governance["cloud_run_revision_restart_supported"] is False


def test_gcp_inventory_collector_contains_no_mutating_control_commands():
    text = (ROOT / "scripts" / "gcp_sre_inventory.py").read_text(encoding="utf-8")
    forbidden = [
        "run jobs " + "execute",
        "run services " + "update",
        "run deploy",
        "projects add-iam-policy-binding",
        "secrets versions " + "access",
        "secrets versions " + "add",
        "update-traffic",
    ]
    for marker in forbidden:
        assert marker not in text


def test_gcp_inventory_risk_ids_are_process_stable():
    text = (ROOT / "scripts" / "gcp_sre_inventory.py").read_text(encoding="utf-8")
    assert "hashlib.sha256" in text
    assert "abs(hash(" not in text
    assert "_stable_risk_suffix" in text
