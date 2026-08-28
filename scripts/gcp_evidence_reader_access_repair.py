#!/usr/bin/env python3
"""Apply only the declared read-only viewer roles for System3 Ultra MRI evidence collection."""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

BASELINE = Path("deploy/gcp/system3_evidence_reader_baseline.json")
REPORT = Path("reports/latest/gcp_evidence_reader_access_repair/summary.json")
ALLOWED_MEMBER = "serviceAccount:system3-evidence-reader@system3-openalgo-safe.iam.gserviceaccount.com"
ALLOWED_ROLES = {
    "roles/iam.serviceAccountViewer",
    "roles/iam.workloadIdentityPoolViewer",
    "roles/storage.viewer",
    "roles/cloudsql.viewer",
    "roles/cloudfunctions.viewer",
    "roles/pubsub.viewer",
}


def _run(args: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(args, capture_output=True, text=True, check=False)
    if check and proc.returncode != 0:
        raise RuntimeError(f"command failed rc={proc.returncode}: {' '.join(args[:4])}")
    return proc


def _load() -> dict:
    data = json.loads(BASELINE.read_text(encoding="utf-8"))
    if data.get("project") != "system3-openalgo-safe":
        raise ValueError("unexpected project")
    if data.get("member") != ALLOWED_MEMBER:
        raise ValueError("unexpected evidence-reader member")
    roles = set(data.get("roles") or [])
    if roles != ALLOWED_ROLES:
        raise ValueError("evidence-reader roles changed from least-privilege allow-list")
    if roles & set(data.get("forbidden_roles") or []):
        raise ValueError("forbidden role overlap")
    return data


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    data = _load()
    project = data["project"]
    member = data["member"]
    current = json.loads(_run(["gcloud", "projects", "get-iam-policy", project, "--format=json"]).stdout or "{}")
    present = {
        b.get("role")
        for b in current.get("bindings") or []
        if member in (b.get("members") or []) and not b.get("condition")
    }
    missing = sorted(ALLOWED_ROLES - present)
    changed: list[str] = []
    if args.apply:
        for role in missing:
            _run([
                "gcloud", "projects", "add-iam-policy-binding", project,
                f"--member={member}", f"--role={role}", "--condition=None", "--quiet",
            ])
            changed.append(role)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "project": project,
        "member": member,
        "requested_roles": sorted(ALLOWED_ROLES),
        "missing_before": missing,
        "changed_roles": changed,
        "secret_payloads_accessed": False,
        "service_account_keys_created": False,
        "live_trading_changed": False,
        "order_action_performed": False,
    }
    REPORT.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
