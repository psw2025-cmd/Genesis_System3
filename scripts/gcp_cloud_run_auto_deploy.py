#!/usr/bin/env python3
"""Canonical Cloud Run deployment entrypoint with immutable digest proof.

The original deployment state machine is preserved byte-for-byte in
``gcp_cloud_run_auto_deploy_impl.py``. This entrypoint verifies that the
implementation still contains every critical PAPER/LIVE-OFF/candidate safety
invariant, replaces only the image-provenance assertion with the fail-closed
Artifact Registry repository+digest verifier, and removes retired dashboard
credential secret mounts before any candidate revision can be created.
"""
from __future__ import annotations

from pathlib import Path

import gcp_cloud_run_auto_deploy_impl as deployer
from gcp_image_provenance import assert_same_artifact_image

_IMPL = Path(__file__).with_name("gcp_cloud_run_auto_deploy_impl.py")
PROJECT = deployer.PROJECT
RUNTIME_SA = f"genesis-system3-web@{PROJECT}.iam.gserviceaccount.com"

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


def main() -> int:
    _verify_implementation_contract()
    deployer._assert_candidate_image = _assert_candidate_image
    deployer._run = _run_with_retired_dashboard_secret_scrub
    return deployer.main()


if __name__ == "__main__":
    raise SystemExit(main())
