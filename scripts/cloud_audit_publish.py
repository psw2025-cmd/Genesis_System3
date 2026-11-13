#!/usr/bin/env python3
"""Publish approved GitHub audit reports to immutable, readback-verified GCS paths.

Only GitHub main push workflows should invoke this module. No Cloud Run, IAM,
Secret Manager, database or broker APIs are used. Exact file allow-list only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

BUCKET = "system3-openalgo-safe-reports"
FILES = (
    "SYSTEM_INVENTORY.md",
    "PRODUCTION_READINESS_TRUTH.md",
    "FAKE_COMPONENTS_REPORT.md",
    "PREDICTION_LIFECYCLE_REPORT.md",
    "READY_FOR_LIVE_TRACE.md",
    "PAPER_TRADING_AUDIT.md",
    "RECONCILIATION_TRUTH.md",
    "WALK_FORWARD_TRUTH.md",
    "ML_TRUTH_REPORT.md",
    "SAFETY_AUDIT.md",
    "TOP20_RELEASE_BLOCKERS.md",
    "EXECUTIVE_TRUTH_REPORT.md",
    "executive_summary.json",
)
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def authorized_files(root: Path):
    audit = root / "audit_results"
    if not audit.is_dir() or audit.is_symlink():
        raise ValueError("AUDIT_DIRECTORY_MISSING_OR_SYMLINK")
    paths = {}
    for name in FILES:
        file = audit / name
        if not file.is_file() or file.is_symlink() or file.stat().st_size > 4_000_000:
            raise ValueError("REQUIRED_AUDIT_FILE_MISSING_OR_UNSAFE: " + name)
        paths[name] = file.read_bytes()
    summary = json.loads(paths["executive_summary.json"])
    if not isinstance(summary, dict) or not SHA_RE.fullmatch(str(summary.get("source_sha", ""))):
        raise ValueError("AUDITED_SOURCE_SHA_UNVERIFIED")
    return paths, summary["source_sha"]


def gcloud(*args):
    try:
        result = subprocess.run(
            ["gcloud.cmd" if os.name == "nt" else "gcloud", "storage", *args],
            text=True, capture_output=True, check=False, timeout=180
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise RuntimeError("GCS_OPERATION_UNAVAILABLE: " + type(exc).__name__) from None
    if result.returncode:
        # Classify safe error codes, never print raw upstream stderr.
        error = (result.stderr or "").lower()
        if any(x in error for x in ("403", "permission_denied", "permission denied", "access denied", "not have permission")):
            reason = "PERMISSION_DENIED"
        elif "requester pays" in error or "billing project" in error:
            reason = "BILLING_PROJECT_REQUIRED"
        elif any(x in error for x in ("unrecognized arguments", "invalid choice", "unknown argument")):
            reason = "INVALID_GCLOUD_ARGUMENT"
        elif "404" in error or "not found" in error:
            reason = "RESOURCE_NOT_FOUND"
        elif "precondition" in error or "412" in error:
            reason = "GENERATION_PRECONDITION_FAILED"
        else:
            reason = "UNKNOWN_GCLOUD_ERROR"
        raise RuntimeError("GCS_" + reason + "_OP_" + str(args[0]).upper())
    return result


def copy_and_verify(source: Path, destination: str, runner=gcloud):
    # No-clobber protects previously published evidence even on reruns.
    runner("cp", "--no-clobber", "--quiet", str(source), destination)
    with tempfile.TemporaryDirectory(prefix="genesis-audit-readback-") as temp:
        local = Path(temp) / "readback.bin"
        runner("cp", "--quiet", destination, str(local))
        if not local.is_file():
            raise RuntimeError("GCS_READBACK_MISSING")
        if digest(source.read_bytes()) != digest(local.read_bytes()):
            raise RuntimeError("GCS_READBACK_SHA256_MISMATCH")
    return digest(source.read_bytes())


def publish(root: Path, commit: str, runner=gcloud):
    if not SHA_RE.fullmatch(commit):
        raise ValueError("INVALID_PUBLICATION_COMMIT_SHA")
    sources, audited_sha = authorized_files(root)
    prefix = f"gs://{BUCKET}/genesis-audits/{commit}/"
    receipt = {
        "schema": "genesis-immutable-gcs-audit-receipt-v1",
        "publication_commit_sha": commit,
        "audited_source_sha": audited_sha,
        "objects": {},
        "object_count": len(FILES),
        "production_traffic_mutated": False,
        "broker_orders_placed": 0,
    }
    with tempfile.TemporaryDirectory(prefix="genesis-audit-publish-") as tmp:
        temp = Path(tmp)
        for name in FILES:
            file = temp / name
            file.write_bytes(sources[name])
            sha = copy_and_verify(file, prefix + name, runner)
            receipt["objects"][name] = {"sha256": sha, "bytes": len(sources[name])}
            print("AUDIT_GCS_READBACK_PASS file=" + name + " sha256=" + sha, flush=True)
        manifest = temp / "publication-receipt.json"
        manifest.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        receipt_sha = copy_and_verify(manifest, prefix + "publication-receipt.json", runner)
    print("AUDIT_GCS_PUBLICATION_PASS objects=" + str(len(FILES) + 1), flush=True)
    print("AUDIT_GCS_PREFIX=" + prefix, flush=True)
    print("AUDIT_GCS_RECEIPT_SHA256=" + receipt_sha, flush=True)
    return receipt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--publication-sha", required=True)
    args = parser.parse_args()
    publish(args.repo_root.resolve(), args.publication_sha)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
