#!/usr/bin/env python3
"""Reconcile only the declared Genesis System3 IAM authority baseline.

This tool never reads Secret Manager payloads, never executes Cloud Run jobs,
and never changes LIVE/order flags. It is intentionally additive except for the
small explicit deny-list of known-forbidden Dhan rotator invokers.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BASELINE = Path("deploy/gcp/system3_iam_baseline.json")
REPORT = Path("reports/latest/gcp_authority_repair/summary.json")
DEPLOYER = "serviceAccount:genesis-system3-automation@system3-openalgo-safe.iam.gserviceaccount.com"
REPAIR_SA = "serviceAccount:gs3-iam-repair@system3-openalgo-safe.iam.gserviceaccount.com"


def _run(args: list[str], *, check: bool = True) -> str:
    proc = subprocess.run(args, capture_output=True, text=True, check=False)
    if check and proc.returncode != 0:
        raise RuntimeError(f"command failed rc={proc.returncode}: {' '.join(args[:4])}: {proc.stderr.strip()}")
    return proc.stdout


def _json(args: list[str]) -> dict[str, Any]:
    raw = _run(args)
    return json.loads(raw or "{}")


def _members(policy: dict[str, Any], role: str) -> set[str]:
    result: set[str] = set()
    for binding in policy.get("bindings") or []:
        if binding.get("role") == role and not binding.get("condition"):
            result.update(binding.get("members") or [])
    return result


def _load_baseline() -> dict[str, Any]:
    data = json.loads(BASELINE.read_text(encoding="utf-8"))
    policy = data.get("policy") or {}
    required = {
        "gcp_is_production_authority": True,
        "render_is_production_authority": False,
        "service_account_keys_allowed": False,
        "live_trading_enabled": False,
        "auto_execute_trades": False,
        "secret_payload_access_by_deployer": False,
        "dhan_web_self_heal_mint": False,
    }
    for key, expected in required.items():
        if policy.get(key) is not expected:
            raise ValueError(f"unsafe baseline policy {key}={policy.get(key)!r}; expected {expected!r}")

    for item in data.get("project_bindings") or []:
        if item.get("member") == REPAIR_SA and item.get("role") in {"roles/owner", "roles/editor", "roles/run.admin"}:
            raise ValueError("repair identity must not receive broad runtime/admin role from baseline")

    for item in data.get("secret_bindings") or []:
        if item.get("member") in {DEPLOYER, REPAIR_SA} and item.get("role") in {
            "roles/secretmanager.secretAccessor",
            "roles/secretmanager.secretVersionAdder",
        }:
            raise ValueError("deployer/repair identity must not receive broker secret payload authority")

    dhan = data.get("dhan_job") or {}
    required_invokers = set(dhan.get("required_invokers") or [])
    if REPAIR_SA in required_invokers or DEPLOYER in required_invokers:
        raise ValueError("deployer/repair identity must not invoke Dhan rotator")
    return data


def _record(changes: list[dict[str, Any]], *, scope: str, resource: str, role: str, member: str, action: str) -> None:
    changes.append({"scope": scope, "resource": resource, "role": role, "member": member, "action": action})


def reconcile(*, apply: bool) -> dict[str, Any]:
    baseline = _load_baseline()
    project = baseline["project"]
    region = baseline["region"]
    changes: list[dict[str, Any]] = []

    project_policy = _json(["gcloud", "projects", "get-iam-policy", project, "--format=json"])
    for item in baseline.get("project_bindings") or []:
        member, role = item["member"], item["role"]
        if member not in _members(project_policy, role):
            _record(changes, scope="project", resource=project, role=role, member=member, action="add")
            if apply:
                _run(["gcloud", "projects", "add-iam-policy-binding", project, f"--member={member}", f"--role={role}", "--condition=None", "--quiet"])

    for item in baseline.get("service_account_bindings") or []:
        target, member, role = item["service_account"], item["member"], item["role"]
        policy = _json(["gcloud", "iam", "service-accounts", "get-iam-policy", target, f"--project={project}", "--format=json"])
        if member not in _members(policy, role):
            _record(changes, scope="service_account", resource=target, role=role, member=member, action="add")
            if apply:
                _run(["gcloud", "iam", "service-accounts", "add-iam-policy-binding", target, f"--project={project}", f"--member={member}", f"--role={role}", "--quiet"])

    for item in baseline.get("secret_bindings") or []:
        secret, member, role = item["secret"], item["member"], item["role"]
        policy = _json(["gcloud", "secrets", "get-iam-policy", secret, f"--project={project}", "--format=json"])
        if member not in _members(policy, role):
            _record(changes, scope="secret_iam_metadata_only", resource=secret, role=role, member=member, action="add")
            if apply:
                _run(["gcloud", "secrets", "add-iam-policy-binding", secret, f"--project={project}", f"--member={member}", f"--role={role}", "--quiet"])

    dhan = baseline["dhan_job"]
    job = dhan["name"]
    job_policy = _json(["gcloud", "run", "jobs", "get-iam-policy", job, f"--project={project}", f"--region={region}", "--format=json"])
    invokers = _members(job_policy, "roles/run.invoker")
    for member in dhan.get("required_invokers") or []:
        if member not in invokers:
            _record(changes, scope="cloud_run_job", resource=job, role="roles/run.invoker", member=member, action="add")
            if apply:
                _run(["gcloud", "run", "jobs", "add-iam-policy-binding", job, f"--project={project}", f"--region={region}", f"--member={member}", "--role=roles/run.invoker", "--quiet"])
    for member in dhan.get("forbidden_invokers") or []:
        if member in invokers:
            _record(changes, scope="cloud_run_job", resource=job, role="roles/run.invoker", member=member, action="remove_known_forbidden")
            if apply:
                _run(["gcloud", "run", "jobs", "remove-iam-policy-binding", job, f"--project={project}", f"--region={region}", f"--member={member}", "--role=roles/run.invoker", "--quiet"])

    report = {
        "as_of_utc": datetime.now(timezone.utc).isoformat(),
        "project": project,
        "mode": "apply" if apply else "check",
        "drift_detected": bool(changes),
        "change_count": len(changes),
        "changes": changes,
        "secret_payloads_accessed": False,
        "service_account_keys_created": False,
        "dhan_rotation_job_executed": False,
        "live_trading_changed": False,
        "order_action_performed": False,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("GCP_AUTHORITY_REPAIR", json.dumps(report, sort_keys=True))
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Apply only declared baseline drift. Default is read-only check.")
    args = parser.parse_args()
    reconcile(apply=args.apply)
    return 0


if __name__ == "__main__":
    sys.exit(main())
