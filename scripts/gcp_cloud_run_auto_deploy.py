#!/usr/bin/env python3
"""Canonical Cloud Run deployment entrypoint with immutable digest proof.

The original deployment state machine is preserved byte-for-byte in
``gcp_cloud_run_auto_deploy_impl.py``. This entrypoint verifies that the
implementation still contains every critical PAPER/LIVE-OFF/candidate safety
invariant, replaces only the image-provenance assertion with the fail-closed
Artifact Registry repository+digest verifier, removes retired dashboard
credential secret mounts before any candidate revision can be created, and
converges the bounded business-lane Cloud Scheduler definitions before the
workflow's scheduler-proof stage.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

import gcp_cloud_run_auto_deploy_impl as deployer
from gcp_image_provenance import assert_same_artifact_image

_IMPL = Path(__file__).with_name("gcp_cloud_run_auto_deploy_impl.py")
PROJECT = deployer.PROJECT
REGION = os.getenv("GCP_REGION", "asia-south1")
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
)

_RETIRED_DASHBOARD_SECRET_ENV = "DASHBOARD_API_KEY"
_ORIGINAL_RUN = deployer._run


def _verify_implementation_contract() -> None:
    text = _IMPL.read_text(encoding="utf-8")
    missing = [marker for marker in _REQUIRED_IMPLEMENTATION_MARKERS if marker not in text]
    if missing:
        raise RuntimeError(f"deployment_safety_contract_missing:{missing}")


def _scrub_retired_dashboard_secret_arg(args: list[str]) -> list[str]:
    """Ensure every Cloud Run candidate explicitly removes retired dashboard auth.

    This is deliberately applied in the canonical wrapper because the preserved
    implementation is the PR #130 provenance state machine. It changes no LIVE,
    order, worker-token, or broker authority; it only removes a retired secret
    mount that must not survive on newly-created revisions.
    """
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


def _run_with_retired_dashboard_secret_scrub(
    args: list[str], *, capture: bool = False
) -> str:
    scrubbed = _scrub_retired_dashboard_secret_arg(args)
    if scrubbed != args:
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
            "gcloud",
            "scheduler",
            "jobs",
            "describe",
            name,
            f"--project={PROJECT}",
            f"--location={REGION}",
            "--format=value(name)",
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
        "gcloud",
        "scheduler",
        "jobs",
        action,
        "http",
        name,
        f"--project={PROJECT}",
        f"--location={REGION}",
        f"--schedule={BUSINESS_SCHEDULES[kind]}",
        "--time-zone=UTC",
        f"--uri={uri}",
        "--http-method=POST",
        f"--oauth-service-account-email={SCHEDULER_SA}",
        "--oauth-token-scope=https://www.googleapis.com/auth/cloud-platform",
        header_flag,
        "--message-body={}",
    ]


def _ensure_business_scheduler_contract() -> None:
    """Create or fully reconcile the three bounded business schedules.

    This function configures Scheduler metadata only. It never executes a Cloud
    Run job and never changes broker, token, order, or LIVE-trading authority.
    """
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


def main() -> int:
    _verify_implementation_contract()
    deployer._assert_candidate_image = _assert_candidate_image
    deployer._run = _run_with_retired_dashboard_secret_scrub
    result = deployer.main()
    if result:
        return result
    _ensure_business_scheduler_contract()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())