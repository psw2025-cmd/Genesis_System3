#!/usr/bin/env python3
"""Read-only inventory of principals that can effectively run Cloud Run Jobs.

Does not mutate IAM. Writes reports/latest/broker_authority_6rules/project_run_jobs_run_inventory.json
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT = "system3-openalgo-safe"
REGION = "asia-south1"
JOB = "genesis-system3-dhan-token-rotate"
OUT = Path("reports/latest/broker_authority_6rules/project_run_jobs_run_inventory.json")

ROLES_OF_INTEREST = {
    "roles/run.invoker",
    "roles/run.jobsExecutor",
    "roles/run.jobsExecutorWithOverrides",
    "roles/run.developer",
    "roles/run.admin",
    "roles/editor",
    "roles/owner",
}

PERMS = {
    "run.jobs.run",
    "run.jobs.runWithOverrides",
}


def _run(args: list[str]) -> str:
    # Resolve gcloud on Windows PATH / common install locations.
    exe = args[0]
    if exe == "gcloud":
        from shutil import which

        resolved = which("gcloud") or which("gcloud.cmd")
        if not resolved:
            raise FileNotFoundError("gcloud not found on PATH")
        args = [resolved, *args[1:]]
    proc = subprocess.run(args, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        return ""
    return proc.stdout


def _load_json(args: list[str]):
    raw = _run(args)
    if not raw.strip():
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def main() -> int:
    project_policy = _load_json(
        ["gcloud", "projects", "get-iam-policy", PROJECT, "--format=json"]
    ) or {"bindings": []}
    job_policy = _load_json(
        [
            "gcloud",
            "run",
            "jobs",
            "get-iam-policy",
            JOB,
            "--project",
            PROJECT,
            "--region",
            REGION,
            "--format=json",
        ]
    ) or {"bindings": []}

    custom_roles = []
    roles_list = _run(
        ["gcloud", "iam", "roles", "list", f"--project={PROJECT}", "--format=json"]
    )
    if roles_list.strip():
        try:
            for role in json.loads(roles_list):
                name = role.get("name") or ""
                detail = _load_json(["gcloud", "iam", "roles", "describe", name, "--format=json"])
                if not detail:
                    continue
                perms = set(detail.get("includedPermissions") or [])
                if perms & PERMS:
                    custom_roles.append(
                        {
                            "name": name,
                            "title": detail.get("title"),
                            "permissions": sorted(perms & PERMS),
                        }
                    )
        except json.JSONDecodeError:
            pass

    project_hits = []
    for binding in project_policy.get("bindings") or []:
        role = binding.get("role") or ""
        members = binding.get("members") or []
        if role in ROLES_OF_INTEREST or any(
            role == c["name"] or role.endswith("/" + c["name"].split("/")[-1])
            for c in custom_roles
        ):
            project_hits.append(
                {
                    "source": "project",
                    "role": role,
                    "members": members,
                    "condition": binding.get("condition"),
                }
            )

    job_hits = []
    for binding in job_policy.get("bindings") or []:
        role = binding.get("role") or ""
        if role in ROLES_OF_INTEREST or "run.invoker" in role or "RunJob" in role:
            job_hits.append(
                {
                    "source": "resource:cloud_run_job",
                    "resource": JOB,
                    "role": role,
                    "members": binding.get("members") or [],
                }
            )

    intended = {
        "scheduler_invoker": f"serviceAccount:gs3-scheduler@{PROJECT}.iam.gserviceaccount.com",
        "manual_recovery_invoker": f"serviceAccount:gs3-token-recovery@{PROJECT}.iam.gserviceaccount.com",
        "web_must_not_invoke": f"serviceAccount:genesis-system3-web@{PROJECT}.iam.gserviceaccount.com",
        "default_compute_should_not_invoke": "serviceAccount:802404398783-compute@developer.gserviceaccount.com",
    }

    invokers = set()
    for hit in job_hits:
        if hit["role"] == "roles/run.invoker":
            invokers.update(hit["members"])

    web_absent = intended["web_must_not_invoke"] not in invokers
    compute_absent = intended["default_compute_should_not_invoke"] not in invokers
    scheduler_present = intended["scheduler_invoker"] in invokers
    recovery_present = intended["manual_recovery_invoker"] in invokers

    remaining_project_run_jobs_run = []
    for hit in project_hits:
        role = hit["role"]
        if role in {
            "roles/run.developer",
            "roles/run.admin",
            "roles/editor",
            "roles/owner",
            "roles/run.jobsExecutor",
            "roles/run.jobsExecutorWithOverrides",
        } or role.startswith(f"projects/{PROJECT}/roles/"):
            for member in hit["members"]:
                remaining_project_run_jobs_run.append({"member": member, "role": role, "source": "project"})

    rule1 = "PASS" if (
        web_absent and compute_absent and scheduler_present and recovery_present
        and not remaining_project_run_jobs_run
    ) else "PARTIAL"

    remediation = [
        "Keep job-level run.invoker for gs3-scheduler and gs3-token-recovery only.",
        "Do not remove project roles/run.admin from genesis-system3-automation until deploy no longer needs job deploy/IAM bind; replace with least-privilege custom role excluding run.jobs.run if deploy execute is retired.",
        "Replace default compute roles/editor with workload-specific roles before claiming Rule-1 PASS.",
        "Shrink gs3-ops-controller and github-actions-deploy run.developer if unused for rotator execute.",
        "Re-run this inventory after each IAM change; do not blind-delete project roles.",
    ]

    report = {
        "as_of_utc": datetime.now(timezone.utc).isoformat(),
        "project": PROJECT,
        "job": JOB,
        "roles_of_interest": sorted(ROLES_OF_INTEREST),
        "custom_roles_with_run_jobs_run": custom_roles,
        "project_bindings": project_hits,
        "job_bindings": job_hits,
        "intended": intended,
        "checks": {
            "web_invoker_absent": web_absent,
            "default_compute_invoker_absent": compute_absent,
            "scheduler_invoker_present": scheduler_present,
            "recovery_invoker_present": recovery_present,
        },
        "remaining_project_principals_with_run_jobs_run_capability": remaining_project_run_jobs_run,
        "rule1_verdict": rule1,
        "least_privilege_remediation_plan": remediation,
        "inherited_org_folder_note": "Org/folder IAM not queried in this pass; re-check with asset inventory if Rule-1 remains PARTIAL after project scrub.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"wrote": str(OUT), "rule1_verdict": rule1, "checks": report["checks"]}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
