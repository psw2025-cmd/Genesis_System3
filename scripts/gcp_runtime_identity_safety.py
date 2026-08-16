#!/usr/bin/env python3
"""Fail-closed runtime identity/scheduler proof for the PAPER Cloud Run lane.

Consumes sanitized control-plane JSON previously written by gcloud. This module
never reads secret payloads and never calls a trading or broker mutation API.
It tolerates documented Cloud Run Job v1/v2 JSON shapes but rejects missing or
ambiguous service-account authority.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

OFF_VALUES = {None, "0", "false", "False"}
EXPECTED_SCHEDULE = "30 7 * * *"
EXPECTED_TIME_ZONE = "Asia/Kolkata"


def _containers(service: dict[str, Any]) -> list[dict[str, Any]]:
    rows = (((service.get("spec") or {}).get("template") or {}).get("spec") or {}).get("containers") or []
    return [row for row in rows if isinstance(row, dict)]


def service_environment(service: dict[str, Any]) -> tuple[dict[str, str], set[str]]:
    env: dict[str, str] = {}
    secret_env_names: set[str] = set()
    for container in _containers(service):
        for row in container.get("env") or []:
            if not isinstance(row, dict) or not row.get("name"):
                continue
            name = str(row["name"])
            if "value" in row:
                env[name] = str(row.get("value") or "")
            if (row.get("valueFrom") or {}).get("secretKeyRef"):
                secret_env_names.add(name)
    return env, secret_env_names


def _nested(data: dict[str, Any], *path: str) -> Any:
    value: Any = data
    for key in path:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


def rotator_service_account(rotator: dict[str, Any]) -> str:
    """Return the single recognized Cloud Run Job service account or fail.

    `gcloud run jobs describe --format=json` currently emits the Knative/v1
    shape `spec.template.spec.template.spec.serviceAccountName`. The Cloud Run
    v2 API represents the task-template identity as `serviceAccount`. Both are
    accepted; disagreement or absence is a hard failure.
    """
    candidates = {
        str(value).strip()
        for value in (
            _nested(rotator, "spec", "template", "spec", "template", "spec", "serviceAccountName"),
            _nested(rotator, "spec", "template", "spec", "template", "spec", "serviceAccount"),
            _nested(rotator, "template", "template", "serviceAccount"),
            _nested(rotator, "template", "template", "serviceAccountName"),
            _nested(rotator, "spec", "template", "template", "serviceAccount"),
            _nested(rotator, "spec", "template", "template", "serviceAccountName"),
        )
        if value is not None and str(value).strip()
    }
    if len(candidates) != 1:
        raise ValueError(f"rotator_service_account_unresolved:{sorted(candidates)}")
    return next(iter(candidates))


def scheduler_service_account(scheduler: dict[str, Any]) -> str:
    value = _nested(scheduler, "httpTarget", "oauthToken", "serviceAccountEmail")
    if not isinstance(value, str) or not value.strip():
        raise ValueError("scheduler_service_account_missing")
    return value.strip()


def serving_traffic(service: dict[str, Any]) -> dict[str, int]:
    traffic: dict[str, int] = {}
    for item in (service.get("status") or {}).get("traffic") or []:
        if not isinstance(item, dict):
            continue
        revision = item.get("revisionName")
        try:
            percent = int(item.get("percent") or 0)
        except (TypeError, ValueError):
            percent = 0
        if revision and percent:
            traffic[str(revision)] = traffic.get(str(revision), 0) + percent
    return traffic


def prove_runtime_safety(
    service: dict[str, Any],
    rotator: dict[str, Any],
    scheduler: dict[str, Any],
    *,
    expected_rotator_service_account: str,
    expected_scheduler_service_account: str,
) -> dict[str, Any]:
    env, secret_env_names = service_environment(service)

    bad_live = [
        key for key in ("LIVE_TRADING_ENABLED", "SYSTEM3_LIVE_TRADING_ALLOWED", "AUTO_EXECUTE_TRADES")
        if env.get(key) not in OFF_VALUES
    ]
    if bad_live:
        raise ValueError(f"live_flags_not_off:{bad_live}")
    if env.get("DHAN_TOKEN_SOURCE") != "gcp-secret-manager-dynamic":
        raise ValueError("dynamic_token_source_missing")
    if env.get("DEFER_INSTRUMENT_WARMUP") != "1":
        raise ValueError("defer_instrument_warmup_missing")
    if str(env.get("REQUIRE_API_KEY") or "").lower() not in {"0", "false", "no", "off"}:
        raise ValueError("public_dashboard_mode_not_enforced")
    if "API_KEY" in secret_env_names:
        raise ValueError("dashboard_api_key_still_mounted")
    if "WORKER_PUSH_TOKEN" not in secret_env_names:
        raise ValueError("worker_push_token_secret_not_mounted")
    if "WORKER_PUSH_TOKEN" in env:
        raise ValueError("worker_push_token_plaintext")

    job_sa = rotator_service_account(rotator)
    if job_sa != expected_rotator_service_account:
        raise ValueError(f"rotator_identity_mismatch:{job_sa}")

    scheduler_sa = scheduler_service_account(scheduler)
    if scheduler_sa != expected_scheduler_service_account:
        raise ValueError(f"scheduler_identity_mismatch:{scheduler_sa}")

    traffic = serving_traffic(service)
    if len(traffic) != 1 or list(traffic.values()) != [100]:
        raise ValueError(f"serving_traffic_not_single_exact_revision:{traffic}")
    if scheduler.get("schedule") != EXPECTED_SCHEDULE or scheduler.get("timeZone") != EXPECTED_TIME_ZONE:
        raise ValueError("scheduler_config_invalid")

    return {
        "state": "PASS",
        "dashboard_access": "public-readonly",
        "rotator_service_account": job_sa,
        "scheduler_service_account": scheduler_sa,
        "serving_traffic": traffic,
        "live_trading_enabled": False,
        "secret_values_exposed": False,
    }


def main() -> int:
    try:
        service = json.loads(Path(os.getenv("SYSTEM3_SERVICE_JSON", "/tmp/svc.json")).read_text(encoding="utf-8"))
        rotator = json.loads(Path(os.getenv("SYSTEM3_ROTATOR_JSON", "/tmp/rotator.json")).read_text(encoding="utf-8"))
        scheduler = json.loads(Path(os.getenv("SYSTEM3_SCHEDULER_JSON", "/tmp/scheduler.json")).read_text(encoding="utf-8"))
        result = prove_runtime_safety(
            service,
            rotator,
            scheduler,
            expected_rotator_service_account=os.environ["DHAN_ROTATOR_SERVICE_ACCOUNT"],
            expected_scheduler_service_account=os.environ["DHAN_SCHEDULER_SERVICE_ACCOUNT"],
        )
        print("CLOUD_RUNTIME_SAFETY_OK " + json.dumps(result, sort_keys=True))
        return 0
    except Exception as exc:
        print(
            "CLOUD_RUNTIME_SAFETY_FAIL "
            + json.dumps({"error_type": type(exc).__name__, "error": str(exc)[:180]}, sort_keys=True),
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
