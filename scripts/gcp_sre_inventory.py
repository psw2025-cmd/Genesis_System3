#!/usr/bin/env python3
"""Read-only Google Cloud inventory for Genesis System3 OperationsTruth.

This collector lists resource metadata only. It never reads Secret Manager
payloads, rotates tokens, deploys revisions, changes IAM, or calls broker order
endpoints. Individual permission/API failures are represented as typed API_ERROR
records instead of being converted to an empty inventory.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "reports" / "latest" / "sre_operations_truth" / "inventory.json"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _resource_name(item: dict[str, Any]) -> str:
    metadata = item.get("metadata") if isinstance(item.get("metadata"), dict) else {}
    return str(item.get("name") or metadata.get("name") or item.get("id") or "UNKNOWN")


def _run_json(label: str, argv: list[str], *, timeout_s: int = 45) -> dict[str, Any]:
    observed_at = _now()
    try:
        completed = subprocess.run(
            argv,
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=timeout_s,
            check=False,
        )
    except FileNotFoundError:
        return {
            "state": "API_ERROR",
            "source": " ".join(argv[:3]),
            "observed_at": observed_at,
            "items": [],
            "reason": "gcloud_not_found",
            "command_label": label,
        }
    except subprocess.TimeoutExpired:
        return {
            "state": "API_ERROR",
            "source": " ".join(argv[:3]),
            "observed_at": observed_at,
            "items": [],
            "reason": f"command_timeout>{timeout_s}s",
            "command_label": label,
        }

    if completed.returncode != 0:
        error = (completed.stderr or completed.stdout or "command_failed").strip()
        # Keep diagnostic text bounded and never include credential-file contents.
        return {
            "state": "API_ERROR",
            "source": " ".join(argv[:3]),
            "observed_at": observed_at,
            "items": [],
            "reason": error[-1200:],
            "command_label": label,
            "returncode": completed.returncode,
        }

    try:
        parsed = json.loads(completed.stdout or "[]")
    except json.JSONDecodeError as exc:
        return {
            "state": "SCHEMA_ERROR",
            "source": " ".join(argv[:3]),
            "observed_at": observed_at,
            "items": [],
            "reason": f"invalid_json:{exc}",
            "command_label": label,
        }

    items = parsed if isinstance(parsed, list) else [parsed]
    return {
        "state": "PROVEN" if items else "PROVEN_EMPTY",
        "source": " ".join(argv[:3]),
        "observed_at": observed_at,
        "items": items,
        "reason": "read_only_inventory_query_completed",
        "command_label": label,
    }


def _commands(project: str, region: str) -> dict[str, list[str]]:
    common = [f"--project={project}", "--format=json", "--quiet"]
    return {
        "cloud_run_services": ["gcloud", "run", "services", "list", f"--region={region}", "--platform=managed", *common],
        "cloud_run_jobs": ["gcloud", "run", "jobs", "list", f"--region={region}", *common],
        "cloud_scheduler_jobs": ["gcloud", "scheduler", "jobs", "list", f"--location={region}", *common],
        "pubsub_topics": ["gcloud", "pubsub", "topics", "list", *common],
        "pubsub_subscriptions": ["gcloud", "pubsub", "subscriptions", "list", *common],
        # Metadata only: no versions access and no secrets access command.
        "secret_manager_secrets": ["gcloud", "secrets", "list", *common],
        "service_accounts": ["gcloud", "iam", "service-accounts", "list", *common],
        "project_iam_bindings": ["gcloud", "projects", "get-iam-policy", project, "--format=json", "--quiet"],
        "artifact_registry_repositories": ["gcloud", "artifacts", "repositories", "list", f"--location={region}", *common],
        "cloud_build_triggers": ["gcloud", "builds", "triggers", "list", "--region=global", *common],
        "cloud_build_recent_builds": ["gcloud", "builds", "list", "--limit=50", *common],
        "monitoring_dashboards": ["gcloud", "monitoring", "dashboards", "list", *common],
        "alert_policies": ["gcloud", "monitoring", "policies", "list", *common],
        "uptime_checks": ["gcloud", "monitoring", "uptime", "list-configs", *common],
    }


def _find_values(value: Any, keys: set[str]) -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key in keys and isinstance(child, str) and child:
                found.append(child)
            found.extend(_find_values(child, keys))
    elif isinstance(value, list):
        for child in value:
            found.extend(_find_values(child, keys))
    return found


def _architecture_map(inventory: dict[str, dict[str, Any]]) -> dict[str, Any]:
    nodes: dict[str, dict[str, Any]] = {}
    edges: list[dict[str, str]] = []
    workloads_by_sa: dict[str, set[str]] = defaultdict(set)

    def add_node(node_id: str, kind: str) -> None:
        if node_id and node_id != "UNKNOWN":
            nodes.setdefault(node_id, {"id": node_id, "kind": kind})

    for category, kind in (("cloud_run_services", "cloud_run_service"), ("cloud_run_jobs", "cloud_run_job")):
        record = inventory.get(category, {})
        for item in record.get("items", []) if isinstance(record.get("items"), list) else []:
            if not isinstance(item, dict):
                continue
            workload = _resource_name(item)
            add_node(workload, kind)
            service_accounts = sorted(set(_find_values(item, {"serviceAccount", "serviceAccountName"})))
            for service_account in service_accounts:
                add_node(service_account, "service_account")
                edges.append({"from": workload, "to": service_account, "relation": "RUNS_AS"})
                workloads_by_sa[service_account].add(workload)
            secret_names = sorted(set(_find_values(item, {"secret", "secretName"})))
            # Cloud Run v1 secret env refs commonly use secretKeyRef.name.
            for secret_ref in _find_values(item, {"name"}):
                if "/secrets/" in secret_ref:
                    secret_names.append(secret_ref)
            for secret_name in sorted(set(secret_names)):
                add_node(secret_name, "secret_reference")
                edges.append({"from": workload, "to": secret_name, "relation": "REFERENCES_SECRET"})

    scheduler_record = inventory.get("cloud_scheduler_jobs", {})
    for item in scheduler_record.get("items", []) if isinstance(scheduler_record.get("items"), list) else []:
        if not isinstance(item, dict):
            continue
        scheduler = _resource_name(item)
        add_node(scheduler, "cloud_scheduler_job")
        for service_account in sorted(set(_find_values(item, {"serviceAccountEmail"}))):
            add_node(service_account, "service_account")
            edges.append({"from": scheduler, "to": service_account, "relation": "AUTHENTICATES_AS"})
            workloads_by_sa[service_account].add(scheduler)
        for uri in sorted(set(_find_values(item, {"uri"}))):
            add_node(uri, "http_target")
            edges.append({"from": scheduler, "to": uri, "relation": "INVOKES"})

    shared_identities = [
        {"service_account": sa, "workloads": sorted(workloads)}
        for sa, workloads in sorted(workloads_by_sa.items())
        if len(workloads) > 1
    ]
    return {
        "state": "PROVEN" if nodes else "PROVEN_EMPTY",
        "nodes": sorted(nodes.values(), key=lambda item: (item["kind"], item["id"])),
        "edges": edges,
        "shared_identities": shared_identities,
    }


def _risk_register(inventory: dict[str, dict[str, Any]], architecture: dict[str, Any]) -> list[dict[str, Any]]:
    risks: list[dict[str, Any]] = []

    def add(risk_id: str, severity: str, category: str, evidence: str, action: str) -> None:
        risks.append(
            {
                "risk_id": risk_id,
                "severity": severity,
                "category": category,
                "evidence": evidence,
                "recommended_action": action,
                "status": "OPEN",
            }
        )

    for category, record in inventory.items():
        if record.get("state") in {"API_ERROR", "SCHEMA_ERROR", "UNKNOWN", "STALE"}:
            add(
                f"INV-{category.upper().replace('_', '-')}",
                "P1",
                "inventory",
                f"{category}={record.get('state')}:{record.get('reason')}",
                "Restore read-only evidence access or collector compatibility; do not infer an empty inventory.",
            )

    if inventory.get("alert_policies", {}).get("state") == "PROVEN_EMPTY":
        add("OBS-ALERT-001", "P1", "observability", "No Cloud Monitoring alert policies discovered.", "Define SLO burn-rate and critical dependency alerts before claiming autonomous operations.")
    if inventory.get("monitoring_dashboards", {}).get("state") == "PROVEN_EMPTY":
        add("OBS-DASH-001", "P2", "observability", "No Cloud Monitoring dashboards discovered.", "Create an operator dashboard from authoritative metrics and typed truth states.")
    if inventory.get("uptime_checks", {}).get("state") == "PROVEN_EMPTY":
        add("OBS-UPTIME-001", "P1", "availability", "No uptime/synthetic monitor configurations discovered.", "Add lightweight uptime checks and redacted read-only synthetic coverage.")

    for shared in architecture.get("shared_identities", []):
        add(
            "IAM-SHARED-" + str(abs(hash(shared["service_account"])) % 100000),
            "P1",
            "iam",
            f"Service account is shared by multiple workloads: {shared['workloads']}",
            "Review whether workloads have different privilege/lifecycle requirements; split identity where needed.",
        )

    return risks


def collect(project: str, region: str) -> dict[str, Any]:
    inventory = {
        category: _run_json(category, command)
        for category, command in _commands(project, region).items()
    }
    architecture = _architecture_map(inventory)
    return {
        "schema_version": 1,
        "project": project,
        "region": region,
        "observed_at": _now(),
        "collector_mode": "READ_ONLY_METADATA",
        "secret_payloads_accessed": False,
        "production_mutations_attempted": 0,
        "broker_order_endpoints_called": 0,
        "inventory": inventory,
        "architecture_map": architecture,
        "risk_register": _risk_register(inventory, architecture),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default=os.getenv("GOOGLE_CLOUD_PROJECT", "system3-openalgo-safe"))
    parser.add_argument("--region", default=os.getenv("GCP_REGION", "asia-south1"))
    parser.add_argument("--output", default=str(DEFAULT_OUT))
    args = parser.parse_args()

    report = collect(args.project, args.region)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    states = {name: record.get("state") for name, record in report["inventory"].items()}
    print(
        "SRE_INVENTORY",
        json.dumps(
            {
                "output": str(output),
                "states": states,
                "risk_count": len(report["risk_register"]),
                "secret_payloads_accessed": False,
                "production_mutations_attempted": 0,
                "broker_order_endpoints_called": 0,
            },
            sort_keys=True,
        ),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
