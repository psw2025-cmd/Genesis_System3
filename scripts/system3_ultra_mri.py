#!/usr/bin/env python3
"""System3 Ultra MRI — reusable read-only capability and production-truth scanner.

Runs inside the canonical GitHub->GCP WIF identity (or any authenticated gcloud
shell) and produces one consolidated evidence pack. It deliberately never reads
Secret Manager payloads. Credential correctness is proven through actual safe
consumers (Cloud Run/API/broker/browser paths), not by dumping plaintext secrets.
"""
from __future__ import annotations

import csv
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import requests
except Exception:  # pragma: no cover
    requests = None

PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "system3-openalgo-safe")
REGION = os.getenv("GCP_REGION", "asia-south1")
SERVICE = os.getenv("GCP_CLOUD_RUN_SERVICE", "genesis-system3-web")
OUT = Path(os.getenv("SYSTEM3_ULTRA_MRI_OUT", "reports/latest/system3_ultra_mri"))
OUT.mkdir(parents=True, exist_ok=True)

SENSITIVE = re.compile(r"(secret|token|password|passwd|private|credential|totp|\bpin\b|api[_-]?key)", re.I)
SAFE_SECRET_KEYS = {"name", "secret", "secretName", "secretKeyRef", "version", "versions", "key"}
CAPS: list[dict[str, str]] = []


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sanitize(value: Any, parent_key: str = "") -> Any:
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for key, val in value.items():
            skey = str(key)
            # Keep structural secret references/names, never payload-like values.
            if SENSITIVE.search(skey) and skey not in SAFE_SECRET_KEYS:
                if isinstance(val, (str, int, float, bool)) or val is None:
                    out[skey] = "<redacted>"
                    continue
            if skey == "value" and isinstance(value.get("name"), str):
                out[skey] = "<redacted-env-value>"
                continue
            out[skey] = _sanitize(val, skey)
        return out
    if isinstance(value, list):
        return [_sanitize(v, parent_key) for v in value]
    return value


def _write(name: str, content: str) -> None:
    (OUT / name).write_text(content, encoding="utf-8")


def _run(label: str, args: list[str], *, critical: bool = False, json_mode: bool = False, timeout: int = 120) -> tuple[int, str]:
    try:
        proc = subprocess.run(args, text=True, capture_output=True, timeout=timeout, check=False)
        rc = proc.returncode
        raw = proc.stdout.strip()
        err = proc.stderr.strip()
        if json_mode and raw:
            try:
                raw = json.dumps(_sanitize(json.loads(raw)), indent=2, sort_keys=True)
            except Exception:
                pass
        safe_err = err
        if SENSITIVE.search(safe_err):
            safe_err = "<stderr redacted: sensitive marker present>"
        _write(f"{label}.txt", (raw + ("\nSTDERR:\n" + safe_err if safe_err else "") + "\n"))
        status = "PASS" if rc == 0 else "FAIL"
        CAPS.append({"capability": label, "status": status, "critical": str(critical).lower(), "detail": f"exit={rc}"})
        return rc, raw
    except Exception as exc:
        _write(f"{label}.txt", f"ERROR {type(exc).__name__}: {exc}\n")
        CAPS.append({"capability": label, "status": "FAIL", "critical": str(critical).lower(), "detail": type(exc).__name__})
        return 99, ""


def _gcloud_json(label: str, parts: list[str], *, critical: bool = False, timeout: int = 120) -> tuple[int, str]:
    return _run(label, ["gcloud", *parts, "--format=json"], critical=critical, json_mode=True, timeout=timeout)


def _list_and_describe(kind: str, list_args: list[str], describe_builder, *, critical: bool = False) -> None:
    rc, raw = _gcloud_json(f"{kind}_list", list_args, critical=critical)
    if rc != 0 or not raw:
        return
    try:
        rows = json.loads(raw)
    except Exception:
        return
    if not isinstance(rows, list):
        return
    for idx, row in enumerate(rows[:200]):
        if not isinstance(row, dict):
            continue
        name = str(row.get("metadata", {}).get("name") or row.get("name") or row.get("id") or "").split("/")[-1]
        if not name:
            continue
        safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", name)[:100]
        _gcloud_json(f"{kind}_{idx:03d}_{safe}", describe_builder(name), critical=False)


