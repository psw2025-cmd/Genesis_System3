#!/usr/bin/env python3
"""Fail-closed read-only GCP inventory; records sanitized metadata only."""
import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

PROJECT = "system3-openalgo-safe"
REGION = "asia-south1"
SCOPES = {
    "project": ("projects", "describe", PROJECT),
    "enabled_apis": ("services", "list", "--enabled", "--project", PROJECT),
    "iam_service_accounts": ("iam", "service-accounts", "list", "--project", PROJECT),
    "cloud_run_services": ("run", "services", "list", "--project", PROJECT, "--region", REGION),
    "cloud_run_jobs": ("run", "jobs", "list", "--project", PROJECT, "--region", REGION),
    "scheduler_jobs": ("scheduler", "jobs", "list", "--project", PROJECT, "--location", REGION),
    "secret_metadata": ("secrets", "list", "--project", PROJECT),
    "artifact_repositories": ("artifacts", "repositories", "list", "--project", PROJECT, "--location", REGION),
    "cloud_builds": ("builds", "list", "--project", PROJECT, "--region", REGION, "--limit", "30"),
    "logging_sinks": ("logging", "sinks", "list", "--project", PROJECT),
}


def run_gcloud(args):
    try:
        result = subprocess.run(["gcloud", *args, "--format=json", "--quiet"],
                                capture_output=True, text=True, timeout=45, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise RuntimeError(type(exc).__name__) from None
    if result.returncode:
        raise RuntimeError("GCLOUD_NONZERO_EXIT")
    try:
        return json.loads(result.stdout)
    except (ValueError, TypeError):
        raise RuntimeError("INVALID_JSON") from None


def safe_name(obj):
    if not isinstance(obj, dict):
        return None
    raw = obj.get("name") or (obj.get("metadata") or {}).get("name") or obj.get("projectId")
    if not isinstance(raw, str):
        return None
    name = raw.rstrip("/").split("/")[-1]
    return name[:100] if name and "@" not in name else None


def summarize(scope, response):
    if scope == "project":
        if not isinstance(response, dict):
            raise ValueError("PROJECT_SCHEMA")
        return {"status": "PASS", "project_id_match": response.get("projectId") == PROJECT,
                "lifecycle_state": str(response.get("lifecycleState") or "UNKNOWN")[:40]}
    if not isinstance(response, list):
        raise ValueError("LIST_SCHEMA")
    names = sorted(set(n for item in response if (n := safe_name(item))))
    result = {"status": "PASS", "count": len(response), "names": names[:100],
              "names_truncated": len(names) > 100}
    if scope == "cloud_run_services":
        result["canonical_production_present"] = "genesis-system3-web" in names
        result["canonical_staging_present"] = "genesis-system3-web-staging" in names
    if scope == "secret_metadata":
        result["note"] = "Identifiers only; secret payloads and versions not retrieved"
    return result


def collect(runner=run_gcloud):
    scopes = {}
    for name, args in SCOPES.items():
        try:
            scopes[name] = summarize(name, runner(args))
        except (RuntimeError, ValueError, TypeError, KeyError) as exc:
            scopes[name] = {"status": "NOT_VERIFIED", "error_class": type(exc).__name__}
    ready = all(entry["status"] == "PASS" for entry in scopes.values())
    if not scopes["project"].get("project_id_match", False):
        ready = False
    return {"schema": "genesis-cloud-infrastructure-inventory-v1",
            "observed_utc": datetime.now(timezone.utc).isoformat(),
            "project": PROJECT, "region": REGION,
            "status": "PASS" if ready else "NOT_VERIFIED",
            "read_only": True, "secret_payloads_accessed": False,
            "broker_order_requests": 0, "cloud_mutations": 0, "scopes": scopes}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = collect()
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for scope, item in result["scopes"].items():
        print(f'CLOUD_INVENTORY scope={scope} status={item["status"]} count={item.get("count", "unknown")}')
    print("CLOUD_INVENTORY_OVERALL=" + result["status"])
    return 0 if result["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
