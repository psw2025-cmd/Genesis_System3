#!/usr/bin/env python3
"""Prove deployed Cloud Run SessionTruth on the exact source revision.

The proof is deliberately independent from Dhan/broker readiness. It validates
only the dashboard authentication boundary and publishes a dedicated
`sessiontruth/runtime-proof` commit status when running in GitHub Actions.

No broker mutation or live-trading route is called. Secret/cookie values are
never printed or written to artifacts.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.request
from dataclasses import asdict, dataclass
from urllib.parse import urlparse

import requests


PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT", "system3-openalgo-safe")
REGION = os.environ.get("GCP_REGION", "asia-south1")
SERVICE = os.environ.get("GCP_CLOUD_RUN_SERVICE", "genesis-system3-web")
API_KEY_SECRET_ID = os.environ.get("API_KEY_SECRET_ID", "system3-dashboard-api-key")
EXPECTED_SHA = os.environ.get("GITHUB_SHA", "").strip()
TIMEOUT_S = 30
STATUS_CONTEXT = "sessiontruth/runtime-proof"


@dataclass
class Proof:
    state: str = "FAIL"
    service: str = SERVICE
    expected_sha: str | None = EXPECTED_SHA or None
    deployed_sha_matches: bool = False
    traffic_100: bool = False
    auth_env_required: bool = False
    live_off: bool = False
    analyze_mode: bool = False
    revision: str | None = None
    anonymous_status: bool = False
    shared_backend: bool = False
    invalid_login_rejected: bool = False
    valid_session_created: bool = False
    cookie_httponly: bool = False
    cookie_secure: bool = False
    cookie_samesite_lax: bool = False
    authenticated_status: bool = False
    csrf_logout_rejected: bool = False
    server_revoked: bool = False
    replay_rejected: bool = False


def _run(*args: str) -> str:
    proc = subprocess.run(
        list(args), check=True, capture_output=True, text=True
    )
    return proc.stdout.strip()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _service_doc() -> dict:
    raw = _run(
        "gcloud", "run", "services", "describe", SERVICE,
        f"--project={PROJECT}", f"--region={REGION}", "--format=json",
    )
    data = json.loads(raw)
    _require(isinstance(data, dict), "Cloud Run service document is not an object")
    return data


def _containers(service: dict) -> list[dict]:
    rows = (((service.get("spec") or {}).get("template") or {}).get("spec") or {}).get("containers") or []
    if not rows:
        rows = ((service.get("template") or {}).get("containers") or [])
    return rows if isinstance(rows, list) else []


def _env_map(service: dict) -> dict[str, str]:
    rows = _containers(service)
    env: dict[str, str] = {}
    if not rows:
        return env
    for item in rows[0].get("env") or []:
        name = str(item.get("name") or "")
        if name and "value" in item:
            env[name] = str(item.get("value") or "")
    return env


def _latest_revision(service: dict) -> str:
    status = service.get("status") or {}
    return str(status.get("latestReadyRevisionName") or status.get("latestReadyRevision") or "")


def _traffic_is_100(service: dict, revision: str) -> bool:
    traffic = (service.get("status") or {}).get("traffic") or service.get("trafficStatuses") or []
    if not isinstance(traffic, list):
        return False
    for row in traffic:
        rev = str(row.get("revisionName") or row.get("revision") or "")
        try:
            pct = int(row.get("percent") or 0)
        except (TypeError, ValueError):
            pct = 0
        if rev == revision and pct == 100:
            return True
        # Some Cloud Run responses identify the current revision as latestRevision.
        if row.get("latestRevision") is True and pct == 100:
            return True
    return False


def _service_url(service: dict) -> str:
    status = service.get("status") or {}
    url = str(status.get("url") or service.get("uri") or "").rstrip("/")
    if not url:
        url = _run(
            "gcloud", "run", "services", "describe", SERVICE,
            f"--project={PROJECT}", f"--region={REGION}",
            "--format=value(status.url)",
        ).rstrip("/")
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.netloc:
        raise RuntimeError("Cloud Run service URL is not a valid HTTPS origin")
    return url


def _dashboard_api_key() -> str:
    value = _run(
        "gcloud", "secrets", "versions", "access", "latest",
        f"--secret={API_KEY_SECRET_ID}", f"--project={PROJECT}",
    )
    if not value:
        raise RuntimeError("Dashboard API key secret resolved empty")
    return value


def _json(response: requests.Response) -> dict:
    try:
        data = response.json()
    except Exception as exc:
        raise RuntimeError(
            f"Expected JSON from {response.request.method} {response.request.url}; "
            f"status={response.status_code}"
        ) from exc
    return data if isinstance(data, dict) else {}


def _publish_status(state: str, description: str) -> None:
    if os.environ.get("GITHUB_ACTIONS") != "true":
        return
    token = os.environ.get("GITHUB_TOKEN", "")
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    sha = EXPECTED_SHA
    api = os.environ.get("GITHUB_API_URL", "https://api.github.com")
    server = os.environ.get("GITHUB_SERVER_URL", "https://github.com")
    run_id = os.environ.get("GITHUB_RUN_ID", "")
    _require(bool(token and repo and sha and run_id), "GitHub status publication context is incomplete")
    target = f"{server}/{repo}/actions/runs/{run_id}"
    body = json.dumps({
        "state": state,
        "context": STATUS_CONTEXT,
        "description": description[:140],
        "target_url": target,
    }).encode()
    req = urllib.request.Request(
        f"{api}/repos/{repo}/statuses/{sha}",
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        _require(response.status in (200, 201), f"GitHub status publish returned {response.status}")


def _verify_service_identity(service: dict, proof: Proof) -> str:
    env = _env_map(service)
    revision = _latest_revision(service)
    _require(bool(revision), "Cloud Run latest ready revision is missing")
    proof.revision = revision
    _require(bool(EXPECTED_SHA), "GITHUB_SHA is required for exact-revision proof")
    proof.deployed_sha_matches = env.get("DEPLOY_GIT_SHA") == EXPECTED_SHA
    _require(
        proof.deployed_sha_matches,
        f"DEPLOY_GIT_SHA does not match exact source SHA {EXPECTED_SHA[:12]}",
    )
    proof.traffic_100 = _traffic_is_100(service, revision)
    _require(proof.traffic_100, "latest ready Cloud Run revision does not own 100% traffic")
    proof.auth_env_required = env.get("REQUIRE_API_KEY", "").strip().lower() in {"1", "true", "yes", "on"}
    _require(proof.auth_env_required, "Cloud Run REQUIRE_API_KEY is not enabled")
    proof.live_off = all(
        env.get(key, "0").strip().lower() in {"0", "false", "no", "off"}
        for key in ("LIVE_TRADING_ENABLED", "SYSTEM3_LIVE_TRADING_ALLOWED", "AUTO_EXECUTE_TRADES")
    )
    _require(proof.live_off, "Cloud Run live-trading-off invariants are not all enforced")
    proof.analyze_mode = env.get("ANALYZE_MODE", "").strip().lower() in {"1", "true", "yes", "on"}
    _require(proof.analyze_mode, "Cloud Run ANALYZE_MODE is not enabled")
    return _service_url(service)


def main() -> int:
    proof = Proof()
    error_text = ""
    exit_code = 1
    try:
        service = _service_doc()
        base = _verify_service_identity(service, proof)
        origin = base
        api_key = _dashboard_api_key()

        anon = requests.get(f"{base}/api/auth/status", timeout=TIMEOUT_S)
        _require(anon.status_code == 200, f"anonymous auth status returned {anon.status_code}")
        anon_data = _json(anon)
        _require(anon_data.get("required") is True, "dashboard auth is not required")
        _require(anon_data.get("configured") is True, "dashboard API auth is not configured")
        _require(anon_data.get("authenticated") is False, "anonymous request unexpectedly authenticated")
        _require(anon_data.get("mode") == "session_cookie_or_header", f"unexpected anonymous auth mode {anon_data.get('mode')!r}")
        _require(anon_data.get("session_backend") == "firestore", f"Cloud Run SessionTruth backend is {anon_data.get('session_backend')!r}, expected 'firestore'")
        proof.anonymous_status = True
        proof.shared_backend = True

        invalid = requests.post(
            f"{base}/api/auth/session",
            json={"api_key": "deploy-ci-invalid-probe"},
            timeout=TIMEOUT_S,
        )
        _require(invalid.status_code == 401, f"invalid login returned {invalid.status_code}, expected 401")
        proof.invalid_login_rejected = True

        browser = requests.Session()
        login = browser.post(
            f"{base}/api/auth/session",
            json={"api_key": api_key},
            timeout=TIMEOUT_S,
        )
        api_key = ""
        _require(login.status_code == 200, f"valid session creation returned {login.status_code}")
        login_data = _json(login)
        _require(login_data.get("authenticated") is True, "valid session response not authenticated")
        _require(login_data.get("mode") == "opaque_server_session", "session is not opaque_server_session")
        _require(login_data.get("session_backend") == "firestore", "valid session did not use Firestore")
        _require((login_data.get("session") or {}).get("state") == "ACTIVE", "issued session not ACTIVE")
        proof.valid_session_created = True

        set_cookie = login.headers.get("Set-Cookie", "")
        lower_cookie = set_cookie.lower()
        proof.cookie_httponly = "httponly" in lower_cookie
        proof.cookie_secure = "secure" in lower_cookie
        proof.cookie_samesite_lax = "samesite=lax" in lower_cookie.replace(" ", "")
        _require(proof.cookie_httponly, "session cookie missing HttpOnly")
        _require(proof.cookie_secure, "session cookie missing Secure")
        _require(proof.cookie_samesite_lax, "session cookie missing SameSite=Lax")

        status = browser.get(f"{base}/api/auth/status", timeout=TIMEOUT_S)
        _require(status.status_code == 200, f"authenticated status returned {status.status_code}")
        status_data = _json(status)
        _require(status_data.get("authenticated") is True, "issued cookie is not authenticated")
        _require(status_data.get("mode") == "opaque_server_session", "authenticated mode is not opaque_server_session")
        _require(status_data.get("session_backend") == "firestore", "authenticated status not backed by Firestore")
        _require((status_data.get("session") or {}).get("state") == "ACTIVE", "authenticated session not ACTIVE")
        proof.authenticated_status = True

        replay = requests.Session()
        replay.cookies.update(browser.cookies)

        bad_logout = browser.post(
            f"{base}/api/auth/logout",
            headers={"Origin": "https://invalid.example"},
            timeout=TIMEOUT_S,
        )
        _require(bad_logout.status_code == 403, f"cross-origin logout returned {bad_logout.status_code}, expected 403")
        proof.csrf_logout_rejected = True

        still_auth = browser.get(f"{base}/api/auth/status", timeout=TIMEOUT_S)
        _require(still_auth.status_code == 200 and _json(still_auth).get("authenticated") is True, "CSRF rejection changed session authority")

        logout = browser.post(
            f"{base}/api/auth/logout",
            headers={"Origin": origin},
            timeout=TIMEOUT_S,
        )
        _require(logout.status_code == 200, f"same-origin logout returned {logout.status_code}")
        logout_data = _json(logout)
        _require(logout_data.get("authenticated") is False, "logout response still authenticated")
        _require(logout_data.get("server_revoked") is True, "logout did not revoke server session")
        _require(logout_data.get("session_backend") == "firestore", "logout revocation not backed by Firestore")
        proof.server_revoked = True

        replay_status = replay.get(f"{base}/api/auth/status", timeout=TIMEOUT_S)
        _require(replay_status.status_code == 200, f"replay status returned {replay_status.status_code}")
        replay_data = _json(replay_status)
        _require(replay_data.get("authenticated") is False, "revoked cookie replay was accepted")
        _require(replay_data.get("session") is None, "revoked replay returned an active session record")
        proof.replay_rejected = True

        proof.state = "PASS"
        exit_code = 0
    except Exception as exc:
        error_text = f"{type(exc).__name__}: {str(exc)[:220]}"
        exit_code = 1

    payload = asdict(proof)
    if error_text:
        payload["error"] = error_text
    stream = sys.stdout if exit_code == 0 else sys.stderr
    print("SESSIONTRUTH_RUNTIME_PROOF " + json.dumps(payload, sort_keys=True), file=stream)

    try:
        _publish_status(
            "success" if exit_code == 0 else "failure",
            "Exact Cloud Run SessionTruth lifecycle passed" if exit_code == 0 else "Exact Cloud Run SessionTruth lifecycle failed",
        )
    except Exception as publish_exc:
        print(
            "SESSIONTRUTH_STATUS_PUBLISH_ERROR "
            + json.dumps({"error_type": type(publish_exc).__name__, "error": str(publish_exc)[:180]}),
            file=sys.stderr,
        )
        return 1
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
