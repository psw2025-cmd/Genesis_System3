#!/usr/bin/env python3
"""Fail-closed read-only GCP inventory; records sanitized metadata only."""
import argparse
import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

PROJECT = "system3-openalgo-safe"
REGION = "asia-south1"
SCOPES = {
    "project": ("projects", "describe", PROJECT),
    "project_iam_policy": ("projects", "get-iam-policy", PROJECT),
    "billing_linkage": ("billing", "projects", "describe", PROJECT),
    "enabled_apis": ("services", "list", "--enabled", "--project", PROJECT),
    "iam_service_accounts": ("iam", "service-accounts", "list", "--project", PROJECT),
    "cloud_run_services": ("run", "services", "list", "--project", PROJECT, "--region", REGION),
    "cloud_run_jobs": ("run", "jobs", "list", "--project", PROJECT, "--region", REGION),
    "scheduler_jobs": ("scheduler", "jobs", "list", "--project", PROJECT, "--location", REGION),
    "secret_metadata": ("secrets", "list", "--project", PROJECT),
    "artifact_repositories": ("artifacts", "repositories", "list", "--project", PROJECT, "--location", REGION),
    "cloud_builds": ("builds", "list", "--project", PROJECT, "--region", REGION, "--limit", "30"),
    "logging_sinks": ("logging", "sinks", "list", "--project", PROJECT),
    "storage_buckets": ("storage", "buckets", "list", "--project", PROJECT),
    "vpc_networks": ("compute", "networks", "list", "--project", PROJECT),
    "vpc_firewall_rules": ("compute", "firewall-rules", "list", "--project", PROJECT),
    "sql_instances": ("sql", "instances", "list", "--project", PROJECT),
}


def _gcloud_command(args, *, windows=None):
    """Build an argument vector that works with both Unix and Windows SDK launchers."""
    if windows is None:
        windows = os.name == "nt"
    if not windows:
        return ["gcloud", *args, "--format=json", "--quiet"]

    # Google Cloud SDK installs gcloud.cmd plus a companion gcloud.ps1. Python
    # cannot CreateProcess a .CMD launcher directly, so use PowerShell's native
    # script runner while preserving every argument as a separate token.
    launcher = shutil.which("gcloud")
    if not launcher:
        raise RuntimeError("GCLOUD_NOT_FOUND")
    ps1 = Path(launcher).with_suffix(".ps1")
    powershell = shutil.which("powershell.exe") or shutil.which("pwsh.exe")
    if ps1.is_file() and powershell:
        return [powershell, "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
                "-File", str(ps1), *args, "--format=json", "--quiet"]
    # An executable launcher (for example a packaged gcloud.exe) can be invoked
    # directly. Do not route arbitrary commands through cmd.exe.
    if launcher.lower().endswith((".exe",)):
        return [launcher, *args, "--format=json", "--quiet"]
    raise RuntimeError("GCLOUD_WINDOWS_LAUNCHER_UNSUPPORTED")


def _safe_gcloud_error(stderr):
    """Map provider text to a small allowlist; never persist raw command output."""
    text = str(stderr or "").lower()
    if "permission_denied" in text or "permission denied" in text or "does not have" in text:
        return "GCLOUD_PERMISSION_DENIED"
    if "not authenticated" in text or "credentials" in text and "invalid" in text:
        return "GCLOUD_AUTH_UNAVAILABLE"
    if "api" in text and ("disabled" in text or "not been used" in text):
        return "GCLOUD_API_DISABLED"
    if "not found" in text or "was not found" in text:
        return "GCLOUD_RESOURCE_NOT_FOUND"
    return "GCLOUD_NONZERO_EXIT"


def run_gcloud(args):
    try:
        result = subprocess.run(_gcloud_command(args),
                                capture_output=True, text=True, timeout=45, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        code = "GCLOUD_TIMEOUT" if isinstance(exc, subprocess.TimeoutExpired) else "GCLOUD_LAUNCH_FAILED"
        raise RuntimeError(code) from None
    if result.returncode:
        raise RuntimeError(_safe_gcloud_error(result.stderr))
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
    if scope == "project_iam_policy":
        if not isinstance(response, dict) or not isinstance(response.get("bindings", []), list):
            raise ValueError("IAM_POLICY_SCHEMA")
        return {"status": "PASS", "binding_count": len(response.get("bindings", [])),
                "policy_version": response.get("version")}
    if scope == "billing_linkage":
        if not isinstance(response, dict):
            raise ValueError("BILLING_SCHEMA")
        enabled = response.get("billingEnabled")
        return {"status": "PASS" if enabled is True else "FAIL",
                "billing_enabled": enabled is True}
    if scope == "project":
        if not isinstance(response, dict):
            raise ValueError("PROJECT_SCHEMA")
        is_match = response.get("projectId") == PROJECT
        is_active = response.get("lifecycleState") == "ACTIVE"
        return {"status": "PASS" if is_match and is_active else "FAIL",
                "project_id_match": is_match, "lifecycle_state": str(response.get("lifecycleState") or "UNKNOWN")[:40]}
    if not isinstance(response, list):
        raise ValueError("LIST_SCHEMA")
    names = sorted(set(n for item in response if (n := safe_name(item))))
    result = {"status": "PASS", "count": len(response), "names": names[:100],
              "names_truncated": len(names) > 100}
    if scope == "cloud_run_services":
        result["canonical_production_present"] = "genesis-system3-web" in names
        result["canonical_staging_present"] = "genesis-system3-web-staging" in names
        if not result["canonical_production_present"] or not result["canonical_staging_present"]:
            result["status"] = "FAIL"
    if scope == "secret_metadata":
        result["note"] = "Identifiers only; secret payloads and versions not retrieved"
    return result


def collect(runner=run_gcloud):
    scopes = {}
    for name, args in SCOPES.items():
        try:
            scopes[name] = summarize(name, runner(args))
        except (RuntimeError, ValueError, TypeError, KeyError) as exc:
            code = str(exc) if str(exc).startswith("GCLOUD_") else type(exc).__name__
            scopes[name] = {"status": "NOT_VERIFIED", "error_code": code}
    ready = all(entry["status"] == "PASS" for entry in scopes.values())
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
