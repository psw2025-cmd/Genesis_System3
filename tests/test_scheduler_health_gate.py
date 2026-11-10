from __future__ import annotations

import json
from pathlib import Path

from scripts.scheduler_health_gate import (
    TRANSPORT_INVALID_JSON,
    TRANSPORT_NON_2XX,
    TRANSPORT_OK,
    TRANSPORT_TIMEOUT,
    classify_transport,
    evaluate,
    evaluate_with_transport,
    main,
)

ROOT = Path(__file__).resolve().parents[1]


def _good_payload():
    return {
        "healthy": True,
        "coverage": {
            "contract_matched": True,
            "total": 6,
            "expected_total": 6,
            "workload": 4,
            "expected_workload": 4,
            "control": 2,
            "expected_control": 2,
            "enabled": 6,
            "expected_enabled": 6,
        },
        "evidence_version": 12,
        "evidence_sha256": "a" * 64,
        "observability": {"alert_severity": "none"},
        "business_readiness": "PARTIAL",
        "live_trading_enabled": False,
        "jobs": [
            {
                "name": "genesis-system3-scheduler-collector",
                "completion_status": "EXECUTION_SUCCEEDED",
                "execution": "collector-canary-123",
                "evidence_role": "current_execution",
            }
        ],
        "access_token": "MUST_NEVER_BE_COPIED",
    }


def test_exact_canary_execution_passes_and_report_is_sanitized():
    failures, report = evaluate(_good_payload(), "collector-canary-123")
    assert failures == []
    assert report["state"] == "PASS"
    assert report["transport_class"] == TRANSPORT_OK
    serialized = str(report)
    assert "MUST_NEVER_BE_COPIED" not in serialized
    assert "a" * 64 not in serialized
    assert report["evidence_sha256_present"] is True
    assert report["evidence_sha256_length"] == 64


def test_prior_succeeded_execution_is_accepted_when_newer_execution_exists():
    payload = _good_payload()
    payload["jobs"][0]["execution"] = "collector-prior-111"
    payload["jobs"][0]["evidence_role"] = "prior_succeeded_execution"
    failures, report = evaluate(payload, "collector-canary-123")
    assert failures == []
    assert report["state"] == "PASS"


def test_wrong_execution_without_prior_role_fails_closed():
    payload = _good_payload()
    payload["jobs"][0]["execution"] = "collector-other-999"
    payload["jobs"][0]["evidence_role"] = "current_execution"
    failures, report = evaluate(payload, "collector-canary-123")
    assert "collector.execution_matches_canary_or_prior_succeeded" in failures
    assert report["state"] == "FAIL"


def test_invalid_scheduler_payload_names_failed_predicates():
    failures, report = evaluate({}, "collector-canary-123")
    expected = {
        "coverage.contract_matched",
        "coverage.total_equals_expected",
        "coverage.workload_equals_expected",
        "coverage.control_equals_expected",
        "coverage.enabled_equals_expected",
        "evidence_version_positive",
        "evidence_sha256_length_64",
        "observability.alert_severity_none",
        "business_readiness_allowed",
        "collector.completion_succeeded",
        "collector.execution_matches_canary_or_prior_succeeded",
    }
    assert expected.issubset(set(failures))
    # Preserve existing jq semantics: an absent/null live flag is not true and
    # therefore is not, by itself, a live-trading violation.
    assert "live_trading_not_true" not in failures
    assert report["state"] == "FAIL"


def test_every_existing_acceptance_dimension_stays_fail_closed():
    mutations = {
        "coverage.contract_matched": lambda p: p["coverage"].__setitem__("contract_matched", False),
        "coverage.total_equals_expected": lambda p: p["coverage"].__setitem__("total", 5),
        "coverage.workload_equals_expected": lambda p: p["coverage"].__setitem__("workload", 3),
        "coverage.control_equals_expected": lambda p: p["coverage"].__setitem__("control", 1),
        "coverage.enabled_equals_expected": lambda p: p["coverage"].__setitem__("enabled", 5),
        "evidence_version_positive": lambda p: p.__setitem__("evidence_version", 0),
        "evidence_sha256_length_64": lambda p: p.__setitem__("evidence_sha256", "short"),
        "observability.alert_severity_none": lambda p: p["observability"].__setitem__("alert_severity", "warning"),
        "business_readiness_allowed": lambda p: p.__setitem__("business_readiness", "UNKNOWN_VALUE"),
        "live_trading_not_true": lambda p: p.__setitem__("live_trading_enabled", True),
        "collector.completion_succeeded": lambda p: p["jobs"][0].__setitem__("completion_status", "EXECUTION_FAILED"),
    }
    for expected_failure, mutate in mutations.items():
        payload = _good_payload()
        mutate(payload)
        failures, report = evaluate(payload, "collector-canary-123")
        assert expected_failure in failures
        assert report["state"] == "FAIL"


