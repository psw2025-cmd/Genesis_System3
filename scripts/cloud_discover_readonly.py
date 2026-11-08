#!/usr/bin/env python3
"""Read-only discovery of the uniquely identifiable Genesis Cloud Run target."""
import json
import os
import re
import subprocess
import sys

REGION = "asia-south1"
EXPECTED = {"PAPER_MODE": "1", "LIVE_ORDER_AUTHORITY": "0", "REAL_BROKER_ORDERS": "0"}
HINTS = (("genesis-system3", "genesis"), ("system3-openalgo-safe", "genesis-system3-web"))


def gcloud(*args, expect_list=True):
    result = subprocess.run(["gcloud", *args, "--format=json"], capture_output=True, text=True, timeout=90)
    if result.returncode:
        raise RuntimeError("GCLOUD_READ_FAILED: " + " ".join(args[:3]))
    value = json.loads(result.stdout)
    if expect_list and not isinstance(value, list):
        raise RuntimeError("GCLOUD_LIST_SCHEMA_INVALID")
    return value


def project_id(p):
    return p.get("projectId") or p.get("project_id") or ""


def service_name(s):
    metadata = s.get("metadata") or {}
    return metadata.get("name") or s.get("name", "").split("/")[-1]


def service_containers(s):
    return ((s.get("spec") or {}).get("template") or {}).get("spec", {}).get("containers") or (s.get("template") or {}).get("containers") or []


def is_safe_service(s):
    containers = service_containers(s)
    if len(containers) != 1:
        return False
    env = containers[0].get("env") or []
    return all(len([e for e in env if e.get("name") == key and e.get("value") == value]) == 1
               and len([e for e in env if e.get("name") == key]) == 1
               for key, value in EXPECTED.items())


def discover(projects, services_by_project):
    matches = []
    for p in projects:
        pid = project_id(p)
        for svc in services_by_project.get(pid, []):
            name = service_name(svc)
            if is_safe_service(svc) and ("genesis" in name.lower() or "system3" in name.lower()):
                matches.append((pid, name))
    return sorted(set(matches))


def main():
    provider = os.getenv("GCP_WIF_PROVIDER", "")
    account = os.getenv("GCP_WIF_SERVICE_ACCOUNT", "")
    if not provider or not account:
        print("NOT_VERIFIED: missing GitHub variables: " + ", ".join(
            k for k, v in (("GCP_WIF_PROVIDER", provider), ("GCP_WIF_SERVICE_ACCOUNT", account)) if not v))
        return 2
    try:
        projects = gcloud("projects", "list")
        services = {}
        print("VISIBLE_GCP_PROJECTS=" + json.dumps(sorted(project_id(p) for p in projects if project_id(p))))
        for p in projects:
            pid = project_id(p)
            if not pid:
                continue
            try:
                entries = gcloud("run", "services", "list", "--project", pid, "--region", REGION)
            except (RuntimeError, subprocess.TimeoutExpired):
                print("PROJECT_SERVICE_DISCOVERY_UNAVAILABLE=" + pid)
                continue
            described = []
            for svc in entries:
                name = service_name(svc)
                if "genesis" not in name.lower() and "system3" not in name.lower():
                    continue
                try:
                    detail = gcloud("run", "services", "describe", name, "--project", pid, "--region", REGION, expect_list=False)
                    described.append(detail)
                except (RuntimeError, subprocess.TimeoutExpired):
                    print("SERVICE_DESCRIPTION_UNAVAILABLE project=" + pid + " service=" + name)
            services[pid] = described
            print("CLOUD_RUN_SERVICES=" + json.dumps({"project": pid, "region": REGION,
                  "names": sorted(service_name(s) for s in entries)}))
        matches = discover(projects, services)
        if len(matches) != 1:
            print("NOT_VERIFIED: expected exactly one Genesis service with explicit PAPER safety; found " + str(len(matches)))
            return 2
        pid, name = matches[0]
        print("DISCOVERED_PRODUCTION_TARGET project=" + pid + " service=" + name + " region=" + REGION)
        print("USER_PROVIDED_HINT genesis-system3/genesis; ACTUAL_DISCOVERED=" + pid + "/" + name)
        output = os.getenv("GITHUB_OUTPUT", "")
        if not output:
            print("NOT_VERIFIED: GITHUB_OUTPUT missing")
            return 2
        with open(output, "a", encoding="utf-8") as f:
            f.write("project=" + pid + "\nservice=" + name + "\n")
        return 0
    except (RuntimeError, ValueError, subprocess.TimeoutExpired) as exc:
        print("NOT_VERIFIED: discovery failed: " + type(exc).__name__)
        return 2


if __name__ == "__main__":
    sys.exit(main())
