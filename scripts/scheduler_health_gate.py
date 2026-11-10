#!/usr/bin/env python3
"""Fail-closed scheduler-health verifier with sanitized diagnostics.

Replaces opaque jq-only assertions in Cloud Run Auto Deploy without relaxing
their acceptance contract. Transport failures are named separately from payload
predicates. The raw scheduler-health payload is never copied into the report;
only explicitly allow-listed control-plane fields are persisted.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

_ALLOWED_BUSINESS_READINESS = {"READY", "PARTIAL", "PENDING", "NOT_APPLICABLE", "BLOCKED"}
_COLLECTOR_NAME = "genesis-system3-scheduler-collector"
TRANSPORT_OK = "OK"
TRANSPORT_TIMEOUT = "CURL_TIMEOUT"
TRANSPORT_NON_2XX = "CURL_NON_2XX"
TRANSPORT_INVALID_JSON = "INVALID_JSON"
SCHEMA = "genesis-system3-scheduler-health-gate-v1"


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


def classify_transport(*, http_status: int | None, curl_exit: int | None, json_ok: bool) -> str:
    """Name curl/HTTP/JSON failures separately from payload predicates."""
    if curl_exit == 28:
        return TRANSPORT_TIMEOUT
    status = -1 if http_status is None else http_status
    if status == 0 or (status > 0 and not (200 <= status <= 299)):
        return TRANSPORT_NON_2XX
    if curl_exit not in (None, 0) and status < 0:
        return TRANSPORT_NON_2XX
    if not json_ok:
        return TRANSPORT_INVALID_JSON
    return TRANSPORT_OK


def _canary_checks(root: dict[str, Any], expected_execution: str) -> dict[str, bool]:
    coverage = _as_dict(root.get("coverage"))
    observability = _as_dict(root.get("observability"))
    collector = _collector_row(root)
    return {
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


def _verify_checks(root: dict[str, Any]) -> dict[str, bool]:
    coverage = _as_dict(root.get("coverage"))
    observability = _as_dict(root.get("observability"))
    return {
        "healthy_true": root.get("healthy") is True,
        "coverage.contract_matched": coverage.get("contract_matched") is True,
        "live_trading_not_true": root.get("live_trading_enabled") is not True,
        "observability.alert_severity_none": observability.get("alert_severity") == "none",
    }


def _sanitized_summary(
    root: dict[str, Any],
    *,
    expected_execution: str,
    mode: str,
    transport_class: str,
    failures: list[str],
) -> dict[str, Any]:
    coverage = _as_dict(root.get("coverage"))
    observability = _as_dict(root.get("observability"))
    collector = _collector_row(root)
    sha = root.get("evidence_sha256")
    return {
        "schema": SCHEMA,
        "mode": mode,
        "state": "PASS" if transport_class == TRANSPORT_OK and not failures else "FAIL",
        "transport_class": transport_class,
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
        "healthy": root.get("healthy"),
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
            "expected_canary_execution": expected_execution or None,
        },
    }


def evaluate(payload: Any, expected_execution: str, *, mode: str = "canary") -> tuple[list[str], dict[str, Any]]:
    """Return failed predicate names and a strictly sanitized evidence summary."""
    root = _as_dict(payload)
    if mode == "verify":
        checks = _verify_checks(root)
    else:
        checks = _canary_checks(root, expected_execution)
    failures = [name for name, passed in checks.items() if not passed]
    report = _sanitized_summary(
        root,
        expected_execution=expected_execution,
        mode=mode,
        transport_class=TRANSPORT_OK,
        failures=failures,
    )
    return failures, report


def evaluate_with_transport(
    payload: Any,
    expected_execution: str,
    *,
    mode: str = "canary",
    http_status: int | None = None,
    curl_exit: int | None = None,
    json_ok: bool = True,
) -> tuple[list[str], dict[str, Any]]:
    transport_class = classify_transport(http_status=http_status, curl_exit=curl_exit, json_ok=json_ok)
    if transport_class != TRANSPORT_OK:
        report = _sanitized_summary(
            _as_dict(payload) if json_ok else {},
            expected_execution=expected_execution,
            mode=mode,
            transport_class=transport_class,
            failures=[],
        )
        return [], report
    return evaluate(payload, expected_execution, mode=mode)


def _parse_optional_int(value: str | None) -> int | None:
    if value is None or value == "":
        return None
    return int(value)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--mode", choices=("canary", "verify"), default="canary")
    parser.add_argument("--expected-execution", default="")
    parser.add_argument("--http-status", default="")
    parser.add_argument("--curl-exit", default="")
    args = parser.parse_args()

    if args.mode == "canary" and not args.expected_execution:
        raise SystemExit("canary mode requires --expected-execution")

    payload: Any = {}
    json_ok = False
    input_path = Path(args.input)
    try:
        payload = json.loads(input_path.read_text(encoding="utf-8"))
        json_ok = True
    except Exception:
        payload = {}
        json_ok = False

    http_status = _parse_optional_int(args.http_status)
    curl_exit = _parse_optional_int(args.curl_exit)
    failures, report = evaluate_with_transport(
        payload,
        args.expected_execution,
        mode=args.mode,
        http_status=http_status,
        curl_exit=curl_exit,
        json_ok=json_ok,
    )
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "state": report["state"],
                "transport_class": report["transport_class"],
                "failed_predicates": failures,
            },
            sort_keys=True,
        )
    )
    return 0 if report["state"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