def test_verify_mode_preserves_existing_four_predicates():
    payload = _good_payload()
    failures, report = evaluate(payload, "", mode="verify")
    assert failures == []
    assert report["mode"] == "verify"
    payload["healthy"] = False
    payload["observability"]["alert_severity"] = "critical"
    failures, report = evaluate(payload, "", mode="verify")
    assert "healthy_true" in failures
    assert "observability.alert_severity_none" in failures
    assert report["state"] == "FAIL"


def test_transport_classes_are_distinct_from_named_predicates():
    assert classify_transport(http_status=200, curl_exit=0, json_ok=True) == TRANSPORT_OK
    assert classify_transport(http_status=0, curl_exit=28, json_ok=False) == TRANSPORT_TIMEOUT
    assert classify_transport(http_status=503, curl_exit=22, json_ok=False) == TRANSPORT_NON_2XX
    assert classify_transport(http_status=200, curl_exit=0, json_ok=False) == TRANSPORT_INVALID_JSON
    failures, report = evaluate_with_transport(
        {},
        "collector-canary-123",
        http_status=0,
        curl_exit=28,
        json_ok=False,
    )
    assert failures == []
    assert report["transport_class"] == TRANSPORT_TIMEOUT
    assert report["state"] == "FAIL"
    assert report["failed_predicates"] == []


def test_cli_writes_allowlisted_report_for_malformed_and_secret_payloads(tmp_path, monkeypatch):
    bad = tmp_path / "bad.json"
    bad.write_text("{not-json", encoding="utf-8")
    out = tmp_path / "report.json"
    monkeypatch.setattr(
        "sys.argv",
        [
            "scheduler_health_gate.py",
            "--input",
            str(bad),
            "--output",
            str(out),
            "--expected-execution",
            "collector-canary-123",
            "--http-status",
            "200",
            "--curl-exit",
            "0",
        ],
    )
    assert main() == 2
    report = json.loads(out.read_text(encoding="utf-8"))
    assert report["transport_class"] == TRANSPORT_INVALID_JSON
    assert "access_token" not in report
    assert "evidence_sha256" not in report

    good = tmp_path / "good.json"
    good.write_text(json.dumps(_good_payload()), encoding="utf-8")
    out2 = tmp_path / "good-report.json"
    monkeypatch.setattr(
        "sys.argv",
        [
            "scheduler_health_gate.py",
            "--input",
            str(good),
            "--output",
            str(out2),
            "--expected-execution",
            "collector-canary-123",
            "--http-status",
            "200",
            "--curl-exit",
            "0",
        ],
    )
    assert main() == 0
    report = json.loads(out2.read_text(encoding="utf-8"))
    assert report["state"] == "PASS"
    serialized = json.dumps(report)
    assert "MUST_NEVER_BE_COPIED" not in serialized
    assert "a" * 64 not in serialized


def test_workflow_wires_gate_and_always_uploads_sanitized_report():
    workflow = (ROOT / ".github/workflows/cloud-run-auto-deploy.yml").read_text(encoding="utf-8")
    assert "scripts/scheduler_health_gate.py" in workflow
    assert "--mode canary" in workflow
    assert "--mode verify" in workflow
    assert "system3-scheduler-health-gate-" in workflow
    assert "reports/latest/scheduler_health_gate/" in workflow
    gate_upload = workflow.index("Upload scheduler-health gate report")
    always = workflow.index("if: always()", gate_upload)
    assert always - gate_upload < 200
    # Opaque jq remains documented so the existing acceptance strings stay locked.
    assert "coverage.contract_matched == true" in workflow
    assert ".coverage.total == .coverage.expected_total" in workflow
