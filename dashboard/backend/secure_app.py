"""Security boundary wrapper for the System3 FastAPI application.

This module keeps the legacy monolithic application intact while replacing only
its dashboard authentication authority with SessionTruth.  Cloud Run launches
this module, so browser cookies are opaque, server-issued, expiring and
revocable.  Header X-API-Key remains a compatibility path for trusted CI/API
clients; the browser no longer stores or replays it.

Analyzer/paper safety is unchanged.  This module contains no broker order code.
"""
from __future__ import annotations

from collections import defaultdict, deque
import hmac
import threading
import time
from typing import Deque, Dict

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

from dashboard.backend import app as legacy
from dashboard.backend.session_truth import get_session_truth_store


app = legacy.app
_SESSION_TRUTH = get_session_truth_store()
_AUTH_ATTEMPTS: Dict[str, Deque[float]] = defaultdict(deque)
_AUTH_ATTEMPTS_LOCK = threading.Lock()
_AUTH_WINDOW_S = 300.0
_AUTH_MAX_FAILURES = 10
_AUTH_PATHS = {
    "/api/auth/session",
    "/api/auth/status",
    "/api/auth/logout",
}


def _client_key(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
    if forwarded:
        return forwarded
    return request.client.host if request.client else "unknown"


def _record_or_reject_login_attempt(request: Request) -> None:
    """Fail closed after repeated failed login attempts from one client."""
    now = time.monotonic()
    key = _client_key(request)
    with _AUTH_ATTEMPTS_LOCK:
        bucket = _AUTH_ATTEMPTS[key]
        while bucket and now - bucket[0] > _AUTH_WINDOW_S:
            bucket.popleft()
        if len(bucket) >= _AUTH_MAX_FAILURES:
            raise HTTPException(
                status_code=429,
                detail="Too many failed dashboard login attempts; retry later",
            )
        bucket.append(now)


def _clear_login_failures(request: Request) -> None:
    key = _client_key(request)
    with _AUTH_ATTEMPTS_LOCK:
        _AUTH_ATTEMPTS.pop(key, None)


def _forwarded_scheme(request: Request) -> str:
    return request.headers.get(
        "X-Forwarded-Proto", request.url.scheme
    ).split(",")[0].strip().lower()


def _same_origin(request: Request) -> str:
    host = request.headers.get("Host", "")
    return f"{_forwarded_scheme(request)}://{host}" if host else ""


def _origin_allowed(request: Request) -> bool:
    origin = request.headers.get("Origin", "")
    if not origin:
        return False
    return origin == _same_origin(request) or origin in set(legacy._allowed_origins)


def _session_record(request: Request):
    token = request.cookies.get(legacy._DASHBOARD_SESSION_COOKIE, "")
    return _SESSION_TRUTH.validate(token)


def _has_dashboard_api_access(request: Request) -> bool:
    """Authoritative access check used by legacy auth middleware at request time."""
    if not legacy._REQUIRE_API_KEY or not legacy._API_KEY:
        return False
    header_key = request.headers.get("X-API-Key", "")
    if header_key and hmac.compare_digest(header_key, legacy._API_KEY):
        return True
    return _session_record(request) is not None


# Existing middleware resolves this global function at request time, so swapping
# the function changes the auth authority without duplicating the middleware.
legacy._has_dashboard_api_access = _has_dashboard_api_access

# Remove the three legacy deterministic-cookie route objects before registering
# the authoritative versions below.  All other app routes/startup hooks remain.
app.router.routes = [
    route for route in app.router.routes
    if getattr(route, "path", None) not in _AUTH_PATHS
]


@app.post("/api/auth/session")
async def create_dashboard_session(payload: legacy.DashboardAuthRequest, request: Request):
    if not legacy._REQUIRE_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="Dashboard authentication is disabled; sessions cannot be created",
        )
    if not legacy._API_KEY:
        raise HTTPException(
            status_code=503,
            detail="Dashboard API auth is required but API_KEY is not configured",
        )
    supplied = (payload.api_key or "").strip()
    if not hmac.compare_digest(supplied, legacy._API_KEY):
        _record_or_reject_login_attempt(request)
        raise HTTPException(status_code=401, detail="Invalid dashboard API key")

    _clear_login_failures(request)
    token, session = _SESSION_TRUTH.issue(
        max_age_seconds=legacy._DASHBOARD_SESSION_MAX_AGE,
        principal="dashboard",
    )
    response = JSONResponse(
        {
            "ok": True,
            "authenticated": True,
            "mode": "opaque_server_session",
            "session": session.public_dict(),
        }
    )
    response.set_cookie(
        legacy._DASHBOARD_SESSION_COOKIE,
        token,
        max_age=legacy._DASHBOARD_SESSION_MAX_AGE,
        httponly=True,
        secure=_forwarded_scheme(request) == "https",
        samesite="lax",
        path="/",
    )
    return response


@app.get("/api/auth/status")
async def dashboard_auth_status(request: Request):
    session = _session_record(request)
    header_key = request.headers.get("X-API-Key", "")
    header_ok = bool(
        legacy._REQUIRE_API_KEY
        and legacy._API_KEY
        and header_key
        and hmac.compare_digest(header_key, legacy._API_KEY)
    )
    return {
        "required": legacy._REQUIRE_API_KEY,
        "configured": bool(legacy._API_KEY),
        "authenticated": bool(session or header_ok),
        "mode": (
            "opaque_server_session"
            if session
            else "api_key_header"
            if header_ok
            else "auth_required"
            if legacy._REQUIRE_API_KEY
            else "auth_disabled"
        ),
        "session": session.public_dict() if session else None,
    }


@app.post("/api/auth/logout")
async def dashboard_auth_logout(request: Request):
    # Logout is a cookie-authenticated mutation; validate browser origin even
    # though the route itself remains publicly callable for expired sessions.
    if request.cookies.get(legacy._DASHBOARD_SESSION_COOKIE) and not _origin_allowed(request):
        raise HTTPException(status_code=403, detail="Origin validation failed")
    token = request.cookies.get(legacy._DASHBOARD_SESSION_COOKIE, "")
    revoked = _SESSION_TRUTH.revoke(token) if token else False
    response = JSONResponse(
        {"ok": True, "authenticated": False, "server_revoked": revoked}
    )
    response.delete_cookie(
        legacy._DASHBOARD_SESSION_COOKIE,
        path="/",
        samesite="lax",
        secure=_forwarded_scheme(request) == "https",
        httponly=True,
    )
    return response
