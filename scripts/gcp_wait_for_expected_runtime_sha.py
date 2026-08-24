#!/usr/bin/env python3
"""Wait read-only for Cloud Run to serve the expected runtime-affecting Git SHA.

This closes a control-plane race where the Full Cloud Audit starts on a main push
before the parallel Cloud Run deployment has promoted that push's runtime image.
Docs/proof-only main commits are handled by resolving the newest first-parent
commit that actually matches the deploy workflow's runtime trigger paths.

No deployment, IAM, secret payload, broker mutation, or order action is performed.
"""
from __future__ import annotations

import json
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from system3_resolve_runtime_deploy_sha import resolve_runtime_deploy_sha

PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "system3-openalgo-safe")
REGION = os.getenv("GCP_REGION", "asia-south1")
SERVICE = os.getenv("GCP_CLOUD_RUN_SERVICE", "genesis-system3-web")
TIMEOUT_S = max(30, min(1800, int(os.getenv("SYSTEM3_RUNTIME_CONVERGENCE_TIMEOUT_S", "900"))))
POLL_S = max(2, min(60, int(os.getenv("SYSTEM3_RUNTIME_CONVERGENCE_POLL_S", "15"))))
OUT = Path(os.getenv("SYSTEM3_RUNTIME_CONVERGENCE_DIR", "reports/latest/full_cloud_audit"))


def _gcloud_json(*args: str) -> dict[str, Any]:
    proc = subprocess.run(list(args), text=True, capture_output=True, check=False, timeout=90)
    if proc.returncode:
        return {"_error": f"command_failed:{proc.returncode}"}
    try:
        value = json.loads(proc.stdout or "{}")
    except Exception as exc:
        return {"_error": f"invalid_json:{type(exc).__name__}"}
    return value if isinstance(value, dict) else {"_error": "unexpected_json_shape"}


def _single_100_revision(service: dict[str, Any]) -> str | None:
    traffic = (service.get("status") or {}).get("traffic") or []
    rows = [
        (str(row.get("revisionName") or ""), int(row.get("percent") or 0))
        for row in traffic if isinstance(row, dict) and row.get("revisionName")
    ]
    if len(rows) == 1 and rows[0][1] == 100:
        return rows[0][0]
    return None


def _safe_deploy_sha(revision: dict[str, Any]) -> str | None:
    containers = ((revision.get("spec") or {}).get("containers") or [])
    if not containers:
        return None
    for row in containers[0].get("env") or []:
        if isinstance(row, dict) and row.get("name") == "DEPLOY_GIT_SHA" and "value" in row:
            value = str(row.get("value") or "").strip()
            return value if len(value) == 40 else None
    return None


def observe() -> tuple[str | None, str | None, str | None]:
    service = _gcloud_json(
        "gcloud", "run", "services", "describe", SERVICE,
        f"--project={PROJECT}", f"--region={REGION}", "--format=json",
    )
    if service.get("_error"):
        return None, None, service["_error"]
    revision_name = _single_100_revision(service)
    if not revision_name:
        return None, None, "serving_traffic_not_single_100"
    revision = _gcloud_json(
        "gcloud", "run", "revisions", "describe", revision_name,
        f"--project={PROJECT}", f"--region={REGION}", "--format=json",
    )
    if revision.get("_error"):
        return revision_name, None, revision["_error"]
    return revision_name, _safe_deploy_sha(revision), None


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    expected_sha, trigger_paths = resolve_runtime_deploy_sha("HEAD")
    started = time.monotonic()
    attempts: list[dict[str, Any]] = []
    final_revision = None
    final_sha = None
    final_error = None

    while True:
        revision, serving_sha, error = observe()
        final_revision, final_sha, final_error = revision, serving_sha, error
        attempts.append({
            "attempt": len(attempts) + 1,
            "revision": revision,
            "serving_sha": serving_sha,
            "error": error,
        })
        if serving_sha == expected_sha:
            state = "PASS"
            break
        elapsed = time.monotonic() - started
        if elapsed >= TIMEOUT_S:
            state = "FAIL"
            break
        time.sleep(min(POLL_S, max(0.0, TIMEOUT_S - elapsed)))

    report = {
        "schema": "system3-runtime-convergence-v1",
        "state": state,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "expected_serving_sha": expected_sha,
        "runtime_trigger_paths": trigger_paths,
        "serving_revision": final_revision,
        "serving_sha": final_sha,
        "last_error": final_error,
        "attempt_count": len(attempts),
        "timeout_seconds": TIMEOUT_S,
        "poll_seconds": POLL_S,
        "attempts": attempts[-20:],
        "read_only": True,
        "secret_payloads_accessed": False,
        "live_trading_enabled": False,
        "order_actions_performed": False,
    }
    (OUT / "runtime_convergence.json").write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    github_env = os.getenv("GITHUB_ENV", "").strip()
    if github_env:
        with open(github_env, "a", encoding="utf-8") as handle:
            handle.write(f"SYSTEM3_EXPECTED_SERVING_SHA={expected_sha}\n")

    print("SYSTEM3_RUNTIME_CONVERGENCE " + json.dumps({
        "state": state,
        "expected_serving_sha": expected_sha,
        "serving_revision": final_revision,
        "serving_sha": final_sha,
        "attempt_count": len(attempts),
    }, sort_keys=True))
    return 0 if state == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
