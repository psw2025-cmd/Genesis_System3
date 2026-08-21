#!/usr/bin/env python3
"""Read-only attribution of Dhan token issuance and Secret Manager writes.

Raw secret values are held only in process memory long enough to decode JWT
``iat``/``exp`` timestamps. They are never printed or written to the report.
No secret, IAM, Cloud Run, Scheduler, broker, or order state is mutated.
"""
from __future__ import annotations

import argparse
import base64
import json
import shutil
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PROJECT = "system3-openalgo-safe"
REGION = "asia-south1"
TOKEN_SECRET_ID = "dhan-access-token"
JOB = "genesis-system3-dhan-token-rotate"
EXPECTED_WRITER = "genesis-system3-dhan-rotator@system3-openalgo-safe.iam.gserviceaccount.com"


def _dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


def _run(args: list[str], timeout: int = 150) -> tuple[int, str]:
    try:
        p = subprocess.run(args, cwd=ROOT, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=timeout, check=False)
        return p.returncode, (p.stdout or "").strip()
    except (OSError, subprocess.TimeoutExpired):
        return 127, ""


def _json(args: list[str]) -> Any:
    rc, out = _run(args)
    if rc != 0:
        return {"_error": f"command_exit_{rc}"}
    for start in range(len(out) + 1):
        if start == len(out) or out[start] not in "[{":
            continue
        try:
            return json.loads(out[start:])
        except json.JSONDecodeError:
            pass
    return {"_error": "invalid_json"}


def _jwt_times(token: str) -> dict[str, str | None]:
    safe = {"issued_at_utc": None, "expires_at_utc": None}
    try:
        part = token.split(".")[1]
        payload = json.loads(base64.urlsafe_b64decode(part + "=" * (-len(part) % 4)))
        for claim, key in (("iat", "issued_at_utc"), ("exp", "expires_at_utc")):
            if payload.get(claim) is not None:
                safe[key] = datetime.fromtimestamp(float(payload[claim]), timezone.utc).isoformat()
    except (IndexError, ValueError, TypeError, json.JSONDecodeError):
        pass
    return safe


def correlate(version: dict[str, Any], executions: list[dict[str, Any]],
              audit_events: list[dict[str, Any]], tolerance_s: int = 180) -> dict[str, Any]:
    created = _dt(version.get("createTime"))
    window = timedelta(seconds=tolerance_s)
    matching_exec: list[str] = []
    for execution in executions:
        start = _dt((execution.get("status") or {}).get("startTime") or execution.get("createTime"))
        end = _dt((execution.get("status") or {}).get("completionTime")) or start
        name = (execution.get("metadata") or {}).get("name") or execution.get("name")
        if created and start and end and start - window <= created <= end + window:
            matching_exec.append(str(name))
    principals: list[str] = []
    for event in audit_events:
        stamp = _dt(event.get("timestamp"))
        if not created or not stamp or abs((stamp - created).total_seconds()) > tolerance_s:
            continue
        principal = (((event.get("protoPayload") or {}).get("authenticationInfo") or {})
                     .get("principalEmail"))
        if principal:
            principals.append(str(principal))
    principals = sorted(set(principals))
    if principals:
        verdict = "CANONICAL_WRITER_PROVEN" if principals == [EXPECTED_WRITER] else "UNEXPECTED_GCP_WRITER_PROVEN"
    elif matching_exec:
        verdict = "CANONICAL_EXECUTION_TIME_MATCH_ONLY"
    else:
        verdict = "UNATTRIBUTED_GCP_VERSION"
    return {"verdict": verdict, "matching_executions": matching_exec,
            "audit_principals": principals, "tolerance_seconds": tolerance_s}


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only Dhan token issuer forensics")
    parser.add_argument("--out", default="reports/latest/dhan_token_issuer_forensics/summary.json")
    parser.add_argument("--lookback-days", type=int, default=7)
    parser.add_argument("--all-versions", action="store_true",
                        help="Also inspect disabled versions (enabled-only is the safe fast default)")
    args = parser.parse_args()
    gcloud = shutil.which("gcloud.cmd") or shutil.which("gcloud") or "gcloud"
    versions = _json([gcloud, "secrets", "versions", "list", TOKEN_SECRET_ID, "--project", PROJECT,
                      "--limit=100", "--format=json(name,state,createTime)"])
    executions = _json([gcloud, "run", "jobs", "executions", "list", "--job", JOB,
                        "--project", PROJECT, "--region", REGION, "--limit=100", "--format=json"])
    audit_filter = (f'protoPayload.methodName="google.cloud.secretmanager.v1.SecretManagerService.AddSecretVersion" '
                    f'AND resource.labels.secret_id="{TOKEN_SECRET_ID}"')
    audits = _json([gcloud, "logging", "read", audit_filter, "--project", PROJECT,
                    f"--freshness={args.lookback_days}d", "--limit=200", "--format=json"])
    safe_versions: list[dict[str, Any]] = []
    selected_versions = versions if isinstance(versions, list) else []
    if not args.all_versions:
        selected_versions = [v for v in selected_versions
                             if str(v.get("state") or "").upper() == "ENABLED"]
    for item in selected_versions:
        version_id = str(item.get("name") or "").rstrip("/").split("/")[-1]
        rc, token = _run([gcloud, "secrets", "versions", "access", version_id,
                          "--secret", TOKEN_SECRET_ID, "--project", PROJECT])
        times = _jwt_times(token) if rc == 0 else {"issued_at_utc": None, "expires_at_utc": None}
        token = ""  # discard payload reference before creating any report object
        safe = {"version": version_id, "state": item.get("state"),
                "secret_created_at_utc": item.get("createTime"), **times,
                "payload_access_succeeded": rc == 0, "raw_token_exposed": False}
        safe["attribution"] = correlate(item, executions if isinstance(executions, list) else [],
                                         audits if isinstance(audits, list) else [])
        safe_versions.append(safe)
    report = {
        "schema": "system3-dhan-token-issuer-forensics-v1",
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "project": PROJECT, "secret_id": TOKEN_SECRET_ID, "canonical_job": JOB,
        "versions": safe_versions,
        "audit_log_available": isinstance(audits, list),
        "limits": [
            "GCP can attribute Secret Manager writes, not an unpersisted token minted on Dhan web/app.",
            "A JWT issued_at later than its Secret Manager create time can prove timing inconsistency, not the human actor.",
            "Exact external issuer requires Dhan login/session/audit history or an observed canonical write event.",
        ],
        "safety": {"cloud_mutations": False, "broker_calls": False, "order_calls": False,
                   "raw_token_exposed": False},
    }
    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"report": str(out), "versions": len(safe_versions),
                      "audit_log_available": report["audit_log_available"],
                      "raw_token_exposed": False}, indent=2))
    return 0 if safe_versions else 2


if __name__ == "__main__":
    raise SystemExit(main())
