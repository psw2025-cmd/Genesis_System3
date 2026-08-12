#!/usr/bin/env python3
"""Fail closed if active Genesis dashboard credential/session authority regresses.

This is a source/CI forensic gate. It does not read secret payloads, mutate GCP,
or touch broker/order paths. Historical Git history is out of scope; current
active execution surfaces must satisfy the permanent public-readonly contract.
"""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def fail(message: str) -> None:
    raise SystemExit(f"PUBLIC_DASHBOARD_NO_KEY_FORENSIC_FAIL {message}")


def require(source: str, marker: str, label: str) -> None:
    if marker not in source:
        fail(f"{label}: missing required marker {marker!r}")


def forbid(source: str, marker: str, label: str) -> None:
    if marker in source:
        fail(f"{label}: forbidden marker {marker!r}")


def main() -> int:
    launcher = text("scripts/start_cloud_run.py")
    secure = text("dashboard/backend/secure_app.py")
    package_boundary = text("dashboard/backend/__init__.py")
    policy = text("dashboard/backend/security_policy.py")
    mutation = text("dashboard/backend/mutation_policy.py")
    deployer = text("scripts/gcp_cloud_run_auto_deploy.py")
    env_example = text(".env.example")

    require(launcher, '"dashboard.backend.secure_app:app"', "cloud launcher")
    forbid(launcher, '"dashboard.backend.app:app"', "cloud launcher")

    # Backend package boundary must neutralize drift before any submodule import.
    require(package_boundary, "scrub_retired_dashboard_auth_environment()", "backend package boundary")
    require(package_boundary, '"REQUIRE_" + "API_KEY"', "backend package boundary")
    require(package_boundary, '"DASHBOARD_" + "API_KEY"', "backend package boundary")

    require(secure, "os.environ.pop", "secure wrapper")
    require(secure, "legacy._REQUIRE_API_KEY = False", "secure wrapper")
    require(secure, 'legacy._API_KEY = ""', "secure wrapper")
    require(secure, "strip_retired_dashboard_credentials", "secure wrapper")
    require(secure, '"credential_surface": "REMOVED"', "secure wrapper")
    forbid(secure, "get_session_truth_store", "secure wrapper")
    forbid(secure, "create_dashboard_session", "secure wrapper")
    forbid(secure, "dashboard_auth_logout", "secure wrapper")
    forbid(secure, "set_cookie(", "secure wrapper")

    forbid(mutation, "SESSION_CREATE", "mutation policy")
    forbid(mutation, "SESSION_REVOKE_SELF", "mutation policy")
    require(mutation, "LIVE_MUTATION_LOCKED", "mutation policy")
    require(mutation, "WORKER_AUTH_INVALID", "mutation policy")

    require(policy, "PUBLIC_DASHBOARD_READ_ONLY", "security policy")
    forbid(policy, "AUTH_REQUIRED_FOR_MUTATION", "security policy")
    forbid(policy, "AUTH_NOT_CONFIGURED", "security policy")
    forbid(policy, "AUTH_INVALID", "security policy")

    # Operator template must not advertise retired dashboard credential knobs.
    retired_assignments = (
        "REQUIRE_" + "API_KEY=",
        "API_" + "KEY=",
        "DASHBOARD_" + "API_KEY=",
        "ENABLE_DASHBOARD_" + "AUTH=",
    )
    for marker in retired_assignments:
        forbid(env_example, marker, ".env.example")

    # Canonical GCP deployer must remove, not configure, retired surfaces and
    # must reject a candidate that still carries one.
    require(deployer, "RETIRED_DASHBOARD_ENV", "canonical deployer")
    require(deployer, "RETIRED_DASHBOARD_SECRETS", "canonical deployer")
    require(deployer, "--remove-env-vars=", "canonical deployer")
    require(deployer, "--remove-secrets=", "canonical deployer")
    require(deployer, "_assert_candidate_has_no_dashboard_credentials", "canonical deployer")

    frontend_root = ROOT / "dashboard/frontend/src"
    frontend_forbidden = (
        "LoginPage",
        "useAuth",
        "/api/auth/" + "session",
        "Enter the dashboard" + " API key",
    )
    frontend_hits = []
    for path in frontend_root.rglob("*"):
        if not path.is_file() or path.suffix not in {".ts", ".tsx", ".js", ".jsx"}:
            continue
        source = path.read_text(encoding="utf-8", errors="replace")
        for marker in frontend_forbidden:
            if marker in source:
                frontend_hits.append(f"{path.relative_to(ROOT)}:{marker}")
    if frontend_hits:
        fail(f"frontend credential regression {frontend_hits}")

    if (ROOT / "dashboard/backend/session_truth.py").exists():
        fail("retired server-side dashboard session authority still exists")
    if (ROOT / "scripts/gcp_session_runtime_proof.py").exists():
        fail("retired dashboard session runtime proof still exists")

    result = {
        "state": "PROVEN",
        "dashboard_visibility": "PUBLIC_READONLY",
        "dashboard_credential_authority": "REMOVED",
        "server_session_authority": "REMOVED",
        "frontend_credential_collector": "ABSENT",
        "cloud_launcher": "SECURE_WRAPPER_ONLY",
        "gcp_drift_scrub": "REQUIRED",
        "worker_authority": "DEDICATED_WORKER_TOKEN",
        "live_mutation": "HARD_DENY",
        "secret_payloads_accessed": False,
    }
    print("PUBLIC_DASHBOARD_NO_KEY_FORENSIC", json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
