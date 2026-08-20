#!/usr/bin/env python3
"""Reconcile only the declared Genesis System3 IAM authority baseline.

This tool never reads Secret Manager payloads, never executes Cloud Run jobs,
and never changes LIVE/order flags. It is additive except for explicit safety
deny-lists: forbidden broker-secret payload roles and forbidden Dhan invokers.
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
REPAIR_SAS = {
    "serviceAccount:gs3-iam-repair@system3-openalgo-safe.iam.gserviceaccount.com",
    "serviceAccount:gs3-iam-repair-b@system3-openalgo-safe.iam.gserviceaccount.com",
}


def _proc(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, capture_output=True, text=True, check=False)


def _run(args: list[str], *, check: bool = True) -> str:
    proc = _proc(args)
    if check and proc.returncode != 0:
        raise RuntimeError(
            f"command failed rc={proc.returncode}: {' '.join(args[:4])}: {proc.stderr.strip()}"
        )
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
        "strict_scheduler_only_iam": False,
        "deployer_run_admin_temporary": False,
    }
    for key, expected in required.items():
        if policy.get(key) is not expected:
            raise ValueError(
                f"unsafe or contradictory baseline policy {key}={policy.get(key)!r}; expected {expected!r}"
            )

    repair = data.get("repair") or {}
    declared_repair = {f"serviceAccount:{item}" for item in repair.get("service_accounts") or []}
    if declared_repair != REPAIR_SAS:
        raise ValueError("repair identity set must exactly match the hard safety contract")

    for item in data.get("project_bindings") or []:
        if item.get("member") in REPAIR_SAS and item.get("role") in {
            "roles/owner",
            "roles/editor",
            "roles/run.admin",
        }:
            raise ValueError("repair identities must not receive broad runtime/admin roles")

    for item in data.get("secret_bindings") or []:
        if item.get("member") in ({DEPLOYER} | REPAIR_SAS) and item.get("role") in {
            "roles/secretmanager.secretAccessor",
            "roles/secretmanager.secretVersionAdder",
        }:
            raise ValueError(
                "deployer/repair identities must not receive broker secret payload authority"
            )

    secret_safety = data.get("secret_safety") or {}
    expected_forbidden_members = {DEPLOYER} | REPAIR_SAS
    if set(secret_safety.get("forbidden_payload_members") or []) != expected_forbidden_members:
        raise ValueError("secret payload deny-list must exactly cover deployer and both repair identities")
    expected_forbidden_roles = {
        "roles/secretmanager.secretAccessor",
        "roles/secretmanager.secretVersionAdder",
    }
    if set(secret_safety.get("forbidden_payload_roles") or []) != expected_forbidden_roles:
        raise ValueError("secret payload deny-list roles changed from hard safety contract")
    if not set(secret_safety.get("protected_secrets") or []):
        raise ValueError("protected broker secret set must not be empty")

    dhan = data.get("dhan_job") or {}
    required_invokers = set(dhan.get("required_invokers") or [])
    if required_invokers & ({DEPLOYER} | REPAIR_SAS):
        raise ValueError("deployer/repair identities must not be Dhan rotator job-level invokers")

    forbidden_custom_permissions = {
        "run.jobs.run",
        "run.jobs.runWithOverrides",
        "secretmanager.versions.access",
        "secretmanager.versions.add",
        "iam.serviceAccountKeys.create",
    }
    custom_permissions = set(repair.get("custom_role_permissions") or [])
    forbidden_hits = sorted(custom_permissions & forbidden_custom_permissions)
    if forbidden_hits:
        raise ValueError(f"unsafe repair custom-role permissions: {forbidden_hits}")
    return data


def _record(
    changes: list[dict[str, Any]],
    *,
    scope: str,
    resource: str,
    role: str,
    member: str,
    action: str,
) -> None:
    changes.append(
        {
            "scope": scope,
            "resource": resource,
            "role": role,
            "member": member,
            "action": action,
        }
    )


def _converge_custom_role(
    baseline: dict[str, Any], *, apply: bool, changes: list[dict[str, Any]]
) -> None:
    project = baseline["project"]
    repair = baseline["repair"]
    role_id = repair["custom_role_id"]
    expected = sorted(set(repair.get("custom_role_permissions") or []))
    describe = _proc(
        ["gcloud", "iam", "roles", "describe", role_id, f"--project={project}", "--format=json"]
    )
    if describe.returncode != 0:
        _record(
            changes,
            scope="custom_role",
            resource=f"projects/{project}/roles/{role_id}",
            role=role_id,
            member="n/a",
            action="create",
        )
        if apply:
            _run(
                [
                    "gcloud",
                    "iam",
                    "roles",
                    "create",
                    role_id,
                    f"--project={project}",
                    "--title=Genesis System3 IAM Repair",
                    "--description=Bounded IAM policy repair without secret payload or Cloud Run job execution",
                    f"--permissions={','.join(expected)}",
                    "--stage=GA",
                    "--quiet",
                ]
            )
        return

    detail = json.loads(describe.stdout or "{}")
    current = sorted(set(detail.get("includedPermissions") or []))
    if current != expected or detail.get("stage") not in {"GA", "ALPHA", "BETA"}:
        _record(
            changes,
            scope="custom_role",
            resource=f"projects/{project}/roles/{role_id}",
            role=role_id,
            member="n/a",
            action="update_permissions",
        )
        if apply:
            _run(
                [
                    "gcloud",
                    "iam",
                    "roles",
                    "update",
                    role_id,
                    f"--project={project}",
                    f"--permissions={','.join(expected)}",
                    "--stage=GA",
                    "--quiet",
                ]
            )


def reconcile(*, apply: bool) -> dict[str, Any]:
    baseline = _load_baseline()
    project = baseline["project"]
    region = baseline["region"]
    changes: list[dict[str, Any]] = []

    _converge_custom_role(baseline, apply=apply, changes=changes)

    project_policy = _json(["gcloud", "projects", "get-iam-policy", project, "--format=json"])
    for item in baseline.get("project_bindings") or []:
        member, role = item["member"], item["role"]
        if member not in _members(project_policy, role):
            _record(
                changes,
                scope="project",
                resource=project,
                role=role,
                member=member,
                action="add",
            )
            if apply:
                _run(
                    [
                        "gcloud",
                        "projects",
                        "add-iam-policy-binding",
                        project,
                        f"--member={member}",
                        f"--role={role}",
                        "--condition=None",
                        "--quiet",
                    ]
                )

    for item in baseline.get("service_account_bindings") or []:
        target, member, role = item["service_account"], item["member"], item["role"]
        policy = _json(
            [
                "gcloud",
                "iam",
                "service-accounts",
                "get-iam-policy",
                target,
                f"--project={project}",
                "--format=json",
            ]
        )
        if member not in _members(policy, role):
            _record(
                changes,
                scope="service_account",
                resource=target,
                role=role,
                member=member,
                action="add",
            )
            if apply:
                _run(
                    [
                        "gcloud",
                        "iam",
                        "service-accounts",
                        "add-iam-policy-binding",
                        target,
                        f"--project={project}",
                        f"--member={member}",
                        f"--role={role}",
                        "--quiet",
                    ]
                )

    # Only IAM metadata is read here; no secret versions or payloads are accessed.
    for item in baseline.get("secret_bindings") or []:
        secret, member, role = item["secret"], item["member"], item["role"]
        policy = _json(
            ["gcloud", "secrets", "get-iam-policy", secret, f"--project={project}", "--format=json"]
        )
        if member not in _members(policy, role):
            _record(
                changes,
                scope="secret_iam_metadata_only",
                resource=secret,
                role=role,
                member=member,
                action="add",
            )
            if apply:
                _run(
                    [
                        "gcloud",
                        "secrets",
                        "add-iam-policy-binding",
                        secret,
                        f"--project={project}",
                        f"--member={member}",
                        f"--role={role}",
                        "--quiet",
                    ]
                )

    secret_safety = baseline["secret_safety"]
    for secret in secret_safety.get("protected_secrets") or []:
        policy = _json(
            ["gcloud", "secrets", "get-iam-policy", secret, f"--project={project}", "--format=json"]
        )
        for role in secret_safety.get("forbidden_payload_roles") or []:
            current_members = _members(policy, role)
            for member in secret_safety.get("forbidden_payload_members") or []:
                if member not in current_members:
                    continue
                _record(
                    changes,
                    scope="secret_iam_safety",
                    resource=secret,
                    role=role,
                    member=member,
                    action="remove_known_forbidden_payload_role",
                )
                if apply:
                    _run(
                        [
                            "gcloud",
                            "secrets",
                            "remove-iam-policy-binding",
                            secret,
                            f"--project={project}",
                            f"--member={member}",
                            f"--role={role}",
                            "--quiet",
                        ]
                    )

    dhan = baseline["dhan_job"]
    job = dhan["name"]
    job_policy = _json(
        [
            "gcloud",
            "run",
            "jobs",
            "get-iam-policy",
            job,
            f"--project={project}",
            f"--region={region}",
            "--format=json",
        ]
    )
    invokers = _members(job_policy, "roles/run.invoker")
    for member in dhan.get("required_invokers") or []:
        if member not in invokers:
            _record(
                changes,
                scope="cloud_run_job",
                resource=job,
                role="roles/run.invoker",
                member=member,
                action="add",
            )
            if apply:
                _run(
                    [
                        "gcloud",
                        "run",
                        "jobs",
                        "add-iam-policy-binding",
                        job,
                        f"--project={project}",
                        f"--region={region}",
                        f"--member={member}",
                        "--role=roles/run.invoker",
                        "--quiet",
                    ]
                )
    for member in dhan.get("forbidden_invokers") or []:
        if member in invokers:
            _record(
                changes,
                scope="cloud_run_job",
                resource=job,
                role="roles/run.invoker",
                member=member,
                action="remove_known_forbidden",
            )
            if apply:
                _run(
                    [
                        "gcloud",
                        "run",
                        "jobs",
                        "remove-iam-policy-binding",
                        job,
                        f"--project={project}",
                        f"--region={region}",
                        f"--member={member}",
                        "--role=roles/run.invoker",
                        "--quiet",
                    ]
                )

    report = {
        "as_of_utc": datetime.now(timezone.utc).isoformat(),
        "project": project,
        "mode": "apply" if apply else "check",
        "drift_detected": bool(changes),
        "change_count": len(changes),
        "changes": changes,
        "strict_scheduler_only_iam": baseline["policy"]["strict_scheduler_only_iam"],
        "deployer_run_admin_temporary": baseline["policy"]["deployer_run_admin_temporary"],
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
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply only declared baseline drift. Default is read-only check.",
    )
    args = parser.parse_args()
    reconcile(apply=args.apply)
    return 0


if __name__ == "__main__":
    sys.exit(main())
