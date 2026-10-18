#!/usr/bin/env python3
"""Read-only System3 cloud deployment candidate preflight. NEVER deploys anything.

This program audits repository-controlled prerequisites only. It never reads a
broker credential, calls Google Cloud, assumes owner approval or reports a
successful production deployment. Its normal exit 0 means REPORT_WRITTEN.
Use --strict to fail closed (exit 2) on any release blocker.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

PROJECT = "system3-openalgo-safe"
PROJECT_NUMBER = "802404398783"
REGION = "asia-south1"
CANONICAL_DOCKERFILE = "dashboard/backend/Dockerfile"
MANUAL_WORKFLOW = ".github/workflows/system3-cloud-paper-deploy.yml"
DEPLOY_ENTRYPOINT = "scripts/system3_cloud_paper_deploy.py"
ROOT_MARKER = "SYSTEM3_ROOT_DOCKERFILE_NONPRODUCTION"


def check_repo(root: Path, source_sha: str = "UNRESOLVED") -> dict:
    def content(rel: str) -> str:
        path = root / rel
        return path.read_text(encoding="utf-8") if path.is_file() else ""

    checks: list[dict[str, str]] = []
    def record(check_id: str, status: str, observed: str, expected: str) -> None:
        checks.append({"id": check_id, "status": status,
                       "observed": observed, "expected": expected})

    directive = content("docs/authority/CLOUD_ONLY_OWNER_DIRECTIVE_20261018.md")
    record("CLOUD_ONLY_AUTHORITY", "PASS" if "SYSTEM3_CLOUD_ONLY_OWNER_DIRECTIVE_20261018" in directive
           and "read-only GCP verification only" in directive else "BLOCKED",
           "active owner directive present" if directive else "missing directive",
           "latest owner directive and separate cloud-mutation consent")

    root_docker = content("Dockerfile")
    record("ROOT_IMAGE_NONPRODUCTION", "PASS" if ROOT_MARKER in root_docker else "BLOCKED",
           "legacy root image explicitly marked" if ROOT_MARKER in root_docker else "unmarked ambiguous root Dockerfile",
           "root Dockerfile explicitly excluded from Cloud Run production")

    docker = content(CANONICAL_DOCKERFILE)
    canonical_markers = ('FROM node:20-slim AS frontend-builder', 'npm run build',
                         'EXPOSE 8080', 'CMD ["python", "scripts/start_cloud_run.py"]')
    record("CANONICAL_IMAGE_SOURCE", "PASS" if all(m in docker for m in canonical_markers) else "BLOCKED",
           "all canonical build markers present" if all(m in docker for m in canonical_markers) else "canonical build markers missing",
           CANONICAL_DOCKERFILE + " with clean frontend build and safe launch")

    launcher = content("scripts/start_cloud_run.py")
    record("CLOUD_PORT_AND_SECURE_APP", "PASS" if
           ('os.getenv("PORT", "8080")' in launcher and
            '"dashboard.backend.secure_app:app"' in launcher and
            'host="0.0.0.0"' in launcher) else "BLOCKED",
           "Cloud Run launcher contract verified" if launcher else "missing launcher",
           "PORT-aware secure read-only app, no fixed 8000 ingress")

    workflow = content(MANUAL_WORKFLOW)
    forbidden = ("\n  push:", "\n  schedule:", "LIVE_TRADING_ENABLED: \"1\"")
    workflow_ok = bool(workflow) and "workflow_dispatch:" in workflow and not any(x in workflow for x in forbidden)
    record("MANUAL_ONLY_DEPLOY_WORKFLOW", "PASS" if workflow_ok else "BLOCKED",
           "manual-only workflow source present" if workflow_ok else
           "missing or unsafe deployment workflow",
           MANUAL_WORKFLOW + " with no push/schedule and independent approval gate")
    deploy = content(DEPLOY_ENTRYPOINT)
    record("DEPLOY_IMPLEMENTATION", "PASS" if deploy and "OWNER_DEPLOYMENT_APPROVAL" in deploy
           and "no-traffic" in deploy else "BLOCKED",
           "candidate deploy implementation source present" if deploy else "deployment entrypoint absent",
           "independently tested approved zero-traffic deploy and rollback")
    if not workflow or not deploy:
        record("HISTORICAL_DEPLOY_STACK", "HISTORICAL_ONLY",
               "prior auto-deploy workflow and Python entrypoint were removed in commit 60034500b52b",
               "do not resurrect an automatic push-to-production path")

    record("GCP_MUTATION_AUTHORITY", "BLOCKED",
           "owner approved GitHub work and read-only GCP inspection only",
           "separate explicit bounded billable deployment approval")
    record("LIVE_PRODUCTION_EVIDENCE", "UNKNOWN",
           "not inspected; repository snapshot is not GCP runtime evidence",
           "fresh project-scoped deployed digest, service/job/scheduler, broker/UI/order-safety receipts")

    overall = "BLOCKED" if any(c["status"] == "BLOCKED" for c in checks) else "NOT_PROVEN"
    report = {
        "schema": "system3-cloud-paper-preflight-v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "project": PROJECT, "project_number": PROJECT_NUMBER, "region": REGION,
        "source_sha": source_sha, "canonical_dockerfile": CANONICAL_DOCKERFILE,
        "overall": overall, "checks": checks,
        "gcp_mutations_performed": False, "broker_calls_performed": False,
        "secrets_read": False, "live_order_authority": False,
    }
    proof = json.dumps(report, sort_keys=True, separators=(",", ":")).encode()
    report["receipt_sha256"] = hashlib.sha256(proof).hexdigest()
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--sha", default=os.getenv("GITHUB_SHA", "UNRESOLVED"))
    parser.add_argument("--strict", action="store_true",
                        help="return 2 when release prerequisites or owner authority are blocked")
    args = parser.parse_args()
    report = check_repo(args.repo.resolve(), args.sha)
    print(json.dumps(report, sort_keys=True, indent=2))
    # A normal zero exit certifies only read-only report generation, never deploy readiness.
    return 2 if args.strict and report["overall"] != "PASS" else 0


if __name__ == "__main__":
    raise SystemExit(main())
