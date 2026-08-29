"""Script to push branch, open PR, and query gcloud services cleanly."""

import json
import os
import subprocess
from pathlib import Path


def run_cmd(args):
    try:
        p = subprocess.run(
            args,
            capture_output=True,
            text=True,
            cwd="C:/Users/ADMIN/Genesis_System3/Genesis_System3",
        )
        return (p.stdout.strip() or p.stderr.strip()).replace("\r\n", "\n")
    except Exception as e:
        return str(e)


def main():
    print("=== 1. CREATE BRANCH & PUSH ===")
    out_branch = run_cmd(
        ["git", "checkout", "-b", "feat/streaming-intelligence-platform-20260829"]
    )
    print("Checkout output:", out_branch)

    out_push = run_cmd(
        [
            "git",
            "push",
            "-u",
            "origin",
            "feat/streaming-intelligence-platform-20260829",
        ]
    )
    print("Push output:", out_push)

    print("\n=== 2. CREATE PR ===")
    pr_body = (
        "Auditable streaming intelligence implementation covering 44-field option chain contracts, "
        "Firestore/GCS state persistence, backtesting audit manifests, and multibagger research workspace.\n\n"
        "Evidence doc: docs/evidence/SYSTEM3_STREAMING_INTELLIGENCE_EVIDENCE_CORRECTED_20260829T083000Z.md\n"
        "Commit SHA: 078f7ff20"
    )
    out_pr = run_cmd(
        [
            "gh",
            "pr",
            "create",
            "--base",
            "main",
            "--head",
            "feat/streaming-intelligence-platform-20260829",
            "--title",
            "feat(streaming): implement auditable streaming intelligence platform and 44-field option chain contracts",
            "--body",
            pr_body,
        ]
    )
    print("PR output:", out_pr)

    print("\n=== 3. GCLOUD RUN DESCRIBE ===")
    out_run = run_cmd(
        [
            "gcloud",
            "run",
            "services",
            "describe",
            "genesis-system3-web",
            "--region=asia-south1",
            "--format=yaml(status.traffic,status.latestReadyRevisionName,status.url,spec.template.spec.serviceAccountName)",
        ]
    )
    print("Cloud Run details:\n", out_run)

    print("\n=== 4. GCLOUD STORAGE CHECK ===")
    out_gcs = run_cmd(["gcloud", "storage", "ls", "gs://system3-openalgo-safe-artifacts/"])
    print("GCS Buckets output:\n", out_gcs)


if __name__ == "__main__":
    main()
