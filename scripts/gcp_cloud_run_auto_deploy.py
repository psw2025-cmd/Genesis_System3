#!/usr/bin/env python3
"""Canonical Cloud Run deployment entrypoint with immutable digest proof.

The original deployment state machine is preserved in
``gcp_cloud_run_auto_deploy_impl.py``. This entrypoint verifies that the
implementation still contains every critical PAPER/LIVE-OFF/candidate safety
invariant, replaces only the image-provenance assertion with the fail-closed
Artifact Registry repository+digest verifier, removes retired dashboard
credential secret mounts before any candidate revision can be created,
converges bounded business-lane Cloud Scheduler definitions, and enforces the
Cloud Run/Monitoring traffic-resilience contract.
"""
from __future__ import annotations

import json
import os
import subprocess
import urllib.request
from pathlib import Path
from typing import Any

import gcp_cloud_run_auto_deploy_impl as deployer
from gcp_image_provenance import assert_same_artifact_image

_IMPL = Path(__file__).with_name("gcp_cloud_run_auto_deploy_impl.py")
PROJECT = deployer.PROJECT
REGION = os.getenv("GCP_REGION", "asia-south1")
SERVICE = os.getenv("GCP_CLOUD_RUN_SERVICE", "genesis-system3-web")
RUNTIME_SA = f"genesis-system3-web@{PROJECT}.iam.gserviceaccount.com"
SCHEDULER_SA = os.getenv(
    "DHAN_SCHEDULER_SERVICE_ACCOUNT",
    f"gs3-scheduler@{PROJECT}.iam.gserviceaccount.com",
)
BUSINESS_SCHEDULES = {
    "rank": "45 3 * * MON-FRI",
    "forecast": "0 4 * * MON-FRI",
    "validate": "5 10 * * MON-FRI",  # 15:35 IST post-close Spearman day
    "signals": "15 13 * * MON-FRI",
}

# Keep max instances unchanged until saturation telemetry proves Cloud Run is
# the dominant 429 source. Raising it prematurely can multiply process-local
# Dhan request budgets across instances.
TRAFFIC_RUNTIME_ENV = {
    "SYSTEM3_TRAFFIC_SHIELD_MAX_PRODUCERS": "8",
    "SYSTEM3_TRAFFIC_SHIELD_FRESH_S": "3",
    "SYSTEM3_TRAFFIC_SHIELD_STALE_S": "60",
    "SYSTEM3_TRAFFIC_SHIELD_WAIT_S": "1.5",
    "SYSTEM3_TRAFFIC_SHIELD_RETRY_AFTER_S": "3",
    "SYSTEM3_CLOUD_RUN_MAX_INSTANCES": "2",
}

# These are executable preconditions: the wrapper refuses to deploy if the
# preserved implementation loses any of these exact safety/provenance markers.
_REQUIRED_IMPLEMENTATION_MARKERS = (
    '"--no-traffic"',
    'f"--tag={CANDIDATE_TAG}"',
    'f"--to-revisions={candidate}=100"',
    '("LIVE_TRADING_ENABLED", "0")',
    '("SYSTEM3_LIVE_TRADING_ALLOWED", "0")',
    '("AUTO_EXECUTE_TRADES", "0")',
    '("REQUIRE_API_KEY", "false")',
    '("DEFER_INSTRUMENT_WARMUP", "1")',
    '("SYSTEM3_STATE_BACKEND", "firestore")',
    '("SYSTEM3_STATE_BACKEND_REQUIRED", "1")',
    '--remove-secrets=API_KEY',
    '--update-secrets=WORKER_PUSH_TOKEN=',
    'WORKER_PUSH_TOKEN_SECRET_ID',
    'DASHBOARD_PUBLIC_READONLY enforced',
    '_traffic_allocations',
    '_wait_revision_ready',
    'gcp_failed_revision_forensic.py',
    'PREVIOUS_TRAFFIC_RESTORED',
    '"--min=1", "--max=2"',
    '"--concurrency=50"',
)

_RETIRED_DASHBOARD_SECRET_ENV = "DASHBOARD_API_KEY"
_ORIGINAL_RUN = deployer._run


def _verify_implementation_contract() -> None:
    text = _IMPL.read_text(encoding="utf-8")
    missing = [marker for marker in _REQUIRED_IMPLEMENTATION_MARKERS if marker not in text]
    if missing:
        raise RuntimeError(f"deployment_safety_contract_missing:{missing}")


