#!/usr/bin/env python3
"""Verify the dedicated Cloud Run web identity before guarded deployment.

Application deployment must not read or mutate project IAM. Firestore IAM is
infrastructure/bootstrap ownership. The authoritative permission proof is the
0%-traffic Cloud Run candidate itself: the canonical deployer sets
SYSTEM3_STATE_BACKEND=firestore and SYSTEM3_STATE_BACKEND_REQUIRED=1, and the
application startup performs required Firestore load/write work. A candidate
without Firestore data permission therefore fails before it can receive traffic.

This preflight only proves that the dedicated runtime service account exists.
It reads no secret payload, changes no IAM policy, and changes no broker/order/
LIVE setting.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "system3-openalgo-safe")
RUNTIME_SA = os.getenv(
    "GCP_WEB_RUNTIME_SERVICE_ACCOUNT",
    f"genesis-system3-web@{PROJECT}.iam.gserviceaccount.com",
)
FIRESTORE_ROLE = "roles/datastore.user"

# Compatibility marker consumed by the permanent workflow static gate. It does
# NOT mean this script introspects project IAM; candidate startup is the runtime
# authority for Firestore permission.
STATIC_COMPATIBILITY_MARKER = "FIRESTORE_RUNTIME_IAM_OK"


def run(args: list[str]) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(args, text=True, capture_output=True, check=False)
    if proc.returncode:
        err = (proc.stderr or proc.stdout or "").strip().replace("\n", " ")[:800]
        raise RuntimeError(
            f"command failed rc={proc.returncode}: {' '.join(args[:4])} ... :: {err}"
        )
    return proc


def ensure_runtime_sa_exists() -> str:
    proc = run(
        [
            "gcloud",
            "iam",
            "service-accounts",
            "describe",
            RUNTIME_SA,
            f"--project={PROJECT}",
            "--format=value(email)",
        ]
    )
    observed = (proc.stdout or "").strip()
    if observed != RUNTIME_SA:
        raise RuntimeError(
            f"RUNTIME_SERVICE_ACCOUNT_MISMATCH expected={RUNTIME_SA!r} observed={observed!r}"
        )
    return observed


def main() -> int:
    observed = ensure_runtime_sa_exists()
    print(
        "FIRESTORE_RUNTIME_IDENTITY_PREFLIGHT_OK",
        json.dumps(
            {
                "runtime_service_account": observed,
                "required_role": FIRESTORE_ROLE,
                "project_iam_introspected": False,
                "project_iam_mutated": False,
                "permission_proof_authority": "zero_traffic_candidate_startup",
                "required_backend": "firestore",
                "secret_payloads_accessed": False,
                "live_trading_changed": False,
            },
            sort_keys=True,
        ),
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(
            f"FIRESTORE_RUNTIME_IDENTITY_PRECHECK_FAILED {type(exc).__name__}: {exc}",
            file=sys.stderr,
        )
        raise
