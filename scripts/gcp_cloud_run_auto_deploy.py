#!/usr/bin/env python3
"""Canonical Cloud Run deployment entrypoint with immutable digest proof.

The original deployment state machine is preserved byte-for-byte in
``gcp_cloud_run_auto_deploy_impl.py``. This entrypoint verifies that the
implementation still contains every critical PAPER/LIVE-OFF/candidate safety
invariant, replaces only the image-provenance assertion with the fail-closed
Artifact Registry repository+digest verifier, removes retired/stale dashboard
and Dhan secret mounts before any candidate revision can be created, preserves
only the canonical web-side Dhan client-id binding plus worker token binding,
validates that web-triggered Dhan token rotation is OFF at the authoritative
SAFE_ENV source so Scheduler/manual recovery remain the only effective rotation
authorities, and converges the bounded business-lane Cloud Scheduler definitions
before the workflow's scheduler-proof stage.

Secret existence is intentionally not preflighted with Secret Manager metadata
reads by the deploy service account. The zero-traffic Cloud Run candidate is the
control-plane validator for referenced secrets: a missing/inaccessible binding
must fail candidate readiness before any production traffic is promoted.
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
    '("DHAN_CANONICAL_ROTATION_SELF_HEAL", "0")',
    '("DHAN_TOKEN_ROTATION_SCHEDULE", "*/5 * * * * Asia/Kolkata")',
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
_STALE_WEB_DHAN_SECRET_ENVS = (
    "DHAN_APP_ID",
    "DHAN_APP_SECRET",
    "DHAN_ACCESS_TOKEN",
    "DHAN_PIN",
    "DHAN_TOTP_SECRET",
    "DHAN_TOTP",
    "dhan-access-token",
)
_CANONICAL_WEB_DHAN_CLIENT_BINDING = "system3-dhan-client-id:latest"
_ORIGINAL_RUN = deployer._run


def _verify_implementation_contract() -> None:
    text = _IMPL.read_text(encoding="utf-8")
    missing = [marker for marker in _REQUIRED_IMPLEMENTATION_MARKERS if marker not in text]
    if missing:
        raise RuntimeError(f"deployment_safety_contract_missing:{missing}")


def _enforce_scheduler_only_dhan_rotation() -> None:
    """Validate the single authoritative web-side Dhan rotation contract.

    ``gcp_cloud_run_auto_deploy_impl.py::SAFE_ENV`` is the source of truth and
    must already declare web canonical self-heal OFF.  This wrapper intentionally
    does not rewrite a contradictory value at runtime: source/config drift must
    fail closed in CI/deploy instead of being masked by a second authority.

    Rotation authority remains Cloud Scheduler plus guarded manual recovery.
    The 5-minute Scheduler cadence is only a bounded trigger/check cadence; the
    rotator's independent 30-minute remint cooldown remains unchanged.
    """
    effective = dict(deployer.SAFE_ENV)
    if effective.get("DHAN_CANONICAL_ROTATION_SELF_HEAL") != "0":
        raise RuntimeError("dhan_web_rotation_not_disabled_at_source")
    if effective.get("DHAN_TOKEN_ROTATION_SCHEDULE") != "*/5 * * * * Asia/Kolkata":
        raise RuntimeError("dhan_rotation_schedule_source_drift")
    if effective.get("DHAN_CANONICAL_ROTATION_COOLDOWN_S") != "900":
        raise RuntimeError("dhan_canonical_rotation_cooldown_drift")
    if effective.get("DHAN_STATUS_AUTO_REFRESH") != "0":
        raise RuntimeError("dhan_web_status_auto_refresh_not_disabled")
    if effective.get("SYSTEM3_STARTUP_TOKEN_REFRESH") != "0":
        raise RuntimeError("dhan_web_startup_refresh_not_disabled")
    if effective.get("BROKER_SELF_HEAL_TOKEN_REFRESH") != "0":
        raise RuntimeError("dhan_web_legacy_self_heal_not_disabled")

    print(
        "DHAN_WEB_ROTATION_DISABLED",
        {
            "canonical_rotation_self_heal": False,
            "status_auto_refresh": False,
            "startup_token_refresh": False,
            "legacy_broker_self_heal": False,
            "rotation_schedule": effective["DHAN_TOKEN_ROTATION_SCHEDULE"],
            "rotation_authority": "gcp-scheduler-plus-guarded-manual-recovery",
            "secret_value_exposed": False,
            "live_trading_enabled": False,
            "order_placement_allowed": False,
        },
    )


def _parse_secret_bindings(arg: str) -> dict[str, str]:
    bindings: dict[str, str] = {}
    raw = arg.split("=", 1)[1] if "=" in arg else ""
    for item in raw.split(","):
        item = item.strip()
        if not item:
            continue
        if "=" not in item:
            raise RuntimeError(f"candidate_update_secret_binding_invalid:{item}")
        name, target = item.split("=", 1)
        name = name.strip()
        target = target.strip()
        if not name or not target:
            raise RuntimeError(f"candidate_update_secret_binding_invalid:{item}")
        bindings[name] = target
    return bindings


def _scrub_retired_dashboard_secret_arg(args: list[str]) -> list[str]:
    """Converge every Cloud Run candidate to the canonical web secret surface.

    Web needs only:
    - ``WORKER_PUSH_TOKEN`` for worker ingestion; and
    - ``DHAN_CLIENT_ID`` for read-only Dhan requests.

    The Dhan access token is loaded dynamically from Secret Manager by the web
    runtime service account. PIN/TOTP/app-secret/access-token mounts therefore
    have no place on the web service and are removed on every candidate deploy.
    """
    if args[:3] != ["gcloud", "run", "deploy"]:
        return list(args)

    result = list(args)
    remove_indexes = [i for i, arg in enumerate(result) if arg.startswith("--remove-secrets=")]
    if len(remove_indexes) != 1:
        raise RuntimeError(f"candidate_remove_secrets_contract_invalid:{len(remove_indexes)}")

    remove_idx = remove_indexes[0]
    names = [name.strip() for name in result[remove_idx].split("=", 1)[1].split(",") if name.strip()]
    if "API_KEY" not in names:
        raise RuntimeError("candidate_api_key_scrub_missing")
    for name in (_RETIRED_DASHBOARD_SECRET_ENV, *_STALE_WEB_DHAN_SECRET_ENVS):
        if name not in names:
            names.append(name)
    result[remove_idx] = "--remove-secrets=" + ",".join(names)

    update_indexes = [i for i, arg in enumerate(result) if arg.startswith("--update-secrets=")]
    if len(update_indexes) != 1:
        raise RuntimeError(f"candidate_update_secrets_contract_invalid:{len(update_indexes)}")
    update_idx = update_indexes[0]
    bindings = _parse_secret_bindings(result[update_idx])
    if "WORKER_PUSH_TOKEN" not in bindings:
        raise RuntimeError("candidate_worker_push_token_binding_missing")
    forbidden = sorted(set(bindings).intersection(_STALE_WEB_DHAN_SECRET_ENVS))
    if forbidden:
        raise RuntimeError(f"candidate_stale_dhan_secret_update_forbidden:{forbidden}")
    bindings["DHAN_CLIENT_ID"] = _CANONICAL_WEB_DHAN_CLIENT_BINDING
    result[update_idx] = "--update-secrets=" + ",".join(
        f"{name}={target}" for name, target in bindings.items()
    )
    return result


def _run_with_retired_dashboard_secret_scrub(
    args: list[str], *, capture: bool = False
) -> str:
    scrubbed = _scrub_retired_dashboard_secret_arg(args)
    if scrubbed != args:
        print("CANONICAL_WEB_SECRET_SURFACE enforced")
    return _ORIGINAL_RUN(scrubbed, capture=capture)


def _defer_worker_secret_validation_to_candidate(_session: object, secret_id: str) -> None:
    """Avoid a deployer Secret Manager metadata read it is not authorized to do.

    ``gcloud run deploy --update-secrets`` plus zero-traffic candidate readiness
    is the actual validation boundary. This keeps the deployer least-privileged
    while still failing closed before traffic promotion if the binding is bad.
    """
    normalized = str(secret_id or "").strip()
    if not normalized:
        raise RuntimeError("worker_push_token_secret_id_empty")
    print("WORKER_SECRET_VALIDATION_DEFERRED_TO_ZERO_TRAFFIC_CANDIDATE", normalized)


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
    """Create or fully reconcile the four bounded business schedules.

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
    _enforce_scheduler_only_dhan_rotation()
    deployer._assert_candidate_image = _assert_candidate_image
    deployer._run = _run_with_retired_dashboard_secret_scrub
    deployer._require_secret_exists = _defer_worker_secret_validation_to_candidate
    result = deployer.main()
    if result:
        return result
    _ensure_business_scheduler_contract()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