def _harden_candidate_runtime_args(args: list[str]) -> list[str]:
    """Converge one candidate command to the traffic/WebSocket runtime contract."""
    if args[:3] != ["gcloud", "run", "deploy"]:
        return list(args)
    result = list(args)

    # Cloud Run WebSockets are still requests; 300s caused periodic reconnect
    # bursts. 60m is Cloud Run's supported maximum, while browser reconnects
    # remain exponential/jittered. Session affinity is best effort only; durable
    # truth remains Firestore and never depends on reconnecting to one instance.
    result = ["--timeout=3600" if item == "--timeout=300" else item for item in result]
    if "--session-affinity" not in result:
        quiet_index = result.index("--quiet") if "--quiet" in result else len(result)
        result.insert(quiet_index, "--session-affinity")

    env_indexes = [i for i, item in enumerate(result) if item.startswith("--update-env-vars=")]
    if len(env_indexes) != 1:
        raise RuntimeError(f"candidate_update_env_contract_invalid:{len(env_indexes)}")
    env_index = env_indexes[0]
    env_blob = result[env_index].split("=", 1)[1]
    for name, value in TRAFFIC_RUNTIME_ENV.items():
        marker = f"{name}="
        if marker not in env_blob:
            env_blob += f",{name}={value}"
    result[env_index] = "--update-env-vars=" + env_blob
    return result


def _scrub_retired_dashboard_secret_arg(args: list[str]) -> list[str]:
    """Ensure every Cloud Run candidate explicitly removes retired dashboard auth."""
    if args[:3] != ["gcloud", "run", "deploy"]:
        return list(args)

    result = list(args)
    indexes = [i for i, arg in enumerate(result) if arg.startswith("--remove-secrets=")]
    if len(indexes) != 1:
        raise RuntimeError(f"candidate_remove_secrets_contract_invalid:{len(indexes)}")

    idx = indexes[0]
    names = [name.strip() for name in result[idx].split("=", 1)[1].split(",") if name.strip()]
    if "API_KEY" not in names:
        raise RuntimeError("candidate_api_key_scrub_missing")
    if _RETIRED_DASHBOARD_SECRET_ENV not in names:
        names.append(_RETIRED_DASHBOARD_SECRET_ENV)
    result[idx] = "--remove-secrets=" + ",".join(names)
    return result


def _run_with_runtime_contract(args: list[str], *, capture: bool = False) -> str:
    hardened = _harden_candidate_runtime_args(args)
    scrubbed = _scrub_retired_dashboard_secret_arg(hardened)
    if scrubbed != args and args[:3] == ["gcloud", "run", "deploy"]:
        print("CANDIDATE_TRAFFIC_RUNTIME_CONTRACT enforced")
        print("RETIRED_DASHBOARD_SECRET_SCRUB enforced")
    return _ORIGINAL_RUN(scrubbed, capture=capture)


def _assert_candidate_image(revision: dict, image: str) -> None:
    containers = ((revision.get("spec") or {}).get("containers") or [])
    if not containers:
        containers = ((((revision.get("spec") or {}).get("template") or {}).get("spec") or {}).get("containers") or [])
    deployed_image = str((containers[0] if containers else {}).get("image") or "")
    if not deployed_image:
        raise RuntimeError("candidate image missing from revision")
    repository, digest = assert_same_artifact_image(image, deployed_image)
    print("CANDIDATE_IMAGE_PROVENANCE_OK", f"{repository}@{digest}")


