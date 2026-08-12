#!/usr/bin/env python3
"""Canonical guarded entrypoint for Cloud Run deployment with immutable image proof.

This wrapper preserves the existing deployment state machine and replaces only
its image-provenance assertion with the fail-closed Artifact Registry
repository+digest verifier. LIVE/order safety remains owned by the canonical
deployer.
"""
from __future__ import annotations

import gcp_cloud_run_auto_deploy as deployer
from gcp_image_provenance import assert_same_artifact_image


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
    deployer._assert_candidate_image = _assert_candidate_image
    return deployer.main()


if __name__ == "__main__":
    raise SystemExit(main())
