#!/usr/bin/env python3
"""Fail-closed scheduler-health verifier with sanitized diagnostics.

This replaces opaque jq-only assertions in the Cloud Run deploy canary without
relaxing their acceptance contract. The raw scheduler-health payload is never
copied into the report; only explicitly allow-listed control-plane fields are
persisted.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

_ALLOWED_BUSINESS_READINESS = {"READY", "PARTIAL", "PENDING", "NOT_APPLICABLE", "BLOCKED"}
_COLLECTOR_NAME = "genesis-system3-scheduler-collector"


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _collector_row(payload: dict[str, Any]) -> dict[str, Any]:
    jobs = payload.get("jobs")
    if not isinstance(jobs, list):
        return {}
    for row in jobs:
        if isinstance(row, dict) and row.get("name") == _COLLECTOR_NAME:
            return row
    return {}


def evaluate(payload: Any, expected_execution: str) -> tuple[list[str], dict[str, Any]]:
    """Return failed predicate names and a strictly sanitized evidence summary."""
    root = _as_dict(payload)
    coverage = _as_dict(root.get("coverage"))
    observability = _as_dict(root.get("observability"))
    collector = _collector_row(root)
    failures: list[str] = []

    checks = {
        "coverage.contract_matched": coverage.get("contract_matched") is True,
        "coverage.total_equals_expected": coverage.get("total") == coverage.get("expected_total")
        and coverage.get("total") is not None,
        "coverage.workload_equals_expected": coverage.get("workload") == coverage.get("expected_workload")
        and coverage.get("workload") is not None,
        "coverage.control_equals_expected": coverage.get("control") == coverage.get("expected_control")
        and coverage.get("control") is not None,
        "coverage.enabled_equals_expected": coverage.get("enabled") == coverage.get("expected_enabled")
        and coverage.get("enabled") is not None,
        "evidence_version_positive": isinstance(root.get("evidence_version"), (int, float))
        and not isinstance(root.get("evidence_version"), bool)
        and root.get("evidence_version") > 0,
        "evidence_sha256_length_64": isinstance(root.get("evidence_sha256"), str)
        and len(root.get("evidence_sha256")) == 64,
        "observability.alert_severity_none": observability.get("alert_severity") == "none",
        "business_readiness_allowed": root.get("business_readiness") in _ALLOWED_BUSINESS_READINESS,
        "live_trading_not_true": root.get("live_trading_enabled") is not True,
        "collector.completion_succeeded": collector.get("completion_status") == "EXECUTION_SUCCEEDED",
        "collector.execution_matches_canary_or_prior_succeeded": bool(collector)
        and (
            collector.get("execution") == expected_execution
            or collector.get("evidence_role") == "prior_succeeded_execution"
        ),
    }
    failures.extend(name for name, passed in checks.items() if not passed)

    sha = root.get("evidence_sha256")
    sanitized = {
        "schema": "genesis-system3-scheduler-health-gate-v1",
        "state": "PASS" if not failures else "FAIL",
        "failed_predicates": failures,
        "coverage": {
            key: coverage.get(key)
            for key in (
                "contract_matched",
                "total",
                "expected_total",
                "workload",
                "expected_workload",
                "control",
                "expected_control",
                "enabled",
                "expected_enabled",
            )
        },
        "evidence_version": root.get("evidence_version"),
        "evidence_sha256_present": isinstance(sha, str) and bool(sha),
        "evidence_sha256_length": len(sha) if isinstance(sha, str) else 0,
        "alert_severity": observability.get("alert_severity"),
        "business_readiness": root.get("business_readiness"),
        "live_trading_enabled": root.get("live_trading_enabled"),
        "collector": {
            "name": collector.get("name"),
            "completion_status": collector.get("completion_status"),
            "execution": collector.get("execution"),
            "evidence_role": collector.get("evidence_role"),
            "expected_canary_execution": expected_execution,
        },
    }
    return failures, sanitized


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--expected-execution", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    try:
        payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    except Exception as exc:
        payload = {}
        load_failure = f"input.invalid_json:{type(exc).__name__}"
    else:
        load_failure = None

    failures, report = evaluate(payload, args.expected_execution)
    if load_failure:
        failures.insert(0, load_failure)
        report["failed_predicates"] = failures
        report["state"] = "FAIL"

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"state": report["state"], "failed_predicates": failures}, sort_keys=True))
    return 0 if not failures else 2


if __name__ == "__main__":
    raise SystemExit(main())