def _scheduler_exists(name: str) -> bool:
    """Return exact scheduler existence; auth/API errors fail closed."""
    proc = subprocess.run(
        [
            "gcloud", "scheduler", "jobs", "describe", name,
            f"--project={PROJECT}", f"--location={REGION}", "--format=value(name)",
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode == 0:
        return True

    detail = ((proc.stderr or "") + " " + (proc.stdout or "")).strip()
    lowered = detail.lower()
    if "not_found" in lowered or "not found" in lowered or "does not exist" in lowered:
        return False
    raise RuntimeError(
        f"business_scheduler_describe_failed:{name}:rc={proc.returncode}:{detail[:300]}"
    )


def _business_scheduler_command(kind: str, *, exists: bool) -> list[str]:
    if kind not in BUSINESS_SCHEDULES:
        raise RuntimeError(f"unsupported_business_scheduler_kind:{kind}")
    action = "update" if exists else "create"
    name = f"genesis-system3-{kind}-daily"
    uri = (
        "https://run.googleapis.com/v2/projects/"
        f"{PROJECT}/locations/{REGION}/jobs/genesis-system3-{kind}:run"
    )
    header_flag = (
        "--update-headers=Content-Type=application/json"
        if exists
        else "--headers=Content-Type=application/json"
    )
    return [
        "gcloud", "scheduler", "jobs", action, "http", name,
        f"--project={PROJECT}", f"--location={REGION}",
        f"--schedule={BUSINESS_SCHEDULES[kind]}", "--time-zone=UTC",
        f"--uri={uri}", "--http-method=POST",
        f"--oauth-service-account-email={SCHEDULER_SA}",
        "--oauth-token-scope=https://www.googleapis.com/auth/cloud-platform",
        header_flag, "--message-body={}",
    ]


def _ensure_business_scheduler_contract() -> None:
    """Create or fully reconcile the bounded business schedules."""
    for kind in BUSINESS_SCHEDULES:
        exists = _scheduler_exists(f"genesis-system3-{kind}-daily")
        command = _business_scheduler_command(kind, exists=exists)
        _ORIGINAL_RUN(command)
        print(
            "BUSINESS_SCHEDULER_CONVERGED",
            {
                "kind": kind,
                "action": "update" if exists else "create",
                "schedule": BUSINESS_SCHEDULES[kind],
                "live_trading_enabled": False,
                "order_action_performed": False,
                "business_job_executed": False,
            },
        )


def _configure_traffic_monitoring() -> None:
    """Fail before production mutation if 24x7 Monitoring cannot be converged."""
    from gcp_configure_traffic_monitoring import main as monitoring_main

    # Keep the monitor's saturation threshold bound to the exact deploy cap.
    os.environ.setdefault("SYSTEM3_CLOUD_RUN_MAX_INSTANCES", TRAFFIC_RUNTIME_ENV["SYSTEM3_CLOUD_RUN_MAX_INSTANCES"])
    rc = int(monitoring_main() or 0)
    if rc != 0:
        raise RuntimeError(f"traffic_monitoring_configuration_failed:{rc}")
    print("SYSTEM3_TRAFFIC_MONITORING_CONTRACT enforced")


def _validate_traffic_runtime(payload: Any) -> list[str]:
    body = payload if isinstance(payload, dict) else {}
    failures: list[str] = []
    if body.get("status") != "ENFORCED":
        failures.append("traffic_shield_not_enforced")
    if body.get("legacy_fixed_delay_middleware_retired") is not True:
        failures.append("legacy_delay_middleware_not_retired")
    if int(body.get("legacy_fixed_delay_middleware_removed_count", 0) or 0) != 1:
        failures.append("legacy_delay_middleware_removed_count_not_one")
    if int(body.get("max_concurrent_producers", 0) or 0) != int(TRAFFIC_RUNTIME_ENV["SYSTEM3_TRAFFIC_SHIELD_MAX_PRODUCERS"]):
        failures.append("traffic_producer_cap_mismatch")
    if body.get("mutation_routes_shielded") is not False:
        failures.append("mutation_routes_unexpectedly_shielded")
    if body.get("live_trading_enabled") is not False:
        failures.append("traffic_runtime_live_not_false")
    if body.get("client_contract") != "RETRY_AFTER_EXPONENTIAL_BACKOFF_JITTER":
        failures.append("client_backoff_contract_missing")
    if body.get("public_dashboard_read_only") is not True:
        failures.append("public_readonly_contract_missing")
    return failures


def _prove_traffic_runtime() -> None:
    service_url = _ORIGINAL_RUN(
        [
            "gcloud", "run", "services", "describe", SERVICE,
            f"--project={PROJECT}", f"--region={REGION}", "--format=value(status.url)",
        ],
        capture=True,
    ).strip().rstrip("/")
    if not service_url.startswith("https://"):
        raise RuntimeError("traffic_runtime_service_url_missing")
    request = urllib.request.Request(
        f"{service_url}/api/traffic/health",
        headers={"User-Agent": "genesis-system3-traffic-runtime-proof"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        if int(getattr(response, "status", 0) or 0) != 200:
            raise RuntimeError(f"traffic_runtime_http_{getattr(response, 'status', 0)}")
        payload = json.loads(response.read().decode("utf-8"))
    failures = _validate_traffic_runtime(payload)
    if failures:
        raise RuntimeError(f"traffic_runtime_proof_failed:{failures}")
    print(
        "SYSTEM3_TRAFFIC_RUNTIME_PROOF",
        {
            "status": "PASS",
            "service_url": service_url,
            "max_concurrent_producers": payload.get("max_concurrent_producers"),
            "legacy_fixed_delay_middleware_retired": True,
            "mutation_routes_shielded": False,
            "live_trading_enabled": False,
        },
    )


def main() -> int:
    _verify_implementation_contract()
    # Alerting must converge before a candidate can alter production runtime.
    _configure_traffic_monitoring()
    deployer._assert_candidate_image = _assert_candidate_image
    deployer._run = _run_with_runtime_contract
    result = deployer.main()
    if result:
        return result
    # The serving revision must prove the new shield before the deploy can pass.
    _prove_traffic_runtime()
    _ensure_business_scheduler_contract()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
