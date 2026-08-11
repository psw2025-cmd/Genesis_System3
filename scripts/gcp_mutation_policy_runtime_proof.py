#!/usr/bin/env python3
"""Prove the deployed MutationPolicy boundary without mutating system state.

All POST probes target either no route or sentinel handlers that contain no
mutation implementation and intentionally fail if reached. No paper engine,
risk setting, scheduler control, broker order, live approval or live execution
handler is invoked by this proof.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.request
from pathlib import Path
from typing import Any

import requests

PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "system3-openalgo-safe")
REGION = os.getenv("GCP_REGION", "asia-south1")
SERVICE = os.getenv("GCP_CLOUD_RUN_SERVICE", "genesis-system3-web")
EXPECTED_SHA = os.getenv("GITHUB_SHA", "").strip()
OUT = Path("reports/latest/mutation_policy_runtime_proof")
TIMEOUT_S = 30


def _run(*args: str) -> str:
    proc = subprocess.run(
        list(args), text=True, capture_output=True, timeout=90, check=False
    )
    if proc.returncode:
        raise RuntimeError(f"command_failed:{args[0]}:{proc.returncode}")
    return proc.stdout.strip()


def _service_url() -> str:
    url = _run(
        "gcloud",
        "run",
        "services",
        "describe",
        SERVICE,
        f"--project={PROJECT}",
        f"--region={REGION}",
        "--format=value(status.url)",
    ).rstrip("/")
    if not url.startswith("https://"):
        raise RuntimeError("cloud_run_https_url_missing")
    return url


def _json(response: requests.Response) -> dict[str, Any]:
    try:
        data = response.json()
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def _request_id(response: requests.Response) -> str:
    return str(response.headers.get("X-Request-ID") or "").strip()


def _publish_status(state: str, description: str) -> None:
    token = os.getenv("GITHUB_TOKEN", "").strip()
    repo = os.getenv("GITHUB_REPOSITORY", "").strip()
    api = os.getenv("GITHUB_API_URL", "https://api.github.com").rstrip("/")
    if not (token and repo and len(EXPECTED_SHA) == 40):
        raise RuntimeError("github_status_context_missing")
    server = os.getenv("GITHUB_SERVER_URL", "https://github.com").rstrip("/")
    run_id = os.getenv("GITHUB_RUN_ID", "").strip()
    target = f"{server}/{repo}/actions/runs/{run_id}" if run_id else f"{server}/{repo}"
    payload = json.dumps(
        {
            "state": state,
            "context": "mutation-policy/runtime-proof",
            "description": description[:140],
            "target_url": target,
        }
    ).encode()
    request = urllib.request.Request(
        f"{api}/repos/{repo}/statuses/{EXPECTED_SHA}",
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        if response.status not in (200, 201):
            raise RuntimeError(f"commit_status_publish_failed:{response.status}")


def _probe(
    base: str,
    path: str,
    *,
    expected_status: int,
    expected_code: str,
) -> dict[str, Any]:
    response = requests.post(
        f"{base}{path}",
        json={"proof": "deny-only"},
        timeout=TIMEOUT_S,
    )
    body = _json(response)
    request_id = _request_id(response)
    ok = (
        response.status_code == expected_status
        and body.get("code") == expected_code
        and bool(request_id)
    )
    return {
        "path": path,
        "http_status": response.status_code,
        "expected_status": expected_status,
        "code": body.get("code"),
        "expected_code": expected_code,
        "request_id_present": bool(request_id),
        "body_detail_present": bool(body.get("detail")),
        "api_key_sent": False,
        "cookie_sent": False,
        "state": "PASS" if ok else "FAIL",
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    proof: dict[str, Any] = {
        "state": "FAIL",
        "expected_sha": EXPECTED_SHA,
        "live_order_endpoints_called": False,
        "paper_mutation_handlers_called": False,
        "secret_values_exposed": False,
    }
    try:
        if len(EXPECTED_SHA) != 40:
            raise RuntimeError("expected_git_sha_missing")
        base = _service_url()

        status_response = requests.get(
            f"{base}/api/security/mutation-policy", timeout=TIMEOUT_S
        )
        status = _json(status_response)
        status_ok = (
            status_response.status_code == 200
            and status.get("state") == "ENFORCED"
            and status.get("runtime_mode") == "ANALYZER_PAPER"
            and status.get("public_dashboard_read_only") is True
            and status.get("control_authority_configured") is False
            and status.get("live_mutation") == "HARD_DENY"
            and status.get("live_approval") == "HARD_DENY"
            and status.get("worker_authority") == "DEDICATED_WORKER_TOKEN"
            and status.get("unknown_count") == 0
            and status.get("duplicate_count") == 0
            and status.get("secret_values_exposed") is False
            and bool(status.get("manifest_sha256"))
        )

        probes = [
            _probe(
                base,
                "/api/security/mutation-policy/probe/paper",
                expected_status=403,
                expected_code="PAPER_MUTATION_AUTHORITY_REQUIRED",
            ),
            _probe(
                base,
                "/api/security/mutation-policy/probe/live",
                expected_status=423,
                expected_code="LIVE_MUTATION_LOCKED",
            ),
            _probe(
                base,
                "/api/security/mutation-policy/probe/worker",
                expected_status=401,
                expected_code="WORKER_AUTH_INVALID",
            ),
            _probe(
                base,
                "/api/security/mutation-policy/probe/unknown",
                expected_status=403,
                expected_code="MUTATION_CAPABILITY_UNKNOWN",
            ),
        ]
        probe_ok = all(row["state"] == "PASS" for row in probes)

        proof = {
            "state": "PASS" if status_ok and probe_ok else "FAIL",
            "expected_sha": EXPECTED_SHA,
            "service": SERVICE,
            "status_http_status": status_response.status_code,
            "manifest_state": status.get("state"),
            "manifest_sha256": status.get("manifest_sha256"),
            "write_route_count": status.get("write_route_count"),
            "unknown_count": status.get("unknown_count"),
            "duplicate_count": status.get("duplicate_count"),
            "public_dashboard_read_only": status.get("public_dashboard_read_only"),
            "control_authority_configured": status.get("control_authority_configured"),
            "live_mutation": status.get("live_mutation"),
            "live_approval": status.get("live_approval"),
            "worker_authority": status.get("worker_authority"),
            "probes": probes,
            "live_order_endpoints_called": False,
            "paper_mutation_handlers_called": False,
            "secret_values_exposed": False,
        }
        (OUT / "proof.json").write_text(
            json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8"
        )

        if proof["state"] != "PASS":
            raise RuntimeError("mutation_policy_runtime_proof_failed")

        _publish_status(
            "success",
            "MutationPolicy runtime deny matrix passed; LIVE hard locked",
        )
        print("MUTATION_POLICY_RUNTIME_PROOF " + json.dumps(proof, sort_keys=True))
        return 0
    except Exception as exc:
        proof["state"] = "FAIL"
        proof["error_type"] = type(exc).__name__
        proof["error"] = str(exc)[:180]
        (OUT / "proof.json").write_text(
            json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8"
        )
        try:
            _publish_status("failure", "MutationPolicy runtime proof failed")
        except Exception as status_exc:
            print(
                f"MUTATION_POLICY_STATUS_PUBLISH_ERROR {type(status_exc).__name__}",
                file=sys.stderr,
            )
        print(
            "MUTATION_POLICY_RUNTIME_PROOF " + json.dumps(proof, sort_keys=True),
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
