#!/usr/bin/env python3
"""Resolve the Git SHA that the Cloud Run service is expected to serve.

A proof-only commit can advance repository `main` without triggering Cloud Run. For
live UI proof we therefore need the newest *first-parent* commit that changed one of
the exact path patterns from `.github/workflows/cloud-run-auto-deploy.yml`.

SYSTEM3_TEMPORAL_TRUTH_V1: current repository HEAD is not automatically current
serving runtime identity.
"""
from __future__ import annotations

import argparse
import fnmatch
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Keep exactly aligned with Cloud Run Auto Deploy `on.push.paths`.
DEPLOY_TRIGGER_PATTERNS = (
    "dashboard/**",
    "core/**",
    "scripts/gcp_worker_job.py",
    "scripts/smoke_ml_validate_e2e.py",
    "scripts/start_cloud_run.py",
    "scripts/gcp_dhan_token_rotation_job.py",
    "scripts/gcp_cloud_run_auto_deploy.py",
    "scripts/gcp_runtime_iam_preflight.py",
    "scripts/gcp_failed_revision_forensic.py",
    "scripts/gcp_runtime_evidence.py",
    "scripts/gcp_public_dashboard_runtime_proof.py",
    "scripts/gcp_mutation_policy_runtime_proof.py",
    "scripts/gcp_runtime_identity_safety.py",
    "scripts/sync_dhan_instruments_master.py",
    "src/**",
    "config/**",
    "deploy/gcp/**",
    ".github/workflows/cloud-run-auto-deploy.yml",
    ".github/workflows/gcp-dhan-token-rotation.yml",
)


def _git(*args: str) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return proc.stdout.strip()


def path_triggers_deploy(path: str) -> bool:
    clean = path.strip().replace("\\", "/")
    return bool(clean) and any(fnmatch.fnmatchcase(clean, pattern) for pattern in DEPLOY_TRIGGER_PATTERNS)


def changed_files_first_parent(commit: str) -> list[str]:
    try:
        parent = _git("rev-parse", f"{commit}^1")
    except subprocess.CalledProcessError:
        output = _git("show", "--pretty=format:", "--name-only", commit)
        return [line for line in output.splitlines() if line.strip()]
    output = _git("diff", "--name-only", parent, commit)
    return [line for line in output.splitlines() if line.strip()]


def resolve_runtime_deploy_sha(head: str = "HEAD") -> tuple[str, list[str]]:
    commits = _git("rev-list", "--first-parent", head).splitlines()
    for commit in commits:
        changed = changed_files_first_parent(commit)
        matched = [path for path in changed if path_triggers_deploy(path)]
        if matched:
            return commit, matched
    raise RuntimeError("NO_RUNTIME_AFFECTING_COMMIT_FOUND")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--write-github-env", action="store_true")
    args = parser.parse_args()

    sha, matched = resolve_runtime_deploy_sha(args.head)
    print(f"SYSTEM3_EXPECTED_SERVING_SHA={sha}")
    print("SYSTEM3_RUNTIME_TRIGGER_PATHS=" + ",".join(matched))

    if args.write_github_env:
        github_env = os.getenv("GITHUB_ENV", "").strip()
        if not github_env:
            raise SystemExit("GITHUB_ENV_MISSING")
        with open(github_env, "a", encoding="utf-8") as handle:
            handle.write(f"SYSTEM3_EXPECTED_SERVING_SHA={sha}\n")
            handle.write("SYSTEM3_RUNTIME_TRIGGER_PATHS=" + ",".join(matched) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
