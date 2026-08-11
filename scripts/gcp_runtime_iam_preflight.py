#!/usr/bin/env python3
"""Ensure the dedicated Cloud Run web identity can use required Firestore state.

This is an idempotent deployment prerequisite, not application runtime logic.
The web service uses Firestore as required shared state and must fail closed if
that authority is unavailable. We therefore repair/verify the narrow predefined
Firestore data role before creating a candidate revision instead of weakening
SYSTEM3_STATE_BACKEND_REQUIRED or falling back to local files.

No secret payload is read. No broker/order/live setting is changed.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time

PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "system3-openalgo-safe")
RUNTIME_SA = os.getenv(
    "GCP_WEB_RUNTIME_SERVICE_ACCOUNT",
    f"genesis-system3-web@{PROJECT}.iam.gserviceaccount.com",
)
FIRESTORE_ROLE = "roles/datastore.user"
MEMBER = f"serviceAccount:{RUNTIME_SA}"


def run(args: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(args, text=True, capture_output=True, check=False)
    if check and proc.returncode:
        # Print only command class and sanitized stderr. gcloud IAM errors do not
        # contain secret payloads, but cap output to avoid noisy evidence logs.
        err = (proc.stderr or proc.stdout or "").strip().replace("\n", " ")[:800]
        raise RuntimeError(f"command failed rc={proc.returncode}: {' '.join(args[:4])} ... :: {err}")
    return proc


def binding_present() -> bool:
    proc = run(
        [
            "gcloud",
            "projects",
            "get-iam-policy",
            PROJECT,
            "--flatten=bindings[].members",
            f"--filter=bindings.role:{FIRESTORE_ROLE} AND bindings.members:{MEMBER}",
            "--format=value(bindings.role)",
        ]
    )
    return FIRESTORE_ROLE in (proc.stdout or "").splitlines()


def ensure_runtime_sa_exists() -> None:
    run(
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


def grant_binding() -> None:
    proc = run(
        [
            "gcloud",
            "projects",
            "add-iam-policy-binding",
            PROJECT,
            f"--member={MEMBER}",
            f"--role={FIRESTORE_ROLE}",
            "--condition=None",
            "--quiet",
        ],
        check=False,
    )
    if proc.returncode:
        err = (proc.stderr or proc.stdout or "").strip().replace("\n", " ")[:800]
        raise RuntimeError(
            "FIRESTORE_RUNTIME_IAM_GRANT_FAILED: deployment identity could not "
            f"grant {FIRESTORE_ROLE} to {RUNTIME_SA}; rc={proc.returncode}; {err}"
        )


def main() -> int:
    ensure_runtime_sa_exists()
    already = binding_present()
    if not already:
        print(
            "FIRESTORE_RUNTIME_IAM_MISSING",
            json.dumps({"runtime_service_account": RUNTIME_SA, "required_role": FIRESTORE_ROLE}),
        )
        grant_binding()
        # IAM changes may take time to propagate. Do not pretend the new role is
        # usable until the policy itself contains the exact binding. Candidate
        # startup remains fail-closed if Firestore still denies during propagation.
        for attempt in range(1, 7):
            if binding_present():
                break
            print(f"FIRESTORE_RUNTIME_IAM_WAIT[{attempt}]")
            time.sleep(10)
        else:
            raise RuntimeError("FIRESTORE_RUNTIME_IAM_BINDING_NOT_VISIBLE_AFTER_GRANT")

    if not binding_present():
        raise RuntimeError("FIRESTORE_RUNTIME_IAM_NOT_PROVEN")

    print(
        "FIRESTORE_RUNTIME_IAM_OK",
        json.dumps(
            {
                "runtime_service_account": RUNTIME_SA,
                "required_role": FIRESTORE_ROLE,
                "binding_preexisting": already,
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
        print(f"FIRESTORE_RUNTIME_IAM_PRECHECK_FAILED {type(exc).__name__}: {exc}", file=sys.stderr)
        raise
