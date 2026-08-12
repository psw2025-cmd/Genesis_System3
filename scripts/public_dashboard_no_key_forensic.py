#!/usr/bin/env python3
"""Fail closed if active Genesis dashboard credential/session authority regresses.

This source/CI forensic gate does not read secret payloads, mutate GCP, or touch
broker/order paths. It scans current active execution surfaces recursively so a
new tool/workflow cannot silently restore dashboard credential authority.
Historical Git history and explanatory docs are not executable authority.
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


def _active_files() -> list[Path]:
    roots = [
        ROOT / "dashboard" / "backend",
        ROOT / "dashboard" / "frontend" / "src",
        ROOT / "scripts",
        ROOT / "tools",
        ROOT / "deploy",
        ROOT / ".github" / "workflows",
        ROOT / "config",
    ]
    suffixes = {
        ".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx",
        ".sh", ".ps1", ".cmd", ".bat", ".yml", ".yaml", ".toml",
    }
    rows: list[Path] = []
    for base in roots:
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if path.is_file() and path.suffix.lower() in suffixes:
                rows.append(path)
    return sorted(set(rows))


def _recursive_active_surface_scan() -> list[str]:
    """Reject credential semantics outside tightly bounded removal/proof code."""
    # These files mention retired names solely to scrub/detect them. The large
    # legacy app is temporarily allowed as inert compatibility code; package
    # import scrubbing + secure_app route/header/cookie removal means it is not
    # serving authority, and direct executable launchers are forbidden below.
    allowed_detection_paths = {
        Path("dashboard/backend/__init__.py"),
        Path("dashboard/backend/secure_app.py"),
        Path("dashboard/backend/app.py"),
        Path("scripts/gcp_cloud_run_auto_deploy.py"),
        Path("scripts/gcp_runtime_evidence.py"),
        Path("scripts/gcp_public_dashboard_runtime_proof.py"),
        Path("scripts/public_dashboard_no_key_forensic.py"),
        Path(".github/workflows/cloud-run-auto-deploy.yml"),
    }
    retired_markers = (
        "REQUIRE_" + "API_KEY",
        "DASHBOARD_" + "API_KEY",
        "ENABLE_DASHBOARD_" + "AUTH",
        "/api/auth/" + "session",
        "/api/auth/" + "logout",
        "X-" + "API-Key",
        "system3_dashboard_" + "session",
    )
    direct_legacy_launch_markers = (
        "dashboard.backend.app:app",
        "from app import app",
    )

    hits: list[str] = []
    for path in _active_files():
        rel = path.relative_to(ROOT)
        source = path.read_text(encoding="utf-8", errors="replace")
        if rel not in allowed_detection_paths:
            for marker in retired_markers:
                if marker in source:
                    hits.append(f"retired:{rel}:{marker}")
        # No active tool/script/workflow may directly launch the legacy app.
        if rel != Path("dashboard/backend/app.py"):
            for marker in direct_legacy_launch_markers:
                if marker in source:
                    hits.append(f"legacy-launch:{rel}:{marker}")
    return sorted(set(hits))


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

    # Package import boundary neutralizes environment drift before any backend
    # submodule (including direct dashboard.backend.app imports) initializes.
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
    # Match retired browser-auth codes exactly. Worker-only codes such as
    # WORKER_AUTH_NOT_CONFIGURED / WORKER_AUTH_INVALID are required and must
    # remain valid independently of dashboard visibility.
    forbid(policy, '"AUTH_REQUIRED_FOR_MUTATION"', "security policy")
    forbid(policy, '"AUTH_NOT_CONFIGURED"', "security policy")
    forbid(policy, '"AUTH_INVALID"', "security policy")

    retired_assignments = (
        "REQUIRE_" + "API_KEY=",
        "API_" + "KEY=",
        "DASHBOARD_" + "API_KEY=",
        "ENABLE_DASHBOARD_" + "AUTH=",
    )
    for marker in retired_assignments:
        forbid(env_example, marker, ".env.example")

    # Canonical deployer removes stale/manual Cloud Run configuration and then
    # refuses to promote a candidate that still carries any retired surface.
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

    active_hits = _recursive_active_surface_scan()
    if active_hits:
        fail(f"active execution surface regression {active_hits}")

    result = {
        "state": "PROVEN",
        "dashboard_visibility": "PUBLIC_READONLY",
        "dashboard_credential_authority": "REMOVED",
        "server_session_authority": "REMOVED",
        "frontend_credential_collector": "ABSENT",
        "cloud_launcher": "SECURE_WRAPPER_ONLY",
        "active_surface_scan": "PASS",
        "active_files_scanned": len(_active_files()),
        "legacy_app_auth_code": "INERT_COMPATIBILITY_ONLY",
        "gcp_drift_scrub": "REQUIRED",
        "worker_authority": "DEDICATED_WORKER_TOKEN",
        "live_mutation": "HARD_DENY",
        "secret_payloads_accessed": False,
    }
    print("PUBLIC_DASHBOARD_NO_KEY_FORENSIC", json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
