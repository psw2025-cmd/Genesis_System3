#!/usr/bin/env python3
"""Read-only System3 production-source hint gate.

The deployment receipt supplies an *expected* SHA, not deployment authority or
production proof. The subsequent browser verifier must independently compare
the real public GCP service identity before AND after capture.
"""
from __future__ import annotations

import argparse
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = Path("SYSTEM3/02_EVIDENCE/DEPLOYMENT_LINEAGE.json")
OUT = Path("live-production-ui-proof/manifest.json")
IDENTITY = {
    "project_id": "system3-openalgo-safe",
    "project_number": "802404398783",
    "region": "asia-south1",
    "service": "genesis-system3-web",
}
SHA40 = re.compile(r"[a-f0-9]{40}\Z")
DIGEST = re.compile(r"sha256:[a-f0-9]{64}\Z")


def resolve(root: Path) -> dict:
    def blocked(reason: str) -> dict:
        return {
            "schema": "system3-release-proof-gate-v1",
            "state": "BLOCKED",
            "reason": reason,
            "observed_at_utc": datetime.now(timezone.utc).isoformat(),
            "production_pass": False,
            "gcp_mutations": 0,
            "broker_calls": 0,
            "order_calls": 0,
        }

    path = root / RECEIPT
    if not path.is_file():
        return blocked("DEPLOYMENT_LINEAGE_RECEIPT_MISSING")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeError):
        return blocked("DEPLOYMENT_LINEAGE_RECEIPT_INVALID")
    if not isinstance(data, dict):
        return blocked("DEPLOYMENT_LINEAGE_SCHEMA_INVALID")
    if any(data.get(k) != v for k, v in IDENTITY.items()):
        return blocked("DEPLOYMENT_IDENTITY_MISMATCH")
    sha = data.get("source_sha")
    digest = data.get("image_digest")
    if not isinstance(sha, str) or not SHA40.fullmatch(sha):
        return blocked("DEPLOYMENT_SOURCE_SHA_INVALID")
    if not isinstance(digest, str) or not DIGEST.fullmatch(digest):
        return blocked("DEPLOYMENT_IMAGE_DIGEST_INVALID")
    if data.get("state") != "DEPLOYED" or not isinstance(data.get("owner_approval_ref"), str) or not data["owner_approval_ref"].strip():
        return blocked("DEPLOYMENT_RECEIPT_NOT_OWNER_APPROVED")
    return {
        "schema": "system3-release-proof-gate-v1",
        "state": "EXPECTED_SHA_RESOLVED",
        "reason": "INDEPENDENT_LIVE_RUNTIME_CHECK_REQUIRED",
        "expected_source_sha": sha,
        "image_digest": digest,
        "production_pass": False,
        "source_authority": "RECEIPT_HINT_ONLY_NOT_SERVING_PROOF",
        "observed_at_utc": datetime.now(timezone.utc).isoformat(),
        "gcp_mutations": 0,
        "broker_calls": 0,
        "order_calls": 0,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=ROOT)
    parser.add_argument("--write-github-env", action="store_true")
    args = parser.parse_args(argv)
    root = args.repo.resolve()
    result = resolve(root)
    if result["state"] != "EXPECTED_SHA_RESOLVED":
        path = root / OUT
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        print("LIVE_PRODUCTION_UI_CAPTURE=BLOCKED reason=" + result["reason"])
        return 2
    if args.write_github_env:
        env_file = os.getenv("GITHUB_ENV", "").strip()
        if not env_file:
            print("LIVE_PRODUCTION_UI_CAPTURE=BLOCKED reason=GITHUB_ENV_MISSING")
            return 2
        with open(env_file, "a", encoding="utf-8") as out:
            out.write("SYSTEM3_EXPECTED_SERVING_SHA=" + result["expected_source_sha"] + "\n")
    print("EXPECTED_SHA_RESOLVED; LIVE_PRODUCTION_UI_PROOF=NOT_PROVEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
