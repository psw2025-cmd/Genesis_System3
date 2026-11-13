"""Fail closed when an immutable Cloud Run build lacks a real commit SHA."""
from __future__ import annotations

import re
import sys

EXPECTED_IMAGE = (
    "asia-south1-docker.pkg.dev/system3-openalgo-safe/"
    "cloud-run-source-deploy/genesis-system3-web"
)


def validate(git_sha: str, image: str) -> None:
    if not re.fullmatch(r"[0-9a-f]{40}", str(git_sha or "")):
        raise ValueError("_GIT_SHA must be a full lowercase 40-character Git commit SHA")
    if image != EXPECTED_IMAGE:
        raise ValueError("_IMAGE must target the approved System3 Artifact Registry repository")


if __name__ == "__main__":
    try:
        if len(sys.argv) != 3:
            raise ValueError("usage: cloud_run_build_metadata_gate.py GIT_SHA IMAGE")
        validate(sys.argv[1], sys.argv[2])
    except ValueError as exc:
        print(f"CLOUD_RUN_BUILD_METADATA=FAIL reason={exc}", file=sys.stderr)
        raise SystemExit(2)
    print("CLOUD_RUN_BUILD_METADATA=PASS sha=full image=approved")
