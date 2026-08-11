#!/usr/bin/env python3
"""Prove the deployed Cloud Run dashboard SessionTruth lifecycle without leaking secrets.

This script is intended for the guarded Cloud Run deployment workflow. It reads
only the dashboard API key from Secret Manager into process memory, never prints
it, and exercises the real deployed auth endpoints:

anonymous status -> one invalid login -> valid opaque session -> authenticated
status -> CSRF rejection -> server logout/revocation -> replay rejection.

No broker mutation or live-trading route is called.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import dataclass, asdict
from urllib.parse import urlparse

import requests


PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT", "system3-openalgo-safe")
REGION = os.environ.get("GCP_REGION", "asia-south1")
SERVICE = os.environ.get("GCP_CLOUD_RUN_SERVICE", "genesis-system3-web")
API_KEY_SECRET_ID = os.environ.get("API_KEY_SECRET_ID", "system3-dashboard-api-key")
TIMEOUT_S = 30


@dataclass
class Proof:
    state: str = "FAIL"
    service: str = SERVICE
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
        list(args),
        check=True,
        capture_output=True,
        text=True,
    )
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
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.netloc:
        raise RuntimeError("Cloud Run service URL is not a valid HTTPS origin")
    return url


def _dashboard_api_key() -> str:
    value = _run(
        "gcloud",
        "secrets",
        "versions",
        "access",
        "latest",
        f"--secret={API_KEY_SECRET_ID}",
        f"--project={PROJECT}",
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


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> int:
    proof = Proof()
    try:
        base = _service_url()
        origin = base
        api_key = _dashboard_api_key()

        anon = requests.get(f"{base}/api/auth/status", timeout=TIMEOUT_S)
        _require(anon.status_code == 200, f"anonymous auth status returned {anon.status_code}")
        anon_data = _json(anon)
        _require(anon_data.get("required") is True, "dashboard auth is not required")
        _require(anon_data.get("configured") is True, "dashboard API auth is not configured")
        _require(anon_data.get("authenticated") is False, "anonymous request unexpectedly authenticated")
        _require(
            anon_data.get("mode") == "session_cookie_or_header",
            f"unexpected anonymous auth mode {anon_data.get('mode')!r}",
        )
        _require(
            anon_data.get("session_backend") == "firestore",
            f"Cloud Run SessionTruth backend is {anon_data.get('session_backend')!r}, expected 'firestore'",
        )
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
        # Drop the secret reference immediately after the one-time exchange.
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

        # Preserve the pre-logout cookie for a true replay attempt after revocation.
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
        _require(
            still_auth.status_code == 200 and _json(still_auth).get("authenticated") is True,
            "CSRF rejection changed session authority",
        )

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
        print("SESSIONTRUTH_RUNTIME_PROOF " + json.dumps(asdict(proof), sort_keys=True))
        return 0
    except Exception as exc:
        # Never include response bodies, cookie values, API keys or secret payloads.
        print(
            "SESSIONTRUTH_RUNTIME_PROOF "
            + json.dumps({**asdict(proof), "error_type": type(exc).__name__, "error": str(exc)[:240]}, sort_keys=True),
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