def _http_probe(base: str, path: str, label: str, *, critical: bool = False) -> None:
    if requests is None:
        CAPS.append({"capability": label, "status": "FAIL", "critical": str(critical).lower(), "detail": "requests_missing"})
        return
    url = base.rstrip("/") + path
    try:
        response = requests.get(url, timeout=30)
        body: Any
        try:
            body = _sanitize(response.json())
            rendered = json.dumps(body, indent=2, sort_keys=True)
        except Exception:
            rendered = response.text[:20000]
        _write(f"{label}.txt", f"HTTP {response.status_code}\n{rendered}\n")
        ok = 200 <= response.status_code < 400
        CAPS.append({"capability": label, "status": "PASS" if ok else "FAIL", "critical": str(critical).lower(), "detail": f"http={response.status_code}"})
    except Exception as exc:
        _write(f"{label}.txt", f"ERROR {type(exc).__name__}: {exc}\n")
        CAPS.append({"capability": label, "status": "FAIL", "critical": str(critical).lower(), "detail": type(exc).__name__})


def main() -> int:
    metadata = {
        "captured_at_utc": _now(),
        "project": PROJECT,
        "region": REGION,
        "service": SERVICE,
        "github_sha": os.getenv("GITHUB_SHA", ""),
        "github_run_id": os.getenv("GITHUB_RUN_ID", ""),
        "mode": "READ_ONLY_ULTRA_MRI",
        "secret_policy": "metadata_and_consumer_validation_only_no_payload_dump",
    }
    _write("00_metadata.json", json.dumps(metadata, indent=2))

    # Identity + project + API authority.
    _run("gcloud_version", ["gcloud", "version"], critical=True)
    _gcloud_json("gcloud_auth", ["auth", "list"], critical=True)
    _gcloud_json("project_describe", ["projects", "describe", PROJECT], critical=True)
    _gcloud_json("enabled_apis", ["services", "list", f"--project={PROJECT}", "--enabled"], critical=True)
    _gcloud_json("project_iam", ["projects", "get-iam-policy", PROJECT], critical=True)
    _gcloud_json("service_accounts", ["iam", "service-accounts", "list", f"--project={PROJECT}"], critical=True)

    # WIF inventory. Failure is recorded, not hidden.
    _gcloud_json("wif_pools", ["iam", "workload-identity-pools", "list", f"--project={PROJECT}", "--location=global"], critical=False)

    # Cloud Run service/job authority and sanitized runtime configuration.
    _list_and_describe(
        "run_service",
        ["run", "services", "list", f"--project={PROJECT}", f"--region={REGION}"],
        lambda n: ["run", "services", "describe", n, f"--project={PROJECT}", f"--region={REGION}"],
        critical=True,
    )
    _list_and_describe(
        "run_job",
        ["run", "jobs", "list", f"--project={PROJECT}", f"--region={REGION}"],
        lambda n: ["run", "jobs", "describe", n, f"--project={PROJECT}", f"--region={REGION}"],
        critical=True,
    )
    _gcloud_json("run_revisions", ["run", "revisions", "list", f"--project={PROJECT}", f"--region={REGION}"], critical=True)

    # Schedulers and their exact targets/schedules.
    _list_and_describe(
        "scheduler",
        ["scheduler", "jobs", "list", f"--project={PROJECT}", f"--location={REGION}"],
        lambda n: ["scheduler", "jobs", "describe", n, f"--project={PROJECT}", f"--location={REGION}"],
        critical=True,
    )

    # Secret inventory/version metadata only. Never access payload data.
    rc, secrets_raw = _gcloud_json("secrets_list", ["secrets", "list", f"--project={PROJECT}"], critical=True)
    if rc == 0 and secrets_raw:
        try:
            secrets = json.loads(secrets_raw)
        except Exception:
            secrets = []
        for idx, item in enumerate(secrets[:200] if isinstance(secrets, list) else []):
            name = str((item.get("name") if isinstance(item, dict) else "") or "").split("/")[-1]
            if name:
                safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", name)[:100]
                _gcloud_json(f"secret_versions_{idx:03d}_{safe}", ["secrets", "versions", "list", name, f"--project={PROJECT}"], critical=False)

    # Data/storage/database infrastructure inventory.
    _gcloud_json("firestore_databases", ["firestore", "databases", "list", f"--project={PROJECT}"], critical=True)
    _gcloud_json("storage_buckets", ["storage", "buckets", "list", f"--project={PROJECT}"], critical=False)
    _gcloud_json("artifact_repositories", ["artifacts", "repositories", "list", f"--project={PROJECT}", f"--location={REGION}"], critical=False)
    _gcloud_json("sql_instances", ["sql", "instances", "list", f"--project={PROJECT}"], critical=False)

    # Other resource classes that can create drift/cost/confusion.
    for label, cmd in [
        ("compute_instances", ["compute", "instances", "list", f"--project={PROJECT}"]),
        ("functions", ["functions", "list", f"--project={PROJECT}"]),
        ("pubsub_topics", ["pubsub", "topics", "list", f"--project={PROJECT}"]),
        ("pubsub_subscriptions", ["pubsub", "subscriptions", "list", f"--project={PROJECT}"]),
        ("logging_sinks", ["logging", "sinks", "list", f"--project={PROJECT}"]),
    ]:
        _gcloud_json(label, cmd, critical=False)

    # Current production logs — bounded and sanitized.
    _run(
        "recent_cloud_run_logs",
        ["gcloud", "logging", "read", f'resource.type="cloud_run_revision" AND resource.labels.service_name="{SERVICE}"', f"--project={PROJECT}", "--limit=100", "--freshness=24h", "--format=json"],
        critical=True,
        json_mode=True,
        timeout=180,
    )

    # Resolve canonical public service URL.
    rc, service_url = _run(
        "service_url",
        ["gcloud", "run", "services", "describe", SERVICE, f"--project={PROJECT}", f"--region={REGION}", "--format=value(status.url)"],
        critical=True,
    )
    service_url = service_url.strip()
    if rc == 0 and service_url.startswith("https://"):
        # Same-session read-only production probes.
        probes = [
            ("/api/health", "api_health", True),
            ("/api/healthz", "api_healthz", True),
            ("/api/deploy/info", "api_deploy_info", True),
            ("/api/broker/status", "api_broker_status", True),
            ("/api/state", "api_state", True),
            ("/api/auto_gates", "api_auto_gates", False),
            ("/api/batch/chains", "api_batch_chains", True),
            ("/api/qc/runtime", "api_qc_runtime", False),
            ("/api/scheduler/health?refresh=true", "api_scheduler_health", False),
            ("/ui", "ui_shell", True),
        ]
        for path, label, critical in probes:
            _http_probe(service_url, path, label, critical=critical)

    # Existing canonical browser proof is itself a capability test. It is allowed
    # to fail closed; Ultra MRI continues so the evidence pack survives.
    proof = Path("scripts/gcp_public_dashboard_runtime_proof.py")
    if proof.exists():
        _run("canonical_browser_proof", [sys.executable, str(proof)], critical=True, timeout=300)
    else:
        CAPS.append({"capability": "canonical_browser_proof", "status": "FAIL", "critical": "true", "detail": "script_missing"})

    # Repo lifecycle/control artifacts: inventory only; agents can trace exact files.
    _run("repo_tracked_files", ["git", "ls-files"], critical=True, timeout=60)
    _run("repo_current_sha", ["git", "rev-parse", "HEAD"], critical=True)
    _run("repo_status", ["git", "status", "--short"], critical=False)

    # Capability matrix + machine verdict.
    with (OUT / "CAPABILITY_MATRIX.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["capability", "status", "critical", "detail"])
        writer.writeheader()
        writer.writerows(CAPS)

    critical_failures = [row for row in CAPS if row["critical"] == "true" and row["status"] != "PASS"]
    verdict = {
        "captured_at_utc": _now(),
        "access_certified": not critical_failures,
        "critical_failures": critical_failures,
        "capabilities_total": len(CAPS),
        "pass": sum(1 for r in CAPS if r["status"] == "PASS"),
        "fail": sum(1 for r in CAPS if r["status"] == "FAIL"),
        "rule": "No later 'missing access' excuse: any failed critical capability must become an immediate access-resolution/takeover action before dependent work.",
    }
    _write("FINAL_VERDICT.json", json.dumps(verdict, indent=2))
    lines = [
        "# System3 Ultra MRI — Final Verdict",
        "",
        f"- Captured: `{verdict['captured_at_utc']}`",
        f"- ACCESS_CERTIFIED: **{str(verdict['access_certified']).upper()}**",
        f"- Capabilities: {verdict['pass']} PASS / {verdict['fail']} FAIL / {verdict['capabilities_total']} total",
        "",
        "## Critical failures",
    ]
    if critical_failures:
        lines.extend([f"- `{r['capability']}` — {r['detail']}" for r in critical_failures])
    else:
        lines.append("- None")
    lines += [
        "",
        "## Evidence policy",
        "Secret payloads are never dumped. Secret names/versions/references are inventoried and correctness is validated through the real consuming runtime/API/browser paths.",
        "",
        "A green access scan is not trading-performance completion. Prediction, PAPER, backtest, historical data and UI outcomes remain independently proof-gated.",
    ]
    _write("FINAL_VERDICT.md", "\n".join(lines) + "\n")
    print(json.dumps(verdict, indent=2))
    return 0  # Always preserve/upload the full diagnostic pack; verdict carries failures.


if __name__ == "__main__":
    raise SystemExit(main())
