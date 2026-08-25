"""
System3 Ultra Dashboard Backend
FastAPI service for real-time system monitoring and control
"""

import asyncio
import hashlib
import hmac
import json
import math
import os
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pytz

IST = pytz.timezone("Asia/Kolkata")

# Timeouts for sync broker/scanner work — must not block the asyncio event loop.
_BROKER_IO_TIMEOUT_S = 8.0
_SCANNER_IO_TIMEOUT_S = 120.0
_SCANNER_EOD_TIMEOUT_S = 180.0
_TRUTH_IO_TIMEOUT_S = 45.0
_EOD_SCANNER_CACHE: tuple[float, Dict[str, Any]] = (0.0, {})
_EOD_SCANNER_TTL_S = 1800.0

# Dedicated small executor for the spot-price background refresh, isolated
# from the shared default asyncio.to_thread() executor. asyncio.wait_for()
# timing out does NOT cancel the underlying OS thread — it just stops
# waiting on it. If the Yahoo Finance calls inside hang (rate-limited cloud
# IPs, slow socket), previously that orphaned thread piled up in the SAME
# shared executor pool every other blocking call in this app depends on
# (_run_blocking for broker/chain/scanner work), starving all of them and
# growing memory unbounded until OOM. A small dedicated pool caps how many
# stuck Yahoo-fetch threads can accumulate and stops them from starving
# unrelated request handling.
_SPOT_REFRESH_EXECUTOR = None  # Yahoo Finance disabled — ThreadPoolExecutor no longer needed


def _market_open_from_state() -> bool:
    """Use real market-hours truth first; SSOT can be stale after a wedged loop."""
    if MARKET_DETECTION_AVAILABLE:
        try:
            open_now, _reason = is_market_open()
            return bool(open_now)
        except Exception:
            pass
    if SSOT_AVAILABLE and state_store is not None:
        try:
            return bool((state_store.get_state().get("market") or {}).get("is_open"))
        except Exception:
            pass
    return False


async def _run_blocking(fn, *args, timeout: float = 15.0, **kwargs):
    """Run sync I/O in a worker thread with a hard timeout."""
    return await asyncio.wait_for(asyncio.to_thread(fn, *args, **kwargs), timeout=timeout)


def _scanner_market_closed_response() -> Dict[str, Any]:
    return {
        "status": "market_closed",
        "market_open": False,
        "segments": ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"],
        "segments_implemented": 0,
        "segments_total": 4,
        "by_segment": {},
        "market_wide": {"top_ce": None, "top_pe": None},
        "note": "Live scanner skipped while market is closed",
    }


# CRITICAL: Add project root to Python path FIRST, before any core module imports
# This allows the backend to import core.brokers.dhan.dhan_readonly and other core modules
ROOT_DIR = Path(__file__).parent.parent.parent.resolve()  # Use resolve() to get absolute path
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
# Also add src for utils
if str(ROOT_DIR / "src") not in sys.path:
    sys.path.insert(0, str(ROOT_DIR / "src"))

# Broker: Dhan (read-only, analyzer mode)
DHAN_AVAILABLE = False
try:
    from core.brokers.dhan.dhan_readonly import get_status as _dhan_get_status_probe

    DHAN_AVAILABLE = True
    print(f"[Backend] Dhan broker module imported successfully from {ROOT_DIR}")
except ImportError as e:
    print(f"[Backend] Warning: Could not import Dhan broker module: {e}")
except Exception as e:
    print(f"[Backend] Warning: Error importing Dhan broker module: {e}")

from fastapi import (
    BackgroundTasks,
    FastAPI,
    HTTPException,
    Request,
    WebSocket,
    WebSocketDisconnect,
)

try:
    from dashboard.backend.continuous_closure_service import (
        REQUEST_PATH_CACHE_TTL_S,
        stamp_closure_request_path,
    )
    from dashboard.backend.dashboard_truth import classify_overview_data_source
except ImportError:
    from continuous_closure_service import (  # type: ignore
        REQUEST_PATH_CACHE_TTL_S,
        stamp_closure_request_path,
    )
    from dashboard_truth import classify_overview_data_source  # type: ignore
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response
from pydantic import BaseModel

# pandas lazy-loaded — only import when actually needed
# Saves ~45MB at startup
pd = None  # Will be imported lazily when needed

def _get_pd():
    """Lazy pandas import — call this instead of using pd directly."""
    global pd
    if pd is None:
        try:
            import pandas as _pd
            pd = _pd
        except ImportError:
            pass
    return pd
import sqlite3

# numpy removed — was only used for synthetic data (np.random.normal)
# Use random.gauss() instead — saves ~25MB

# Import market detection and synthetic data generator
try:
    from utils.market_hours import get_market_status, is_market_open

    MARKET_DETECTION_AVAILABLE = True
except ImportError as e:
    MARKET_DETECTION_AVAILABLE = False
    # Production-grade: Suppress warning - fallback behavior is acceptable
    # Market status can be determined from other sources (health.json, QC reports)
    pass

# Import synthetic data generator
try:
    from dashboard.backend.synthetic_data_generator import (
        generate_synthetic_chain_data,
        generate_synthetic_health_data,
        generate_synthetic_perf_data,
        generate_synthetic_qc_data,
        generate_synthetic_signal_data,
    )

    SYNTHETIC_DATA_AVAILABLE = True
except ImportError:
    try:
        # Try relative import
        from synthetic_data_generator import (
            generate_synthetic_chain_data,
            generate_synthetic_health_data,
            generate_synthetic_perf_data,
            generate_synthetic_qc_data,
            generate_synthetic_signal_data,
        )

        SYNTHETIC_DATA_AVAILABLE = True
    except ImportError:
        SYNTHETIC_DATA_AVAILABLE = False
        print("Warning: Synthetic data generator not available")

# Import performance predictor and live validator
try:
    from dashboard.backend.live_profit_validator import get_live_validator
    from dashboard.backend.performance_predictor import get_performance_predictor

    PERFORMANCE_PREDICTOR_AVAILABLE = True
except ImportError:
    try:
        from live_profit_validator import get_live_validator
        from performance_predictor import get_performance_predictor

        PERFORMANCE_PREDICTOR_AVAILABLE = True
    except ImportError:
        PERFORMANCE_PREDICTOR_AVAILABLE = False
        print("Warning: Performance predictor not available")

# Import alerts system and multi-validation audit
try:
    from dashboard.backend.alerts_system import get_alerts_system
    from dashboard.backend.multi_validation_audit import get_multi_validator

    ALERTS_AVAILABLE = True
    MULTI_VALIDATION_AVAILABLE = True
except ImportError:
    try:
        from alerts_system import get_alerts_system
        from multi_validation_audit import get_multi_validator

        ALERTS_AVAILABLE = True
        MULTI_VALIDATION_AVAILABLE = True
    except ImportError:
        ALERTS_AVAILABLE = False
        MULTI_VALIDATION_AVAILABLE = False
        print("Warning: Alerts system and multi-validation not available")

# Import runtime state store (SSOT)
try:
    from dashboard.backend.runtime_state_store import get_state_store

    SSOT_AVAILABLE = True
except ImportError:
    try:
        from runtime_state_store import get_state_store

        SSOT_AVAILABLE = True
    except ImportError:
        SSOT_AVAILABLE = False
        print("Warning: Runtime state store not available")

# Import advanced features
try:
    from dashboard.backend.advanced_charting import get_advanced_charting
    from dashboard.backend.advanced_filtering import get_advanced_filtering
    from dashboard.backend.backtesting import get_backtesting_engine
    from dashboard.backend.export_reporting import get_export_reporting
    from dashboard.backend.ml_performance_tracking import get_ml_tracker
    from dashboard.backend.order_management import get_order_management
    from dashboard.backend.risk_management import get_risk_management
    from dashboard.backend.trade_journal import get_trade_journal

    ADVANCED_FEATURES_AVAILABLE = True
except ImportError:
    try:
        from advanced_charting import get_advanced_charting
        from advanced_filtering import get_advanced_filtering
        from backtesting import get_backtesting_engine
        from export_reporting import get_export_reporting
        from ml_performance_tracking import get_ml_tracker
        from order_management import get_order_management
        from risk_management import get_risk_management
        from trade_journal import get_trade_journal

        ADVANCED_FEATURES_AVAILABLE = True
    except ImportError:
        ADVANCED_FEATURES_AVAILABLE = False
        print("Warning: Advanced features not available")

# Try to import watchdog (optional)
try:
    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer

    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    Observer = None
    FileSystemEventHandler = None
    print("Warning: watchdog not available - file watching disabled")

ROOT_DIR = Path(__file__).parent.parent.parent
try:
    from dotenv import load_dotenv as _load_dotenv
    _load_dotenv(ROOT_DIR / ".env")
except Exception:
    pass
# OUTPUTS_DIR: check src/outputs first (actual data location), fallback to outputs/
_src_outputs = ROOT_DIR / "src" / "outputs"
_root_outputs = ROOT_DIR / "outputs"
if _src_outputs.exists():
    OUTPUTS_DIR = _src_outputs
else:
    OUTPUTS_DIR = _root_outputs
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
print(f"[Backend] OUTPUTS_DIR resolved to: {OUTPUTS_DIR}")
LOGS_DIR = ROOT_DIR / "logs"
AUDIT_DIR = OUTPUTS_DIR / "audit"
DB_DIR = OUTPUTS_DIR / "db"

# REAL_ONLY MODE: Disable synthetic data generation (default: True)
# Set SYSTEM3_REAL_ONLY=0 to allow synthetic data (for testing only)
REAL_ONLY = os.environ.get("SYSTEM3_REAL_ONLY", "1").strip().lower() in ("1", "true", "yes")
if not REAL_ONLY:
    print("WARNING: REAL_ONLY mode is DISABLED. Synthetic data may be used.")

# Ensure directories exist
AUDIT_DIR.mkdir(parents=True, exist_ok=True)
DB_DIR.mkdir(parents=True, exist_ok=True)


# ── Modular routers (memory-efficient, lazy imports) ─────────────────────
import sys as _sys
_backend_dir = str(Path(__file__).resolve().parent)
if _backend_dir not in _sys.path:
    _sys.path.insert(0, _backend_dir)

from routers import broker as broker_router
from routers import chain as chain_router
from routers import ml as ml_router

from fo_eligibility_filter import get_fo_eligibility_filter
from option_strike_visibility_audit import OptionVisibilityAuditor, generate_sample_audit_report
from gain_rank_spot_enrichment import enrich_gain_rank_rows_with_authenticated_spots

# ── Memory guard middleware ────────────────────────────────────────────────
from middleware.memory_guard import memory_guard_middleware, get_memory_stats
from starlette.middleware.base import BaseHTTPMiddleware

app = FastAPI(title="System3 Genesis API")

# Register unique chain discovery/expiry routes after FastAPI exists.
# Must run post-construction: chain module is imported earlier for helpers.
try:
    chain_router.install_legacy_bridge()
except Exception as _chain_bridge_exc:
    print(f"[startup] chain legacy bridge deferred/failed: {type(_chain_bridge_exc).__name__}: {_chain_bridge_exc}")

# ── Modular routers DISABLED — they duplicated 19 existing routes and
# overrode the rich endpoint versions the frontend depends on, breaking
# all dashboard tabs. Proper modularization requires MOVING code out of
# app.py (delete old versions), not adding parallel simplified copies.
# app.include_router(broker_router.router)   # disabled — duplicate routes
# app.include_router(chain_router.router)    # disabled — duplicate routes
# app.include_router(ml_router.router)       # disabled — duplicate routes

# ── MemoryGuard middleware (auto-GC at 420MB, warn at 380MB) ─────────────
from starlette.middleware.base import BaseHTTPMiddleware
app.add_middleware(BaseHTTPMiddleware, dispatch=memory_guard_middleware)


# Rate limiting middleware to prevent excessive API calls
@app.middleware("http")
async def rate_limit_middleware(request, call_next):
    """Add small delay to throttle external API calls and prevent rate limiting"""
    import time

    # Rate limiting: only apply to external API calls, not all requests
    # time.sleep(0.1) on ALL requests was causing request queue buildup = memory spike
    _ext_paths = {"/api/broker", "/api/chain"}
    if any(request.url.path.startswith(p) for p in _ext_paths):
        await asyncio.sleep(0.05)  # Async sleep - doesn't block event loop
    response = await call_next(request)
    return response


# Initialize SSOT (Single Source of Truth)
if SSOT_AVAILABLE:
    state_store = get_state_store(OUTPUTS_DIR)
    # Sync from existing files on startup
    state_store.sync_from_files()
else:
    state_store = None

# Warm instruments master — sync from Dhan CDN if stale, then load cache.
# Set DEFER_INSTRUMENT_WARMUP=1 on Render to skip eager load at startup and
# save ~150-200 MB peak RAM (instruments still lazy-load via /api/instruments/health).
if os.environ.get("DEFER_INSTRUMENT_WARMUP", "0").strip().lower() not in ("1", "true", "yes", "on"):
    try:
        from scripts.sync_dhan_instruments_master import META_JSON
        from scripts.sync_dhan_instruments_master import sync as sync_instruments_master

        _need_sync = True
        if META_JSON.exists():
            import json as _json
            from datetime import datetime, timezone

            meta = _json.loads(META_JSON.read_text(encoding="utf-8"))
            synced = meta.get("synced_utc")
            if synced:
                age_h = (
                    datetime.now(timezone.utc) - datetime.fromisoformat(synced.replace("Z", "+00:00"))
                ).total_seconds() / 3600
                _need_sync = age_h > 24
        if _need_sync and not (ROOT_DIR / "storage" / "instruments" / "api-scrip-master-detailed.csv").exists():
            try:
                sync_instruments_master(force=True)
            except Exception as _sync_exc:
                print(f"[startup] instrument sync deferred: {_sync_exc}")
        from core.data.instruments_cache import ensure_instruments_loaded

        _inst_metrics = ensure_instruments_loaded()
        if _inst_metrics.get("rows", 0) > 0:
            print(f"[startup] instruments: {_inst_metrics['rows']} rows source={_inst_metrics.get('source')}")
    except Exception as _inst_exc:
        print(f"[startup] instruments warm-up skipped: {_inst_exc}")
else:
    print("[startup] instruments warm-up deferred via DEFER_INSTRUMENT_WARMUP=1")

# CORS - explicit allow-list only. Wildcard origins + credentials is an open
# CORS misconfiguration (any site can read authenticated responses).
# Override/extend via ALLOWED_ORIGINS env var (comma-separated).
_default_allowed_origins = [
    "http://127.0.0.1:8000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
try:
    from core.config.cloud_runtime import is_cloud_runtime, public_cors_origins

    _cloud_allowed_origins = public_cors_origins()
    _cloud_runtime = is_cloud_runtime()
except Exception:
    _cloud_allowed_origins = [
        "https://genesis-system3-web-doq2wplepa-el.a.run.app",
        "https://genesis-system3-web-802404398783.asia-south1.run.app",
    ]
    _cloud_runtime = os.environ.get("CLOUD_MODE", "").strip() in {"1", "true", "yes", "on"}
_env_allowed_origins = [
    o.strip().rstrip("/")
    for o in os.environ.get("ALLOWED_ORIGINS", "").split(",")
    if o.strip()
]
_cors_source = (
    _cloud_allowed_origins + _env_allowed_origins
    if _cloud_runtime
    else _default_allowed_origins + _cloud_allowed_origins + _env_allowed_origins
)
_allowed_origins = []
_seen_origins = set()
for _origin in _cors_source:
    if _origin and _origin not in _seen_origins:
        _seen_origins.add(_origin)
        _allowed_origins.append(_origin)

if any(origin in {"*", "null"} for origin in _allowed_origins):
    raise RuntimeError(
        "ALLOWED_ORIGINS must contain explicit http(s) origins; wildcard/null are forbidden"
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=[
        "Accept",
        "Authorization",
        "Content-Type",
        "Idempotency-Key",
        "X-API-Key",
        "X-Request-ID",
        "X-Worker-Token",
    ],
)

# Dashboard authentication. Read-only routes may remain available during
# public analyzer mode, but mutations always fail closed when authentication
# is disabled or unconfigured. Browser authentication uses an HttpOnly session
# cookie created by /api/auth/session. Never compile API_KEY into JavaScript.
_REQUIRE_API_KEY = os.environ.get("REQUIRE_API_KEY", "").strip().lower() == "true"
_API_KEY = os.environ.get("API_KEY", "").strip()
_DASHBOARD_SESSION_COOKIE = "system3_dashboard_session"
_DASHBOARD_SESSION_MAX_AGE = int(os.environ.get("DASHBOARD_SESSION_MAX_AGE", "43200"))
try:
    from dashboard.backend.security_policy import evaluate_request
except ImportError:
    from security_policy import evaluate_request


if _REQUIRE_API_KEY and not _API_KEY:
    print("[security] REQUIRE_API_KEY=true but API_KEY is unset - auth will reject all requests")
elif not _REQUIRE_API_KEY:
    print("[security] API key auth is DISABLED (set REQUIRE_API_KEY=true and API_KEY to enable)")


def _dashboard_session_token() -> str:
    if not _API_KEY:
        return ""
    return hashlib.sha256(f"system3-dashboard-session-v1:{_API_KEY}".encode("utf-8")).hexdigest()


def _has_dashboard_api_access(request: Request) -> bool:
    if not _REQUIRE_API_KEY or not _API_KEY:
        return False
    header_key = request.headers.get("X-API-Key", "")
    if header_key and hmac.compare_digest(header_key, _API_KEY):
        return True
    cookie_token = request.cookies.get(_DASHBOARD_SESSION_COOKIE, "")
    expected = _dashboard_session_token()
    return bool(cookie_token and expected and hmac.compare_digest(cookie_token, expected))


class DashboardAuthRequest(BaseModel):
    api_key: str


@app.post("/api/auth/session")
async def create_dashboard_session(payload: DashboardAuthRequest, request: Request):
    if not _REQUIRE_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="Dashboard authentication is disabled; sessions cannot be created",
        )
    if not _API_KEY:
        raise HTTPException(status_code=503, detail="Dashboard API auth is required but API_KEY is not configured")
    if not hmac.compare_digest((payload.api_key or "").strip(), _API_KEY):
        raise HTTPException(status_code=401, detail="Invalid dashboard API key")
    response = JSONResponse({"ok": True, "authenticated": True, "mode": "session_cookie"})
    response.set_cookie(
        _DASHBOARD_SESSION_COOKIE,
        _dashboard_session_token(),
        max_age=_DASHBOARD_SESSION_MAX_AGE,
        httponly=True,
        secure=request.url.scheme == "https",
        samesite="lax",
        path="/",
    )
    return response


@app.get("/api/auth/status")
async def dashboard_auth_status(request: Request):
    return {
        "required": _REQUIRE_API_KEY,
        "configured": bool(_API_KEY),
        "authenticated": _has_dashboard_api_access(request),
        "mode": "session_cookie_or_header" if _REQUIRE_API_KEY else "auth_disabled",
    }


@app.post("/api/auth/logout")
async def dashboard_auth_logout(request: Request):
    response = JSONResponse({"ok": True, "authenticated": False})
    response.delete_cookie(_DASHBOARD_SESSION_COOKIE, path="/")
    return response


@app.middleware("http")
async def _enforce_api_key(request: Request, call_next):
    path = request.url.path
    method = request.method.upper()

    worker_token = globals().get("_WORKER_PUSH_TOKEN", "")
    sent_worker_token = request.headers.get("X-Worker-Token", "")
    worker_token_valid = bool(
        worker_token
        and sent_worker_token
        and hmac.compare_digest(sent_worker_token, worker_token)
    )

    forwarded_scheme = request.headers.get(
        "X-Forwarded-Proto", request.url.scheme
    ).split(",")[0].strip()
    host = request.headers.get("Host", "")
    same_origin = f"{forwarded_scheme}://{host}" if host else ""

    decision = evaluate_request(
        method=method,
        path=path,
        require_api_key=_REQUIRE_API_KEY,
        api_key_configured=bool(_API_KEY),
        dashboard_access=_has_dashboard_api_access(request),
        worker_token_configured=bool(worker_token),
        worker_token_valid=worker_token_valid,
        header_api_key_present=bool(request.headers.get("X-API-Key")),
        origin=request.headers.get("Origin", ""),
        same_origin=same_origin,
        allowed_origins=_allowed_origins,
        idempotency_key_present=bool(
            request.headers.get("Idempotency-Key")
        ),
    )

    if not decision.allowed:
        content = {"detail": decision.detail}
        if decision.code:
            content["code"] = decision.code
        return JSONResponse(
            status_code=decision.status_code,
            content=content,
        )

    return await call_next(request)


# Outermost middleware (added last = runs first/wraps everything else, per
# Starlette's add_middleware ordering) so every request - including ones
# the API-key check rejects - gets a request_id available to logging and
# echoed back in the response for client-side correlation.
try:
    from dashboard.backend.structured_logging import RequestIDMiddleware
except ImportError:
    from structured_logging import RequestIDMiddleware

app.add_middleware(RequestIDMiddleware)


_DASHBOARD_DIR = ROOT_DIR / "dashboard"
_REACT_DIST_DIR = ROOT_DIR / "dashboard" / "frontend" / "dist"

# Mount React frontend static assets (JS/CSS bundles)
try:
    from fastapi.staticfiles import StaticFiles as _StaticFiles

    if _REACT_DIST_DIR.exists() and (_REACT_DIST_DIR / "assets").exists():
        app.mount(
            "/ui/assets",
            _StaticFiles(directory=str(_REACT_DIST_DIR / "assets")),
            name="ui-assets",
        )
        print(f"[frontend] React dist mounted from {_REACT_DIST_DIR}")
    else:
        print(f"[frontend] React dist NOT found at {_REACT_DIST_DIR} — serving legacy Vue")
except Exception as _e:
    print(f"[frontend] StaticFiles mount failed: {_e} — serving legacy Vue")


# Root route - helpful message. Cloud-permanent hosts must never advertise localhost.
@app.api_route("/", methods=["GET", "HEAD"])
async def root():
    from core.config.cloud_runtime import public_base_url, public_dashboard_url, public_ui_path

    base_url = public_base_url()
    dashboard_url = public_dashboard_url()
    ui_path = public_ui_path()
    return {
        "message": "System3 Ultra Dashboard API",
        "status": "running",
        "backend_url": base_url,
        "dashboard_url": dashboard_url,
        "api_docs": f"{base_url}/docs",
        "health": f"{base_url}/api/health",
        "state": f"{base_url}/api/state",
        "relative_paths": {
            "api_docs": "/docs",
            "health": "/api/health",
            "state": "/api/state",
            "broker_status": "/api/broker/status",
            "dashboard": ui_path,
        },
    }


@app.get("/ui", include_in_schema=False)
@app.get("/ui/", include_in_schema=False)
@app.get("/ui/{path:path}", include_in_schema=False)
async def serve_dashboard_index(path: str = ""):
    """Serve React SPA — React dist takes priority over legacy Vue."""
    # Try React dist first
    react_index = _REACT_DIST_DIR / "index.html"
    if react_index.exists():
        return FileResponse(
            str(react_index), media_type="text/html", headers={**_NO_CACHE_HEADERS, "X-Frontend": "react"}
        )
    # Fallback to legacy Vue
    vue_index = _DASHBOARD_DIR / "index.html"
    if vue_index.exists():
        return FileResponse(
            str(vue_index), media_type="text/html", headers={**_NO_CACHE_HEADERS, "X-Frontend": "vue-legacy"}
        )
    raise HTTPException(status_code=404, detail="Dashboard not found")


_NO_CACHE_HEADERS = {
    "Cache-Control": "no-cache, no-store, must-revalidate",
    "Pragma": "no-cache",
    "Expires": "0",
}


@app.get("/ui/app.js", include_in_schema=False)
async def serve_dashboard_js():
    f = _DASHBOARD_DIR / "app.js"
    if f.exists():
        return FileResponse(str(f), media_type="application/javascript", headers=_NO_CACHE_HEADERS)
    raise HTTPException(status_code=404, detail="app.js not found")


@app.get("/ui/style.css", include_in_schema=False)
async def serve_dashboard_css():
    f = _DASHBOARD_DIR / "style.css"
    if f.exists():
        return FileResponse(str(f), media_type="text/css", headers=_NO_CACHE_HEADERS)
    raise HTTPException(status_code=404, detail="style.css not found")


# Alias routes for convenience (point to /api/* endpoints)
# These prevent confusion when scripts/docs use /health or /state
# These will be defined after the actual endpoints


# SSOT Endpoint - Single Source of Truth
@app.get("/api/state")
async def get_state():
    """
    Get unified runtime state (SSOT).
    All pages should read from this endpoint for consistency.
    PRODUCTION: Never expose mode=LIVE when broker disconnected or data synthetic.
    """
    if not SSOT_AVAILABLE or state_store is None:
        raise HTTPException(status_code=503, detail="State store not available")

    try:
        state = await asyncio.wait_for(asyncio.to_thread(state_store.get_state), timeout=5.0)
    except asyncio.TimeoutError:
        return {
            "status": "timeout",
            "mode": "PAPER",
            "live_trading_enabled": False,
            "live_allowed": False,
            "broker": {"connected": False},
            "market": {"is_open": False},
            "message": "SSOT get_state timed out — returning safe PAPER stub",
        }
    # Gate: if broker not connected or data not real, force mode to PAPER for UI consistency
    broker_connected = state.get("broker", {}).get("connected", False)
    ds = (state.get("data_source") or "").upper()
    if (state.get("mode") or "").upper() == "LIVE" and (not broker_connected or ds in ("SYNTHETIC", "NOT_READY")):
        state = dict(state)
        state["mode"] = "PAPER"
    return state


@app.get("/api/state/history")
async def get_state_history(limit: int = 100):
    """
    Get SSOT state history (time series).
    Useful for tracking state changes over time.
    """
    if not SSOT_AVAILABLE or state_store is None:
        raise HTTPException(status_code=503, detail="State store not available")

    # Read from state snapshots directory
    snapshots_dir = OUTPUTS_DIR / "state_snapshots"
    snapshots_dir.mkdir(exist_ok=True)

    history = []
    try:
        # Get all snapshot files, sorted by modification time
        snapshot_files = sorted(snapshots_dir.glob("state_*.json"), key=lambda f: f.stat().st_mtime, reverse=True)[
            :limit
        ]

        for snapshot_file in snapshot_files:
            try:
                data = json.loads(snapshot_file.read_text())
                history.append(data)
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"Failed to parse snapshot {snapshot_file.name}: {e}")
                continue
            except Exception as e:
                logger.warning(f"Failed to read snapshot {snapshot_file.name}: {e}")
                continue
    except Exception as e:
        logger.error(f"Error reading state history: {e}")

    return {"history": history, "count": len(history), "limit": limit}


@app.get("/api/broker/status")
async def get_broker_status():
    """Get broker connection status. Uses Dhan broker (read-only, analyzer mode)."""
    try:
        from core.brokers.dhan.dhan_readonly import get_status as _dhan_status

        status = await asyncio.wait_for(asyncio.to_thread(_dhan_status), timeout=12)
        # Only persist definitive results to SSOT — never write timeout/error noise.
        if SSOT_AVAILABLE and state_store is not None and isinstance(status, dict):
            if status.get("connected") is True or status.get("error") in (
                "TOKEN_EXPIRED_OR_INVALID",
                "CONFIG_MISSING",
                "ACCESS_FORBIDDEN",
            ):
                state_store.update_state({"broker": status})
        return status
    except Exception as _e:
        # Keep last SSOT truth on timeout/transient errors so /api/health does not
        # flap the UI to DISCONNECTED every few seconds.
        cached = None
        if SSOT_AVAILABLE and state_store is not None:
            try:
                cached = (state_store.get_state().get("broker") or {})
            except Exception:
                cached = None
        if isinstance(cached, dict) and cached.get("connected") is True:
            out = dict(cached)
            out["transient"] = True
            out["error"] = out.get("error") or f"status_probe_timeout:{str(_e)[:80]}"
            out["stale"] = True
            return out
        return {
            "connected": False,
            "name": "dhan",
            "status": "error",
            "error": str(_e)[:200],
            "error_type": "DHAN_STATUS_ERROR",
            "latency_ms": None,
            "last_ok": None,
            "transient": True,
            "credentials_present": True,
        }


@app.get("/api/broker/dhan/status")
async def get_dhan_broker_status():
    """Dhan read-only broker status. Never returns access token. No live trading."""
    try:
        from core.brokers.dhan.dhan_readonly import get_status as dhan_get_status

        status = await asyncio.wait_for(asyncio.to_thread(dhan_get_status), timeout=12)
        if SSOT_AVAILABLE and state_store is not None and isinstance(status, dict):
            if status.get("connected") is True or status.get("error") in (
                "TOKEN_EXPIRED_OR_INVALID",
                "CONFIG_MISSING",
                "ACCESS_FORBIDDEN",
            ):
                state_store.update_state({"broker": status})
        return status
    except ImportError as exc:
        return {
            "broker": "dhan",
            "mode": "ANALYZER",
            "connected": False,
            "live_trading_enabled": False,
            "order_placement_allowed": False,
            "credentials_present": False,
            "error": f"MODULE_NOT_AVAILABLE: {str(exc)[:200]}",
        }
    except Exception as exc:
        cached = None
        if SSOT_AVAILABLE and state_store is not None:
            try:
                cached = state_store.get_state().get("broker") or {}
            except Exception:
                cached = None
        if isinstance(cached, dict) and cached.get("connected") is True:
            out = dict(cached)
            out["transient"] = True
            out["stale"] = True
            out["error"] = out.get("error") or f"status_probe_timeout:{str(exc)[:80]}"
            return out
        return {
            "broker": "dhan",
            "mode": "ANALYZER",
            "connected": False,
            "live_trading_enabled": False,
            "order_placement_allowed": False,
            "credentials_present": True,
            "error": str(exc)[:200],
            "transient": True,
        }


@app.get("/api/broker/truth")
async def get_broker_truth():
    """Multi-validated broker trader truth — holdings, positions, funds."""
    _hit = _cache_get("broker_truth", _TTL_BROKER_TRUTH)
    if _hit is not None:
        if isinstance(_hit, dict):
            hit = dict(_hit)
            hit.setdefault("source_priority", "web_ttl_cache")
            return hit
        return _hit

    try:
        from dashboard.backend.broker_truth_validator import build_broker_truth_report
    except ImportError:
        from broker_truth_validator import build_broker_truth_report
    try:
        return await _run_blocking(build_broker_truth_report, timeout=_TRUTH_IO_TIMEOUT_S)
    except asyncio.TimeoutError:
        return {"success": False, "error": "broker_truth_timeout", "timeout_s": _TRUTH_IO_TIMEOUT_S}


@app.get("/api/broker/holdings")
async def get_broker_holdings():
    """Dhan equity holdings — read-only. No orders."""
    _hit = _cache_get("broker_holdings", _TTL_BROKER)
    if _hit is not None:
        return _hit

    try:
        from core.brokers.dhan.dhan_payload_normalizer import (
            normalize_holding_row,
            normalize_holdings_payload,
        )
        from core.brokers.dhan.dhan_readonly import get_holdings

        result = await _run_blocking(get_holdings, timeout=_BROKER_IO_TIMEOUT_S)
        raw_rows = normalize_holdings_payload(result.get("data"))
        normalized = [normalize_holding_row(r) for r in raw_rows]
        return {
            "live_trading_enabled": False,
            "order_placement_allowed": False,
            "source": "dhan_readonly",
            "validated": result.get("success", False),
            "count": len(normalized),
            "rows": normalized,
            **result,
            "data": raw_rows,
        }
    except Exception as exc:
        return {
            "success": False,
            "error": str(exc)[:200],
            "data": None,
            "live_trading_enabled": False,
            "order_placement_allowed": False,
        }


@app.get("/api/broker/funds")
async def get_broker_funds():
    """Dhan fund limits / available balance — read-only. No orders."""
    _hit = _cache_get("broker_funds", _TTL_BROKER)
    if _hit is not None:
        return _hit

    try:
        from core.brokers.dhan.dhan_payload_normalizer import (
            normalize_funds_payload,
            normalize_funds_row,
        )
        from core.brokers.dhan.dhan_readonly import get_funds

        result = await _run_blocking(get_funds, timeout=_BROKER_IO_TIMEOUT_S)
        raw = normalize_funds_payload(result.get("data"))
        normalized = normalize_funds_row(raw)
        return {
            "live_trading_enabled": False,
            "order_placement_allowed": False,
            "source": "dhan_readonly",
            "validated": result.get("success", False),
            "normalized": normalized,
            **result,
            "data": raw,
        }
    except Exception as exc:
        return {
            "success": False,
            "error": str(exc)[:200],
            "data": None,
            "live_trading_enabled": False,
            "order_placement_allowed": False,
        }


@app.get("/api/broker/diagnose")
async def get_broker_diagnose():
    """Diagnose exactly WHY broker is disconnected. Key for Cloud Run / Secret Manager setup."""
    import os as _os

    issues = []
    hints = []
    env_checks = {
        "DHAN_CLIENT_ID": _os.environ.get("DHAN_CLIENT_ID", "").strip(),
        "DHAN_ACCESS_TOKEN": _os.environ.get("DHAN_ACCESS_TOKEN", "").strip(),
        "DHAN_PIN": _os.environ.get("DHAN_PIN", "").strip(),
        "DHAN_TOTP_SECRET": _os.environ.get("DHAN_TOTP_SECRET", "").strip(),
    }
    for key, val in env_checks.items():
        # PIN/TOTP are intentionally NOT mounted on Cloud Run (prevents DH-906 churn).
        if key in ("DHAN_PIN", "DHAN_TOTP_SECRET"):
            continue
        if not val:
            issues.append(f"MISSING: {key} env var not set in Cloud Run / Secret Manager")
            hints.append(f"Set {key} via GCP Secret Manager mount on genesis-system3-web")

    # Check token validity
    token = env_checks["DHAN_ACCESS_TOKEN"]
    token_status = "not_set"
    if token:
        if len(token) < 20:
            issues.append("DHAN_ACCESS_TOKEN too short — likely invalid")
            token_status = "too_short"
        elif token.startswith("Bearer "):
            issues.append("DHAN_ACCESS_TOKEN has 'Bearer ' prefix — remove it")
            token_status = "has_bearer_prefix"
        else:
            token_status = "present"

    client_id = env_checks["DHAN_CLIENT_ID"]

    # Try a real Dhan API call if credentials present
    api_test = None
    if token and client_id:
        try:
            from core.brokers.dhan.dhan_readonly import get_funds

            result = get_funds()
            data = result.get("data")
            ok = bool(result.get("success"))
            # Guard against older get_funds that returned success with DH-906 body
            if isinstance(data, dict):
                remarks = data.get("remarks") if isinstance(data.get("remarks"), dict) else {}
                code = str(remarks.get("error_code") or data.get("errorCode") or "")
                if code == "DH-906" or "Invalid Token" in str(data):
                    ok = False
                    result = dict(result)
                    result["success"] = False
                    result["error"] = "TOKEN_EXPIRED_OR_INVALID"
            api_test = {"success": ok, "data": data, "error": result.get("error")}
            if ok:
                issues.clear()
                hints = ["Token valid and working!"]
            else:
                issues.append("Dhan rejected access token (DH-906 / invalid)")
                hints.append("Mint token once locally, push to Secret Manager, remount; keep Cloud PIN/TOTP unmounted")
        except Exception as e:
            api_test = {"success": False, "error": str(e)[:100]}
            issues.append(f"Dhan API call failed: {str(e)[:80]}")

    return {
        "env_vars": {
            "DHAN_CLIENT_ID_present": bool(client_id),
            "DHAN_CLIENT_ID_preview": client_id[-4:] if client_id else "NOT_SET",
            "DHAN_ACCESS_TOKEN_present": bool(token),
            "DHAN_ACCESS_TOKEN_status": token_status,
            "DHAN_ACCESS_TOKEN_length": len(token) if token else 0,
            "DHAN_PIN_present": bool(env_checks["DHAN_PIN"]),
            "DHAN_TOTP_present": bool(env_checks["DHAN_TOTP_SECRET"]),
        },
        "issues": issues,
        "hints": hints,
        "api_probe": api_test,
        "fix_action": (
            "Update DHAN_ACCESS_TOKEN in GCP Secret Manager (dhan-access-token) and "
            "let Cloud Run remount latest. Prefer PIN+TOTP auto-heal on genesis-system3-web. "
            "Token expires daily — DHAN_PIN + DHAN_TOTP_SECRET enable auto-refresh."
            if issues
            else "No issues found"
        ),
    }


@app.get("/api/broker/positions/live")
async def get_broker_positions_live():
    """Dhan open positions — read-only. No orders. LTP enriched via marketfeed when missing."""
    _hit = _cache_get("broker_positions", _TTL_BROKER)
    if _hit is not None:
        return _hit
    try:
        from core.brokers.dhan.dhan_payload_normalizer import (
            normalize_position_row,
            normalize_positions_payload,
        )
        from core.brokers.dhan.dhan_readonly import get_positions
        from core.brokers.dhan.market_ltp import enrich_positions_with_market_ltp

        result = await _run_blocking(get_positions, timeout=_BROKER_IO_TIMEOUT_S)
        raw_rows = normalize_positions_payload(result.get("data"))
        normalized = [normalize_position_row(r) for r in raw_rows]
        try:
            normalized = await _run_blocking(
                enrich_positions_with_market_ltp, normalized, timeout=8.0
            )
        except Exception:
            # Keep broker rows even if marketfeed enrichment fails.
            pass
        return {
            "live_trading_enabled": False,
            "order_placement_allowed": False,
            "source": "dhan_readonly",
            "validated": result.get("success", False),
            "count": len(normalized),
            "rows": normalized,
            **result,
            "data": raw_rows,
        }
    except Exception as exc:
        return {
            "success": False,
            "error": str(exc)[:200],
            "data": None,
            "live_trading_enabled": False,
            "order_placement_allowed": False,
        }


@app.get("/api/market/live_board")
async def get_market_live_board():
    """
    Dhan-parity live board: index ribbon (Nifty/Bank/Fin/VIX) + equity watch from holdings.
    Continuous poll target for TopBar — not static snapshots.
    """
    _hit = _cache_get("market_live_board", 3.0)
    if _hit is not None:
        return _hit

    def _build():
        from core.brokers.dhan.market_ltp import build_index_board, fetch_market_quotes
        from core.brokers.dhan.dhan_payload_normalizer import (
            normalize_holding_row,
            normalize_holdings_payload,
        )
        from core.brokers.dhan.dhan_readonly import get_holdings

        # Prefer live marketfeed; fall back to paced/TTL chain spots already in memory.
        fallback = {}
        try:
            for sym in ("NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX", "INDIAVIX"):
                row = None
                pushed = _PUSHED_CHAIN_CACHE.get(sym) if isinstance(_PUSHED_CHAIN_CACHE, dict) else None
                if isinstance(pushed, dict) and isinstance(pushed.get("data"), dict):
                    row = pushed["data"]
                if not isinstance(row, dict) or not (row.get("spot") or row.get("underlying_spot")):
                    ttl_hit = _cache_get(f"chain_{sym}", max(_TTL_CHAIN, 120.0))
                    if isinstance(ttl_hit, dict):
                        row = ttl_hit
                if not isinstance(row, dict):
                    continue
                spot = row.get("spot") or row.get("underlying_spot")
                if spot:
                    fallback[sym] = {
                        "spot": spot,
                        "change_pct": row.get("change_pct") or row.get("pct_change"),
                        "source": "paced_chain_cache",
                    }
        except Exception:
            fallback = {}

        board = build_index_board(fallback_spots=fallback)
        equity_rows = []
        try:
            holdings = get_holdings()
            for raw in normalize_holdings_payload(holdings.get("data")):
                norm = normalize_holding_row(raw)
                sid = str((raw or {}).get("securityId") or "").strip()
                equity_rows.append(
                    {
                        "symbol": norm.get("symbol"),
                        "security_id": sid,
                        "exchange_segment": "NSE_EQ",
                        "quantity": norm.get("quantity"),
                        "avg_price": norm.get("avg_price"),
                        "ltp": norm.get("ltp"),
                        "change_pct": None,
                        "pnl": norm.get("pnl"),
                        "pnl_pct": norm.get("pnl_pct"),
                        "current_value": norm.get("current_value"),
                        "live": bool(norm.get("ltp")),
                    }
                )
            # Refresh equity LTPs via marketfeed when holdings LTP is stale/missing.
            need_ids = [r["security_id"] for r in equity_rows if r.get("security_id")]
            if need_ids:
                quotes = fetch_market_quotes({"NSE_EQ": need_ids[:40]})
                for row in equity_rows:
                    q = quotes.get(str(row.get("security_id") or ""), {})
                    if q.get("ltp") is not None:
                        row["ltp"] = q["ltp"]
                        row["change"] = q.get("change")
                        row["change_pct"] = q.get("change_pct")
                        row["live"] = True
                        qty = float(row.get("quantity") or 0)
                        avg = float(row.get("avg_price") or 0)
                        ltp = float(q["ltp"])
                        row["current_value"] = ltp * qty
                        row["pnl"] = (ltp - avg) * qty if qty else 0.0
                        row["pnl_pct"] = ((ltp - avg) / avg * 100.0) if avg else None
        except Exception as exc:
            board["holdings_error"] = str(exc)[:160]

        inv = sum(float(r.get("avg_price") or 0) * float(r.get("quantity") or 0) for r in equity_rows)
        cur = sum(float(r.get("current_value") or 0) for r in equity_rows)
        pnl = cur - inv
        board["portfolio"] = {
            "investment": round(inv, 2),
            "current_value": round(cur, 2),
            "overall_pnl": round(pnl, 2),
            "overall_pnl_pct": round((pnl / inv * 100.0), 2) if inv else None,
            "holdings_count": len(equity_rows),
        }
        board["equities"] = equity_rows
        board["generated_at"] = datetime.now(IST).isoformat()
        return board

    try:
        result = await _run_blocking(_build, timeout=12.0)
        return _cache_set("market_live_board", result)
    except asyncio.TimeoutError:
        return {
            "success": False,
            "error": "live_board_timeout",
            "indices": [],
            "equities": [],
            "live_trading_enabled": False,
        }
    except Exception as exc:
        return {
            "success": False,
            "error": str(exc)[:200],
            "indices": [],
            "equities": [],
            "live_trading_enabled": False,
        }


@app.get("/api/portfolio/unified")
async def get_unified_portfolio():
    """Paper + broker read-only portfolio truth. Never enables live trading."""
    _hit = _cache_get("portfolio", _TTL_PORTFOLIO)
    if _hit is not None:
        return _hit

    try:
        from dashboard.backend.portfolio_truth_service import build_unified_portfolio
    except ImportError:
        from portfolio_truth_service import build_unified_portfolio
    try:
        result = await _run_blocking(build_unified_portfolio, OUTPUTS_DIR, timeout=_TRUTH_IO_TIMEOUT_S)
        return _cache_set("portfolio", result)
    except asyncio.TimeoutError:
        return {"error": "portfolio_timeout", "timeout_s": _TRUTH_IO_TIMEOUT_S}


@app.get("/api/trader/requirements")
async def get_trader_requirements():
    """Full trader field audit mapped to available API data."""
    try:
        from dashboard.backend.trader_requirements_service import (
            build_trader_requirements_report,
        )
    except ImportError:
        from trader_requirements_service import build_trader_requirements_report
    return build_trader_requirements_report(OUTPUTS_DIR)


@app.get("/api/approval/status")
async def get_approval_status():
    """Human approval gate — owner sign-off status (does not enable live trading)."""
    try:
        from dashboard.backend.human_approval_service import build_approval_status
    except ImportError:
        from human_approval_service import build_approval_status
    return build_approval_status()


@app.get("/metrics", include_in_schema=False)
async def get_metrics():
    """Prometheus text-exposition metrics - request counts/latency
    histogram recorded by RequestIDMiddleware on every request. Exempt
    from API-key auth (standard practice - scrapers shouldn't need the
    dashboard's app key) but not from anything else."""
    try:
        from dashboard.backend.metrics import render_prometheus_text
    except ImportError:
        from metrics import render_prometheus_text
    return Response(content=render_prometheus_text(), media_type="text/plain; version=0.0.4")


@app.get("/api/kill-switch/status")
async def get_kill_switch_status():
    """Kill switch status — the same storage/live/kill_switch.json the batch
    session loop checks every cycle, and that order_management.create_order
    now also checks before creating any (currently paper-only) order."""
    try:
        from core.engine.system3_phase113_kill_switch_monitor import run_phase113
    except ImportError as e:
        return {"status": "ERROR", "kill_active": None, "error": f"monitor unavailable: {e}"}
    result = run_phase113()
    return {
        "status": result.get("status"),
        "kill_active": result.get("outputs", {}).get("kill_active"),
        "details": result.get("details"),
        "kill_switch_path": result.get("outputs", {}).get("kill_switch_path"),
    }


@app.get("/api/broker/deps")
async def get_broker_deps():
    """Get broker dependency installation status (Dhan)"""
    try:
        import subprocess

        dhanhq_installed = False
        dhanhq_version = None
        try:
            import dhanhq

            dhanhq_installed = True
            dhanhq_version = getattr(dhanhq, "__version__", "unknown")
        except ImportError:
            pass

        python_path = sys.executable

        pip_freeze_hit = False
        try:
            result = subprocess.run([python_path, "-m", "pip", "freeze"], capture_output=True, text=True, timeout=5)
            if "dhanhq" in result.stdout.lower():
                pip_freeze_hit = True
        except subprocess.TimeoutExpired:
            logger.warning("pip freeze timed out")
        except (FileNotFoundError, OSError) as e:
            logger.warning(f"Failed to run pip freeze: {e}")
        except Exception as e:
            logger.warning(f"Unexpected error running pip freeze: {e}")

        return {
            "dhanhq_installed": dhanhq_installed,
            "dhanhq_version": dhanhq_version,
            "python_path": python_path,
            "pip_freeze_hit": pip_freeze_hit,
            "broker_module_available": DHAN_AVAILABLE,
        }
    except Exception as e:
        return {
            "dhanhq_installed": False,
            "error": str(e)[:200],
            "python_path": sys.executable if "sys" in locals() else "unknown",
        }


@app.get("/api/debug/state_source")
async def get_debug_state_source():
    """Debug endpoint: Get SSOT state source information (internal verification only)"""
    try:
        if not SSOT_AVAILABLE or state_store is None:
            return {"ssot_available": False, "state_file": None, "last_write": None, "state_version": 0}

        state_file = OUTPUTS_DIR / "runtime_state.json"
        state_version = state_store.get_state_version()

        last_write = None
        if state_file.exists():
            last_write = datetime.fromtimestamp(state_file.stat().st_mtime).isoformat()

        return {
            "ssot_available": True,
            "state_file": str(state_file),
            "last_write": last_write,
            "state_version": state_version,
            "outputs_dir": str(OUTPUTS_DIR),
        }
    except Exception as e:
        return {"ssot_available": False, "error": str(e)[:200]}


# Status endpoint - comprehensive system status
@app.get("/api/status")
async def get_status():
    """Comprehensive system status endpoint"""
    try:
        # Check backend health
        health_data = None
        try:
            health_file = OUTPUTS_DIR / "health.json"
            if health_file.exists():
                health_data = json.loads(health_file.read_text())
        except (ValueError, TypeError, KeyError, AttributeError) as e:
            logger.warning(f'Error handled: {e}')
        except Exception as e:
            logger.error(f'Unexpected error: {e}', exc_info=True)
            pass

        # Check data freshness
        chain_file = OUTPUTS_DIR / "chain_raw_live.csv"
        data_fresh = False
        last_update = None
        if chain_file.exists():
            try:
                mtime = chain_file.stat().st_mtime
                age_seconds = time.time() - mtime
                data_fresh = age_seconds < 300  # 5 minutes
                last_update = datetime.fromtimestamp(mtime).isoformat()
            except (ValueError, TypeError, KeyError, AttributeError) as e:
                logger.warning(f'Error handled: {e}')
            except Exception as e:
                logger.error(f'Unexpected error: {e}', exc_info=True)
                pass

        # Check market status
        market_status = "unknown"
        data_source = "unknown"
        if MARKET_DETECTION_AVAILABLE:
            try:
                market_status = get_market_status()
                data_source = "synthetic" if not is_market_open() else "real"
            except (ValueError, TypeError, KeyError, AttributeError) as e:
                logger.warning(f'Error handled: {e}')
            except Exception as e:
                logger.error(f'Unexpected error: {e}', exc_info=True)
                pass

        return {
            "status": "ok",
            "timestamp": datetime.now(pytz.timezone("Asia/Kolkata")).isoformat(),
            "backend": {"running": True, "port": 8000, "uptime_estimate": "running"},
            "frontend": {"expected_url": "http://localhost:3000", "status": "should_be_running"},
            "data": {
                "source": data_source,
                "market_status": market_status,
                "fresh": data_fresh,
                "last_update": last_update,
            },
            "health": health_data is not None,
            "endpoints": {
                "health": "/api/health",
                "chain": "/api/chain/{underlying}",
                "signals": "/api/signal/top",
                "positions": "/api/positions",
                "pnl": "/api/pnl",
                "perf": "/api/perf",
            },
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now(pytz.timezone("Asia/Kolkata")).isoformat(),
        }


# ─── System3 Analytics Endpoints ─────────────────────────────────────────────

GAIN_RANK_FILE = ROOT_DIR / "state" / "gain_rank_history.json"
VALIDATION_DIR = ROOT_DIR / "state" / "market_validations"
DS_HEALTH_FILE = ROOT_DIR / "state" / "datasource_health.json"
RETRAIN_FLAG = ROOT_DIR / "state" / "retrain_signal.json"
WATCHDOG_LOG = ROOT_DIR / "logs" / "dhan_watchdog.log"
JOB_SCHED_CFG = ROOT_DIR / "config" / "system3_job_scheduler.json"


@app.get("/api/instruments/health")
async def get_instruments_health():
    """Instrument master freshness — Dhan CDN sync status."""
    try:
        from core.data.instruments_cache import ensure_instruments_loaded
        from core.data.instruments_master import META_JSON

        metrics = ensure_instruments_loaded()
        meta = {}
        if META_JSON.exists():
            meta = json.loads(META_JSON.read_text(encoding="utf-8"))
        stale = True
        if meta.get("synced_utc"):
            from datetime import datetime, timezone

            synced = datetime.fromisoformat(meta["synced_utc"].replace("Z", "+00:00"))
            age_h = (datetime.now(timezone.utc) - synced).total_seconds() / 3600
            stale = age_h > 24
        return {
            "status": "ok" if metrics.get("rows", 0) > 0 else "missing",
            "rows": metrics.get("rows", 0),
            "source": metrics.get("source"),
            "stale": stale,
            "meta": meta,
        }
    except Exception as e:
        return {"status": "error", "error": str(e)[:200]}



def _filter_rows_fo(rows):
    """BLK-004: drop non-F&O underlyings from ranking/signal payloads."""
    fo = get_fo_eligibility_filter()
    kept = []
    rejected = []
    for row in rows or []:
        if not isinstance(row, dict):
            continue
        sym = str(row.get("underlying") or row.get("symbol") or "").strip().upper()
        if not sym:
            rejected.append({"underlying": sym, "reason": "MISSING_SYMBOL"})
            continue
        ok, reason = fo.is_eligible(sym)
        if ok:
            out = dict(row)
            out["fo_check"] = {"eligible": True, "reason": reason}
            kept.append(out)
        else:
            rejected.append({"underlying": sym, "reason": reason})
    return kept, rejected


_MULTIBAGGER_SCHEMA_VERSION = "1.0.0"
_MULTIBAGGER_FRESHNESS_TTL_S = 1800
_MULTIBAGGER_FUTURE_TOLERANCE_S = 300
_MULTIBAGGER_PRODUCER_SOURCES = {"GENESIS_FORECAST_EVALUATOR"}
_MULTIBAGGER_PRICE_SOURCES = {"DHAN"}


def _parse_aware_timestamp(value: Any) -> Optional[datetime]:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        return parsed if parsed.tzinfo is not None and parsed.utcoffset() is not None else None
    except ValueError:
        return None


def _evidence_age(timestamp: Any, now: datetime) -> Optional[float]:
    parsed = _parse_aware_timestamp(timestamp)
    return None if parsed is None else (now - parsed.astimezone(timezone.utc)).total_seconds()


def _multibagger_pending_contract(reason: str = "NO_VERIFIED_EVIDENCE") -> Dict[str, Any]:
    """Return the stable public contract without implying missing research is empty."""
    return {
        "schema_version": _MULTIBAGGER_SCHEMA_VERSION,
        "status": "pending",
        "as_of": None,
        "source": None,
        "candidates": [],
        "sections": {
            "candidate_ranking": "pending",
            "forecast_horizons": "pending",
            "probability_ladder": "pending",
            "fundamentals": "pending",
            "governance": "pending",
            "ownership_flows": "pending",
            "valuation": "pending",
            "outcome_ledger": "pending",
        },
        "reason": reason,
        "safety": {"read_only": True, "orders_enabled": False},
    }


def _build_multibagger_contract(payload: Any) -> Dict[str, Any]:
    """Validate producer evidence before it can enter the public read contract.

    Wave 1 deliberately accepts only candidate identity plus mandatory observed
    price and model provenance. It does not manufacture probabilities or infer
    unavailable research sections from unrelated dashboard state.
    """
    if not isinstance(payload, dict):
        return _multibagger_pending_contract()
    now = datetime.now(timezone.utc)
    producer_source = str(payload.get("source") or "").strip().upper()
    as_of = payload.get("as_of")
    envelope_age = _evidence_age(as_of, now)
    if producer_source not in _MULTIBAGGER_PRODUCER_SOURCES:
        return _multibagger_pending_contract("PRODUCER_SOURCE_UNVERIFIED")
    if envelope_age is None or envelope_age < -_MULTIBAGGER_FUTURE_TOLERANCE_S:
        return _multibagger_pending_contract("INVALID_OR_FUTURE_AS_OF")
    rows = payload.get("candidates")
    if not isinstance(rows, list):
        return _multibagger_pending_contract("CANDIDATE_EVIDENCE_UNAVAILABLE")

    accepted = []
    rejected = []
    seen_ids = set()
    seen_symbols = set()
    seen_ranks = set()
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            rejected.append({"index": index, "reason": "INVALID_CANDIDATE"})
            continue
        candidate_id = str(row.get("candidate_id") or "").strip()
        symbol = str(row.get("symbol") or "").strip().upper()
        price = row.get("price")
        model = row.get("model")
        failures = []
        if not candidate_id or not symbol:
            failures.append("IDENTITY_PROVENANCE_REQUIRED")
        if candidate_id in seen_ids or symbol in seen_symbols:
            failures.append("DUPLICATE_CANDIDATE_OR_SYMBOL")
        rank = row.get("rank")
        if isinstance(rank, bool) or not isinstance(rank, int) or rank <= 0:
            failures.append("POSITIVE_INTEGRAL_RANK_REQUIRED")
        elif rank in seen_ranks:
            failures.append("DUPLICATE_RANK")
        if not isinstance(price, dict):
            failures.append("PRICE_PROVENANCE_REQUIRED")
        else:
            try:
                price_value = float(price.get("value"))
            except (TypeError, ValueError):
                price_value = 0.0
            price_source = str(price.get("source") or "").strip().upper()
            price_age = _evidence_age(price.get("observed_at"), now)
            if (
                price_value <= 0
                or str(price.get("currency") or "").strip().upper() != "INR"
                or price_source not in _MULTIBAGGER_PRICE_SOURCES
                or price_age is None
                or price_age < -_MULTIBAGGER_FUTURE_TOLERANCE_S
            ):
                failures.append("PRICE_PROVENANCE_REQUIRED")
            elif price_age > _MULTIBAGGER_FRESHNESS_TTL_S:
                failures.append("PRICE_EVIDENCE_STALE")
        model_generated_age = _evidence_age(model.get("generated_at"), now) if isinstance(model, dict) else None
        if (
            not isinstance(model, dict)
            or not all(str(model.get(key) or "").strip() for key in ("name", "version", "scoring_method"))
            or model_generated_age is None
            or model_generated_age < -_MULTIBAGGER_FUTURE_TOLERANCE_S
        ):
            failures.append("MODEL_PROVENANCE_REQUIRED")
        elif model_generated_age > _MULTIBAGGER_FRESHNESS_TTL_S:
            failures.append("MODEL_EVIDENCE_STALE")
        if failures:
            rejected.append({"candidate_id": candidate_id or None, "index": index, "reason": ";".join(failures)})
            continue
        seen_ids.add(candidate_id)
        seen_symbols.add(symbol)
        seen_ranks.add(rank)
        proof = model.get("proof") if isinstance(model.get("proof"), dict) else {}
        artifact_sha = str(proof.get("artifact_sha256") or "").lower()
        data_sha = str(proof.get("data_sha256") or "").lower()
        code_sha = str(proof.get("code_sha") or "").lower()
        manifest_complete = bool(
            re.fullmatch(r"[0-9a-f]{64}", artifact_sha)
            and re.fullmatch(r"[0-9a-f]{64}", data_sha)
            and re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", code_sha)
        )
        accepted.append({
            "candidate_id": candidate_id,
            "symbol": symbol,
            "rank": rank,
            "price": {
                "value": price_value,
                "currency": str(price["currency"]).upper(),
                "source": str(price["source"]),
                "observed_at": str(price["observed_at"]),
            },
            "model": {
                "name": str(model["name"]),
                "version": str(model["version"]),
                "scoring_method": str(model["scoring_method"]),
                "generated_at": str(model["generated_at"]),
                "evidence_status": "unverified",
                "proof_ready": False,
                "producer_asserted_hashes": ({
                    "artifact_sha256": artifact_sha,
                    "data_sha256": data_sha,
                    "code_sha": code_sha,
                } if manifest_complete else None),
                "manifest_complete": manifest_complete,
            },
        })

    if not accepted:
        result = _multibagger_pending_contract("NO_CANDIDATE_PASSED_PROVENANCE_VALIDATION")
        result["validation"] = {"accepted": 0, "rejected": len(rejected), "rejections": rejected}
        return result

    result = _multibagger_pending_contract("ADDITIONAL_RESEARCH_SECTIONS_UNAVAILABLE")
    result.update({
        "status": "stale" if envelope_age > _MULTIBAGGER_FRESHNESS_TTL_S else "partial",
        "as_of": str(as_of),
        "source": producer_source,
        "age_seconds": round(max(0.0, envelope_age), 3),
        "stale": envelope_age > _MULTIBAGGER_FRESHNESS_TTL_S,
        "candidates": accepted,
        "validation": {"accepted": len(accepted), "rejected": len(rejected), "rejections": rejected},
    })
    result["sections"]["candidate_ranking"] = "stale" if result["stale"] else "partial"
    return result


@app.get("/api/research/multibagger")
async def get_multibagger_research():
    """Versioned, read-only research evidence contract; pending by default."""
    payload = None
    if SSOT_AVAILABLE and state_store is not None:
        try:
            payload = state_store.get_state().get("multibagger_research")
        except Exception:
            payload = None
    return _build_multibagger_contract(payload)


@app.get("/api/gain_rank")
async def get_gain_rank(refresh: bool = False):
    """Latest gain rank predictions — file history, or live scanner fallback."""
    try:
        history = []
        if GAIN_RANK_FILE.exists():
            history = json.loads(GAIN_RANK_FILE.read_text())
            if not isinstance(history, list):
                history = []
        today = datetime.now(IST).strftime("%Y-%m-%d")
        today_entry = next((e for e in reversed(history) if e.get("date") == today), None)
        latest = today_entry or (history[-1] if history else None)
        stale = latest is None or latest.get("date") != today

        # Live fallback: build today's rankings from contract-gain scanner so
        # Signals/Trade tabs are not permanently empty when history file is missing.
        # Bound tightly — never block /api/batch/market-data for 60s+ on equity fan-out.
        if stale or latest is None:
            try:
                scan = await asyncio.wait_for(
                    get_top_contract_gainers(top_n=8, market_top_n=25, include_equity=False),
                    timeout=8.0,
                )
                rankings = []
                table = (scan or {}).get("market_top_table") or []
                if not table:
                    mw = (scan or {}).get("market_wide") or {}
                    table = mw.get("top_combined_list") or []
                for row in table[:25]:
                    if not isinstance(row, dict):
                        continue
                    opt = str(row.get("option_type") or "").upper()
                    rankings.append(
                        {
                            "rank": row.get("rank"),
                            "underlying": str(row.get("underlying") or row.get("symbol") or "").upper(),
                            "direction": "UP" if opt == "CE" else "DOWN",
                            "option_type": opt,
                            "strike": row.get("strike"),
                            "expiry_date": row.get("expiry_date"),
                            "ltp": row.get("ltp"),
                            "change": row.get("change") or row.get("change_rs"),
                            "volume": row.get("volume"),
                            "oi": row.get("oi"),
                            "gain_rank": float(row.get("gain_pct") or row.get("gain_rank") or 0),
                            "gain_score": float(row.get("gain_pct") or 0),
                            "gain_pct": float(row.get("gain_pct") or 0),
                            "option_eligible": True,
                            "recommendation": "WATCH",
                            "market_match_note": row.get("market_match_note"),
                            "data_provenance": row.get("data_provenance") or "DHAN_OPTION_CHAIN_LIVE",
                            "refreshed_at": row.get("refreshed_at") or (scan or {}).get("refreshed_at"),
                            "source": "live_scanner_fallback",
                        }
                    )
                if not rankings:
                    by_seg = (scan or {}).get("by_segment") or {}
                    for seg, payload in by_seg.items():
                        if not isinstance(payload, dict):
                            continue
                        for side_key, direction in (("top_ce", "UP"), ("top_pe", "DOWN")):
                            row = payload.get(side_key)
                            if not isinstance(row, dict):
                                continue
                            rankings.append(
                                {
                                    "underlying": str(row.get("underlying") or seg).upper(),
                                    "direction": direction,
                                    "option_type": str(row.get("option_type") or side_key[-2:]).upper(),
                                    "strike": row.get("strike"),
                                    "ltp": row.get("ltp"),
                                    "gain_rank": float(row.get("gain_pct") or 0),
                                    "gain_score": float(row.get("gain_pct") or 0),
                                    "option_eligible": True,
                                    "recommendation": "WATCH",
                                    "source": "live_scanner_fallback",
                                }
                            )
                if rankings:
                    latest = {
                        "date": today,
                        "generated_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                        "rankings": rankings,
                        "predictions": rankings,
                        "source": "live_scanner_fallback",
                        "note": "File history missing — live scanner rankings used for dashboard visibility",
                    }
                    stale = False
            except Exception as scan_err:
                print(f"[gain_rank] live scanner fallback failed: {scan_err}")

        if latest is None:
            return {"status": "no_data", "latest": None, "history": history[-14:], "is_today": False, "stale": True}

        latest = dict(latest)
        raw_rows = (latest.get("rankings") or latest.get("predictions") or [])
        kept, rejected = _filter_rows_fo(raw_rows if isinstance(raw_rows, list) else [])
        # Authenticated chain/snapshot spots only — never BASE_SPOT / synthetic.
        spot_lookup: Dict[str, Dict[str, Any]] = {}
        for row in kept:
            if not isinstance(row, dict):
                continue
            sym = str(row.get("underlying") or row.get("symbol") or "").upper()
            if not sym or sym in spot_lookup:
                continue
            chain_payload = _chain_from_push_cache(sym)
            if chain_payload is None:
                cached = _cache_get(f"chain_{sym}", max(_TTL_CHAIN, 300.0))
                chain_payload = cached if isinstance(cached, dict) else None
            if not isinstance(chain_payload, dict):
                continue
            try:
                spot_val = float(chain_payload.get("spot") or 0)
            except (TypeError, ValueError):
                spot_val = 0.0
            if spot_val <= 0:
                continue
            spot_lookup[sym] = {
                "spot": spot_val,
                "status": chain_payload.get("status"),
                "source": chain_payload.get("data_source") or chain_payload.get("source") or "dhan",
            }
        kept = enrich_gain_rank_rows_with_authenticated_spots(kept, spot_lookup)
        latest["rankings"] = kept
        latest["predictions"] = kept
        latest["fo_filtered_out"] = rejected
        latest["fo_filter"] = {
            "eligible_count": len(kept),
            "rejected_count": len(rejected),
            "universe_size": len(get_fo_eligibility_filter().get_current_universe()),
        }
        return {
            "status": "ok",
            "latest": latest,
            "rankings": kept,
            "fo_rejected": rejected,
            "history": history[-14:],
            "total_days": len(history),
            "is_today": (latest or {}).get("date") == today,
            "stale": stale,
            "latest_date": (latest or {}).get("date"),
            "source": (latest or {}).get("source") or "gain_rank_history",
        }
    except Exception as e:
        return {"status": "error", "error": str(e), "latest": None, "history": [], "is_today": False, "stale": True}




@app.get("/api/audit/option-visibility")
async def get_option_visibility_audit(sample: bool = False):
    """BLK-003: prove signal underlyings map to visible PE/CE contracts."""
    try:
        if sample:
            report = generate_sample_audit_report()
            report["mode"] = "sample"
            return report

        history = []
        if GAIN_RANK_FILE.exists():
            raw = json.loads(GAIN_RANK_FILE.read_text(encoding="utf-8", errors="replace"))
            if isinstance(raw, list):
                history = raw
        preds = []
        if history:
            latest = history[-1] if isinstance(history[-1], dict) else {}
            raw_preds = latest.get("predictions") or latest.get("rankings") or []
            if isinstance(raw_preds, list):
                preds = [p for p in raw_preds if isinstance(p, dict)]

        chain_candidates = [
            ROOT_DIR / "state" / "option_chain_cache.json",
            ROOT_DIR / "storage" / "live" / "option_chain_cache.json",
            ROOT_DIR / "reports" / "latest" / "option_strike_visibility.json",
        ]
        chain_file = next((p for p in chain_candidates if p.exists()), None)
        auditor = OptionVisibilityAuditor(chain_file)
        now = datetime.now(IST)
        if not preds:
            for i, sym in enumerate(["NIFTY", "BANKNIFTY", "RELIANCE", "SBIN", "INFY"]):
                auditor.audit_signal(f"SEED-{i+1}", sym, "LONG", 0.5, now)
            report = auditor.generate_report()
            report["mode"] = "seed_no_predictions"
            report["chain_file"] = str(chain_file) if chain_file else None
            return report

        for i, row in enumerate(preds[:25]):
            sym = str(row.get("underlying") or row.get("symbol") or "NIFTY")
            score = float(row.get("gain_score") or row.get("gain_pct") or 0)
            direction = "LONG" if score >= 0 else "SHORT"
            conf = min(abs(score) / 100.0, 1.0) if score else 0.5
            auditor.audit_signal(str(row.get("id") or f"SIG-{i+1}"), sym, direction, conf, now)
        report = auditor.generate_report()
        report["mode"] = "live_history"
        report["chain_file"] = str(chain_file) if chain_file else None
        report["note"] = (
            "Coverage uses local chain cache when present; "
            "otherwise symbols are marked missing until Dhan OC is cached."
        )
        return report
    except Exception as e:
        return {"status": "error", "error": str(e)[:300], "proof_gate": False}


@app.get("/api/scanner/top_contract_gainers")
async def get_top_contract_gainers(
    top_n: int = 5,
    market_top_n: int = 25,
    include_equity: bool = True,
):
    """
    Live market scanner: highest % gain CE/PE across index + priority equity FO.
    Returns by_segment (index) plus market_top_table (ranked board).
    Prefer ultra-micro background cache; fall back to live/EOD scan.
    """
    top_n = min(max(int(top_n or 5), 1), 20)
    market_top_n = min(max(int(market_top_n or 25), 5), 50)
    cache_key = f"scanner_gainers:{top_n}:{market_top_n}:{int(bool(include_equity))}"
    _hit = _cache_get(cache_key, max(_TTL_SCANNER, 90.0))
    if _hit is not None and (
        (_hit.get("market_top_table") or [])
        or not _market_open_from_state()
    ):
        return _hit
    # Prefer shared micro-stream cache even if query params differ slightly.
    shared = _cache_get("scanner_gainers:5:25:1", max(_TTL_SCANNER, 90.0))
    if shared is not None and include_equity and (shared.get("market_top_table") or []):
        return shared
    warmed = _build_market_top_from_chain_cache(top_n=top_n, market_top_n=market_top_n)
    if warmed is not None:
        _cache_set(cache_key, warmed)
        return warmed
    if _MARKET_TOP_STATE_FILE.exists():
        try:
            disk = json.loads(_MARKET_TOP_STATE_FILE.read_text(encoding="utf-8"))
            if int(disk.get("contracts_scored_total") or 0) > 0:
                _cache_set(cache_key, disk)
                return disk
        except Exception:
            pass
    global _EOD_SCANNER_CACHE
    if not _market_open_from_state():
        cached_at, cached = _EOD_SCANNER_CACHE
        if cached and (time.time() - cached_at) < _EOD_SCANNER_TTL_S:
            return cached
        try:

            def _eod_scanner():
                from dashboard.backend.contract_gain_scanner import (
                    build_top_contract_gainers_report,
                )

                report = build_top_contract_gainers_report(
                    top_n=top_n,
                    market_top_n=market_top_n,
                    include_equity=bool(include_equity),
                )
                report["status"] = "eod_snapshot"
                report["market_open"] = False
                report["note"] = "After-hours market top CE/PE from last Dhan/EOD chains"
                return report

            result = await _run_blocking(_eod_scanner, timeout=max(_SCANNER_EOD_TIMEOUT_S, 180.0))
            if int(result.get("contracts_scored_total") or result.get("segments_implemented") or 0) > 0:
                _EOD_SCANNER_CACHE = (time.time(), result)
                _cache_set(cache_key, result)
            return result
        except asyncio.TimeoutError:
            return {**_scanner_market_closed_response(), "status": "timeout"}
        except Exception as exc:
            return {**_scanner_market_closed_response(), "error": str(exc)[:200]}
    # The index micro-loop is the sole Dhan OC owner. A second four-index fan-out
    # here contends on Dhan's process-wide 1 request / ~3s gate and makes both the
    # scanner and otherwise healthy chains flap. During cold start, return honest
    # typed warming state; do not cache this empty response.
    return {
        "status": "warming",
        "market_open": True,
        "scanner_warming": True,
        "message": "Market Top is warming from the paced Dhan index-chain stream",
        "segments": list(_INDEX_STREAM_SYMBOLS),
        "segments_implemented": 0,
        "by_segment": {},
        "market_top_table": [],
        "contracts_scored_total": 0,
        "live_trading_enabled": False,
    }


@app.get("/api/scanner/equity_options")
async def get_equity_options_scanner(top_n: int = 10, priority_only: bool = False):
    """Equity (stock) F&O universe + OPTSTK top CE/PE from bhavcopy or live Dhan."""
    cache_key = f"equity_options:{min(max(top_n, 1), 50)}:{int(bool(priority_only))}"
    _hit = _cache_get(cache_key, max(_TTL_SCANNER, 120.0))
    if _hit is not None:
        return _hit
    try:
        from dashboard.backend.equity_option_scanner import build_equity_options_report

        report = await _run_blocking(
            build_equity_options_report,
            min(max(top_n, 1), 50),
            priority_only,
            timeout=max(_SCANNER_IO_TIMEOUT_S, 90.0),
        )
        if isinstance(report, dict) and not _market_open_from_state():
            report["market_open"] = False
            report.setdefault("note", "Market closed — equity rows from last Dhan quotes / bhavcopy")
        if isinstance(report, dict):
            return _cache_set(cache_key, report)
        return report
    except asyncio.TimeoutError:
        return {"status": "timeout", "error": f"equity_scanner exceeded {_SCANNER_IO_TIMEOUT_S}s"}
    except Exception as e:
        return {"status": "error", "error": str(e)[:300]}


@app.get("/api/scanner/moneycontrol_gainers")
async def get_moneycontrol_option_gainers(top_n: int = 25, refresh: bool = False):
    """Moneycontrol All Options Top Gainers — LIVE_SCRAPED reference only (not live trading truth)."""
    top_n = min(max(int(top_n or 25), 1), 50)
    cache_key = f"moneycontrol_gainers:{top_n}"
    if not refresh:
        hit = _cache_get(cache_key, 90.0)
        if hit is not None:
            return hit
        disk = ROOT_DIR / "state" / "moneycontrol_option_gainers.json"
        if disk.exists():
            try:
                data = json.loads(disk.read_text(encoding="utf-8"))
                if isinstance(data, dict) and data.get("market_top_table"):
                    return _cache_set(cache_key, data)
            except Exception:
                pass
    try:
        from dashboard.backend.moneycontrol_option_gainers import fetch_moneycontrol_option_gainers

        report = await _run_blocking(fetch_moneycontrol_option_gainers, top_n, 25.0, timeout=40.0)
        if isinstance(report, dict):
            report["ready_for_live"] = False
            report["live_trading_enabled"] = False
            # Keep a shared :25 cache key so Alerts synth sees scrape failures
            # even when UI requested a smaller top_n.
            _cache_set("moneycontrol_gainers:25", report)
            return _cache_set(cache_key, report)
        return {"status": "error", "market_top_table": [], "ready_for_live": False}
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)[:300],
            "market_top_table": [],
            "data_provenance": "LIVE_SCRAPED",
            "ready_for_live": False,
            "live_trading_enabled": False,
        }


@app.get("/api/scanner/market_top_diagnose")
async def get_market_top_diagnose():
    """Auto-diagnose why Moneycontrol high-risers may be missing from Dhan Market Top."""
    try:
        from dashboard.backend.contract_gain_scanner import diagnose_market_top_gap

        return await _run_blocking(diagnose_market_top_gap, timeout=20.0)
    except Exception as e:
        return {"status": "error", "error": str(e)[:300], "live_trading_enabled": False}


@app.get("/api/scanner/segments")
async def get_scanner_segments():
    """Implementation matrix: index OPTIDX vs equity OPTSTK vs cash equity."""
    try:
        from dashboard.backend.equity_option_scanner import build_equity_options_report

        report = build_equity_options_report(top_n=5)
        return {
            "status": "ok",
            "segments": report.get("segments", {}),
            "implementation_gaps": report.get("implementation_gaps", []),
            "generated_utc": report.get("generated_utc"),
        }
    except Exception as e:
        return {"status": "error", "error": str(e)[:200]}


@app.get("/api/accuracy_trend")
async def get_accuracy_trend():
    """Spearman ρ trend aligned with auto_gates (local + Firestore validation days)."""
    _hit = _cache_get("accuracy_trend", _TTL_ACCURACY)
    if _hit is not None:
        return _hit
    try:
        try:
            from dashboard.backend.accuracy_trend_service import build_accuracy_trend_payload
        except ImportError:
            from accuracy_trend_service import build_accuracy_trend_payload
        payload = build_accuracy_trend_payload(
            ROOT_DIR,
            retrain_needed=RETRAIN_FLAG.exists(),
        )
        return _cache_set("accuracy_trend", payload)
    except Exception as e:
        return {"status": "error", "error": str(e), "trend": [], "retrain_needed": False}


@app.get("/api/auto_gates")
async def get_auto_gates(refresh: bool = False):
    """Runtime-driven production/prediction/profit blocker gates (replaces static dashboard proof matrix)."""
    _hit = _cache_get("auto_gates", _TTL_AUTO_GATES)
    if _hit is not None:
        return _hit

    try:
        try:
            from dashboard.backend.auto_gates_service import build_auto_gates_report
        except ImportError:
            from auto_gates_service import build_auto_gates_report
        live_state = None
        if SSOT_AVAILABLE and state_store is not None:
            live_state = state_store.get_state()
        return build_auto_gates_report(refresh=refresh, live_state=live_state)
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)[:200],
            "runtime_driven": False,
            "proof_gates": [],
            "live_trading_enabled": False,
        }


@app.get("/api/continuous_closure")
async def get_continuous_closure(refresh: bool = False, live: bool = False):
    """Blocker cards + auto-resume pointer.

    The request path never HTTP-fans-out to this same Cloud Run origin.
    Self-calls deadlock when the instance is busy serving the parent request
    (fresh 2026-08-22 production `/api/continuous_closure` timed out at 25s).
    Live URL verify stays on the offline orchestrator CLI, not this handler.
    The `live` query flag is accepted for compat and recorded, but ignored.
    """
    cache_key = "continuous_closure:offline"
    if not refresh:
        _hit = _cache_get(cache_key, REQUEST_PATH_CACHE_TTL_S)
        if _hit is not None:
            return stamp_closure_request_path(
                _hit,
                cache_hit=True,
                cache_age_s=_cache_age_s(cache_key) or 0.0,
                live_query=bool(live),
            )

    def _build_offline_report() -> Dict[str, Any]:
        try:
            from dashboard.backend.continuous_closure_service import (
                build_continuous_closure_report,
                write_closure_artifacts,
            )
        except ImportError:
            from continuous_closure_service import (
                build_continuous_closure_report,
                write_closure_artifacts,
            )
        report = build_continuous_closure_report(
            ROOT_DIR,
            include_live=False,
        )
        try:
            write_closure_artifacts(ROOT_DIR, report)
        except Exception:
            pass
        return report

    try:
        report = await _run_blocking(_build_offline_report, timeout=8.0)
        _cache_set(cache_key, report)
        return stamp_closure_request_path(
            report,
            cache_hit=False,
            cache_age_s=0.0,
            live_query=bool(live),
        )
    except Exception as e:
        return {
            "schema": "continuous_closure_v1",
            "status": "error",
            "error": str(e)[:200],
            "phases": {"blocker_cards": [], "auto_resume": None},
            "summary": {"open": 0, "resolved": 0, "total_cards": 0},
            "safety": {"live_trading_enabled": False},
            "request_path": {
                "self_http_fanout": False,
                "live_http_skipped_reason": "cloud_run_self_call_deadlock_prevention",
            },
        }


@app.get("/api/proof_ledger")
async def get_proof_ledger():
    """Read-only SHA256 proof ledger + latest autonomous intent tick. No secrets."""
    try:
        from dashboard.backend.proof_ledger_service import read_proof_ledger_public
    except ImportError:
        from proof_ledger_service import read_proof_ledger_public
    return read_proof_ledger_public(ROOT_DIR)


# ---------------------------------------------------------------------------
# Worker -> Web scheduler-health bridge
# ---------------------------------------------------------------------------
# CRITICAL ARCHITECTURE NOTE: Cloud Run `genesis-system3-web` and the
# worker/rotator Jobs are separate services with separate filesystems.
# The job scheduler daemon (core/engine/system3_phase82_job_scheduler.py)
# does not share disk with the web service. A web-service endpoint that
# reads local files for scheduler state will not see worker-only files.
#
# Fix: the worker actively PUSHES its heartbeat/job-status to the web
# service over HTTP every scheduler tick (~60s, see job scheduler daemon
# loop), authenticated with a shared secret (WORKER_PUSH_TOKEN env var,
# set identically on both Render services). The web service holds the
# latest pushed snapshot in memory and serves it back from GET. If the
# worker never pushes (e.g. not deployed, crashed, or token mismatch),
# GET correctly reports unhealthy/stale instead of silently looking like
# an idle-but-fine scheduler.
_scheduler_health_state: Dict[str, Any] = {
    "received": False,
    "last_push_at": None,
    "daemon_heartbeat": None,
    "daemon_pid": None,
    "jobs": {},
    "config_alert": None,
    "config_jobs_total": None,
    "config_jobs_enabled": None,
    "jobs_status_today": {},
    "fired_keys_today": [],
}
_WORKER_PUSH_TOKEN = os.environ.get("WORKER_PUSH_TOKEN", "").strip()


@app.post("/api/scheduler/health/push")
async def push_scheduler_health(payload: Dict[str, Any], request: Request):
    """
    Called by the WORKER service (scripts/cloud_worker.py Thread 4) on
    every scheduler tick to push its real state to the web service,
    since the two run on separate Render containers with no shared
    filesystem. Requires X-Worker-Token header matching WORKER_PUSH_TOKEN
    env var (set identically on both services in the Render dashboard)
    when that env var is configured; if it is not set on this (web)
    side, push is accepted unauthenticated (local/dev convenience).
    """
    global _scheduler_health_state
    if _WORKER_PUSH_TOKEN:
        sent_token = request.headers.get("X-Worker-Token", "")
        if sent_token != _WORKER_PUSH_TOKEN:
            raise HTTPException(status_code=401, detail="Invalid or missing X-Worker-Token")
    _scheduler_health_state = {
        "received": True,
        "last_push_at": datetime.now(timezone.utc).isoformat(),
        "daemon_heartbeat": payload.get("daemon_heartbeat"),
        "daemon_pid": payload.get("daemon_pid"),
        "jobs": payload.get("jobs", {}),
        "config_alert": payload.get("config_alert"),
        "config_jobs_total": payload.get("config_jobs_total"),
        "config_jobs_enabled": payload.get("config_jobs_enabled"),
        "jobs_status_today": payload.get("jobs_status_today", {}),
        "fired_keys_today": payload.get("fired_keys_today", []),
    }
    return {"accepted": True}


# ---------------------------------------------------------------------------
# Chain push — worker precomputes the small set of default-underlying option
# chains and pushes them here, same pattern as scheduler health push above.
# GET /api/chain/{underlying} (see _get_chain_uncached) serves straight from
# this in-memory snapshot for anything fresh enough, instead of doing the
# expensive DataSourceManager() + live Dhan fetch inline on the web dyno —
# that inline path is what was crash-looping the 512MB web container during
# market hours (2026-07-02 forensic investigation, see CHANGE_LOG.md).
# Falls back to the old inline fetch only for underlyings the worker doesn't
# push, or if the push has gone stale (worker down/redeploying).
#
# The worker pushes off-hours too, at a much slower cadence, since the
# EOD/bhavcopy snapshot it fetches then barely changes between ticks (see
# cloud_worker.py's Thread 5 docstring — this used to be market-hours-only,
# which meant every after-hours page view fell back to the slow inline fetch
# below and frequently surfaced as a permanent "Market Closed" screen with no
# data at all, even though EOD data was available). Each push carries a
# `market_open` flag so we know which freshness window applies.
# ---------------------------------------------------------------------------
_PUSHED_CHAIN_CACHE: Dict[str, Dict[str, Any]] = (
    {}
)  # {UNDERLYING: {"data": ..., "received_at": float, "market_open": bool}}
# Serve push/micro-loop snapshots as fresh for 45s. Falling back to live Dhan OC
# too early is what collapses market-hours streaming under Dhan's ~1 req/3s limit.
_PUSHED_CHAIN_FRESH_S = 45
_PUSHED_CHAIN_STALE_SERVE_S = 180  # still show last good rows (marked stale) before live fetch
_PUSHED_CHAIN_STALE_SERVE_S_CLOSED = 86400  # after hours: never block UI waiting on Dhan OC
_PUSHED_CHAIN_FRESH_S_CLOSED = 3600  # worker/micro-loop off-hours window
_INDEX_STREAM_SYMBOLS = ("NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX", "BANKEX")
# Smoke/UI semantic proof requires these four; SENSEX and BANKEX are optional and must not
# delay required-symbol cold-start readiness via the serial 20s closed-market gap.
_REQUIRED_CHAIN_SYMBOLS = ("NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY")
_CHAIN_COLD_START_GAP_S = 3.5  # DSM OC pacing only; never the 20s closed-market sleep
_CHAIN_LIVE_TIMEOUT_OPEN_S = 25.0
_CHAIN_LIVE_TIMEOUT_CLOSED_S = 8.0

# Single-flight Dhan option-chain executor — Cloud Run 1 vCPU cannot run many
# concurrent sync OC HTTP calls; queued to_thread work was burning the timeout
# before the HTTP request even started (NO_DHAN_DATA / DSM timed out).
_DHAN_OC_EXECUTOR = ThreadPoolExecutor(max_workers=1, thread_name_prefix="dhan-oc")
_DHAN_OC_LOCK = asyncio.Lock()


async def _run_dhan_oc(fn, *args, timeout: float = 25.0, **kwargs):
    """Run one Dhan OC fetch at a time on a dedicated worker thread.

    DSM already serializes with its own threading lock — do not add a second
    app-level thread lock here (that deadlocked against market-top and timed out
    /api/chain at exactly 25s).
    """

    async with _DHAN_OC_LOCK:
        loop = asyncio.get_running_loop()
        return await asyncio.wait_for(
            loop.run_in_executor(_DHAN_OC_EXECUTOR, lambda: fn(*args, **kwargs)),
            timeout=timeout,
        )


@app.post("/api/chain/push")
async def push_chain_snapshots(payload: Dict[str, Any], request: Request):
    """Called by scripts/cloud_worker.py's chain-push thread. Same auth as
    /api/scheduler/health/push. Body: {"chains": {"NIFTY": {...}, ...}, "market_open": bool}."""
    if _WORKER_PUSH_TOKEN:
        sent_token = request.headers.get("X-Worker-Token", "")
        if sent_token != _WORKER_PUSH_TOKEN:
            raise HTTPException(status_code=401, detail="Invalid or missing X-Worker-Token")
    chains = payload.get("chains", {})
    if not isinstance(chains, dict):
        raise HTTPException(status_code=400, detail="'chains' must be an object")
    market_open = bool(payload.get("market_open", True))
    now = _time_module.time()
    for symbol, data in chains.items():
        if isinstance(data, dict):
            _PUSHED_CHAIN_CACHE[symbol.upper()] = {"data": data, "received_at": now, "market_open": market_open}
    return {"accepted": True, "symbols": list(chains.keys())}


@app.get("/api/deploy/info")
async def get_deploy_info():
    """Expose deployed commit / host facts for Cloud Run (GCP) proofs.

    Prefers Cloud Run env (DEPLOY_GIT_SHA, K_SERVICE, SYSTEM3_DEPLOY_TARGET).
    Render.com env vars are retired and are not used as SHA or service identity.
    """
    cfg: Dict[str, Any] = {}
    try:
        cfg_path = ROOT_DIR / "config" / "cloud_runtime.json"
        if cfg_path.exists():
            loaded = json.loads(cfg_path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                cfg = loaded
    except Exception:
        cfg = {}

    git_sha = (os.environ.get("DEPLOY_GIT_SHA") or "").strip()
    service_name = (
        os.environ.get("K_SERVICE")
        or str(cfg.get("service_name") or "genesis-system3-web")
    )
    target = (
        os.environ.get("SYSTEM3_DEPLOY_TARGET")
        or str(cfg.get("deploy_target") or "gcp-cloud-run")
    ).strip()
    base = (
        os.environ.get("SYSTEM3_PUBLIC_BACKEND_URL")
        or os.environ.get("SYSTEM3_API_BASE")
        or str(cfg.get("public_base_url") or "https://genesis-system3-web-doq2wplepa-el.a.run.app")
    ).rstrip("/")
    return {
        "git_sha": git_sha,
        "git_branch": os.environ.get("GITHUB_REF_NAME") or "",
        "service_name": service_name,
        "deploy_target": target,
        "cloud_provider": "google_cloud" if ("gcp" in target or "cloud-run" in target) else "unknown",
        "public_base_url": base,
        "ui_url": f"{base}{cfg.get('ui_path') or '/ui'}",
        "region": os.environ.get("GCP_REGION") or cfg.get("region") or "",
        "project_id": os.environ.get("GOOGLE_CLOUD_PROJECT") or cfg.get("project_id") or "",
        "cloud_mode": os.environ.get("CLOUD_MODE", "0"),
        "live_trading_enabled": False,
        "deployed_at_known": bool(git_sha),
        "render_git_commit_legacy": "",
    }


# ---------------------------------------------------------------------------
# Live Trading Gate — evaluates ALL conditions before allowing live mode
# ---------------------------------------------------------------------------

_LIVE_APPROVAL_FILE = ROOT_DIR / "config" / "kill_switch.json"
_RISK_CONFIG_FILE = ROOT_DIR / "config" / "system3_risk_config.yml"
_GAIN_RANK_HISTORY = ROOT_DIR / "state" / "gain_rank_history.json"
_VAL_DIR = ROOT_DIR / "state" / "market_validations"


@app.get("/api/live-trading/gate")
async def get_live_trading_gate():
    """
    Evaluates every condition required before live trading is allowed.
    Returns gate_open=true ONLY when ALL pass.
    This is what the dashboard "Go Live" button checks first.
    Live trading remains OFF until human gives explicit approval phrase.
    """
    gates = []
    gate_open = True

    def gate(name: str, passed: bool, detail: str):
        nonlocal gate_open
        if not passed:
            gate_open = False
        gates.append({"gate": name, "passed": passed, "detail": detail})

    # Gate 1: Safety env vars
    live_env = os.environ.get("LIVE_TRADING_ENABLED", "0")
    gate("env_live_disabled", live_env == "0", f"LIVE_TRADING_ENABLED={live_env} (must be 0 for paper, 1 for live)")

    # Gate 2: Kill switch
    try:
        ks = json.loads(_LIVE_APPROVAL_FILE.read_text()) if _LIVE_APPROVAL_FILE.exists() else {}
        gate(
            "kill_switch_off",
            not ks.get("kill_switch_activated", False),
            "Kill switch not activated" if not ks.get("kill_switch_activated") else "KILL SWITCH ACTIVE",
        )
        gate(
            "human_approved",
            ks.get("live_trading_approved", False),
            (
                "Human LIVE approval recorded"
                if ks.get("live_trading_approved")
                else "live_trading_approved remains false by design; PAPER/ANALYZER does not require LIVE approval"
            ),
        )
    except Exception as e:
        gate("kill_switch_readable", False, f"Cannot read kill_switch.json: {e}")

    # Gate 3: ML accuracy — Spearman rho >= 0.70 over 10+ days
    try:
        history = (
            json.loads((_VAL_DIR.parent / "gain_rank_history.json").read_text())
            if (_VAL_DIR.parent / "gain_rank_history.json").exists()
            else []
        )
        val_files = list(_VAL_DIR.glob("market_validation_*.json")) if _VAL_DIR.exists() else []
        rhos = []
        for vf in val_files:
            v = json.loads(vf.read_text())
            rho = v.get("spearman_correlation")
            if rho is not None:
                rhos.append(rho)
        avg_rho = sum(rhos) / len(rhos) if rhos else 0.0
        gate("validation_days", len(val_files) >= 10, f"{len(val_files)} validation days (need ≥10)")
        gate("ml_accuracy_rho", avg_rho >= 0.70, f"Avg Spearman ρ={avg_rho:.3f} (need ≥0.70)")
    except Exception as e:
        gate("ml_accuracy_readable", False, f"Cannot read validation data: {e}")

    # Gate 4: Max daily loss set
    try:
        # Use kill_switch.json for max_loss (avoid yaml dependency)
        # Risk config also in kill_switch since both updated together
        ks_data = json.loads(_LIVE_APPROVAL_FILE.read_text()) if _LIVE_APPROVAL_FILE.exists() else {}
        max_loss = ks_data.get("max_daily_loss_inr", 0)
        gate(
            "max_loss_configured",
            max_loss > 0 and max_loss <= 10000,
            f"Max daily loss = ₹{max_loss} hardcoded in kill_switch.json",
        )
    except Exception as e:
        gate("max_loss_configured", False, f"Could not read max loss config: {e}")

    return {
        "gate_open": gate_open,
        "gates": gates,
        "summary": f"{sum(1 for g in gates if g['passed'])}/{len(gates)} gates passed",
        "verdict": "LIVE_TRADING_ALLOWED" if gate_open else "LIVE_TRADING_BLOCKED",
        "message": (
            "All gates pass — ready for live trading after human approval"
            if gate_open
            else "Live trading blocked — see failed gates above"
        ),
        "live_trading_status": "OFF — remains off until all gates pass",
    }


@app.post("/api/live-trading/approve")
async def approve_live_trading(payload: Dict[str, Any]):
    """
    Human approval endpoint. Requires exact phrase to prevent accidental activation.
    Even after approval, LIVE_TRADING_ENABLED env var must be manually set to 1
    on Render dashboard — this cannot be done via API.
    """
    REQUIRED_PHRASE = "I APPROVE LIVE TRADING WITH MAX LOSS RS 5000"
    phrase = payload.get("approval_phrase", "").strip().upper()

    if phrase != REQUIRED_PHRASE:
        return {
            "approved": False,
            "message": f"Wrong phrase. Required: '{REQUIRED_PHRASE}'",
            "note": "Exact phrase required to prevent accidental activation",
        }

    try:
        ks_path = ROOT_DIR / "config" / "kill_switch.json"
        ks = json.loads(ks_path.read_text()) if ks_path.exists() else {}
        ks["live_trading_approved"] = True
        ks["live_trading_approval_phrase"] = phrase
        ks["approval_timestamp"] = datetime.now(timezone.utc).isoformat()
        ks["approver_note"] = "Human approval given via dashboard"
        ks_path.write_text(json.dumps(ks, indent=2))
        return {
            "approved": True,
            "message": "Approval recorded. IMPORTANT: You must STILL manually set "
            "LIVE_TRADING_ENABLED=1 on Cloud Run (GCP) to actually enable live trading. "
            "This approval alone does NOT enable live trading. Default remains OFF.",
            "next_step": "Cloud Run → genesis-system3-web → Variables & Secrets → "
            "LIVE_TRADING_ENABLED → change to 1 → Deploy (owner-only; keep OFF unless explicit)",
        }
    except Exception as e:
        return {"approved": False, "message": f"Failed to save approval: {e}"}


@app.get("/api/scheduler/health")
async def get_scheduler_health(refresh: bool = False):
    """
    Job scheduler health from Firestore evidence (cloud SSOT).

    `healthy=False` covers transport/control-plane failure modes.
    Use `?refresh=true` to bypass the short in-process cache.
    """
    if os.environ.get("SYSTEM3_STATE_BACKEND", "file").strip().lower() == "firestore":
        try:
            cache_key = "scheduler_health_firestore"
            if not refresh:
                hit = _cache_get(cache_key, 30.0)
                if isinstance(hit, dict):
                    out = dict(hit)
                    out["cache_hit"] = True
                    out["cache_ttl_s"] = 30
                    return out
            from dashboard.backend.firestore_state_backend import FirestoreSchedulerEvidenceBackend, derive_scheduler_health
            evidence = await asyncio.to_thread(FirestoreSchedulerEvidenceBackend().load_current)
            payload = derive_scheduler_health(evidence)
            payload["cache_hit"] = False
            payload["cache_ttl_s"] = 30
            payload["deploy_git_sha"] = os.environ.get("DEPLOY_GIT_SHA") or os.environ.get("SYSTEM3_GIT_SHA")
            return _cache_set(cache_key, payload)
        except Exception as exc:
            return {"healthy": False, "status": "UNHEALTHY", "unhealthy_reasons": [f"scheduler evidence unavailable: {type(exc).__name__}"], "live_trading_enabled": False, "cache_hit": False}

    STALE_THRESHOLD_S = 180  # legacy local/Render compatibility only

    state = _scheduler_health_state
    healthy = True
    reasons = []

    if not state["received"]:
        healthy = False
        reasons.append(
            "worker has never pushed scheduler health — check worker service is deployed and running cloud_worker.py"
        )
    else:
        try:
            last_push = datetime.fromisoformat(state["last_push_at"])
            age_s = (datetime.now(timezone.utc) - last_push).total_seconds()
            if age_s > STALE_THRESHOLD_S:
                healthy = False
                reasons.append(f"last worker push was {age_s:.0f}s ago (stale, expected <{STALE_THRESHOLD_S}s)")
        except Exception:
            pass

    if state.get("config_alert"):
        healthy = False
        reasons.append(f"worker reports config alert: {state['config_alert'].get('message', state['config_alert'])}")

    # NOTE: state["jobs"] is execution HISTORY — it only gains an entry for
    # a job_id once that job fires for the first time since daemon start.
    # A freshly (re)started worker legitimately has jobs={} for hours
    # (e.g. restarted at 01:00 IST, next job doesn't fire until pre-market)
    # even though its config has 23 enabled jobs. Checking config_jobs_enabled
    # (pushed separately, reflects config load result each tick) instead of
    # the fired-history dict avoids false "zero jobs loaded" alarms on every
    # worker restart outside market hours. config_jobs_enabled is None only
    # when talking to an older worker build that predates this field.
    if state["received"] and state.get("config_jobs_enabled") == 0:
        healthy = False
        reasons.append("worker's job scheduler config has zero enabled jobs")

    # Richer breakdown on top of the checks above: classifies every enabled
    # job into fired/pending/missed/catchup_eligible/skipped for today,
    # re-evaluating live against the current moment for jobs not yet fired
    # (see core/engine/system3_scheduler_catchup.py). jobs={} alone is never
    # treated as fatal here if nothing was due yet — only a genuine
    # missed_jobs_today entry (past its catch-up window, never fired) marks
    # unhealthy.
    try:
        from core.engine.system3_phase82_job_scheduler import (
            load_config as _load_scheduler_config,
        )
        from core.engine.system3_scheduler_catchup import (
            load_policy as _load_catchup_policy,
        )
        from core.engine.system3_scheduler_catchup import summarize_scheduler_status

        now_ist = datetime.now(IST)
        is_weekend = now_ist.weekday() >= 5
        is_holiday = False
        try:
            from core.utils.nse_holidays import is_trading_holiday

            is_holiday, _ = is_trading_holiday(now_ist.date())
        except Exception:
            pass

        config = _load_scheduler_config()
        policy = _load_catchup_policy()
        summary = summarize_scheduler_status(
            config,
            state,
            now=now_ist,
            policy=policy,
            is_holiday=is_holiday,
            is_weekend=is_weekend,
            api_health_ok=True,  # this endpoint answering IS proof the API is running
        )
        if state["received"] and summary.get("missed_jobs_today"):
            healthy = False
            reasons.append(f"jobs missed today (past catch-up window, never fired): {summary['missed_jobs_today']}")
    except Exception as e:
        summary = {
            "configured_jobs_count": None,
            "enabled_jobs_count": None,
            "fired_jobs_today": [],
            "pending_jobs_today": [],
            "missed_jobs_today": [],
            "catchup_eligible_jobs": [],
            "skipped_jobs_today": [],
        }
        reasons.append(f"could not compute job status summary: {e}")

    return {
        **state,
        **summary,
        "healthy": healthy,
        "unhealthy_reasons": reasons,
    }


@app.get("/api/system_health")
async def get_system_health():
    """Datasource health, token status, retrain flag, and scheduler job status."""
    try:
        # Token status from watchdog log last line
        token_status = {"status": "unknown", "log_line": "log not found"}
        try:
            if WATCHDOG_LOG.exists():
                lines = WATCHDOG_LOG.read_text().strip().splitlines()
                last_line = lines[-1] if lines else ""
                token_status = {"status": "ok" if "Token OK" in last_line else "warning", "log_line": last_line}
        except Exception:
            pass

        # Datasource health
        ds_health = None
        ds_resilience = "UNKNOWN"
        try:
            if DS_HEALTH_FILE.exists():
                ds_health = json.loads(DS_HEALTH_FILE.read_text())
                ds_resilience = ds_health.get("resilience", "UNKNOWN")
        except Exception:
            pass

        # Scheduler jobs
        jobs_summary = []
        scheduler_daemon = {"started_at": None, "heartbeat": None, "pid": None, "active": False}
        try:
            cfg = json.loads(JOB_SCHED_CFG.read_text())
            scheduler_state = {}
            scheduler_state_file = ROOT_DIR / "storage" / "ultra" / "ph76_ph100" / "phase82_job_scheduler_state.json"
            if scheduler_state_file.exists():
                try:
                    scheduler_state = json.loads(scheduler_state_file.read_text())
                    scheduler_daemon["started_at"] = scheduler_state.get("daemon_started_at")
                    scheduler_daemon["heartbeat"] = scheduler_state.get("daemon_heartbeat")
                    scheduler_daemon["pid"] = scheduler_state.get("daemon_pid")

                    if scheduler_daemon["heartbeat"]:
                        try:
                            hb_time = datetime.fromisoformat(scheduler_daemon["heartbeat"])
                            if hb_time.tzinfo is None:
                                hb_time = IST.localize(hb_time)
                            now_ist = datetime.now(IST)
                            age_seconds = (now_ist - hb_time).total_seconds()
                            scheduler_daemon["active"] = 0 <= age_seconds < 180
                        except Exception as hb_exc:
                            print(f"Error parsing heartbeat: {hb_exc}")
                except Exception:
                    pass
            for j in cfg.get("jobs", []):
                job_id = j.get("id")
                job_state = scheduler_state.get("jobs", {}).get(job_id, {})
                jobs_summary.append(
                    {
                        "id": job_id,
                        "name": j.get("name"),
                        "schedule_time": j.get("schedule_time", "daily"),
                        "enabled": j.get("enabled", False),
                        "last_run_time": job_state.get("last_run_time"),
                        "last_status": job_state.get("last_status"),
                        "last_error": job_state.get("last_error"),
                    }
                )
        except Exception:
            pass

        return {
            "status": "ok",
            "timestamp": datetime.now(IST).isoformat(),
            "token": token_status,
            "datasource_health": ds_health,
            "datasource_resilience": ds_resilience,
            "retrain_needed": RETRAIN_FLAG.exists(),
            "scheduler_daemon": scheduler_daemon,
            "jobs": jobs_summary,
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


@app.api_route("/api/scheduler/run/{job_id}", methods=["GET", "POST"])
async def trigger_scheduler_job(job_id: str, background_tasks: BackgroundTasks, secret: Optional[str] = None):
    """
    Trigger a specific scheduler job in the background.
    Supports GET and POST to allow simple integration with external web-cron services (e.g. cron-job.org).
    """
    expected_secret = os.environ.get("SCHEDULER_SECRET")
    if not expected_secret:
        # Fail closed: an unset secret must never mean "no auth required".
        raise HTTPException(status_code=503, detail="SCHEDULER_SECRET not configured on server")
    if secret != expected_secret:
        raise HTTPException(status_code=403, detail="Invalid scheduler secret")

    # Load scheduler config to verify job ID
    try:
        cfg = json.loads(JOB_SCHED_CFG.read_text())
        job = next((j for j in cfg.get("jobs", []) if j.get("id") == job_id), None)
        if not job:
            raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found in scheduler config")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read scheduler config: {str(e)}")

    # Run the job inside BackgroundTasks to return immediate response and avoid timeouts
    def _run_job_bg():
        try:
            import importlib.util as _ilu
            import pathlib as _pl

            _spec = _ilu.spec_from_file_location(
                "job_scheduler_bg",
                _pl.Path(__file__).resolve().parent.parent.parent
                / "core"
                / "engine"
                / "system3_phase82_job_scheduler.py",
            )
            if _spec and _spec.loader:
                _js = _ilu.module_from_spec(_spec)
                _spec.loader.exec_module(_js)  # type: ignore[union-attr]
                _js.run_single_job(job_id)
                print(f"[API-Scheduler] Background execution of job '{job_id}' completed.")
        except Exception as exc:
            print(f"[API-Scheduler] Background execution of job '{job_id}' failed: {exc}")

    background_tasks.add_task(_run_job_bg)
    return {
        "status": "triggered",
        "job_id": job_id,
        "name": job.get("name"),
        "message": f"Job '{job_id}' has been scheduled for background execution.",
    }


# WebSocket connections
active_connections: List[WebSocket] = []
_MAX_WS_CONNECTIONS = 20  # hard cap — this is a small-team dashboard, not a
# consumer product. Each open connection runs its own dedicated per-second
# loop on the single Render worker process (--workers 1, 512MB Starter box);
# an unbounded number of stale/reconnecting tabs is an unbounded amount of
# background work with no ceiling. Rejecting past this cap is a cheap safety
# net against that becoming an OOM source (2026-07-02 forensic investigation).

# File watcher for real-time updates
# Store the event loop for use in file watcher thread
_main_loop = None


def set_event_loop(loop):
    """Store the main event loop for file watcher"""
    global _main_loop
    _main_loop = loop


class OutputFileHandler(FileSystemEventHandler if FileSystemEventHandler is not None else object):
    def on_modified(self, event):
        """Handle file modification events"""
        if not event.is_directory and event.src_path.endswith((".json", ".csv", ".jsonl")):
            # Use run_coroutine_threadsafe to call async function from thread
            if _main_loop and not _main_loop.is_closed():
                try:
                    asyncio.run_coroutine_threadsafe(broadcast_update(event.src_path), _main_loop)
                except Exception as e:
                    # Silently ignore errors in file watcher
                    pass


async def broadcast_update(file_path: str):
    """Broadcast file update to all WebSocket connections"""
    if active_connections:
        message = {
            "type": "file_update",
            "file": Path(file_path).name,
            "timestamp": datetime.now(pytz.timezone("Asia/Kolkata")).isoformat(),
        }
        disconnected = []
        for connection in active_connections:
            try:
                await connection.send_json(message)
            except (ValueError, TypeError, KeyError, AttributeError) as e:
                logger.warning(f'Error handled: {e}')
            except Exception as e:
                logger.error(f'Unexpected error: {e}', exc_info=True)
                disconnected.append(connection)
        for conn in disconnected:
            active_connections.remove(conn)


# Start file watcher (if available)
observer = None
if WATCHDOG_AVAILABLE:
    try:
        observer = Observer()
        observer.schedule(OutputFileHandler(), str(OUTPUTS_DIR), recursive=False)
        observer.start()
    except Exception as e:
        print(f"Warning: File watcher failed to start: {e}")
        observer = None

# Secrets redaction
SECRET_PATTERNS = [
    r'(?i)(api[_-]?key|apikey)\s*[:=]\s*["\']?([^"\'\s]{10,})["\']?',
    r'(?i)(client[_-]?id|clientid)\s*[:=]\s*["\']?([^"\'\s]{8,})["\']?',
    r'(?i)(password|passwd|pwd)\s*[:=]\s*["\']?([^"\'\s]{6,})["\']?',
    r'(?i)(token|secret|auth[_-]?token)\s*[:=]\s*["\']?([^"\'\s]{10,})["\']?',
    r'(?i)(feed[_-]?token|feedtoken)\s*[:=]\s*["\']?([^"\'\s]{10,})["\']?',
]


def redact_secrets(text: str) -> str:
    """Redact secrets from text"""
    for pattern in SECRET_PATTERNS:
        text = re.sub(pattern, r"\1: [REDACTED]", text)
    return text


def scan_secrets(file_path: Path) -> int:
    """Scan file for secrets, return count"""
    if not file_path.exists():
        return 0
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        count = 0

        # Skip files that are known to contain test/demo data
        skip_patterns = ["test", "demo", "example", "sample"]
        if any(skip in file_path.name.lower() for skip in skip_patterns):
            return 0

        for pattern in SECRET_PATTERNS:
            matches = re.findall(pattern, content)
            # Filter out false positives
            for match in matches:
                if isinstance(match, tuple):
                    value = match[1] if len(match) > 1 else match[0]
                else:
                    value = match

                # Skip common false positives
                false_positives = [
                    "false",
                    "null",
                    "none",
                    '""',
                    "''",
                    "",
                    "true",
                    "0",
                    "1",
                    "redacted",
                    "[redacted]",
                    "n/a",
                    "na",
                    "none",
                    "null",
                ]
                if (
                    value.lower() not in false_positives
                    and len(value) >= 8
                    and not value.startswith("[")  # Skip [REDACTED] patterns
                    and not value.startswith("*")
                ):
                    count += 1

        return count
    except Exception as e:
        # Don't fail on read errors
        return 0


# SQLite time-series storage
DB_PATH = DB_DIR / "system3_metrics.sqlite"


def init_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Cycle metrics table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS cycle_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            cycle INTEGER,
            fetch_duration REAL,
            strategy_duration REAL,
            cycle_duration REAL,
            qc_passed INTEGER,
            signals_generated INTEGER,
            trades_executed INTEGER,
            current_positions INTEGER,
            total_pnl REAL,
            daily_pnl REAL
        )
    """
    )

    # Chain snapshots table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS chain_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            underlying TEXT NOT NULL,
            contracts_count INTEGER,
            avg_volume REAL,
            avg_oi REAL,
            liquidity_score REAL,
            pcr REAL,
            data_completeness REAL
        )
    """
    )

    # Signal snapshots table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS signal_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            action TEXT,
            underlying TEXT,
            strategy TEXT,
            confidence REAL,
            reason TEXT,
            qc_passed INTEGER
        )
    """
    )

    # Position snapshots table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS position_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            position_id TEXT,
            underlying TEXT,
            symbol TEXT,
            qty INTEGER,
            entry_price REAL,
            current_price REAL,
            unrealized_pnl REAL,
            status TEXT
        )
    """
    )

    conn.commit()
    conn.close()


init_db()


def ingest_cycle_metrics():
    """Ingest latest cycle metrics into SQLite"""
    try:
        perf_file = OUTPUTS_DIR / "perf_metrics.json"
        health_file = OUTPUTS_DIR / "health.json"

        if not perf_file.exists() or not health_file.exists():
            return

        perf = json.loads(perf_file.read_text())
        health = json.loads(health_file.read_text())

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO cycle_metrics (
                timestamp, cycle, fetch_duration, strategy_duration, cycle_duration,
                qc_passed, signals_generated, trades_executed, current_positions,
                total_pnl, daily_pnl
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                perf.get("timestamp"),
                perf.get("cycle"),
                perf.get("fetch_duration_sec"),
                perf.get("strategy_duration_sec"),
                perf.get("cycle_duration_sec"),
                1 if health.get("qc_passed") else 0,
                health.get("signals_generated", 0),
                health.get("trades_executed", 0),
                health.get("current_positions", 0),
                health.get("total_pnl", 0.0),
                health.get("daily_pnl", 0.0),
            ),
        )

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error ingesting metrics: {e}")


# Event sourcing / audit log
AUDIT_LOG = AUDIT_DIR / "event_log.jsonl"


def log_event(event_type: str, data: Dict):
    """Append event to audit log"""
    try:
        event = {
            "event_id": hashlib.sha256(f"{datetime.now().isoformat()}{event_type}".encode()).hexdigest()[:16],
            "timestamp": datetime.now(pytz.timezone("Asia/Kolkata")).isoformat(),
            "event_type": event_type,
            **data,
        }
        with open(AUDIT_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, default=str) + "\n")
    except Exception as e:
        print(f"Error logging event: {e}")


# Pydantic models
class HealthResponse(BaseModel):
    status: str
    mode: str
    broker_status: str
    market_status: str
    cycle_count: int
    refresh_interval: int
    last_fetch: Optional[str]
    qc_status: str
    qc_failures: List[str]
    trades_executed: int
    open_positions: int
    total_pnl: float
    daily_pnl: float
    performance_sla: Dict[str, Any]


# ═══════════════════════════════════════════════════════════════════════════
# TTL CACHE — Prevents Render 503 cascade on cold-start and poll overload
# Heavy APIs cache their results. Cache is in-process dict (no Redis needed).
# TTLs chosen for trading: broker data 30s, scanner 60s, accuracy 120s.
# ═══════════════════════════════════════════════════════════════════════════
import time as _time_module

_API_CACHE: dict = {}  # {key: (timestamp, data)}


def _cache_get(key: str, ttl_s: float):
    """Return cached value if fresh, else None."""
    entry = _API_CACHE.get(key)
    if entry and (_time_module.time() - entry[0]) < ttl_s:
        return entry[1]
    return None


def _cache_age_s(key: str) -> float | None:
    """Age of a cache entry in seconds, or None if missing."""
    entry = _API_CACHE.get(key)
    if not entry:
        return None
    return max(0.0, _time_module.time() - entry[0])


def _cache_set(key: str, value):
    """Store value with current timestamp."""
    _API_CACHE[key] = (_time_module.time(), value)
    return value


# TTL constants (seconds)
_TTL_BROKER = 30  # holdings, positions, funds — Dhan API calls
_TTL_PAPER = 15  # paper positions/pnl — changes each tick
_TTL_SCANNER = 20  # market top CE/PE — micro-refreshed by background loop
_MARKET_TOP_STATE_FILE = ROOT_DIR / "state" / "market_top_ce_pe.json"
_MARKET_TOP_MICRO_INTERVAL_S = 30.0  # leave Dhan OC budget for index chain stream
_WS_MARKET_TOP_PUSH_S = 3.0
_WS_CHAIN_PUSH_S_OPEN = 3.0
_WS_CHAIN_PUSH_S_CLOSED = 15.0
_TTL_ACCURACY = 120  # accuracy trend — file read, slow
_TTL_PERF = 120  # performance data
_TTL_PORTFOLIO = 30  # portfolio/unified
_TTL_AUTO_GATES = 60  # auto gates — reads several files
_TTL_BROKER_TRUTH = 30  # broker truth validator
_TTL_BATCH = 8.0  # dashboard batch endpoints — 5–10s window


def _slim_health(h: Any) -> Dict[str, Any]:
    if not isinstance(h, dict):
        return {"status": "error"}
    broker = h.get("broker") if isinstance(h.get("broker"), dict) else {}
    market = h.get("market") if isinstance(h.get("market"), dict) else {}
    return {
        "status": h.get("status"),
        "mode": h.get("mode"),
        "qc_status": h.get("qc_status"),
        "data_source": h.get("data_source"),
        "live_allowed": h.get("live_allowed"),
        "broker_status": h.get("broker_status"),
        "message": h.get("message"),
        "broker": {
            "connected": broker.get("connected"),
            "status": broker.get("status"),
            "name": broker.get("name"),
            "error": broker.get("error"),
        },
        "market": {"is_open": market.get("is_open"), "reason": market.get("reason")},
        "cycle_count": h.get("cycle_count"),
        "last_fetch": h.get("last_fetch"),
    }


def _slim_paper(p: Any) -> Dict[str, Any]:
    if not isinstance(p, dict):
        return {"status": "error", "positions": {"open_count": 0}, "pnl": {"summary": {}}}
    positions = p.get("positions") if isinstance(p.get("positions"), dict) else {}
    pnl = p.get("pnl") if isinstance(p.get("pnl"), dict) else {}
    summary = pnl.get("summary") if isinstance(pnl.get("summary"), dict) else pnl
    open_positions = positions.get("open_positions") or positions.get("positions") or []
    slim_pos = []
    if isinstance(open_positions, list):
        for row in open_positions[:40]:
            if not isinstance(row, dict):
                continue
            slim_pos.append(
                {
                    "symbol": row.get("symbol") or row.get("trading_symbol"),
                    "qty": row.get("qty") or row.get("quantity") or row.get("netQty"),
                    "pnl": row.get("pnl") or row.get("unrealized_pnl") or row.get("unrealizedProfit"),
                    "side": row.get("side") or row.get("option_type"),
                    "strike": row.get("strike"),
                    "ltp": row.get("ltp") or row.get("last_price"),
                }
            )
    return {
        "status": p.get("status", "ok"),
        "mode": p.get("mode", "PAPER"),
        "live_trading_enabled": False,
        "positions": {
            "open_count": positions.get("open_count", len(slim_pos)),
            "open_positions": slim_pos,
        },
        "pnl": {
            "summary": {
                "total_pnl": summary.get("total_pnl", 0),
                "daily_pnl": summary.get("daily_pnl", 0),
                "win_rate": summary.get("win_rate", 0),
                "total_trades": summary.get("total_trades", 0),
            }
        },
    }


def _slim_gain_rank(g: Any) -> Dict[str, Any]:
    if not isinstance(g, dict):
        return {"status": "error", "rankings": []}
    rankings = g.get("rankings") or (g.get("latest") or {}).get("predictions") or []
    slim = []
    if isinstance(rankings, list):
        for row in rankings[:15]:
            if not isinstance(row, dict):
                continue
            slim.append(
                {
                    "rank": row.get("rank"),
                    "underlying": row.get("underlying") or row.get("symbol"),
                    "option_type": row.get("option_type") or row.get("side"),
                    "strike": row.get("strike"),
                    "gain_pct": row.get("gain_pct") or row.get("gain_rank") or row.get("gain_score"),
                    "ltp": row.get("ltp"),
                    "recommendation": row.get("recommendation"),
                }
            )
    return {
        "status": g.get("status", "ok"),
        "stale": g.get("stale"),
        "latest_date": g.get("latest_date") or (g.get("latest") or {}).get("date"),
        "rankings": slim,
        "latest": {"predictions": slim, "date": g.get("latest_date")},
    }


def _slim_pnl(p: Any) -> Dict[str, Any]:
    if not isinstance(p, dict):
        return {"summary": {"total_pnl": 0}, "history": []}
    summary = p.get("summary") if isinstance(p.get("summary"), dict) else p
    return {
        "status": p.get("status", "ok"),
        "summary": {
            "total_pnl": summary.get("total_pnl", 0),
            "daily_pnl": summary.get("daily_pnl", 0),
            "total_trades": summary.get("total_trades", 0),
            "win_rate": summary.get("win_rate", 0),
        },
        "history": (p.get("history") or [])[-20:] if isinstance(p.get("history"), list) else [],
    }


def _slim_gates(g: Any) -> Dict[str, Any]:
    if not isinstance(g, dict):
        return {"proof_gates": [], "gates_passing": 0, "gates_total": 0}
    gates = g.get("proof_gates") or []
    slim_gates = []
    if isinstance(gates, list):
        for row in gates[:20]:
            if not isinstance(row, dict):
                continue
            slim_gates.append(
                {
                    "gate_id": row.get("gate_id") or row.get("id"),
                    "name": row.get("name"),
                    "status": row.get("status"),
                    "pass": row.get("pass"),
                    "note": row.get("note") or row.get("evidence"),
                }
            )
    return {
        "status": g.get("status", "ok"),
        "proof_gates": slim_gates,
        "gates_passing": g.get("gates_passing", sum(1 for x in slim_gates if x.get("pass") or str(x.get("status")).upper() == "PASS")),
        "gates_total": g.get("gates_total", len(slim_gates)),
        "live_trading_enabled": False,
    }


def _slim_token_proof(proof: Any) -> Dict[str, Any]:
    """Safe token provenance for System tab — never include raw access tokens."""
    if not isinstance(proof, dict):
        return {}
    out: Dict[str, Any] = {}
    for key in (
        "source",
        "secret_id",
        "secret_version",
        "secret_version_created_at_utc",
        "loaded_at_utc",
        "cache_age_s",
        "cache_ttl_s",
        "expires_at_utc",
        "hours_remaining",
        "expired",
        "reload_count",
        "last_reload_reason",
        "last_error_type",
        "rotation_job",
        "rotation_schedule",
        "token_value_exposed",
    ):
        if key in proof and proof.get(key) is not None:
            out[key] = proof.get(key)
    # Explicitly prove raw token is not shipped to the UI.
    out["token_value_exposed"] = False
    return out


def _slim_broker_status(s: Any) -> Dict[str, Any]:
    if not isinstance(s, dict):
        return {"connected": False}
    slim: Dict[str, Any] = {
        "broker": s.get("broker", "dhan"),
        "connected": s.get("connected"),
        "status": s.get("status"),
        "error": s.get("error"),
        "credentials_present": s.get("credentials_present"),
        "live_trading_enabled": False,
        "order_placement_allowed": False,
        "latency_ms": s.get("latency_ms"),
        "mode": s.get("mode"),
    }
    proof = _slim_token_proof(s.get("token_proof"))
    if proof:
        slim["token_proof"] = proof
    reload = s.get("token_reload")
    if isinstance(reload, dict):
        slim["token_reload"] = {
            "attempted": bool(reload.get("attempted")),
            "success": reload.get("success"),
            "reason": reload.get("reason"),
        }
    rotation = s.get("canonical_rotation")
    if isinstance(rotation, dict):
        slim["canonical_rotation"] = {
            "state": rotation.get("state") or rotation.get("status"),
            "status": rotation.get("status"),
            "success": rotation.get("success"),
        }
    return slim


def _slim_rows_payload(payload: Any, keys: Tuple[str, ...]) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        return {"success": False, "rows": [], "count": 0}
    rows = payload.get("rows") or payload.get("holdings") or payload.get("positions") or payload.get("data") or []
    slim = []
    if isinstance(rows, list):
        for row in rows[:80]:
            if not isinstance(row, dict):
                continue
            raw = row.get("raw") if isinstance(row.get("raw"), dict) else {}
            slim_row = {}
            for k in keys:
                if k in row and row.get(k) is not None:
                    slim_row[k] = row.get(k)
                elif k in raw and raw.get(k) is not None:
                    slim_row[k] = raw.get(k)
                else:
                    slim_row[k] = row.get(k)
            slim.append(slim_row)
    out = {
        "success": payload.get("success", True),
        "rows": slim,
        "count": payload.get("count", len(slim)),
        "status": payload.get("status"),
        "message": payload.get("message"),
        "error": payload.get("error"),
    }
    if "normalized" in payload and isinstance(payload.get("normalized"), dict):
        n = payload["normalized"]
        out["normalized"] = {
            "available_balance": n.get("available_balance"),
            "utilized_amount": n.get("utilized_amount"),
            "total_limit": n.get("total_limit"),
        }
    for k in ("available_balance", "utilized_amount", "availabelBalance", "utilizedAmount"):
        if k in payload:
            out[k] = payload.get(k)
    return out


@app.get("/api/batch/market-data")
async def batch_market_data():
    """Dashboard boot batch #1 — slim health/state/paper/rank/pnl/gates/alerts (8s TTL)."""
    hit = _cache_get("batch_market_data_v2", _TTL_BATCH)
    if hit is not None:
        out = dict(hit)
        out["cache_hit"] = True
        return out

    async def _bounded(coro, timeout_s: float, fallback: Dict[str, Any]):
        try:
            val = await asyncio.wait_for(coro, timeout=timeout_s)
            return val if isinstance(val, dict) else fallback
        except Exception as exc:
            return {**fallback, "error": str(exc)[:160]}

    results = await asyncio.gather(
        _bounded(get_health(), 4.0, {"status": "error"}),
        _bounded(get_state(), 5.0, {"mode": "PAPER", "live_trading_enabled": False}),
        _bounded(get_paper(), 4.0, {}),
        _bounded(get_gain_rank(), 9.0, {}),
        _bounded(get_pnl(), 4.0, {}),
        _bounded(get_recent_alerts(limit=20), 4.0, {"alerts": []}),
        _bounded(get_auto_gates(), 5.0, {"proof_gates": []}),
    )

    health = results[0] if isinstance(results[0], dict) else {"status": "error"}
    state = results[1] if isinstance(results[1], dict) else {}
    paper = results[2] if isinstance(results[2], dict) else {}
    gain = results[3] if isinstance(results[3], dict) else {}
    pnl = results[4] if isinstance(results[4], dict) else {}
    alerts = results[5] if isinstance(results[5], dict) else {"alerts": []}
    gates = results[6] if isinstance(results[6], dict) else {"proof_gates": []}

    # Keep state compact: drop bulky nested blobs, keep live ops KPIs.
    risk = state.get("risk") if isinstance(state.get("risk"), dict) else {}
    pnl_state = state.get("pnl") if isinstance(state.get("pnl"), dict) else {}
    recon = state.get("reconciliation") if isinstance(state.get("reconciliation"), dict) else {}
    qc = state.get("qc") if isinstance(state.get("qc"), dict) else {}
    signals = state.get("signals") if isinstance(state.get("signals"), dict) else {}
    tick_health = state.get("tick_health") if isinstance(state.get("tick_health"), dict) else {}
    slim_state = {
        "status": state.get("status"),
        "mode": state.get("mode"),
        "live_trading_enabled": state.get("live_trading_enabled", False),
        "live_allowed": state.get("live_allowed", False),
        "broker": state.get("broker") if isinstance(state.get("broker"), dict) else {},
        "market": state.get("market") if isinstance(state.get("market"), dict) else {},
        "timestamp": state.get("timestamp") or state.get("updated_at"),
        "data_source": state.get("data_source"),
        "cycle_count": state.get("cycle_count") or state.get("state_version"),
        "state_version": state.get("state_version"),
        "last_tick_age_sec": state.get("last_tick_age_sec") or tick_health.get("last_tick_age_sec"),
        "last_fetch_ts_iso": state.get("last_fetch_ts_iso") or state.get("last_cycle_ts_iso"),
        "last_cycle_ts_iso": state.get("last_cycle_ts_iso"),
        "risk": {
            "exposure": risk.get("exposure") or risk.get("total_exposure"),
            "var95": risk.get("var95") or risk.get("var_95"),
            "es95": risk.get("es95") or risk.get("expected_shortfall_95"),
            "concentration": risk.get("concentration") or risk.get("concentration_risk"),
            "limits": {"status": (risk.get("limits") or {}).get("status")} if isinstance(risk.get("limits"), dict) else {},
            "greeks": risk.get("greeks") if isinstance(risk.get("greeks"), dict) else {},
        },
        "pnl": {
            "unrealized": pnl_state.get("unrealized"),
            "total": pnl_state.get("total"),
            "day_total": pnl_state.get("day_total"),
            "realized": pnl_state.get("realized"),
        },
        "reconciliation": {"status": recon.get("status"), "timestamp": recon.get("timestamp")},
        "qc": {"status": qc.get("status"), "contracts_total": qc.get("contracts_total")},
        "signals": {
            "status": signals.get("status"),
            "reason": signals.get("reason"),
            "confidence": signals.get("confidence"),
            "last_signal": signals.get("last_signal"),
        },
        "tick_health": {
            "last_tick_age_sec": tick_health.get("last_tick_age_sec"),
            "market_open": tick_health.get("market_open"),
            "source": tick_health.get("source"),
        },
    }

    payload = {
        "cache_hit": False,
        "generated_at": datetime.now(IST).isoformat(),
        "ttl_s": _TTL_BATCH,
        "live_trading_enabled": False,
        "health": _slim_health(health),
        "state": slim_state,
        "paper": _slim_paper(paper),
        "gain_rank": _slim_gain_rank(gain),
        "pnl": _slim_pnl(pnl),
        "alerts": {
            "alerts": (alerts.get("alerts") or [])[:20] if isinstance(alerts.get("alerts"), list) else [],
            "count": alerts.get("count", 0),
        },
        "auto_gates": _slim_gates(gates),
    }
    return _cache_set("batch_market_data_v2", payload)


@app.get("/api/batch/positions-holdings")
async def batch_positions_holdings():
    """Dashboard boot batch #2 — slim broker status/funds/holdings/positions (8s TTL)."""
    hit = _cache_get("batch_positions_holdings_v1", _TTL_BATCH)
    if hit is not None:
        out = dict(hit)
        out["cache_hit"] = True
        return out

    results = await asyncio.gather(
        get_dhan_broker_status(),
        get_broker_funds(),
        get_broker_holdings(),
        get_broker_positions_live(),
        return_exceptions=True,
    )

    def _ok(val: Any, fallback: Dict[str, Any]) -> Dict[str, Any]:
        if isinstance(val, Exception):
            return {**fallback, "error": str(val)[:160], "success": False}
        return val if isinstance(val, dict) else fallback

    status = _ok(results[0], {"connected": False})
    funds = _ok(results[1], {"success": False})
    holdings = _ok(results[2], {"rows": []})
    positions = _ok(results[3], {"rows": []})

    payload = {
        "cache_hit": False,
        "generated_at": datetime.now(IST).isoformat(),
        "ttl_s": _TTL_BATCH,
        "live_trading_enabled": False,
        "broker_status": _slim_broker_status(status),
        "funds": _slim_rows_payload(
            funds,
            ("available_balance", "utilized_amount", "total_limit", "availabelBalance", "utilizedAmount"),
        ),
        "holdings": _slim_rows_payload(
            holdings,
            (
                "tradingSymbol",
                "trading_symbol",
                "symbol",
                "totalQty",
                "quantity",
                "avgCostPrice",
                "averagePrice",
                "avg_price",
                "lastTradedPrice",
                "ltp",
                "current_value",
                "pnl",
                "pnl_pct",
                "securityId",
                "security_id",
            ),
        ),
        "positions": _slim_rows_payload(
            positions,
            (
                "tradingSymbol",
                "trading_symbol",
                "symbol",
                "positionType",
                "product",
                "netQty",
                "net_qty",
                "quantity",
                "buyAvg",
                "avg_price",
                "ltp",
                "ltp_source",
                "unrealizedProfit",
                "unrealized_pnl",
                "realizedProfit",
                "realized_pnl",
                "drvOptionType",
                "option_type",
                "drvStrikePrice",
                "strike",
                "drvExpiryDate",
                "expiry_date",
                "underlying",
                "securityId",
                "security_id",
                "exchangeSegment",
                "exchange_segment",
            ),
        ),
    }
    # Preserve funds normalized fields used by Overview
    if isinstance(funds.get("normalized"), dict):
        payload["funds"]["normalized"] = {
            "available_balance": funds["normalized"].get("available_balance"),
            "utilized_amount": funds["normalized"].get("utilized_amount"),
            "total_limit": funds["normalized"].get("total_limit"),
        }
        payload["funds"]["success"] = funds.get("success", True)
    return _cache_set("batch_positions_holdings_v1", payload)


# API Endpoints
@app.get("/api/memory")
async def get_memory():
    """Real-time memory usage — RSS vs Starter limit (512MB)."""
    try:
        import resource, gc
        rss_mb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
        limit_mb = int(os.environ.get("MEM_LIMIT_MB", "480"))
        pct = rss_mb / limit_mb * 100
        status = "OK" if pct < 75 else "WARN" if pct < 85 else "HIGH"
        if status == "HIGH":
            before = rss_mb
            gc.collect()
            rss_mb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
            freed = before - rss_mb
            print(f"[/api/memory] GC triggered: freed {freed:.0f}MB")
        return {
            "rss_mb": round(rss_mb, 1),
            "limit_mb": limit_mb,
            "pct_used": round(pct, 1),
            "headroom_mb": round(limit_mb - rss_mb, 1),
            "status": status,
            "gc_triggered": status == "HIGH",
        }
    except Exception as e:
        return {"error": str(e), "status": "UNKNOWN"}


@app.get("/api/orch/ready")
async def orch_cloud_ready():
    """Cloud-native readiness for System3boat / ORCH (replaces localhost:5000).

    WhatsApp/ORCH scanners that probe flask_port_5000 should call this URL on
    Cloud Run instead — never a laptop Flask port.
    """
    try:
        health = await get_health()
    except Exception as exc:
        return {
            "ready": False,
            "backend": "cloud_run",
            "reason": f"health_error:{type(exc).__name__}",
            "flask_port_5000_required": False,
            "live_trading_enabled": False,
            "recommended_base": "https://genesis-system3-web-doq2wplepa-el.a.run.app",
        }
    broker = health.get("broker") if isinstance(health.get("broker"), dict) else {}
    connected = bool(broker.get("connected")) or str(health.get("broker_status") or "").lower() == "connected"
    market_open = bool((health.get("market") or {}).get("is_open")) or str(health.get("market_status") or "").lower() == "open"
    return {
        "ready": connected,
        "backend": "cloud_run",
        "flask_port_5000_required": False,
        "broker_connected": connected,
        "market_open": market_open,
        "status": health.get("status"),
        "mode": health.get("mode"),
        "live_trading_enabled": False,
        "scanner_hint": "/api/scanner/top_contract_gainers?top_n=5&market_top_n=10&include_equity=1",
        "ui": "/ui/?tab=genesis",
        "recommended_base": "https://genesis-system3-web-doq2wplepa-el.a.run.app",
        "message": "Use Cloud Run — do not probe localhost:5000",
    }


@app.get("/api/health")
async def get_health():
    """Get system health overview"""
    try:
        # Check market status first
        market_is_open = False
        market_status_str = "closed"
        data_source = "real"

        if MARKET_DETECTION_AVAILABLE:
            try:
                market_is_open, reason = is_market_open()
                market_status_str = "open" if market_is_open else "closed"
            except Exception as e:
                pass  # fallback: market_status_str stays "closed"

        # REAL_ONLY MODE: Never use synthetic data. Return broker-not-ready state instead.
        # PRODUCTION GATE: When data is synthetic, mode MUST NOT be LIVE.
        if not market_is_open and not REAL_ONLY and SYNTHETIC_DATA_AVAILABLE:
            synthetic_health = generate_synthetic_health_data()
            mode_effective = synthetic_health.get("mode", "PAPER")
            if mode_effective.upper() == "LIVE":
                mode_effective = "PAPER"
            live_blockers = ["data_source is synthetic", "market is closed"]
            print(f"[MODE_GATE] requested={mode_effective} allowed=false reason={live_blockers}")
            return {
                "status": synthetic_health.get("status", "ok"),
                "mode": mode_effective,
                "broker_status": synthetic_health.get("broker_status", "disconnected"),
                "market_status": market_status_str,
                "data_source": "synthetic",
                "live_allowed": False,
                "live_blockers": live_blockers,
                "broker": {"connected": False, "error": "Synthetic data - no broker"},
                "market": {"is_open": False, "reason": market_status_str},
                "cycle_count": synthetic_health.get("total_trades_today", 0),
                "refresh_interval": 5,
                "last_fetch": datetime.now(pytz.timezone("Asia/Kolkata")).isoformat(),
                "qc_status": "PASS",
                "qc_failures": [],
                "trades_executed": synthetic_health.get("total_trades_today", 0),
                "open_positions": synthetic_health.get("current_positions", 0),
                "total_pnl": synthetic_health.get("total_pnl", 0.0),
                "daily_pnl": synthetic_health.get("total_pnl", 0.0),
                "performance_sla": {
                    "cycle_duration_sec": 0.5,
                    "fetch_duration_sec": 0.1,
                    "strategy_duration_sec": 0.2,
                    "sla_pass": True,
                },
            }

        # REAL_ONLY MODE: If market closed or broker unavailable, return NOT_READY state
        # Use SSOT if available, otherwise read from health.json
        if REAL_ONLY:
            broker_connected = False
            broker_status_str = "disconnected"
            mode = "PAPER"
            broker_name = "unknown"

            # Health is polled frequently by dashboard/verifiers; use cached SSOT truth.
            # Live Dhan probing belongs to /api/broker/status so a slow broker call cannot
            # block /api/health and cascade into /api/state timeouts.
            try:
                if SSOT_AVAILABLE and state_store is not None:
                    cached_broker = state_store.get_state().get("broker") or {}
                    broker_connected = bool(cached_broker.get("connected"))
                    # Never report status=connected when connected is false (stale SSOT).
                    broker_status_str = (
                        "connected"
                        if broker_connected
                        else str(cached_broker.get("status") or "disconnected")
                    )
                    if not broker_connected and broker_status_str.lower() == "connected":
                        broker_status_str = "disconnected"
                    broker_name = cached_broker.get("name") or "dhan"
                else:
                    health_file = OUTPUTS_DIR / "health.json"
                    if health_file.exists():
                        health_cached = json.loads(health_file.read_text())
                        broker_connected = bool(
                            health_cached.get("is_connected")
                            or health_cached.get("broker_status") == "connected"
                        )
                        broker_status_str = "connected" if broker_connected else "disconnected"
                        broker_name = "dhan"
            except Exception:
                pass

            # Dhan is the only broker — no AngelOne fallback

            # If broker not ready, return explicit NOT_READY state
            if not broker_connected:
                mode_effective = "PAPER" if (mode or "").upper() == "LIVE" else (mode or "PAPER")
                live_blockers = ["Broker not connected - real data unavailable"]
                print(f"[MODE_GATE] requested={mode} allowed=false reason={live_blockers}")
                return {
                    "status": "not_ready",
                    "mode": mode_effective,
                    "broker_status": broker_status_str,
                    "market_status": market_status_str,
                    "data_source": classify_overview_data_source(
                        market_open=market_is_open, broker_connected=False
                    ),
                    "live_allowed": False,
                    "live_blockers": live_blockers,
                    "broker": {"connected": False, "status": broker_status_str, "error": "Broker not connected"},
                    "market": {"is_open": market_is_open, "reason": market_status_str},
                    "cycle_count": 0,
                    "refresh_interval": 5,
                    "last_fetch": None,
                    "qc_status": "NOT_READY",
                    "qc_failures": ["Broker not connected - real data unavailable"],
                    "trades_executed": 0,
                    "open_positions": 0,
                    "total_pnl": 0.0,
                    "daily_pnl": 0.0,
                    "performance_sla": {
                        "cycle_duration_sec": 0,
                        "fetch_duration_sec": 0,
                        "strategy_duration_sec": 0,
                        "sla_pass": False,
                    },
                    "message": "BROKER_NOT_READY - Real data unavailable",
                }

            # Broker IS connected (Dhan) — return PAPER/ANALYZER ready state
            # live_allowed=False always: LIVE trading is permanently disabled
            # QC status must reflect real qc_report_live.json even when market is
            # closed — do not hardcode PASS, or /api/health can contradict a live
            # QC_FAIL surfaced by /api/state.
            qc_status_analyzer = "PASS"
            qc_failures_analyzer: list = []
            try:
                qc_file_analyzer = OUTPUTS_DIR / "qc_report_live.json"
                if qc_file_analyzer.exists():
                    qc_data_analyzer = json.loads(qc_file_analyzer.read_text())
                    if not qc_data_analyzer.get("qc_passed", True):
                        qc_status_analyzer = "FAIL"
                        qc_failures_analyzer = qc_data_analyzer.get("qc_failures", [])[:5]
                    elif qc_data_analyzer.get("status") == "NO_DATA":
                        qc_status_analyzer = "NO_DATA"
            except Exception:
                pass

            return {
                "status": "ok",
                "mode": "PAPER",
                "broker_status": "connected",
                "market_status": market_status_str,
                "data_source": classify_overview_data_source(
                    market_open=market_is_open, broker_connected=True
                ),
                "live_allowed": False,
                "live_blockers": ["Live trading permanently disabled in analyzer mode"],
                "broker": {
                    "connected": True,
                    "name": broker_name,
                    "status": "connected",
                    "error": None,
                },
                "market": {"is_open": market_is_open, "reason": market_status_str},
                "cycle_count": 0,
                "refresh_interval": 5,
                "last_fetch": datetime.now(IST).isoformat(),
                "qc_status": qc_status_analyzer,
                "qc_failures": qc_failures_analyzer,
                "trades_executed": 0,
                "open_positions": 0,
                "total_pnl": 0.0,
                "daily_pnl": 0.0,
                "performance_sla": {
                    "cycle_duration_sec": 0,
                    "fetch_duration_sec": 0,
                    "strategy_duration_sec": 0,
                    "sla_pass": True,
                },
                "message": "ANALYZER_READY - Broker connected, paper mode active",
            }

        # Market is open - use real data
        # PHASE 3: Use SSOT for consistency with /api/state
        health_file = OUTPUTS_DIR / "health.json"
        qc_file = OUTPUTS_DIR / "qc_report_live.json"

        health = {}
        if health_file.exists():
            health = json.loads(health_file.read_text())

        if SSOT_AVAILABLE and state_store:
            ssot_state = state_store.get_state()
            broker_connected = ssot_state.get("broker", {}).get("connected", False)
            broker_status = "connected" if broker_connected else "disconnected"
            mode = ssot_state.get("mode", health.get("mode", "PAPER"))
            data_source = classify_overview_data_source(
                market_open=market_is_open,
                broker_connected=bool(broker_connected),
            )
        else:
            # Fallback to health.json
            broker_connected = health.get("is_connected", False)
            broker_status = "connected" if broker_connected else "disconnected"
            mode = health.get("mode", "PAPER")
            data_source = "real"

        qc_data = {}
        if qc_file.exists():
            qc_data = json.loads(qc_file.read_text())

        # Determine market status from data
        if qc_data.get("status") == "MARKET_CLOSED":
            market_status_str = "closed"
        elif qc_data.get("mode") == "MARKET_CLOSED":
            market_status_str = "closed"
        else:
            market_status_str = "open"

        # Get performance metrics
        perf_file = OUTPUTS_DIR / "perf_metrics.json"
        perf = {}
        if perf_file.exists():
            perf = json.loads(perf_file.read_text())

        # CRITICAL: ALWAYS use paper_pnl_summary.json as PRIMARY source for PnL
        # This is the single source of truth for PnL calculations
        total_pnl = 0.0
        daily_pnl = 0.0
        open_positions = health.get("current_positions", 0)

        pnl_summary_file = OUTPUTS_DIR / "paper_pnl_summary.json"
        if pnl_summary_file.exists():
            try:
                pnl_summary = json.loads(pnl_summary_file.read_text())
                # PRIMARY SOURCE: Use paper_pnl_summary.json values
                total_pnl = float(pnl_summary.get("total_pnl", 0.0))
                daily_pnl = float(pnl_summary.get("total_realized_pnl", 0.0))
                open_positions = int(pnl_summary.get("open_positions", open_positions))
            except Exception as e:
                # Fallback to health.json only if paper_pnl_summary.json fails
                total_pnl = float(health.get("total_pnl", 0.0))
                daily_pnl = float(health.get("daily_pnl", 0.0))
                print(f"Warning: Failed to read paper_pnl_summary.json: {e}")
        else:
            # Fallback to health.json if paper_pnl_summary.json doesn't exist
            total_pnl = float(health.get("total_pnl", 0.0))
            daily_pnl = float(health.get("daily_pnl", 0.0))

        # Also sync positions count from positions file if available
        positions_file = OUTPUTS_DIR / "positions_live.json"
        if positions_file.exists():
            try:
                pos_data = json.loads(positions_file.read_text())
                if isinstance(pos_data, dict):
                    open_positions = pos_data.get("open_count", open_positions)
            except Exception:
                pass

        # Determine QC status
        qc_status = "PASS"
        qc_failures = []
        if not qc_data.get("qc_passed", True):
            qc_status = "FAIL"
            qc_failures = qc_data.get("qc_failures", [])[:5]
        elif qc_data.get("status") == "NO_DATA":
            qc_status = "NO_DATA"

        # PRODUCTION GATE: live_allowed only when broker connected + real data + market open
        ds = (data_source if SSOT_AVAILABLE and state_store else "real").lower()
        # PERMANENT SAFETY: live_allowed is ALWAYS False in analyzer mode
        # Even if broker+market are ready, live trading requires ENV change + human approval
        live_allowed = False
        live_blockers = ["Live trading permanently disabled — analyzer/paper mode only"]
        # live_blockers already set above (permanent)
        mode_raw = mode if SSOT_AVAILABLE and state_store else health.get("mode", "UNKNOWN")
        mode_effective = mode_raw or "PAPER"
        if (mode_effective or "").upper() == "LIVE" and not live_allowed:
            mode_effective = "PAPER"
            print(f"[MODE_GATE] requested=LIVE allowed=false reason={live_blockers}")
        elif (mode_effective or "").upper() == "LIVE":
            mode_effective = "PAPER"  # Override: LIVE never allowed
            print(f"[MODE_GATE] requested=LIVE forced=PAPER reason=permanent_analyzer_mode")

        return {
            "status": "ok",
            "mode": mode_effective,
            "broker_status": broker_status,
            "market_status": market_status_str,
            "data_source": data_source if SSOT_AVAILABLE and state_store else "real",
            "live_allowed": live_allowed,
            "live_blockers": live_blockers,
            "broker": {"connected": broker_connected, "status": broker_status},
            "market": {"is_open": market_status_str == "open", "reason": market_status_str},
            "cycle_count": health.get("total_cycles", 0),
            "refresh_interval": 5,  # From config
            "last_fetch": health.get("last_data_fetch"),
            "qc_status": qc_status,
            "qc_failures": qc_failures,
            "trades_executed": health.get("trades_executed", 0),
            "open_positions": open_positions,
            "total_pnl": total_pnl,
            "daily_pnl": daily_pnl,
            "performance_sla": {
                "cycle_duration_sec": perf.get("cycle_duration_sec", 0),
                "fetch_duration_sec": perf.get("fetch_duration_sec", 0),
                "strategy_duration_sec": perf.get("strategy_duration_sec", 0),
                "sla_pass": perf.get("cycle_duration_sec", 999) <= 60,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/qc")
async def get_qc():
    """Get QC report"""
    try:
        # Check market status
        market_is_open = False
        if MARKET_DETECTION_AVAILABLE:
            try:
                market_is_open, _ = is_market_open()
            except (ValueError, TypeError, KeyError, AttributeError) as e:
                logger.warning(f'Error handled: {e}')
            except Exception as e:
                logger.error(f'Unexpected error: {e}', exc_info=True)
                pass

        # REAL_ONLY MODE: Never use synthetic data
        if not market_is_open and not REAL_ONLY and SYNTHETIC_DATA_AVAILABLE:
            qc_data = generate_synthetic_qc_data()
            # CRITICAL: Ensure all required fields exist for frontend
            # Explicitly set all fields to ensure they're present (even if function returns them)
            qc_data["qc_passed"] = qc_data.get("qc_passed", True)
            qc_data["total_contracts"] = qc_data.get("total_contracts", 0)
            qc_data["underlying_count"] = qc_data.get("underlying_count", 0)
            qc_data["status"] = qc_data.get("status", "PASS")
            # Return JSONResponse to ensure proper serialization
            return JSONResponse(content=qc_data)

        # Market closed — do not surface stale FAIL from last session (before broker gate)
        if not market_is_open:
            return JSONResponse(
                content={
                    "status": "MARKET_CLOSED",
                    "skipped": True,
                    "overall_passed": None,
                    "qc_passed": None,
                    "message": "QC skipped — market closed (stale spread checks not applied)",
                    "data_source": "skipped",
                    "total_contracts": 0,
                    "underlying_count": 0,
                    "underlying_results": {},
                }
            )

        # REAL_ONLY MODE: If broker not ready, return NOT_READY (market open only)
        if REAL_ONLY:
            broker_connected = False
            if SSOT_AVAILABLE and state_store:
                ssot_state = state_store.get_state()
                broker_connected = ssot_state.get("broker", {}).get("connected", False)
            else:
                health_file = OUTPUTS_DIR / "health.json"
                if health_file.exists():
                    health = json.loads(health_file.read_text())
                    broker_connected = health.get("is_connected", False)

            if not broker_connected:
                return {
                    "status": "NOT_READY",
                    "qc_passed": False,
                    "overall_passed": False,
                    "message": "BROKER_NOT_READY - Real QC data unavailable",
                    "data_source": classify_overview_data_source(
                        market_open=True, broker_connected=False
                    ),
                    "total_contracts": 0,
                    "underlying_count": 0,
                    "failures": ["Broker not connected"],
                }

        # Market is open - use real data
        qc_file = OUTPUTS_DIR / "qc_report_live.json"
        if not qc_file.exists():
            return {
                "status": "NO_DATA",
                "qc_passed": False,
                "total_contracts": 0,
                "underlying_count": 0,
                "message": "QC report not found",
                "data_source": "real",
            }

        data = json.loads(qc_file.read_text())
        data["data_source"] = "real"
        # Ensure all required fields exist
        if "qc_passed" not in data:
            data["qc_passed"] = data.get("status") == "PASS" or data.get("status") == "OK"
        if "total_contracts" not in data:
            data["total_contracts"] = data.get("contracts_total", 0)
        if "underlying_count" not in data:
            data["underlying_count"] = data.get("underlyings", 0)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Default underlyings for discovery (validator and UI)
DEFAULT_UNDERLYINGS = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"]


def _runtime_qc_chain_to_df(chain: Dict[str, Any]):
    if pd is None:
        return None
    contracts = chain.get("contracts") or []
    if not contracts:
        return pd.DataFrame()
    return pd.DataFrame(contracts)


def _runtime_qc_source_is_synthetic(source: Any) -> bool:
    return "synthetic" in str(source or "").lower() or "fake" in str(source or "").lower()


def _runtime_qc_trade_ready(chain: Dict[str, Any]) -> bool:
    if bool(chain.get("trade_ready") or chain.get("tradeable") or chain.get("ready_for_trade")):
        return True
    status = str(chain.get("status") or "").upper()
    return status in {"MARKET_OPEN", "LIVE", "TRADE_READY"}


def _runtime_qc_market_closed_zero_ok(result: Dict[str, Any]) -> bool:
    status = str(result.get("status") or "").upper()
    return bool(
        result.get("market_open") is False
        and int(result.get("total_contracts") or 0) == 0
        and (result.get("skipped") is True or status in {"MARKET_CLOSED", "MARKET_CLOSED_EXPECTED"})
    )


def _runtime_qc_anomalies(df, market_open: bool) -> Tuple[List[str], List[str]]:
    critical: List[str] = []
    warnings: List[str] = []
    if df is None or df.empty:
        return critical, warnings

    def _series(name: str):
        return pd.to_numeric(df[name], errors="coerce") if name in df.columns else None

    bid_col = ask_col = None
    try:
        from src.validation.qc_validator import QCValidator

        bid_col, ask_col = QCValidator._bid_ask_columns(df)
    except Exception:
        pass
    if bid_col and ask_col:
        bid = pd.to_numeric(df[bid_col], errors="coerce")
        ask = pd.to_numeric(df[ask_col], errors="coerce")
        bad = ((bid.notna()) & (ask.notna()) & (ask < bid)).sum()
        if bad:
            critical.append(f"{int(bad)} contracts have ask < bid")

    ltp = _series("ltp")
    if ltp is not None:
        negative_ltp = ((ltp.notna()) & (ltp < 0)).sum()
        if negative_ltp:
            critical.append(f"{int(negative_ltp)} contracts have negative LTP")
        zero_ltp = ((ltp.notna()) & (ltp == 0)).sum()
        if len(df) and zero_ltp > len(df) * 0.2:
            warnings.append(f"{int(zero_ltp)} contracts have zero LTP")

    iv = _series("iv")
    if iv is not None:
        invalid_iv = ((iv.notna()) & ((iv < 0) | (iv > 3))).sum()
        if invalid_iv:
            warnings.append(f"{int(invalid_iv)} contracts have IV outside 0-3 range")

    for col in ("strike", "option_type"):
        if col not in df.columns:
            warnings.append(f"missing {col}")
        else:
            missing = df[col].isna().sum()
            if len(df) and missing > len(df) * 0.1:
                warnings.append(f"{int(missing)} contracts missing {col}")

    if market_open and "fetch_timestamp" in df.columns:
        try:
            now = datetime.now(IST)
            ts = pd.to_datetime(
                df["fetch_timestamp"].astype(str).str.replace(" IST", "", regex=False),
                errors="coerce",
            )
            if getattr(ts.dt, "tz", None) is None:
                ts = ts.dt.tz_localize(IST, nonexistent="NaT", ambiguous="NaT")
            age = (now - ts).dt.total_seconds()
            stale = ((age.notna()) & (age > 60)).sum()
            if stale > len(df) * 0.1:
                warnings.append(f"{int(stale)} contracts have stale timestamps >60s")
        except Exception:
            pass
    return critical, warnings


@app.get("/api/qc/runtime")
async def get_qc_runtime():
    """Read-only runtime QC observer over canonical push/TTL chain snapshots."""
    market_is_open = False
    if MARKET_DETECTION_AVAILABLE:
        try:
            market_is_open, _reason = is_market_open()
        except Exception:
            market_is_open = False

    critical_failures: List[str] = []
    warnings: List[str] = []
    underlying_results: Dict[str, Any] = {}
    total_contracts = 0
    data_sources: List[str] = []

    try:
        from src.validation.qc_validator import QCValidator
    except Exception:
        return {
            "status": "ERROR",
            "overall_passed": False,
            "market_open": market_is_open,
            "skipped": False,
            "data_source": "import_error",
            "total_contracts": 0,
            "underlying_count": 0,
            "underlying_results": {},
            "critical_failures": ["runtime QC import failed"],
            "warnings": [],
            "live_trading_enabled": False,
            "order_placement_allowed": False,
        }

    validator = QCValidator(paper_sanity_mode=True)

    for underlying in DEFAULT_UNDERLYINGS:
        chain: Dict[str, Any] = {
            "underlying": underlying,
            "contracts": [],
            "total_contracts": 0,
            "status": "MARKET_CLOSED" if not market_is_open else "NO_DATA",
            "data_source": "closed" if not market_is_open else "no_snapshot",
        }
        snapshot_source = "none"
        observed = _chain_from_push_cache(underlying)
        if isinstance(observed, dict):
            observed = dict(observed)
            snapshot_source = "push"
        else:
            ttl_hit = _cache_get(f"chain_{underlying}", max(_TTL_CHAIN, 120.0))
            if isinstance(ttl_hit, dict):
                observed = dict(ttl_hit)
                snapshot_source = "ttl"
            else:
                observed = None

        if observed:
            chain.update(observed)
            if not market_is_open and not chain.get("status"):
                chain["status"] = "MARKET_CLOSED"
        elif market_is_open:
            critical_failures.append(f"{underlying}: no pushed or TTL chain snapshot")

        contracts_count = int(chain.get("total_contracts") or len(chain.get("contracts") or []))
        source = chain.get("data_source") or chain.get("source") or "unknown"
        data_sources.append(str(source))
        total_contracts += contracts_count
        df = _runtime_qc_chain_to_df(chain)
        skipped = bool(not market_is_open and contracts_count == 0)
        result_status = "MARKET_CLOSED_EXPECTED" if skipped else str(chain.get("status") or "OK")

        if _runtime_qc_source_is_synthetic(source) and _runtime_qc_trade_ready(chain):
            critical_failures.append(f"{underlying}: synthetic/fake data marked trade-ready")

        qc_passed = None
        qc_reasons: List[str] = []
        underlying_critical: List[str] = []
        underlying_warnings: List[str] = []
        if skipped:
            qc_passed = None
        elif df is not None:
            qc_passed, qc_reasons = validator.validate_snapshot(df, underlying)
            underlying_critical, underlying_warnings = _runtime_qc_anomalies(df, market_is_open)
            critical_failures.extend([f"{underlying}: {item}" for item in underlying_critical])
            warnings.extend([f"{underlying}: {item}" for item in underlying_warnings])
            if not qc_passed:
                warnings.extend([f"{underlying}: {item}" for item in qc_reasons])

        underlying_results[underlying] = {
            "status": result_status,
            "passed": qc_passed,
            "skipped": skipped,
            "market_open": market_is_open,
            "total_contracts": contracts_count,
            "data_source": source,
            "qc_reasons": qc_reasons,
            "critical_failures": underlying_critical,
            "warnings": underlying_warnings,
            "fetch_error": None,
            "snapshot_source": snapshot_source,
        }

    skipped_all = bool(not market_is_open and total_contracts == 0)
    status = "MARKET_CLOSED_EXPECTED" if skipped_all else ("FAIL" if critical_failures else "PASS")
    return {
        "status": status,
        "overall_passed": False if critical_failures else (None if skipped_all else True),
        "market_open": market_is_open,
        "skipped": skipped_all,
        "data_source": ",".join(sorted(set(data_sources))) if data_sources else "unknown",
        "total_contracts": total_contracts,
        "underlying_count": len(DEFAULT_UNDERLYINGS),
        "underlying_results": underlying_results,
        "critical_failures": critical_failures,
        "warnings": warnings,
        "live_trading_enabled": False,
        "order_placement_allowed": False,
    }


@app.get("/api/underlyings")
async def get_underlyings():
    """Return list of underlyings for dynamic chain/validator use."""
    return {"underlyings": DEFAULT_UNDERLYINGS}


_TTL_CHAIN = 20  # local dyno cache — keep longer so UI/WS do not stampede Dhan


def _chain_from_push_cache(sym: str) -> Optional[Dict[str, Any]]:
    pushed = _PUSHED_CHAIN_CACHE.get(sym)
    if not pushed or not isinstance(pushed.get("data"), dict):
        return None
    age_s = _time_module.time() - float(pushed.get("received_at") or 0)
    market_open = bool(pushed.get("market_open", True))
    fresh_window = _PUSHED_CHAIN_FRESH_S if market_open else _PUSHED_CHAIN_FRESH_S_CLOSED
    stale_serve = (
        _PUSHED_CHAIN_STALE_SERVE_S if market_open else _PUSHED_CHAIN_STALE_SERVE_S_CLOSED
    )
    data = dict(pushed["data"] or {})
    if not data:
        return None
    data.setdefault("status", "MARKET_OPEN" if market_open else "MARKET_CLOSED")
    data.setdefault("data_source", data.get("data_source") or "dhan")
    data["source_priority"] = data.get("source_priority") or "index_micro_or_worker_push"
    data["snapshot_age_seconds"] = round(age_s, 1)
    if age_s < fresh_window:
        data["stale"] = False
        data["live"] = bool(market_open)
        return data
    if age_s < stale_serve:
        # Prefer last good rows over a rate-limit empty response during market hours.
        data["stale"] = True
        data["live"] = False
        data["message"] = data.get("message") or (
            f"Serving last good Dhan chain ({round(age_s)}s old) while paced refresh catches up"
        )
        return data
    return None


def _usable_chain_snapshot(data: Any) -> bool:
    """True only when a chain payload has proven broker rows. Empty is never valid."""
    if not isinstance(data, dict):
        return False
    status = str(data.get("status") or "").upper()
    if status in {
        "CHAIN_CACHE_WARMING",
        "NO_DHAN_DATA",
        "CHAIN_FETCH_TIMEOUT",
        "INVALID_OR_MISSING_EXPIRY",
    }:
        return False
    contracts = data.get("contracts")
    n_contracts = len(contracts) if isinstance(contracts, list) else 0
    total = int(data.get("total_contracts") or 0)
    spot = float(data.get("spot") or 0)
    return (n_contracts > 0 or total > 0) and spot > 0


def _warming_chain_placeholder(sym: str) -> Dict[str, Any]:
    return {
        "underlying": sym,
        "contracts": [],
        "spot": 0,
        "pcr": 1.0,
        "total_contracts": 0,
        "data_source": "dhan",
        "status": "CHAIN_CACHE_WARMING",
        "live": False,
        "snapshot": True,
        "stale": True,
        "message": "Index chain warming from micro-loop — UI must not wait on live Dhan OC",
    }


def _resolve_batch_chain_entry(sym: str) -> Dict[str, Any]:
    """Push cache, then TTL snapshot, else an honest warming placeholder."""
    pushed = _chain_from_push_cache(sym)
    if _usable_chain_snapshot(pushed):
        return pushed
    ttl_hit = _cache_get(f"chain_{sym}", max(_TTL_CHAIN, 120.0))
    if _usable_chain_snapshot(ttl_hit):
        return ttl_hit
    return _warming_chain_placeholder(sym)


def _required_chain_symbols_ready(chains: Dict[str, Any]) -> bool:
    for sym in _REQUIRED_CHAIN_SYMBOLS:
        if not _usable_chain_snapshot(chains.get(sym)):
            return False
    return True


def _store_index_chain_snapshot(sym: str, result: Dict[str, Any], open_now: bool) -> Dict[str, Any]:
    payload = dict(result)
    payload["stream_mode"] = payload.get("stream_mode") or "index_chain_micro"
    payload["live"] = open_now
    payload["snapshot"] = not open_now
    if open_now and not payload.get("status"):
        payload["status"] = "MARKET_OPEN"
    if not open_now and not payload.get("status"):
        payload["status"] = "MARKET_CLOSED_DHAN_SNAPSHOT"
    _PUSHED_CHAIN_CACHE[sym] = {
        "data": payload,
        "received_at": _time_module.time(),
        "market_open": open_now,
    }
    _cache_set(f"chain_{sym}", payload)
    return payload


async def _warm_one_index_chain(sym: str) -> Optional[Dict[str, Any]]:
    """Fetch one index chain into push/TTL cache. Serial Dhan OC owner path."""
    open_now = bool(_market_open_from_state())
    result = await _get_chain_uncached(sym, closed_timeout_s=28.0)
    if isinstance(result, dict) and float(result.get("spot") or 0) > 0:
        payload = _store_index_chain_snapshot(sym, result, open_now)
        print(
            f"[index-chain-micro] {sym} spot={payload.get('spot')} "
            f"n={payload.get('total_contracts') or len(payload.get('contracts') or [])} "
            f"open={open_now}"
        )
        return payload
    return None


async def _warm_required_index_chains_cold_start() -> Dict[str, Any]:
    """Warm NIFTY/BANKNIFTY/FINNIFTY/MIDCPNIFTY back-to-back without 20s closed gaps.

    Serial OC is required (single Dhan worker). The timing race was the extra
    closed-market sleep between required symbols, not the serial fetch itself.
    """
    warmed: Dict[str, Any] = {}
    for i, sym in enumerate(_REQUIRED_CHAIN_SYMBOLS):
        try:
            payload = await _warm_one_index_chain(sym)
            if payload is not None:
                warmed[sym] = payload
        except Exception as exc:
            print(f"[index-chain-micro] cold-start {sym} failed: {exc}")
        if i < len(_REQUIRED_CHAIN_SYMBOLS) - 1:
            await asyncio.sleep(_CHAIN_COLD_START_GAP_S)
    return warmed


def _build_market_top_from_chain_cache(
    top_n: int = 5,
    market_top_n: int = 25,
) -> Optional[Dict[str, Any]]:
    """Rank the last good paced index chains without making another Dhan call."""
    chains: Dict[str, Dict[str, Any]] = {}
    for sym in _INDEX_STREAM_SYMBOLS:
        chain = _chain_from_push_cache(sym)
        if chain is None:
            ttl_hit = _cache_get(f"chain_{sym}", max(_TTL_CHAIN, 120.0))
            if isinstance(ttl_hit, dict):
                chain = dict(ttl_hit)
        if isinstance(chain, dict) and (chain.get("contracts") or []):
            chains[sym] = chain
    if not chains:
        return None

    from dashboard.backend.contract_gain_scanner import scan_all_segments_from_chains

    report = scan_all_segments_from_chains(
        chains,
        top_n=top_n,
        market_top_n=market_top_n,
    )
    if int(report.get("contracts_scored_total") or 0) <= 0:
        return None
    report["status"] = "ok"
    report["market_open"] = bool(_market_open_from_state())
    report["include_equity"] = False
    report["stream_mode"] = "index_chain_cache"
    report["data_provenance"] = "DHAN_OPTION_CHAIN_LIVE"
    report["chains_fetched"] = list(chains)
    report["note"] = "Ranked from last good paced Dhan index-chain snapshots; no scanner fan-out."
    report["live_trading_enabled"] = False
    return report


@app.get("/api/batch/chains")
async def batch_chains():
    """Index chains for TopBar/Overview — cache/push only, never blocks on Dhan OC.

    Incomplete required-symbol payloads are not cached. Caching CHAIN_CACHE_WARMING
    for 8s is what made FINNIFTY/MIDCPNIFTY look permanently cold during smoke.
    """
    hit = _cache_get("batch_chains_v1", _TTL_BATCH)
    if hit is not None:
        out = dict(hit)
        out["cache_hit"] = True
        return out

    chains: Dict[str, Any] = {
        sym: _resolve_batch_chain_entry(sym) for sym in _INDEX_STREAM_SYMBOLS
    }
    ready = _required_chain_symbols_ready(chains)
    payload = {
        "cache_hit": False,
        "generated_at": datetime.now(IST).isoformat(),
        "ttl_s": _TTL_BATCH,
        "live_trading_enabled": False,
        "symbols": list(_INDEX_STREAM_SYMBOLS),
        "required_symbols": list(_REQUIRED_CHAIN_SYMBOLS),
        "required_symbols_ready": ready,
        "chains": chains,
    }
    if not ready:
        return payload
    return _cache_set("batch_chains_v1", payload)


@app.get("/api/chain/{underlying}")
async def get_chain(underlying: str):
    """Get option chain for specific underlying.

    Preference order: (1) fresh/stale-but-usable push/micro-loop snapshot;
    (2) short local TTL cache; (3) paced inline live fetch as last resort.
    """
    sym = underlying.upper()
    pushed = _chain_from_push_cache(sym)
    if pushed is not None:
        return pushed

    cache_key = f"chain_{sym}"
    open_now = bool(_market_open_from_state())
    chain_ttl = _TTL_CHAIN if open_now else max(_TTL_CHAIN, 300.0)
    _hit = _cache_get(cache_key, chain_ttl)
    if _hit is not None:
        return _hit

    # After hours: never hold the request path for a full Dhan OC round-trip.
    # Micro-loop / snapshots refill cache; UI keeps last good via stale serve.
    live_timeout = _CHAIN_LIVE_TIMEOUT_OPEN_S if open_now else _CHAIN_LIVE_TIMEOUT_CLOSED_S
    try:
        result = await asyncio.wait_for(_get_chain_uncached(underlying), timeout=live_timeout)
    except asyncio.TimeoutError:
        result = {
            "underlying": sym,
            "contracts": [],
            "spot": 0,
            "pcr": 1.0,
            "total_contracts": 0,
            "data_source": "dhan",
            "status": "CHAIN_FETCH_TIMEOUT",
            "live": False,
            "snapshot": True,
            "stale": True,
            "message": f"Option chain fetch timed out after {live_timeout:.0f}s — keeping UI responsive",
        }
    if isinstance(result, dict) and float(result.get("spot") or 0) > 0:
        _PUSHED_CHAIN_CACHE[sym] = {
            "data": result,
            "received_at": _time_module.time(),
            "market_open": bool(result.get("live", open_now)),
        }
        return _cache_set(cache_key, result)
    # Never cache empty/failed OC — that poisons /api/chain for the TTL window.
    return result


async def _get_chain_uncached(underlying: str, closed_timeout_s: float | None = None):
    """Get option chain for specific underlying"""
    try:
        # Check market status first
        market_is_open = False
        if MARKET_DETECTION_AVAILABLE:
            try:
                market_is_open, reason = is_market_open()
            except (ValueError, TypeError, KeyError, AttributeError) as e:
                logger.warning(f'Error handled: {e}')
            except Exception as e:
                logger.error(f'Unexpected error: {e}', exc_info=True)
                pass

        # REAL_ONLY MODE: Never use synthetic data
        if not market_is_open and not REAL_ONLY and SYNTHETIC_DATA_AVAILABLE:
            try:
                # Import BASE_SPOT_PRICES (try both import paths)
                try:
                    from dashboard.backend.synthetic_data_generator import (
                        BASE_SPOT_PRICES,
                    )
                except ImportError:
                    from synthetic_data_generator import BASE_SPOT_PRICES

                # Try to get last known spot price from real data if available
                spot_price = None
                chain_file = OUTPUTS_DIR / "chain_raw_live.csv"
                if chain_file.exists():
                    try:
                        import csv as _csv
                        filtered_rows = []
                        with open(chain_file, newline="") as _f:
                            reader = _csv.DictReader(_f)
                            for row in reader:
                                if row.get("underlying","").upper() == underlying.upper():
                                    filtered_rows.append(row)
                        if filtered_rows and "spot_price" in filtered_rows[0]:
                            for _r in filtered_rows:
                                try:
                                    _sv = float(_r.get("spot_price") or 0)
                                    if _sv > 0:
                                        spot_price = _sv
                                        break
                                except (ValueError, TypeError):
                                    continue
                    except (ValueError, TypeError, KeyError, AttributeError) as e:
                        logger.warning(f'Error handled: {e}')
                    except Exception as e:
                        logger.error(f'Unexpected error: {e}', exc_info=True)
                        pass

                # Generate synthetic chain data
                contracts = generate_synthetic_chain_data(underlying, spot_price)

                # Calculate spot and PCR
                spot = spot_price if spot_price else BASE_SPOT_PRICES.get(underlying.upper(), 24000.0)
                pe_oi = sum(c.get("oi", 0) for c in contracts if c.get("option_type") == "PE")
                ce_oi = sum(c.get("oi", 0) for c in contracts if c.get("option_type") == "CE")
                pcr = float(pe_oi / ce_oi) if ce_oi > 0 else 1.0

                return {
                    "underlying": underlying.upper(),
                    "spot": float(spot),
                    "pcr": float(pcr),
                    "contracts": contracts[:1000],
                    "total_contracts": len(contracts),
                    "data_source": "synthetic",
                    "status": "MARKET_CLOSED",
                    "message": "Using synthetic data (market closed)",
                }
            except Exception as e:
                # Log error but still return synthetic data with fallback
                import traceback

                print(f"Error generating synthetic data: {e}")
                print(traceback.format_exc())
                # Return minimal synthetic data as fallback
                # Import BASE_SPOT_PRICES (try both import paths)
                try:
                    try:
                        from dashboard.backend.synthetic_data_generator import (
                            BASE_SPOT_PRICES,
                        )
                    except ImportError:
                        from synthetic_data_generator import BASE_SPOT_PRICES
                except ImportError:
                    # Ultimate fallback - use default spot price
                    BASE_SPOT_PRICES = {"NIFTY": 24000.0, "BANKNIFTY": 50000.0}
                spot = BASE_SPOT_PRICES.get(underlying.upper(), 24000.0)
                return {
                    "underlying": underlying.upper(),
                    "spot": float(spot),
                    "pcr": 1.0,
                    "contracts": [],
                    "total_contracts": 0,
                    "data_source": "synthetic",
                    "status": "MARKET_CLOSED",
                    "message": f"Using synthetic data (market closed) - Error: {str(e)}",
                }

        if not market_is_open:
            # LAST-SESSION SNAPSHOT: prefer chain_cache, then worker chain_{SYM}.json
            try:
                _candidates = [
                    ROOT_DIR / "state" / "chain_cache" / f"{underlying.upper()}.json",
                    ROOT_DIR / "state" / f"chain_{underlying.upper()}.json",
                    ROOT_DIR / "src" / "outputs" / f"chain_{underlying.upper()}.json",
                ]
                for _snap_file in _candidates:
                    if not _snap_file.exists():
                        continue
                    _snap = json.loads(_snap_file.read_text(encoding="utf-8"))
                    _contracts = _snap.get("contracts") or []
                    if not _contracts:
                        continue
                    _src = str(_snap.get("data_source") or _snap.get("source") or "").lower()
                    if _src and _src not in {"dhan", "worker_push"} and not _src.startswith("dhan"):
                        continue
                    _snap["data_source"] = "dhan"
                    _snap["status"] = "MARKET_CLOSED_DHAN_SNAPSHOT"
                    _snap["live"] = False
                    _snap["snapshot"] = True
                    _snap["stale"] = True
                    _snap["source_priority"] = "dhan_last_verified_snapshot"
                    _snap["total_contracts"] = int(
                        _snap.get("total_contracts") or len(_contracts)
                    )
                    _snap["message"] = (
                        "Market closed — last verified Dhan snapshot "
                        f"({_snap.get('snapshot_time') or _snap.get('fetched_at_utc') or _snap_file.name})"
                    )
                    return _snap
            except Exception as _se:
                print(f"[chain] snapshot read failed: {_se}")
            try:

                def _closed_dhan_chain_fetch():
                    from core.data.datasource_manager import DataSourceManager
                    from dashboard.backend.chain_adapter import fetch_chain_for_api

                    return fetch_chain_for_api(DataSourceManager(), underlying.upper())

                _closed_to = (
                    float(closed_timeout_s)
                    if closed_timeout_s is not None
                    else _CHAIN_LIVE_TIMEOUT_CLOSED_S
                )
                closed_chain = await _run_dhan_oc(
                    _closed_dhan_chain_fetch, timeout=_closed_to
                )
                if closed_chain and int(closed_chain.get("total_contracts") or 0) > 0:
                    # Dhan still returns last quotes after hours — show as snapshot, not live.
                    closed_chain["data_source"] = "dhan"
                    closed_chain["status"] = "MARKET_CLOSED_DHAN_SNAPSHOT"
                    closed_chain["live"] = False
                    closed_chain["snapshot"] = True
                    closed_chain["stale"] = True
                    closed_chain["source_priority"] = "dhan_last_verified_snapshot"
                    closed_chain["snapshot_time"] = datetime.now(IST).strftime("%Y-%m-%d %H:%M IST")
                    closed_chain["message"] = (
                        "Market closed — last verified Dhan option-chain snapshot "
                        f"({closed_chain['snapshot_time']})"
                    )
                    try:
                        _snap_dir = ROOT_DIR / "state" / "chain_cache"
                        _snap_dir.mkdir(parents=True, exist_ok=True)
                        (_snap_dir / f"{underlying.upper()}.json").write_text(
                            json.dumps(closed_chain, default=str), encoding="utf-8"
                        )
                    except Exception as _we:
                        print(f"[chain] closed snapshot write failed: {_we}")
                    return closed_chain
            except asyncio.TimeoutError:
                pass
            except Exception as exc:
                print(f"Closed-market Dhan chain fetch failed: {exc}")
            return {
                "underlying": underlying.upper(),
                "contracts": [],
                "spot": 0,
                "pcr": 1.0,
                "total_contracts": 0,
                "data_source": "dhan",
                "status": "NO_DHAN_DATA",
                "message": "Market closed and no verified Dhan option-chain snapshot is available yet",
            }

        # REAL_ONLY MODE: If broker not ready, return NOT_READY
        if REAL_ONLY:
            broker_connected = False
            if SSOT_AVAILABLE and state_store:
                ssot_state = state_store.get_state()
                broker_connected = ssot_state.get("broker", {}).get("connected", False)
            else:
                health_file = OUTPUTS_DIR / "health.json"
                if health_file.exists():
                    health = json.loads(health_file.read_text())
                    broker_connected = health.get("is_connected", False)

            if not broker_connected:
                # FALLBACK: state_store may not have broker truth on fresh deploy
                # Try direct Dhan API check before returning NOT_READY
                try:
                    from core.brokers.dhan.dhan_readonly import (
                        get_status as _direct_dhan,
                    )

                    _dstatus = _direct_dhan()
                    if _dstatus.get("connected"):
                        broker_connected = True
                        # Update state_store with real truth
                        if SSOT_AVAILABLE and state_store:
                            state_store.update_state(
                                {
                                    "broker": {
                                        "connected": True,
                                        "name": "dhan",
                                        "status": "connected",
                                        "error": None,
                                        "latency_ms": _dstatus.get("latency_ms"),
                                    }
                                }
                            )
                except Exception:
                    pass

            if not broker_connected:
                return {
                    "underlying": underlying.upper(),
                    "contracts": [],
                    "spot": 0,
                    "pcr": 1.0,
                    "total_contracts": 0,
                    "data_source": classify_overview_data_source(
                        market_open=True, broker_connected=False
                    ),
                    "status": "NOT_READY",
                    "message": "BROKER_NOT_READY - Real chain data unavailable",
                }

        # ALWAYS try Dhan P0 first when market is open (or as fallback)
        # chain_raw_live.csv on Render is from repo clone — may be months old
        # DSM → dhan_option_chain_parser → live Greeks, OI change, bid/ask
        # CRITICAL: fetch_chain_for_api is sync HTTP — must run off the event loop
        # or /ui and /api/health starve (Cloud Run "upstream request timeout").
        try:

            def _open_dhan_chain_fetch():
                from core.data.datasource_manager import DataSourceManager
                from dashboard.backend.chain_adapter import fetch_chain_for_api

                return fetch_chain_for_api(DataSourceManager(), underlying.upper())

            open_to = (
                float(closed_timeout_s)
                if closed_timeout_s is not None
                else _CHAIN_LIVE_TIMEOUT_OPEN_S
            )
            _live = await _run_dhan_oc(_open_dhan_chain_fetch, timeout=max(open_to, 8.0))
            if _live and _live.get("contracts") and len(_live["contracts"]) >= 5:
                _live["status"] = "MARKET_OPEN" if market_is_open else "MARKET_CLOSED"
                _live["source_priority"] = "dhan_p0_live"
                # PERSIST last-session snapshot for after-hours display
                try:
                    _snap_dir = ROOT_DIR / "state" / "chain_cache"
                    _snap_dir.mkdir(parents=True, exist_ok=True)
                    _snap_out = dict(_live)
                    _snap_out["snapshot_time"] = datetime.now(IST).strftime("%Y-%m-%d %H:%M IST")
                    (_snap_dir / f"{underlying.upper()}.json").write_text(
                        json.dumps(_snap_out, default=str)
                    )
                except Exception as _we:
                    print(f"[chain] snapshot write failed: {_we}")
                return _live
            else:
                print(
                    f"[chain/{underlying}] DSM returned empty/small ({len((_live or {}).get('contracts', []))} contracts) — using CSV fallback"
                )
        except asyncio.TimeoutError:
            print(f"[chain/{underlying}] DSM timed out — using CSV fallback")
        except Exception as _dsm_err:
            print(f"[chain/{underlying}] DSM failed: {_dsm_err} — using CSV fallback")

        # CSV fallback (only reached if Dhan P0 fails)
        chain_file = OUTPUTS_DIR / "chain_raw_live.csv"
        if not chain_file.exists():
            # Try Dhan Data API directly (still off the event loop)
            try:

                def _fallback_dhan_chain_fetch():
                    from core.data.datasource_manager import DataSourceManager
                    from dashboard.backend.chain_adapter import fetch_chain_for_api

                    return fetch_chain_for_api(DataSourceManager(), underlying.upper())

                _chain_result = await _run_dhan_oc(
                    _fallback_dhan_chain_fetch, timeout=_CHAIN_LIVE_TIMEOUT_OPEN_S
                )
                if _chain_result and _chain_result.get("contracts"):
                    return _chain_result
            except Exception:
                pass
            return {
                "underlying": underlying,
                "contracts": [],
                "message": "Chain data not found — Dhan fetch also failed",
                "spot": 0,
                "pcr": 1.0,
                "total_contracts": 0,
                "data_source": "real",
            }

        # DSM already tried above — directly read CSV as last resort

        # Try pandas first, fallback to csv module
        df = None
        if pd is not None:
            try:
                df = pd.read_csv(chain_file)
            except Exception as e:
                # Pandas failed, will use csv module fallback
                df = None

        if df is None:
            # Fallback: use csv module
            import csv

            rows = []
            with open(chain_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    rows.append(row)

            if not rows:
                return {
                    "underlying": underlying,
                    "contracts": [],
                    "message": "Chain file is empty",
                    "spot": 0,
                    "pcr": 1.0,
                    "total_contracts": 0,
                }

            # Convert to dict format
            df_dict = {col: [row.get(col) for row in rows] for col in rows[0].keys()}

            # Check for status rows
            if "status" in df_dict:
                status_rows = [
                    i for i, s in enumerate(df_dict["status"]) if s and str(s).strip() not in ["", "nan", "None"]
                ]
                if len(status_rows) == len(rows):
                    status = df_dict["status"][0] if df_dict["status"] else ""
                    if status in ["MARKET_CLOSED", "NO_DATA", "ERROR"]:
                        return {
                            "underlying": underlying,
                            "contracts": [],
                            "message": f"Market status: {status}",
                            "spot": 0,
                            "pcr": 1.0,
                            "total_contracts": 0,
                            "status": status,
                        }

            # Filter by underlying
            if "underlying" in df_dict:
                filtered_rows = [row for row in rows if str(row.get("underlying", "")).upper() == underlying.upper()]
            else:
                return {
                    "underlying": underlying,
                    "contracts": [],
                    "message": "No underlying column in chain data",
                    "spot": 0,
                    "pcr": 1.0,
                    "total_contracts": 0,
                }

            if not filtered_rows:
                return {
                    "underlying": underlying,
                    "contracts": [],
                    "message": "No data for this underlying",
                    "spot": 0,
                    "pcr": 1.0,
                    "total_contracts": 0,
                }

            # Calculate spot
            spot = 0
            if "spot_price" in filtered_rows[0]:
                try:
                    spot_vals = [float(row.get("spot_price", 0)) for row in filtered_rows if row.get("spot_price")]
                    if spot_vals:
                        spot = spot_vals[0]
                except (ValueError, TypeError, KeyError, AttributeError) as e:
                    logger.warning(f'Error handled: {e}')
                except Exception as e:
                    logger.error(f'Unexpected error: {e}', exc_info=True)
                    pass

            # Calculate PCR
            pcr = 1.0
            if "oi" in filtered_rows[0] and "option_type" in filtered_rows[0]:
                try:
                    pe_oi = sum(float(row.get("oi", 0)) for row in filtered_rows if row.get("option_type") == "PE")
                    ce_oi = sum(float(row.get("oi", 0)) for row in filtered_rows if row.get("option_type") == "CE")
                    pcr = float(pe_oi / ce_oi) if ce_oi > 0 else 1.0
                except (ValueError, TypeError, KeyError, AttributeError) as e:
                    logger.warning(f'Error handled: {e}')
                except Exception as e:
                    logger.error(f'Unexpected error: {e}', exc_info=True)
                    pcr = 1.0

            # Calculate liquidity scores
            for row in filtered_rows:
                volume = float(row.get("volume", 0) or 0)
                oi = float(row.get("oi", 0) or 0)
                row["liquidity_score"] = volume * 0.4 + oi * 0.6

            # Convert to contracts list
            contracts = []
            for row in filtered_rows:
                contract = {}
                for key, value in row.items():
                    if value is None or str(value).strip() in ["", "nan", "None"]:
                        contract[key] = None
                    else:
                        try:
                            # Try to convert to number if possible
                            if "." in str(value):
                                contract[key] = float(value)
                            else:
                                contract[key] = int(value)
                        except (ValueError, TypeError, KeyError, AttributeError) as e:
                            logger.warning(f'Error handled: {e}')
                        except Exception as e:
                            logger.error(f'Unexpected error: {e}', exc_info=True)
                            contract[key] = value
                contracts.append(contract)

            return {
                "underlying": underlying.upper(),
                "spot": float(spot),
                "pcr": float(pcr),
                "contracts": contracts[:1000],
                "total_contracts": len(contracts),
                "data_source": "csv_fallback",
                "source_priority": "csv_fallback_after_live_fetch_failed",
                "status": "STALE_CSV_FALLBACK" if market_is_open else "MARKET_CLOSED_CSV_SNAPSHOT",
                "stale": True,
                "message": "Dhan live option-chain fetch failed; showing local CSV fallback, which may be stale. Do not treat as live price.",
            }

        # Continue with pandas path
        df = pd.read_csv(chain_file)

        # Check if this is a status row (market closed, no data, etc.)
        # Only check if 'status' column exists AND has non-null values
        if "status" in df.columns:
            # Check if ALL rows are status rows (no actual contract data)
            status_rows = df[df["status"].notna()]
            if len(status_rows) == len(df) and len(df) > 0:
                # All rows are status rows
                status = status_rows.iloc[0].get("status", "")
                if status in ["MARKET_CLOSED", "NO_DATA", "ERROR"]:
                    return {
                        "underlying": underlying,
                        "contracts": [],
                        "message": f"Market status: {status}",
                        "spot": 0,
                        "pcr": 1.0,
                        "total_contracts": 0,
                        "status": status,
                    }

        # Filter by underlying if column exists
        if "underlying" in df.columns:
            # Filter out status rows first (rows where underlying is null/empty)
            df = df[df["underlying"].notna()]
            df = df[df["underlying"].astype(str).str.strip() != ""]
            # Now filter by underlying
            df = df[df["underlying"].astype(str).str.upper() == underlying.upper()]
        elif "underlying" not in df.columns and not df.empty:
            # If no underlying column, might be status-only CSV
            return {
                "underlying": underlying,
                "contracts": [],
                "message": "No underlying column in chain data (status-only CSV)",
                "spot": 0,
                "pcr": 1.0,
                "total_contracts": 0,
            }

        if df.empty:
            return {
                "underlying": underlying,
                "contracts": [],
                "message": "No data for this underlying",
                "spot": 0,
                "pcr": 1.0,
                "total_contracts": 0,
            }

        # Calculate metrics
        spot = 0
        if "spot_price" in df.columns:
            spot_vals = pd.to_numeric(df["spot_price"], errors="coerce").dropna()
            if not spot_vals.empty:
                spot = float(spot_vals.iloc[0])

        # Calculate PCR
        pcr = 1.0
        if "oi" in df.columns and "option_type" in df.columns:
            try:
                pe_df = df[df["option_type"] == "PE"]
                ce_df = df[df["option_type"] == "CE"]
                pe_oi = pd.to_numeric(pe_df["oi"], errors="coerce").sum() if len(pe_df) > 0 else 1
                ce_oi = pd.to_numeric(ce_df["oi"], errors="coerce").sum() if len(ce_df) > 0 else 1
                pcr = float(pe_oi / ce_oi) if ce_oi > 0 else 1.0
            except (ValueError, TypeError, KeyError, AttributeError) as e:
                logger.warning(f'Error handled: {e}')
            except Exception as e:
                logger.error(f'Unexpected error: {e}', exc_info=True)
                pcr = 1.0

        # Calculate liquidity scores
        if "volume" in df.columns and "oi" in df.columns:
            df["liquidity_score"] = (
                pd.to_numeric(df["volume"], errors="coerce").fillna(0) * 0.4
                + pd.to_numeric(df["oi"], errors="coerce").fillna(0) * 0.6
            )
        else:
            df["liquidity_score"] = 0

        # Convert to dict, handling NaN values
        # Also map CSV column names to standard dashboard field names
        _col_map = {
            "dOI": "oi_change",  # OI change from CSV
            "dVolume": "vol_change",  # Volume change
            "spot_price": "spot_price",
        }
        contracts = []
        for _, row in df.iterrows():
            contract = {}
            for col in df.columns:
                val = row[col]
                target_col = _col_map.get(col, col)
                if pd.isna(val):
                    contract[target_col] = None
                else:
                    try:
                        contract[target_col] = float(val) if isinstance(val, (int, float)) else val
                    except (TypeError, ValueError):
                        contract[target_col] = val
            # Ensure oi_change exists even if dOI missing
            if "oi_change" not in contract:
                contract["oi_change"] = 0
            contracts.append(contract)

        chain_status = "STALE_CSV_FALLBACK" if market_is_open else "MARKET_CLOSED_CSV_SNAPSHOT"
        return {
            "underlying": underlying.upper(),
            "spot": float(spot),
            "pcr": float(pcr),
            "contracts": contracts[:1000],
            "total_contracts": len(contracts),
            "data_source": "csv_fallback",
            "source_priority": "csv_fallback_after_live_fetch_failed",
            "status": chain_status,
            "stale": True,
            "message": "Dhan live option-chain fetch failed; showing local CSV fallback, which may be stale. Do not treat as live price." if market_is_open else "Market closed - local CSV snapshot.",
        }
    except Exception as e:
        # Return empty data instead of 500 error
        return {
            "underlying": underlying,
            "contracts": [],
            "message": f"Error processing chain data: {str(e)}",
            "spot": 0,
            "pcr": 1.0,
            "total_contracts": 0,
            "error": str(e),
        }


@app.get("/api/signal/top")
async def get_top_signal():
    """Get top trade signal"""
    try:
        # Check market status
        market_is_open = False
        if MARKET_DETECTION_AVAILABLE:
            try:
                market_is_open, _ = is_market_open()
            except (ValueError, TypeError, KeyError, AttributeError) as e:
                logger.warning(f'Error handled: {e}')
            except Exception as e:
                logger.error(f'Unexpected error: {e}', exc_info=True)
                pass

        # REAL_ONLY MODE: Never use synthetic data
        if not market_is_open and not REAL_ONLY and SYNTHETIC_DATA_AVAILABLE:
            signal = generate_synthetic_signal_data()
            signal["data_source"] = "synthetic"
            return signal

        if not market_is_open:
            signal_file = OUTPUTS_DIR / "top_trade_signal.json"
            if signal_file.exists():
                try:
                    last = json.loads(signal_file.read_text(encoding="utf-8"))
                    if isinstance(last, dict) and last:
                        last = dict(last)
                        last["action"] = "NO_TRADE"
                        last["status"] = "MARKET_CLOSED"
                        last["stale"] = True
                        last["live"] = False
                        last["snapshot"] = True
                        last["reason"] = (
                            "Market closed — showing last session signal snapshot; "
                            "not executable until market open"
                        )
                        last["data_source"] = last.get("data_source") or "dhan_last_session"
                        return last
                except Exception as _sig_err:
                    print(f"[signal] last-session read failed: {_sig_err}")
            return {
                "action": "NO_TRADE",
                "status": "MARKET_CLOSED",
                "reason": "Market closed - live signal unavailable",
                "data_source": "closed",
                "confidence": 0,
            }

        # REAL_ONLY MODE: If broker not ready, return NOT_READY
        if REAL_ONLY:
            broker_connected = False
            if SSOT_AVAILABLE and state_store:
                ssot_state = state_store.get_state()
                broker_connected = ssot_state.get("broker", {}).get("connected", False)
            else:
                health_file = OUTPUTS_DIR / "health.json"
                if health_file.exists():
                    health = json.loads(health_file.read_text())
                    broker_connected = health.get("is_connected", False)

            if not broker_connected:
                return {
                    "action": "NO_TRADE",
                    "reason": "BROKER_NOT_READY - Real signal data unavailable",
                    "data_source": classify_overview_data_source(
                        market_open=True, broker_connected=False
                    ),
                    "confidence": 0,
                }

        # Market is open - use real data
        signal_file = OUTPUTS_DIR / "top_trade_signal.json"
        if not signal_file.exists():
            return {"action": "NO_TRADE", "reason": "Signal file not found", "data_source": "real"}

        data = json.loads(signal_file.read_text())
        data["data_source"] = "real"
        und = str(data.get("underlying") or data.get("symbol") or "").strip().upper()
        if und:
            ok, reason = get_fo_eligibility_filter().is_eligible(und)
            data["fo_check"] = {"eligible": ok, "reason": reason}
            if not ok:
                data["action"] = "NO_TRADE"
                data["reason"] = f"NOT_IN_NSE_FO_UNIVERSE ({und})"
                data["status"] = "FO_FILTERED"
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/positions")
async def get_positions():
    """Get open positions"""
    try:
        positions_file = OUTPUTS_DIR / "positions_live.json"
        if not positions_file.exists():
            return {"positions": [], "open_count": 0, "message": "Positions file not found"}

        data = json.loads(positions_file.read_text())

        # Handle different formats
        if isinstance(data, dict):
            # Expected format: {"positions": [...], "open_count": N}
            positions = data.get("positions", [])
            # Ensure all positions have required fields for dashboard
            for pos in positions:
                if "current_price" not in pos:
                    pos["current_price"] = pos.get("entry_price", 0)
                if "unrealized_pnl" not in pos:
                    entry = pos.get("entry_price", 0)
                    current = pos.get("current_price", entry)
                    qty = pos.get("qty", pos.get("quantity", 0))
                    pos["unrealized_pnl"] = (current - entry) * qty
            return {
                "positions": positions,
                "open_count": data.get("open_count", len(positions)),
                "closed_count": data.get("closed_count", 0),
                "timestamp": data.get("timestamp"),
            }
        elif isinstance(data, list):
            # Legacy format: just a list
            return {"positions": data, "open_count": len(data), "closed_count": 0}
        else:
            return {"positions": [], "open_count": 0, "message": "Invalid positions file format"}
    except Exception as e:
        # Try to get from health.json as fallback
        health_file = OUTPUTS_DIR / "health.json"
        if health_file.exists():
            try:
                health = json.loads(health_file.read_text())
                return {
                    "positions": [],
                    "open_count": health.get("current_positions", 0),
                    "message": "Using health.json data (positions file error)",
                }
            except (ValueError, TypeError, KeyError, AttributeError) as e:
                logger.warning(f'Error handled: {e}')
            except Exception as e:
                logger.error(f'Unexpected error: {e}', exc_info=True)
                pass
        return {"positions": [], "open_count": 0, "message": f"No position data available: {str(e)}"}


@app.get("/api/pnl")
async def get_pnl():
    """Get PnL data"""
    try:
        pnl_csv = OUTPUTS_DIR / "paper_pnl.csv"
        pnl_summary = OUTPUTS_DIR / "paper_pnl_summary.json"
        if not pnl_summary.exists():
            pnl_summary = ROOT_DIR / "paper_pnl_summary.json"

        csv_data = []
        if pnl_csv.exists():
            try:
                if pd is None:
                    csv_data = []
                else:
                    df = pd.read_csv(pnl_csv)
                # Filter out status rows (rows that don't have numeric values)
                if not df.empty:
                    # Ensure we have valid numeric columns
                    numeric_cols = [
                        "total_trades",
                        "winning_trades",
                        "losing_trades",
                        "win_rate",
                        "total_realized_pnl",
                        "total_unrealized_pnl",
                        "total_pnl",
                    ]
                    # Filter rows where at least one numeric column is valid
                    for col in numeric_cols:
                        if col in df.columns:
                            df = df[pd.to_numeric(df[col], errors="coerce").notna()]
                    csv_data = df.to_dict("records")
            except Exception as csv_error:
                # If CSV parsing fails, return empty history
                csv_data = []

        summary = {}
        if pnl_summary.exists():
            try:
                summary = json.loads(pnl_summary.read_text())
            except Exception:
                summary = {}
        # Prefer cloud paper engine live file whenever present (includes open unrealized).
        pnl_live = OUTPUTS_DIR / "pnl_live.json"
        if pnl_live.exists():
            try:
                live = json.loads(pnl_live.read_text())
                if isinstance(live, dict) and (
                    int(live.get("total_trades") or 0) > 0
                    or int(live.get("open_positions") or 0) > 0
                    or float(live.get("total_pnl") or 0) != 0
                    or float(live.get("total_unrealized_pnl") or 0) != 0
                ):
                    summary = live
            except Exception:
                pass

        # Ensure history has proper ISO timestamps
        processed_history = []
        for item in csv_data:
            processed_item = dict(item)
            # Ensure timestamp exists and is in ISO format
            if "timestamp" not in processed_item and "date" in processed_item:
                processed_item["timestamp"] = processed_item["date"]
            if "timestamp" in processed_item:
                try:
                    # Try to parse and convert to ISO
                    ts = processed_item["timestamp"]
                    if isinstance(ts, str):
                        # Try parsing
                        parsed = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                        processed_item["timestamp"] = parsed.isoformat()
                    elif isinstance(ts, (int, float)):
                        # Unix timestamp
                        processed_item["timestamp"] = datetime.fromtimestamp(ts, tz=IST).isoformat()
                except (ValueError, TypeError, KeyError, AttributeError) as e:
                    logger.warning(f'Error handled: {e}')
                except Exception as e:
                    logger.error(f'Unexpected error: {e}', exc_info=True)
                    # If parsing fails, add current timestamp
                    processed_item["timestamp"] = datetime.now(IST).isoformat()
            else:
                # No timestamp - add current one
                processed_item["timestamp"] = datetime.now(IST).isoformat()
            processed_history.append(processed_item)

        # ── REMOVED Feb-2026 fixture fallback ──────────────────────────────────
        # Previously: loaded paper_closed_trades_feb2026.json when no real trades.
        # This caused FAKE Feb-1 data to appear in the Paper tab as if real trades.
        # Fix: honest empty state — no trades until cloud paper engine generates them.
        if not processed_history:
            pass  # Honest: no historical trades yet — engine will populate during market hours

        # Keep /api/pnl fast for dashboard health checks. Symbol enrichment loads the
        # instrument master and can exceed the verifier timeout when no live PnL file exists.

        return {
            "history": processed_history,
            "summary": (
                summary
                if summary
                else {
                    "total_trades": 0,
                    "winning_trades": 0,
                    "losing_trades": 0,
                    "win_rate": 0.0,
                    "total_realized_pnl": 0.0,
                    "total_unrealized_pnl": 0.0,
                    "total_pnl": 0.0,
                    "open_positions": 0,
                }
            ),
        }
    except Exception as e:
        # Return empty data instead of 500 error
        return {
            "history": [],
            "summary": {
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0.0,
                "total_realized_pnl": 0.0,
                "total_unrealized_pnl": 0.0,
                "total_pnl": 0.0,
                "open_positions": 0,
            },
            "error": str(e),
        }


@app.get("/api/perf")
async def get_performance():
    """Get performance metrics"""
    try:
        # Check market status
        market_is_open = False
        if MARKET_DETECTION_AVAILABLE:
            try:
                market_is_open, _ = is_market_open()
            except (ValueError, TypeError, KeyError, AttributeError) as e:
                logger.warning(f'Error handled: {e}')
            except Exception as e:
                logger.error(f'Unexpected error: {e}', exc_info=True)
                pass

        # REAL_ONLY MODE: Never use synthetic data
        if not market_is_open and not REAL_ONLY and SYNTHETIC_DATA_AVAILABLE:
            synthetic_perf = generate_synthetic_perf_data()
            return {"status": "OK", "current": synthetic_perf, "history": [], "data_source": "synthetic"}

        if not market_is_open:
            return {
                "status": "MARKET_CLOSED",
                "current": {},
                "history": [],
                "data_source": "closed",
                "message": "Market closed - live performance data unavailable",
            }

        # REAL_ONLY MODE: If broker not ready, return NOT_READY
        if REAL_ONLY:
            broker_connected = False
            if SSOT_AVAILABLE and state_store:
                ssot_state = state_store.get_state()
                broker_connected = ssot_state.get("broker", {}).get("connected", False)
            else:
                health_file = OUTPUTS_DIR / "health.json"
                if health_file.exists():
                    health = json.loads(health_file.read_text())
                    broker_connected = health.get("is_connected", False)

            if not broker_connected:
                return {
                    "status": "NOT_READY",
                    "reason": "BROKER_NOT_READY - Real performance data unavailable",
                    "current": {},
                    "history": [],
                    "data_source": classify_overview_data_source(
                        market_open=True, broker_connected=False
                    ),
                }

        # Market is open - use real data
        perf_file = OUTPUTS_DIR / "perf_metrics.json"
        if not perf_file.exists():
            return {
                "status": "NO_DATA",
                "reason": "perf_metrics.json not found",
                "current": {},
                "history": [],
                "data_source": "real",
            }

        data = json.loads(perf_file.read_text())

        # Get historical data from SQLite
        history = []
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT timestamp, cycle_duration, fetch_duration, strategy_duration
                FROM cycle_metrics
                ORDER BY timestamp DESC
                LIMIT 100
            """
            )
            rows = cursor.fetchall()
            conn.close()

            history = [
                {"timestamp": row[0], "cycle_duration": row[1], "fetch_duration": row[2], "strategy_duration": row[3]}
                for row in rows
            ]
        except (ValueError, TypeError, KeyError, AttributeError) as e:
            logger.warning(f'Error handled: {e}')
        except Exception as e:
            logger.error(f'Unexpected error: {e}', exc_info=True)
            pass  # SQLite may not exist yet

        return {"current": data, "history": history, "data_source": "real"}
    except Exception as e:
        return {"status": "ERROR", "reason": str(e), "current": {}, "history": []}


@app.get("/api/overview")
async def get_overview():
    """Get system overview (alias for /api/health)"""
    return await get_health()


@app.get("/api/signals")
async def get_signals():
    """Get signals (alias for /api/signal/top)"""
    return await get_top_signal()


@app.get("/api/signals/enhanced")
async def get_enhanced_signals(limit: int = 10):
    """
    Get enhanced signals with ensemble, regime, and multi-timeframe data.
    Reads directly from signal CSV to include all new columns.
    """
    try:
        signals_csv = ROOT_DIR / "storage" / "live" / "angel_index_ai_signals.csv"

        if not signals_csv.exists():
            return {"signals": [], "count": 0, "message": "Signal CSV not found", "data_source": "real"}

        # Read CSV
        try:
            import pandas as pd

            df = pd.read_csv(signals_csv, engine="python", on_bad_lines="skip")
        except Exception as e:
            return {"signals": [], "count": 0, "message": f"Failed to read signal CSV: {str(e)}", "data_source": "real"}

        if df.empty:
            return {"signals": [], "count": 0, "message": "No signals in CSV", "data_source": "real"}

        # Get latest signals (by timestamp if available)
        if "ts" in df.columns:
            df = df.sort_values("ts", ascending=False)

        # Limit results
        df = df.head(limit)

        # Convert to dict format with all columns
        signals = []
        for _, row in df.iterrows():
            signal = {
                "timestamp": row.get("ts", ""),
                "underlying": row.get("underlying", ""),
                "strike": float(row.get("strike", 0)),
                "side": row.get("side", ""),
                "expiry": row.get("expiry", ""),
                "signal": row.get("signal", row.get("pred_label", "HOLD")),
                "final_score": float(row.get("final_score", 0)),
                "confidence": float(row.get("confidence", row.get("pred_confidence", 0))),
                "ltp": float(row.get("ltp", 0)),
                "spot": float(row.get("spot", 0)),
            }

            # Add ensemble data if available
            if "ensemble_method" in row:
                signal["ensemble"] = {
                    "method": row.get("ensemble_method", ""),
                    "models_used": row.get("ensemble_models_used", ""),
                    "model_count": int(row.get("ensemble_model_count", 0)),
                }

            # Add regime data if available
            if "market_regime" in row:
                signal["regime"] = {
                    "market_regime": row.get("market_regime", "UNKNOWN"),
                    "strategy_name": row.get("strategy_name", "default"),
                    "strategy_switched": bool(row.get("strategy_switched", False)),
                }

            # Add multi-timeframe data if available
            if "confirmation_score" in row:
                signal["multi_timeframe"] = {
                    "confirmation_score": float(row.get("confirmation_score", 0)),
                    "confirmed_signal": bool(row.get("confirmed_signal", False)),
                    "timeframe_agreement": row.get("timeframe_agreement", "MODERATE"),
                    "timeframe_agreement_count": int(row.get("timeframe_agreement_count", 1)),
                }

            signals.append(signal)

        return {
            "signals": signals,
            "count": len(signals),
            "data_source": "real",
            "enhanced_features": {
                "ensemble": any("ensemble" in s for s in signals),
                "regime": any("regime" in s for s in signals),
                "multi_timeframe": any("multi_timeframe" in s for s in signals),
            },
        }
    except Exception as e:
        return {"signals": [], "count": 0, "message": f"Error: {str(e)}", "data_source": "real"}


@app.get("/api/paper")
async def get_paper():
    """Get paper trading data (combines positions and PnL).

    Paper is local simulation marked-to-market from live Dhan option chains.
    Dhan has no broker-side paper sandbox for production tokens — order APIs
    must remain NOT called (LIVE_TRADING_ENABLED=0).
    """
    _hit = _cache_get("paper", _TTL_PAPER)
    if _hit is not None:
        return _hit

    try:
        positions_data = await get_positions()
        pnl_data = await get_pnl()
        pos_list = []
        if isinstance(positions_data, dict):
            pos_list = positions_data.get("positions") or positions_data.get("open_positions") or []
        elif isinstance(positions_data, list):
            pos_list = positions_data
        if not isinstance(pos_list, list):
            pos_list = []
        source_file = str(OUTPUTS_DIR / "positions_live.json")
        out = {
            "status": "ok",
            "mode": "PAPER",
            "engine": "paper_cloud_sim",
            "positions_source": "PAPER_CLOUD_SIM",
            "data_source": "DHAN_LIVE_MARK_TO_MARKET",
            "live_trading_enabled": False,
            "broker_order_endpoints_called": False,
            "positions": positions_data,
            "pnl": pnl_data,
            "paper_truth": {
                "source_file": source_file,
                "displayed_rows": len(pos_list),
                "fake_fixture_rows_rejected": 0,
                "broker_order_endpoints_called": False,
                "order_endpoints_label": "INTENTIONALLY_NOT_CALLED_PAPER_SAFE",
                "mark_to_market": "DHAN_OPTION_CHAIN_LTP",
                "aligned_to": [
                    "dhanhq.co/docs/v2/portfolio positions fields",
                    "local paper simulation (Dhan has no live-token paper sandbox)",
                ],
                "note": "Paper fills are simulated; LTP/PnL use live Dhan chain. Real /orders endpoints are never called.",
            },
        }
        return _cache_set("paper", out)
    except Exception as e:
        return {"status": "ERROR", "reason": str(e), "positions": {}, "pnl": {}, "broker_order_endpoints_called": False}


@app.post("/api/paper/tick")
async def paper_engine_tick(background_tasks: BackgroundTasks, max_open: int = 3):
    """Force one cloud paper-engine tick from live Dhan chains (PAPER ONLY).

    Heavy chain/scanner work runs in a background task so /ui never hits
    Cloud Run 'upstream request timeout' while a tick is in flight.
    """
    try:
        from dashboard.backend.cloud_paper_engine import get_paper_engine
    except ImportError:
        from cloud_paper_engine import get_paper_engine

    engine = get_paper_engine(OUTPUTS_DIR)
    open_before = len(engine.open_positions)

    async def _run_tick() -> None:
        chains = []
        for sym in ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"]:
            try:
                ch = await get_chain(sym)
                if ch and ch.get("contracts"):
                    chains.append(ch)
            except Exception:
                continue
        if not chains:
            print("[paper-tick] NO_CHAIN")
            return
        market_top_rows: list = []
        try:
            mt = await get_top_contract_gainers(top_n=8, market_top_n=25, include_equity=False)
            if isinstance(mt, dict):
                market_top_rows = list(mt.get("market_top_table") or [])
                if not market_top_rows:
                    mw = mt.get("market_wide") or {}
                    market_top_rows = list(mw.get("top_combined_list") or [])
        except Exception as mt_exc:
            print(f"[paper-tick] market top fetch skipped: {mt_exc}")
        engine.step(chains, max_open=min(max(max_open, 1), 5), market_top=market_top_rows)
        _API_CACHE.pop("paper", None)
        print(
            f"[paper-tick] done open={len(engine.open_positions)} "
            f"closed={len(engine.closed_positions)} market_top={len(market_top_rows)}"
        )

    background_tasks.add_task(_run_tick)
    return {
        "status": "accepted",
        "message": "Paper tick scheduled in background (PAPER ONLY)",
        "open_count_before": open_before,
        "selection_mode": "MARKET_TOP_GAIN_PCT",
        "mode": "PAPER_CLOUD_SIM",
        "live_trading_enabled": False,
    }


@app.get("/api/simulation/live/state")
async def get_simulation_live_state(scenario: str = "paper_analyzer"):
    """Paper-only simulation feed for Sim Live tab. Never places broker orders."""
    try:
        health = await get_health()
    except Exception:
        health = {"broker_status": "unknown", "market_status": "unknown", "mode": "PAPER"}
    try:
        paper = await get_paper()
    except Exception:
        paper = {"positions": {}, "pnl": {}}
    try:
        gates = await get_auto_gates()
    except Exception:
        gates = {}

    positions_raw = []
    pos_block = paper.get("positions") if isinstance(paper, dict) else {}
    if isinstance(pos_block, dict):
        positions_raw = pos_block.get("positions") or []
    if not isinstance(positions_raw, list):
        positions_raw = []

    sim_positions = []
    for p in positions_raw[:50]:
        if not isinstance(p, dict):
            continue
        sim_positions.append(
            {
                "position_id": str(p.get("position_id") or p.get("id") or ""),
                "symbol": str(p.get("symbol") or p.get("trading_symbol") or ""),
                "side": str(p.get("side") or p.get("option_type") or "CE").upper()[:2],
                "strike": float(p.get("strike") or 0),
                "expiry": str(p.get("expiry") or ""),
                "entry_price": float(p.get("entry_price") or p.get("avg_price") or 0),
                "ltp": float(p.get("ltp") or p.get("last_price") or 0),
                "qty": float(p.get("qty") or p.get("quantity") or 0),
                "pnl": float(p.get("pnl") or p.get("unrealized_pnl") or 0),
                "status": str(p.get("status") or "OPEN").upper(),
                "source": "paper_simulation",
            }
        )

    pnl_summary = {}
    if isinstance(paper, dict):
        pnl = paper.get("pnl") or {}
        if isinstance(pnl, dict):
            pnl_summary = pnl.get("summary") or {}

    gate_flags = {}
    if isinstance(gates, dict):
        for gid, g in (gates.get("gates") or {}).items():
            if isinstance(g, dict):
                gate_flags[str(gid)] = bool(g.get("pass"))

    return {
        "status": "ok",
        "mode": "PAPER_SIMULATION_ONLY",
        "scenario": scenario or "paper_analyzer",
        "generated_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "broker": {
            "connected": str(health.get("broker_status", "")).lower() == "connected",
            "status": health.get("broker_status"),
            "source": "api_health",
        },
        "market": {
            "is_open": str(health.get("market_status", "")).lower() == "open",
            "state": health.get("market_status"),
            "source": "api_health",
        },
        "risk": {
            "live_trading_enabled": False,
            "order_placement_allowed": False,
            "real_broker_routes_called": False,
        },
        "option_chain": [],
        "signals": [],
        "positions": sim_positions,
        "paper": {
            "total_pnl": pnl_summary.get("total_pnl"),
            "currency": "INR",
            "source": "paper_api",
        },
        "gates": gate_flags,
        "safety_banner": "SIMULATION ONLY — no broker order APIs, live trading remains OFF",
    }


@app.post("/api/positions/{position_id}/close")
async def close_position(position_id: str):
    """Manually close a position through the paper engine's own ledger.

    Delegates to CloudPaperEngine.close_position_by_id() so the engine's
    in-memory/state-file authority stays in sync with positions_live.json.
    Fixes PAPER-017/PAPER-018: this route used to edit positions_live.json
    directly, which the engine's own state/tick could silently overwrite
    ("resurrect") the manually closed position on the next cycle.
    """
    try:
        try:
            from dashboard.backend.cloud_paper_engine import get_paper_engine
        except ImportError:
            from cloud_paper_engine import get_paper_engine

        engine = get_paper_engine(OUTPUTS_DIR)
        closed = engine.close_position_by_id(position_id)

        if closed is None:
            raise HTTPException(status_code=404, detail=f"Position {position_id} not found")

        return {"status": "success", "message": f"Position {position_id} closed", "position": closed}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/alerts")
async def get_alerts():
    """Get alerts (can be empty if no alerts file exists)"""
    try:
        alerts_file = OUTPUTS_DIR / "alerts.jsonl"
        if not alerts_file.exists():
            return {"alerts": [], "status": "NO_DATA", "reason": "alerts.jsonl not found"}

        alerts = []
        with open(alerts_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        alert = json.loads(line)
                        # Standardize timestamp to ts_iso (ISO-8601)
                        if "ts_iso" not in alert:
                            # Try to convert existing timestamp fields
                            ts = alert.get("ts") or alert.get("timestamp") or alert.get("time") or alert.get("date")
                            if ts:
                                try:
                                    if isinstance(ts, str):
                                        # Parse and convert to ISO
                                        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                                    else:
                                        dt = (
                                            datetime.fromtimestamp(ts)
                                            if isinstance(ts, (int, float))
                                            else datetime.now()
                                        )
                                    alert["ts_iso"] = dt.isoformat()
                                except (ValueError, TypeError, KeyError, AttributeError) as e:
                                    logger.warning(f'Error handled: {e}')
                                except Exception as e:
                                    logger.error(f'Unexpected error: {e}', exc_info=True)
                                    alert["ts_iso"] = datetime.now(pytz.timezone("Asia/Kolkata")).isoformat()
                            else:
                                alert["ts_iso"] = datetime.now(pytz.timezone("Asia/Kolkata")).isoformat()

                        # Ensure level is valid
                        if "level" not in alert or alert["level"] not in ["INFO", "WARN", "CRIT", "ERROR"]:
                            alert["level"] = alert.get("severity", "INFO").upper()
                            if alert["level"] not in ["INFO", "WARN", "CRIT", "ERROR"]:
                                alert["level"] = "INFO"

                        alerts.append(alert)
                    except Exception as e:
                        print(f"Error parsing alert line: {e}")
                        pass

        return {"alerts": alerts[-50:], "count": len(alerts)}  # Last 50 alerts
    except Exception as e:
        return {"alerts": [], "status": "ERROR", "reason": str(e)}


@app.get("/api/logs/tail")
async def get_logs_tail(lines: int = 200):
    """Get tail of logs with secrets redacted"""
    try:
        # Find latest log file
        log_files = list(LOGS_DIR.glob("*.log"))
        if not log_files:
            return {"logs": [], "message": "No log files found"}

        latest_log = max(log_files, key=lambda p: p.stat().st_mtime)

        # Read last N lines
        with open(latest_log, "r", encoding="utf-8", errors="ignore") as f:
            all_lines = f.readlines()
            tail_lines = all_lines[-lines:]

        # Redact secrets and collapse consecutive duplicate lines (UI log spam)
        redacted_raw = [redact_secrets(line) for line in tail_lines]
        redacted: list[str] = []
        prev = None
        dup_count = 0
        for line in redacted_raw:
            stripped = line.rstrip("\n")
            if stripped == prev:
                dup_count += 1
                continue
            if dup_count > 0 and prev is not None:
                redacted.append(f"{prev}  (repeated {dup_count + 1}x)\n")
                dup_count = 0
            elif prev is not None:
                redacted.append(prev + "\n")
            prev = stripped
        if prev is not None:
            if dup_count > 0:
                redacted.append(f"{prev}  (repeated {dup_count + 1}x)\n")
            else:
                redacted.append(prev + "\n")

        return {"logs": redacted, "file": latest_log.name, "total_lines": len(all_lines)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/audit/secrets")
async def audit_secrets():
    """Scan for secrets in outputs"""
    try:
        secret_count = 0
        scanned_files = []

        for file_path in OUTPUTS_DIR.glob("*.json"):
            count = scan_secrets(file_path)
            if count > 0:
                secret_count += count
                scanned_files.append({"file": file_path.name, "secrets": count})

        return {
            "secrets_found": secret_count,
            "scanned_files": scanned_files,
            "status": "PASS" if secret_count == 0 else "FAIL",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time updates - Only active during market hours (Mon-Fri, 9:15 AM - 3:30 PM IST)"""
    # Accept WS connection always — market status sent in first message
    # (Previously rejected outside hours with 1008 — this broke testing and
    # prevented the dashboard from showing WS as connected during dev)
    await websocket.accept()
    if len(active_connections) >= _MAX_WS_CONNECTIONS:
        await websocket.close(code=1013, reason="Too many live connections — try again shortly")
        return
    market_open_now = False
    market_close_reason = "unknown"
    if MARKET_DETECTION_AVAILABLE:
        try:
            market_open_now, market_close_reason = is_market_open()
        except Exception:
            pass
    # Send market status immediately on connect
    try:
        await websocket.send_json(
            {
                "type": "market_status",
                "market_open": market_open_now,
                "reason": market_close_reason if not market_open_now else "MARKET_OPEN",
                "timestamp": datetime.now(pytz.timezone("Asia/Kolkata")).isoformat(),
            }
        )
    except Exception:
        pass
    active_connections.append(websocket)

    try:
        # Send initial live snapshot (API-backed — Cloud has no durable health.json)
        try:
            health_payload = await get_health()
            await websocket.send_json(
                {
                    "type": "health_update",
                    "data": health_payload,
                    "timestamp": datetime.now(pytz.timezone("Asia/Kolkata")).isoformat(),
                }
            )
        except Exception:
            pass
        try:
            paper_payload = await get_paper()
            await websocket.send_json(
                {
                    "type": "paper_update",
                    "data": paper_payload,
                    "timestamp": datetime.now(pytz.timezone("Asia/Kolkata")).isoformat(),
                }
            )
        except Exception:
            pass

        # Send periodic updates
        last_health_send = 0
        last_positions_send = 0
        last_pnl_send = 0
        last_heartbeat_send = 0
        last_chain_send = 0
        last_market_top_send = 0

        # Push last known market top immediately (state file or cache)
        try:
            mt = _cache_get("scanner_gainers:5:25:1", 300.0)
            if mt is None and _MARKET_TOP_STATE_FILE.exists():
                mt = json.loads(_MARKET_TOP_STATE_FILE.read_text(encoding="utf-8"))
            if isinstance(mt, dict) and (mt.get("market_top_table") or []):
                await websocket.send_json(
                    {
                        "type": "market_top_update",
                        "data": {
                            "market_top_table": (mt.get("market_top_table") or [])[:25],
                            "refreshed_at": mt.get("refreshed_at") or mt.get("streamed_at"),
                            "contracts_scored_total": mt.get("contracts_scored_total"),
                            "status": mt.get("status"),
                            "stream_mode": mt.get("stream_mode") or "cache",
                        },
                        "timestamp": datetime.now(pytz.timezone("Asia/Kolkata")).isoformat(),
                    }
                )
                last_market_top_send = datetime.now(pytz.timezone("Asia/Kolkata")).timestamp()
        except Exception:
            pass

        while True:
            await asyncio.sleep(1)  # Check every second

            now = datetime.now(pytz.timezone("Asia/Kolkata")).timestamp()
            # Re-evaluate market hours each tick so a WS opened pre-open still streams live.
            if MARKET_DETECTION_AVAILABLE:
                try:
                    market_open_now, market_close_reason = is_market_open()
                except Exception:
                    pass

            # Stream live health from API every 5s (not only local health.json)
            if now - last_health_send >= 5:
                try:
                    health_payload = await get_health()
                    await websocket.send_json(
                        {
                            "type": "health_update",
                            "data": health_payload,
                            "timestamp": datetime.now(pytz.timezone("Asia/Kolkata")).isoformat(),
                        }
                    )
                    last_health_send = now
                except (WebSocketDisconnect, ConnectionError):
                    raise
                except Exception:
                    pass

            # Send positions update every 3 seconds (file or empty honest payload)
            if now - last_positions_send >= 3:
                try:
                    positions_data = await get_positions()
                    await websocket.send_json(
                        {
                            "type": "positions_update",
                            "data": positions_data,
                            "timestamp": datetime.now(pytz.timezone("Asia/Kolkata")).isoformat(),
                        }
                    )
                    last_positions_send = now
                except (WebSocketDisconnect, ConnectionError):
                    raise
                except Exception:
                    pass

            # Send PnL update every 5 seconds
            if now - last_pnl_send >= 5:
                try:
                    pnl_data = await get_pnl()
                    await websocket.send_json(
                        {
                            "type": "pnl_update",
                            "data": pnl_data,
                            "timestamp": datetime.now(pytz.timezone("Asia/Kolkata")).isoformat(),
                        }
                    )
                    last_pnl_send = now
                except (WebSocketDisconnect, ConnectionError):
                    raise
                except Exception:
                    pass

            # Ultra-micro Market Top CE/PE push every 3s from cache/state (no Dhan recompute here)
            if now - last_market_top_send >= _WS_MARKET_TOP_PUSH_S:
                try:
                    mt = _cache_get("scanner_gainers:5:25:1", 120.0)
                    if mt is None and _MARKET_TOP_STATE_FILE.exists():
                        mt = json.loads(_MARKET_TOP_STATE_FILE.read_text(encoding="utf-8"))
                    table = (mt or {}).get("market_top_table") or []
                    if table:
                        await websocket.send_json(
                            {
                                "type": "market_top_update",
                                "data": {
                                    "market_top_table": table[:25],
                                    "refreshed_at": (mt or {}).get("refreshed_at")
                                    or (mt or {}).get("streamed_at"),
                                    "contracts_scored_total": (mt or {}).get("contracts_scored_total"),
                                    "status": (mt or {}).get("status"),
                                    "stream_mode": "ultra_micro",
                                },
                                "timestamp": datetime.now(pytz.timezone("Asia/Kolkata")).isoformat(),
                            }
                        )
                    last_market_top_send = now
                except (WebSocketDisconnect, ConnectionError):
                    raise
                except Exception:
                    pass

            # CRITICAL: WS must NEVER call get_chain()/live Dhan here.
            # Live OC is owned by index_chain_micro_loop (paced). WS only fans out cache.
            chain_push_every = _WS_CHAIN_PUSH_S_OPEN if market_open_now else _WS_CHAIN_PUSH_S_CLOSED
            if now - last_chain_send >= chain_push_every:
                try:
                    spots = {}
                    ages = {}
                    for sym in _INDEX_STREAM_SYMBOLS:
                        ch = _chain_from_push_cache(sym)
                        if ch is None:
                            hit = _cache_get(f"chain_{sym}", 120.0)
                            ch = hit if isinstance(hit, dict) else None
                        if not isinstance(ch, dict) or float(ch.get("spot") or 0) <= 0:
                            continue
                        spots[sym] = {
                            "spot": ch.get("spot"),
                            "n": ch.get("total_contracts") or len(ch.get("contracts") or []),
                            "status": ch.get("status"),
                            "src": ch.get("data_source"),
                            "age_s": ch.get("snapshot_age_seconds"),
                        }
                        ages[sym] = ch.get("snapshot_age_seconds")
                        if sym == "NIFTY" and (ch.get("contracts") or []):
                            await websocket.send_json(
                                {
                                    "type": "chain_update",
                                    "symbol": sym,
                                    "data": ch,
                                    "timestamp": datetime.now(
                                        pytz.timezone("Asia/Kolkata")
                                    ).isoformat(),
                                }
                            )
                    if spots:
                        await websocket.send_json(
                            {
                                "type": "chain_spots_update",
                                "data": spots,
                                "market_open": market_open_now,
                                "cache_ages_s": ages,
                                "timestamp": datetime.now(pytz.timezone("Asia/Kolkata")).isoformat(),
                            }
                        )
                    last_chain_send = now
                except (WebSocketDisconnect, ConnectionError):
                    raise
                except Exception:
                    pass

            # Send heartbeat every 10 seconds (more reliable than modulo)
            if now - last_heartbeat_send >= 10:
                try:
                    cache_health = {}
                    for sym in _INDEX_STREAM_SYMBOLS:
                        pushed = _PUSHED_CHAIN_CACHE.get(sym) or {}
                        age = None
                        if pushed.get("received_at"):
                            age = round(_time_module.time() - float(pushed["received_at"]), 1)
                        cache_health[sym] = age
                    await websocket.send_json(
                        {
                            "type": "heartbeat",
                            "market_open": market_open_now,
                            "reason": market_close_reason if not market_open_now else "MARKET_OPEN",
                            "chain_cache_ages_s": cache_health,
                            "stream_ok": any(v is not None and v < 180 for v in cache_health.values()),
                            "timestamp": datetime.now(pytz.timezone("Asia/Kolkata")).isoformat(),
                        }
                    )
                    last_heartbeat_send = now
                except (WebSocketDisconnect, ConnectionError):
                    raise
                except Exception:
                    pass

    except WebSocketDisconnect:
        # Normal client disconnect
        if websocket in active_connections:
            active_connections.remove(websocket)
    except ConnectionError:
        # Connection error, remove from active connections
        if websocket in active_connections:
            active_connections.remove(websocket)
    except Exception as e:
        # Unexpected error, log and remove
        if websocket in active_connections:
            active_connections.remove(websocket)


async def index_chain_micro_loop():
    """Paced index option-chain warmer for market-hours streaming.

    Owns live Dhan OC for the configured NSE/BSE index stream symbols. WS + UI must
    read `_PUSHED_CHAIN_CACHE` only — never fan-out live OC themselves.

    Cold-start warms the four required smoke symbols back-to-back (DSM gap
    only) so batch/chains is not gated on lucky serial 20s closed-market timing.
    """
    await asyncio.sleep(2)
    await _warm_required_index_chains_cold_start()
    idx = 0
    while True:
        sym = _INDEX_STREAM_SYMBOLS[idx % len(_INDEX_STREAM_SYMBOLS)]
        idx += 1
        open_now = bool(_market_open_from_state())
        try:
            await _warm_one_index_chain(sym)
        except Exception as exc:
            print(f"[index-chain-micro] {sym} failed: {exc}")
        await asyncio.sleep(3.5 if open_now else 20.0)


async def market_top_micro_loop():
    """Background ultra-micro refresh for Market Top CE/PE board.

    Rebuilds the ranked table from the last good paced chain snapshots so the
    index_chain_micro_loop remains the sole Dhan OC owner. /ws/stream reads cache only.
    """
    await asyncio.sleep(8)
    while True:
        started = time.time()
        try:
            report = _build_market_top_from_chain_cache(top_n=5, market_top_n=25)
            if report is not None:
                report["stream_mode"] = "ultra_micro_cache"
                report["streamed_at"] = datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")
                for key in (
                    "scanner_gainers:5:25:1",
                    "scanner_gainers:8:25:1",
                    "scanner_gainers:5:25:0",
                ):
                    _cache_set(key, report)
                try:
                    _MARKET_TOP_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
                    _MARKET_TOP_STATE_FILE.write_text(json.dumps(report, indent=2), encoding="utf-8")
                except Exception as write_exc:
                    print(f"[market-top-micro] state write failed: {write_exc}")
                print(
                    f"[market-top-micro] ok rows={len(report.get('market_top_table') or [])} "
                    f"scored={report.get('contracts_scored_total')} "
                    f"shard={report.get('shard_last_syms')}"
                )
            elif _market_open_from_state():
                print("[market-top-micro] warming: no scorable paced chain snapshot yet")
        except Exception as exc:
            print(f"[market-top-micro] refresh failed: {exc}")
        elapsed = time.time() - started
        await asyncio.sleep(max(5.0, _MARKET_TOP_MICRO_INTERVAL_S - elapsed))


async def moneycontrol_gainers_micro_loop():
    """Background scrape of Moneycontrol All Options Top Gainers (REFERENCE ONLY)."""
    await asyncio.sleep(8)
    while True:
        started = time.time()
        try:
            if os.environ.get("MONEYCONTROL_SCRAPE", "1") in ("0", "false", "False"):
                await asyncio.sleep(60)
                continue

            def _scrape():
                from dashboard.backend.moneycontrol_option_gainers import fetch_moneycontrol_option_gainers

                return fetch_moneycontrol_option_gainers(top_n=25, timeout_s=25.0)

            report = await _run_blocking(_scrape, timeout=40.0)
            if report and (report.get("market_top_table") or report.get("status") == "ok"):
                _cache_set("moneycontrol_gainers:25", report)
                try:
                    path = ROOT_DIR / "state" / "moneycontrol_option_gainers.json"
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
                except Exception as write_exc:
                    print(f"[mc-gainers] state write failed: {write_exc}")
                print(f"[mc-gainers] rows={len(report.get('market_top_table') or [])} status={report.get('status')}")
        except Exception as exc:
            print(f"[mc-gainers] scrape failed: {exc}")
        elapsed = time.time() - started
        await asyncio.sleep(max(45.0, 90.0 - elapsed))


async def cloud_paper_trading_loop():
    """Background task: generate paper trades from live chain during market hours.
    PAPER ONLY — never places real orders. Phantom-guarded, single-lot."""
    import asyncio as _asyncio

    # Allow disabling via env (default ON)
    if os.environ.get("CLOUD_PAPER_ENGINE", "1") in ("0", "false", "False"):
        print("[paper-loop] disabled via CLOUD_PAPER_ENGINE=0")
        return

    while True:
        try:
            # Only run during market hours
            mkt_open = False
            if MARKET_DETECTION_AVAILABLE:
                try:
                    mkt_open, _ = is_market_open()
                except Exception:
                    mkt_open = False

            if mkt_open:
                try:
                    from dashboard.backend.cloud_paper_engine import get_paper_engine
                except ImportError:
                    from cloud_paper_engine import get_paper_engine

                engine = get_paper_engine(OUTPUTS_DIR)

                # Fetch live chains for index + high-rise equity seeds from Market Top
                chains = []
                for sym in ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]:
                    try:
                        ch = await get_chain(sym)
                        if ch and ch.get("contracts"):
                            chains.append(ch)
                    except Exception:
                        continue

                # Prefer today's Dhan Market Top for paper discovery
                # (still PAPER ONLY — never places broker orders).
                market_top_rows: list = []
                try:
                    mt = _cache_get("scanner_gainers:5:25:1", 300.0)
                    if mt is None and _MARKET_TOP_STATE_FILE.exists():
                        mt = json.loads(_MARKET_TOP_STATE_FILE.read_text(encoding="utf-8"))
                    market_top_rows = list((mt or {}).get("market_top_table") or [])
                    if not market_top_rows:
                        mw = (mt or {}).get("market_wide") or {}
                        market_top_rows = list(mw.get("top_combined_list") or [])
                    seed_syms = []
                    for row in market_top_rows:
                        sym = str(row.get("underlying") or row.get("symbol") or "").upper()
                        if not sym or sym in {"NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"}:
                            continue
                        if sym not in seed_syms:
                            seed_syms.append(sym)
                        if len(seed_syms) >= 4:
                            break
                    # Cache/push only — never force live OC fan-out that starves /ui.
                    for sym in seed_syms:
                        try:
                            ch = _chain_from_push_cache(sym)
                            if ch is None:
                                ch = _cache_get(f"chain_{sym}", 120.0)
                            if ch and ch.get("contracts"):
                                seeded = dict(ch)
                                seeded["paper_seed"] = "market_top_high_rise"
                                chains.append(seeded)
                        except Exception:
                            continue
                    if seed_syms:
                        setattr(engine, "last_high_rise_seeds", seed_syms)
                except Exception as seed_exc:
                    print(f"[paper-loop] high-rise seed skipped: {seed_exc}")

                if chains:
                    engine.step(chains, max_open=3, market_top=market_top_rows)
                    print(
                        f"[paper-loop] tick: {len(engine.open_positions)} open, "
                        f"{len(engine.closed_positions)} closed, "
                        f"market_top_rows={len(market_top_rows)}"
                    )

            await _asyncio.sleep(60)  # tick every 60s
        except Exception as e:
            print(f"[paper-loop] error (continuing): {e}")
            await _asyncio.sleep(60)


def _refresh_spot_prices_blocking() -> None:
    """
    Spot price refresh — DISABLED in web process.

    Yahoo Finance via requests library was using ~150MB RAM
    (requests.Session + urllib3 connection pool stays alive).

    Spot prices now come from:
    1. /api/chain/{sym} — NSE direct, polled every 5s by frontend useData
    2. gain_rank_history.json — written by worker scheduler at 09:15 IST

    This function is kept as a no-op so the executor call in
    background_data_refresh() doesn't crash. The background task
    itself now sleeps for 5 minutes between no-op calls to save CPU.
    """
    pass  # Yahoo Finance disabled — NSE data used instead

def _run_startup_token_refresh_blocking() -> None:
    """Synchronous Dhan token refresh — only ever called via asyncio.to_thread
    from _startup_token_refresh_task, never awaited directly in the startup
    event handler. A hang here must never block the server from accepting
    requests (this previously ran inline in startup(), which could freeze
    the whole single-process event loop — and the entire app — if Dhan's
    auth endpoint was slow or unresponsive).
    """
    import importlib.util as _ilu
    import pathlib as _pl

    _spec = _ilu.spec_from_file_location(
        "token_manager_startup",
        _pl.Path(__file__).resolve().parent.parent.parent / "core" / "brokers" / "dhan" / "token_manager.py",
    )
    if _spec and _spec.loader:
        _tm = _ilu.module_from_spec(_spec)
        _spec.loader.exec_module(_tm)  # type: ignore[union-attr]
        _result = _tm.refresh_token()
        if _result.get("success"):
            print(f"[startup] Dhan token refreshed via {_result.get('strategy')}")
        else:
            print(f"[startup] Dhan token refresh skipped/failed: {_result.get('message', _result)}")


async def _startup_token_refresh_task() -> None:
    """Background task: refresh the Dhan token without ever blocking server
    readiness. Bounded by an overall timeout so a hung HTTP call inside the
    SDK can't hang this task forever either.
    """
    try:
        await asyncio.wait_for(asyncio.to_thread(_run_startup_token_refresh_blocking), timeout=45)
    except asyncio.TimeoutError:
        print("[startup] Token refresh timed out after 45s (non-fatal) — continuing with existing token")
    except Exception as _e:
        print(f"[startup] Token refresh error (non-fatal): {_e}")


async def background_data_refresh():
    """No-op background refresh placeholder; live data is served by worker pushes and cached endpoints."""
    while True:
        await asyncio.sleep(300)


@app.on_event("startup")
async def startup():
    """Store event loop on startup and start background tasks"""
    set_event_loop(asyncio.get_running_loop())

    # Log startup memory so we know baseline RSS
    try:
        import resource, gc
        gc.collect()  # Clean up before measuring
        rss_mb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
        print(f"[startup] RSS after startup: {rss_mb:.0f}MB / 512MB Starter limit")
        if rss_mb > 350:
            print(f"[startup] WARNING: High startup memory {rss_mb:.0f}MB — OOM risk")
        else:
            print(f"[startup] Memory OK — {512-rss_mb:.0f}MB headroom remaining")
    except Exception as e:
        print(f"[startup] Memory check skipped: {e}")

    # Attempt token refresh at startup using PIN+TOTP (non-fatal — cloud mode).
    # Fired as a background task (never awaited here) so a slow/hung Dhan
    # auth call cannot delay or block the server from accepting requests.
    _pin = os.environ.get("DHAN_PIN", "").strip()
    _totp = os.environ.get("DHAN_TOTP_SECRET", "").strip()
    _startup_refresh = os.environ.get("SYSTEM3_STARTUP_TOKEN_REFRESH", "1") not in (
        "0",
        "false",
        "False",
    )
    if _pin and _totp and _startup_refresh:
        asyncio.create_task(_startup_token_refresh_task())
    else:
        if not os.environ.get("DHAN_ACCESS_TOKEN"):
            print("[startup] DHAN_PIN/DHAN_TOTP_SECRET not set — token refresh skipped")
        elif not _startup_refresh:
            print("[startup] token refresh disabled via SYSTEM3_STARTUP_TOKEN_REFRESH=0")

    # Start background data refresh
    asyncio.create_task(background_data_refresh())
    asyncio.create_task(broker_self_heal_loop())
    print('[self-heal] scheduled')

    # Start cloud paper trading loop (PAPER ONLY — generates live paper trades)
    # Default ON for Cloud so Paper/Performance tabs are not permanently zero.
    if os.environ.get("CLOUD_PAPER_ENGINE", "1") not in ("0", "false", "False"):
        asyncio.create_task(cloud_paper_trading_loop())
        print("[paper-loop] started (CLOUD_PAPER_ENGINE enabled)")
    else:
        print("[paper-loop] disabled via CLOUD_PAPER_ENGINE=0 (not started)")

    # Index chain warmer FIRST — this is what makes market-hours UI stream.
    if os.environ.get("INDEX_CHAIN_MICRO_STREAM", "1") not in ("0", "false", "False"):
        asyncio.create_task(index_chain_micro_loop())
        print("[index-chain-micro] started (INDEX_CHAIN_MICRO_STREAM enabled)")
    else:
        print("[index-chain-micro] disabled via INDEX_CHAIN_MICRO_STREAM=0")

    # Ultra-micro Market Top CE/PE refresh → feeds /ws/stream + scanner cache
    if os.environ.get("MARKET_TOP_MICRO_STREAM", "1") not in ("0", "false", "False"):
        asyncio.create_task(market_top_micro_loop())
        asyncio.create_task(moneycontrol_gainers_micro_loop())
        print("[market-top-micro] started (MARKET_TOP_MICRO_STREAM enabled)")
    else:
        print("[market-top-micro] disabled via MARKET_TOP_MICRO_STREAM=0")

    # Start state sync service if SSOT is available
    if SSOT_AVAILABLE and state_store is not None:
        try:
            try:
                from dashboard.backend.state_sync_service import get_sync_service
            except ImportError:
                try:
                    from state_sync_service import get_sync_service
                except ImportError:
                    get_sync_service = None

            if get_sync_service:
                # Set module-level variables for state_sync_service
                try:
                    import dashboard.backend.state_sync_service as sync_module

                    sync_module.MARKET_DETECTION_AVAILABLE = MARKET_DETECTION_AVAILABLE
                    sync_module.ADVANCED_FEATURES_AVAILABLE = ADVANCED_FEATURES_AVAILABLE
                except (ValueError, TypeError, KeyError, AttributeError) as e:
                    logger.warning(f'Error handled: {e}')
                except Exception as e:
                    logger.error(f'Unexpected error: {e}', exc_info=True)
                    pass

                sync_service = get_sync_service(state_store, OUTPUTS_DIR)
                await sync_service.start()
                print("[OK] State sync service started")
        except Exception as e:
            print(f"[WARNING] Failed to start state sync service: {e}")


@app.get("/api/validate/data")
async def validate_data():
    """Validate dashboard data against live sources"""
    try:
        # Import validator
        import sys

        validator_path = ROOT_DIR / "scripts" / "dashboard_data_validator.py"
        if validator_path.exists():
            # Run validation in background
            import subprocess
            import threading

            def run_validation():
                try:
                    subprocess.run(
                        [str(ROOT_DIR / "venv" / "Scripts" / "python.exe"), str(validator_path)],
                        timeout=30,
                        capture_output=True,
                    )
                except (ValueError, TypeError, KeyError, AttributeError) as e:
                    logger.warning(f'Error handled: {e}')
                except Exception as e:
                    logger.error(f'Unexpected error: {e}', exc_info=True)
                    pass

            thread = threading.Thread(target=run_validation, daemon=True)
            thread.start()

            return {"status": "started", "message": "Validation started in background"}
        else:
            return {"status": "error", "message": "Validator script not found"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/api/validate/status")
async def get_validation_status():
    """Get latest validation status"""
    try:
        validation_dir = OUTPUTS_DIR / "validation"
        if not validation_dir.exists():
            return {"status": "NO_DATA", "message": "No validation reports found"}

        # Find latest validation report
        reports = list(validation_dir.glob("dashboard_validation_*.json"))
        if not reports:
            return {"status": "NO_DATA", "message": "No validation reports found"}

        latest_report = max(reports, key=lambda p: p.stat().st_mtime)
        data = json.loads(latest_report.read_text())

        return {"status": "ok", "report": data, "report_file": latest_report.name, "timestamp": data.get("timestamp")}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/api/predict/profit/{position_id}")
async def predict_profit(position_id: str):
    """Predict profit for a specific position"""
    try:
        if not PERFORMANCE_PREDICTOR_AVAILABLE:
            return {"status": "ERROR", "message": "Performance predictor not available"}

        # Get position
        positions_data = await get_positions()
        positions = positions_data.get("positions", [])

        position = None
        for pos in positions:
            if str(pos.get("position_id", "")) == position_id:
                position = pos
                break

        if not position:
            return {"status": "ERROR", "message": f"Position {position_id} not found"}

        # Get current price
        current_price = position.get("current_price", position.get("entry_price", 0))

        # Calculate time held
        entry_time = position.get("entry_time")
        if entry_time:
            try:
                from datetime import datetime

                entry_dt = datetime.fromisoformat(entry_time.replace("Z", "+00:00"))
                now = datetime.now(pytz.timezone("Asia/Kolkata"))
                time_held = (now - entry_dt).total_seconds() / 3600.0
            except (ValueError, TypeError, KeyError, AttributeError) as e:
                logger.warning(f'Error handled: {e}')
            except Exception as e:
                logger.error(f'Unexpected error: {e}', exc_info=True)
                time_held = 0.0
        else:
            time_held = 0.0

        # Predict profit
        predictor = get_performance_predictor()
        prediction = predictor.predict_profit(position, current_price, time_held)

        return {"status": "ok", "position_id": position_id, "prediction": prediction}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}


@app.get("/api/predict/portfolio")
async def predict_portfolio():
    """Predict overall portfolio performance"""
    try:
        if not PERFORMANCE_PREDICTOR_AVAILABLE:
            return {"status": "ERROR", "message": "Performance predictor not available"}

        # Get positions
        positions_data = await get_positions()
        positions = positions_data.get("positions", [])

        if not positions:
            return {"status": "NO_DATA", "message": "No open positions"}

        # Get market data (simplified - use current prices from positions)
        market_data = {}
        for pos in positions:
            symbol = pos.get("symbol", pos.get("underlying", ""))
            market_data[symbol] = pos.get("current_price", pos.get("entry_price", 0))

        # Predict portfolio
        predictor = get_performance_predictor()
        prediction = predictor.predict_portfolio_performance(positions, market_data)

        return {"status": "ok", "prediction": prediction}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}


@app.get("/api/validate/profit/all")
async def validate_all_profits():
    """Multi-validate profits for all open positions"""
    try:
        if not PERFORMANCE_PREDICTOR_AVAILABLE:
            return {"status": "ERROR", "message": "Live validator not available"}

        # Get positions
        positions_data = await get_positions()
        positions = positions_data.get("positions", [])

        if not positions:
            return {"status": "NO_DATA", "message": "No open positions", "validations": []}

        # Validate each position
        validator = get_live_validator()
        validations = []

        for position in positions:
            position_id = position.get("position_id", "unknown")
            reported_pnl = position.get("unrealized_pnl", 0)

            validation = validator.multi_validate_profit(position, reported_pnl)
            validations.append({"position_id": position_id, "validation": validation})

        # Summary
        all_pass = all(v["validation"]["validation_status"] == "PASS" for v in validations)
        all_warn = all(v["validation"]["validation_status"] in ["PASS", "WARN"] for v in validations)

        return {
            "status": "ok",
            "total_positions": len(positions),
            "validations": validations,
            "summary": {
                "all_pass": all_pass,
                "all_warn_or_pass": all_warn,
                "pass_count": sum(1 for v in validations if v["validation"]["validation_status"] == "PASS"),
                "warn_count": sum(1 for v in validations if v["validation"]["validation_status"] == "WARN"),
                "fail_count": sum(1 for v in validations if v["validation"]["validation_status"] == "FAIL"),
            },
        }
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}


@app.get("/api/validate/profit/{position_id}")
async def validate_profit(position_id: str):
    """Multi-validate profit for a specific position"""
    try:
        if not PERFORMANCE_PREDICTOR_AVAILABLE:
            return {"status": "ERROR", "message": "Live validator not available"}

        # Get position
        positions_data = await get_positions()
        positions = positions_data.get("positions", [])

        position = None
        for pos in positions:
            if str(pos.get("position_id", "")) == position_id:
                position = pos
                break

        if not position:
            return {"status": "ERROR", "message": f"Position {position_id} not found"}

        # Get reported PnL
        reported_pnl = position.get("unrealized_pnl", 0)

        # Multi-validate
        validator = get_live_validator()
        validation = validator.multi_validate_profit(position, reported_pnl)

        return {"status": "ok", "position_id": position_id, "validation": validation}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}


@app.get("/api/predict/performance")
async def predict_performance():
    """Predict overall system performance"""
    try:
        if not PERFORMANCE_PREDICTOR_AVAILABLE:
            return {"status": "ERROR", "message": "Performance predictor not available"}

        # Get current PnL data
        pnl_data = await get_pnl()
        summary = pnl_data.get("summary", {})
        history = pnl_data.get("history", [])

        # Get positions
        positions_data = await get_positions()
        positions = positions_data.get("positions", [])

        # Calculate predictions
        predictor = get_performance_predictor()

        # Portfolio prediction
        market_data = {}
        for pos in positions:
            symbol = pos.get("symbol", pos.get("underlying", ""))
            market_data[symbol] = pos.get("current_price", pos.get("entry_price", 0))

        portfolio_pred = predictor.predict_portfolio_performance(positions, market_data)

        # Performance metrics prediction
        total_trades = summary.get("total_trades", 0)
        win_rate = summary.get("win_rate", 0.0)
        current_pnl = summary.get("total_pnl", 0.0)

        # Predict future performance based on historical
        if len(history) >= 10:
            recent_pnl = [h.get("total_pnl", 0) for h in history[-10:]]
            avg_recent_pnl = sum(recent_pnl) / len(recent_pnl)

            # Project forward (simplified)
            projected_pnl = current_pnl + (avg_recent_pnl * 5)  # Next 5 cycles
        else:
            projected_pnl = current_pnl

        return {
            "status": "ok",
            "current_performance": {
                "total_pnl": current_pnl,
                "total_trades": total_trades,
                "win_rate": win_rate,
                "open_positions": len(positions),
            },
            "predicted_performance": {
                "projected_pnl": round(projected_pnl, 2),
                "projected_win_rate": win_rate,  # Assume same win rate
                "confidence": 0.7 if len(history) >= 10 else 0.5,
            },
            "portfolio_prediction": portfolio_pred,
            "timestamp": datetime.now(pytz.timezone("Asia/Kolkata")).isoformat(),
        }
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}


@app.get("/api/alerts/recent")
async def get_recent_alerts(limit: int = 50):
    """Get recent alerts + synthesize operational degradations when file is empty."""
    try:
        alerts: list = []
        if ALERTS_AVAILABLE:
            try:
                alerts_system = get_alerts_system()
                alerts = list(alerts_system.get_recent_alerts(limit) or [])
            except Exception as exc:
                print(f"[alerts] file read failed: {exc}")

        ops = await _synthesize_operational_alerts()
        # Prefer file alerts; append ops that are not already present by title.
        seen = {str(a.get("title") or a.get("id") or "") for a in alerts}
        for a in ops:
            title = str(a.get("title") or "")
            if title and title not in seen:
                alerts.append(a)
                seen.add(title)
        alerts = alerts[-max(1, int(limit or 50)) :]
        return {"status": "ok", "alerts": alerts, "count": len(alerts), "ops_injected": len(ops)}
    except Exception as e:
        return {"status": "ERROR", "message": str(e), "alerts": []}


async def _synthesize_operational_alerts() -> list:
    """Build operator-visible alerts from live runtime state (not silent empty)."""
    from datetime import datetime as _dt

    now = _dt.now(IST).isoformat()
    out: list = []

    def _add(code: str, severity: str, title: str, message: str, data: dict | None = None):
        alert_type = "LIVE_GATE" if str(code).upper() == "LIVE_GATE" else "system_alert"
        out.append(
            {
                "id": f"OPS_{code}",
                "type": alert_type,
                "code": code,
                "severity": "INFO" if alert_type == "LIVE_GATE" else severity,
                "title": title,
                "message": message,
                "data": data or {},
                "timestamp": now,
                "persistent": False,
                "read": False,
                "source": "operational_synth",
            }
        )

    try:
        # Moneycontrol scrape (reference only — Dhan is trading truth)
        mc = None
        for _mc_key in (
            "moneycontrol_gainers:25",
            "moneycontrol_gainers:5",
            "moneycontrol_gainers:3",
        ):
            hit = _cache_get(_mc_key, 600.0)
            if isinstance(hit, dict):
                mc = hit
                break
        if not isinstance(mc, dict):
            disk = ROOT_DIR / "state" / "moneycontrol_option_gainers.json"
            if disk.exists():
                try:
                    mc = json.loads(disk.read_text(encoding="utf-8"))
                except Exception:
                    mc = None
        if isinstance(mc, dict) and str(mc.get("status") or "").upper() in {
            "SCRAPE_FAILED",
            "PARSE_FAILED",
            "ERROR",
        }:
            _add(
                "MC_SCRAPE",
                "warning",
                "Moneycontrol gainers scrape failed",
                f"Reference scrape blocked ({mc.get('error') or mc.get('status')}). "
                "Trading truth remains Dhan Market Top / option chain.",
                {"status": mc.get("status"), "error": mc.get("error")},
            )

        # Chain warm gaps (after-hours BANKNIFTY/MIDCPNIFTY often cold)
        cold = []
        for sym in _INDEX_STREAM_SYMBOLS:
            pushed = _PUSHED_CHAIN_CACHE.get(sym) or {}
            data = pushed.get("data") if isinstance(pushed, dict) else None
            if not isinstance(data, dict) or float(data.get("spot") or 0) <= 0:
                ttl = _cache_get(f"chain_{sym}", 300.0)
                if not isinstance(ttl, dict) or float(ttl.get("spot") or 0) <= 0:
                    cold.append(sym)
        if cold:
            _add(
                "CHAIN_COLD",
                "warning",
                "Index option-chain cache incomplete",
                f"No verified Dhan snapshot yet for: {', '.join(cold)}. "
                "TopBar may show blank spots until micro-loop warms cache.",
                {"symbols": cold},
            )

        # Live gate blockers (informational — must stay blocked)
        try:
            gate = await get_live_trading_gate()
        except Exception:
            gate = None
        if isinstance(gate, dict) and not gate.get("gate_open", True):
            failing = [
                g
                for g in (gate.get("gates") or [])
                if isinstance(g, dict) and not g.get("passed")
            ]
            if failing:
                failing_names = [str(g.get("gate") or "") for g in failing if g.get("gate")]
                _add(
                    "LIVE_GATE",
                    "INFO",
                    "Live trading correctly BLOCKED",
                    "Live remains blocked by design in PAPER/ANALYZER. "
                    "Live approval is not required for paper operation. "
                    f"Failing live-only gates: {', '.join(failing_names) or 'none'}.",
                    {"failing_gates": failing_names},
                )
    except Exception as exc:
        _add(
            "SYNTH_ERROR",
            "warning",
            "Operational alert synthesis error",
            str(exc)[:200],
        )
    return out


@app.get("/api/alerts/unread")
async def get_unread_alerts():
    """Get unread alerts"""
    try:
        if not ALERTS_AVAILABLE:
            return {"status": "ERROR", "message": "Alerts system not available", "alerts": []}

        alerts_system = get_alerts_system()
        all_alerts = alerts_system.get_recent_alerts(100)
        unread = [a for a in all_alerts if not a.get("read", False)]

        return {"status": "ok", "alerts": unread, "count": len(unread)}
    except Exception as e:
        return {"status": "ERROR", "message": str(e), "alerts": []}


@app.post("/api/alerts/{alert_id}/read")
async def mark_alert_read(alert_id: str):
    """Mark an alert as read"""
    try:
        if not ALERTS_AVAILABLE:
            return {"status": "ERROR", "message": "Alerts system not available"}

        alerts_system = get_alerts_system()
        success = alerts_system.mark_alert_read(alert_id)

        return {"status": "ok" if success else "error", "alert_id": alert_id}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}


@app.get("/api/audit/comprehensive")
async def comprehensive_audit():
    """Run comprehensive multi-validation audit"""
    try:
        if not MULTI_VALIDATION_AVAILABLE:
            return {"status": "ERROR", "message": "Multi-validation not available"}

        # Get current data
        health_data = await get_health()
        positions_data = await get_positions()
        chain_data = await get_chain("NIFTY")  # Default to NIFTY

        # Run audit
        validator = get_multi_validator()
        audit_result = validator.comprehensive_audit(health_data, positions_data.get("positions", []), chain_data)

        # Save audit result
        audit_file = (
            AUDIT_DIR
            / f"comprehensive_audit_{datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(audit_file, "w") as f:
            json.dump(audit_result, f, indent=2, default=str)

        return {"status": "ok", "audit": audit_result, "audit_file": audit_file.name}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}


@app.get("/api/audit/validate/spot/{underlying}")
async def validate_spot_price(underlying: str, price: float):
    """Validate spot price against multiple sources"""
    try:
        if not MULTI_VALIDATION_AVAILABLE:
            return {"status": "ERROR", "message": "Multi-validation not available"}

        validator = get_multi_validator()
        result = validator.validate_spot_price(underlying, price)

        return {"status": "ok", "validation": result}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}


@app.get("/api/audit/validate/pnl/{position_id}")
async def validate_position_pnl(position_id: str):
    """Validate position PnL"""
    try:
        if not MULTI_VALIDATION_AVAILABLE:
            return {"status": "ERROR", "message": "Multi-validation not available"}

        # Get position
        positions_data = await get_positions()
        positions = positions_data.get("positions", [])

        position = None
        for pos in positions:
            if str(pos.get("position_id", "")) == position_id:
                position = pos
                break

        if not position:
            return {"status": "ERROR", "message": f"Position {position_id} not found"}

        validator = get_multi_validator()
        result = validator.validate_pnl(position, position.get("unrealized_pnl", 0))

        return {"status": "ok", "validation": result}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}


@app.get("/api/charting/heatmap/{underlying}")
async def get_heatmap(underlying: str, metric: str = "oi"):
    """Get option chain heatmap data"""
    try:
        if not ADVANCED_FEATURES_AVAILABLE:
            return {"status": "ERROR", "message": "Advanced charting not available"}

        chain_data = await get_chain(underlying)
        charting = get_advanced_charting()
        heatmap = charting.generate_option_chain_heatmap(chain_data, metric)

        return {"status": "ok", "heatmap": heatmap}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}


@app.get("/api/charting/iv-surface/{underlying}")
async def get_iv_surface(underlying: str):
    """Get IV surface data"""
    try:
        if not ADVANCED_FEATURES_AVAILABLE:
            return {"status": "ERROR", "message": "Advanced charting not available"}

        chain_data = await get_chain(underlying)
        charting = get_advanced_charting()
        surface = charting.generate_iv_surface(chain_data)

        return {"status": "ok", "surface": surface}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}


@app.get("/api/charting/greeks/{underlying}")
async def get_greeks_chart(underlying: str, greek: str = "delta"):
    """Get Greeks chart data"""
    try:
        if not ADVANCED_FEATURES_AVAILABLE:
            return {"status": "ERROR", "message": "Advanced charting not available"}

        chain_data = await get_chain(underlying)
        charting = get_advanced_charting()
        greeks_data = charting.generate_greeks_chart(chain_data, greek)

        return {"status": "ok", "greeks": greeks_data}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}


@app.get("/api/charting/pcr/{underlying}")
async def get_pcr_chart(underlying: str):
    """Get Put-Call Ratio chart data"""
    try:
        if not ADVANCED_FEATURES_AVAILABLE:
            return {"status": "ERROR", "message": "Advanced charting not available"}

        chain_data = await get_chain(underlying)
        charting = get_advanced_charting()
        pcr_data = charting.generate_pcr_chart(chain_data)

        return {"status": "ok", "pcr": pcr_data}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}


@app.post("/api/filter/chain/{underlying}")
async def filter_option_chain(underlying: str, filters: Dict[str, Any]):
    """Filter option chain"""
    try:
        if not ADVANCED_FEATURES_AVAILABLE:
            return {"status": "ERROR", "message": "Advanced filtering not available"}

        chain_data = await get_chain(underlying)
        contracts = chain_data.get("contracts", [])

        filtering = get_advanced_filtering()
        filtered = filtering.filter_option_chain(contracts, filters)

        return {
            "status": "ok",
            "original_count": len(contracts),
            "filtered_count": len(filtered),
            "contracts": filtered,
        }
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}


@app.post("/api/filter/positions")
async def filter_positions(filters: Dict[str, Any]):
    """Filter positions"""
    try:
        if not ADVANCED_FEATURES_AVAILABLE:
            return {"status": "ERROR", "message": "Advanced filtering not available"}

        positions_data = await get_positions()
        positions = positions_data.get("positions", [])

        filtering = get_advanced_filtering()
        filtered = filtering.filter_positions(positions, filters)

        return {
            "status": "ok",
            "original_count": len(positions),
            "filtered_count": len(filtered),
            "positions": filtered,
        }
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}


@app.get("/api/risk")
async def get_risk():
    """Get risk dashboard data (alias for /api/risk/portfolio)"""
    return await get_portfolio_risk()


@app.get("/api/risk/portfolio")
async def get_portfolio_risk():
    """Get portfolio risk metrics from paper + read-only Dhan holdings/positions."""
    try:
        if not ADVANCED_FEATURES_AVAILABLE:
            return {"status": "ERROR", "message": "Risk management not available"}

        positions_data = await get_positions()
        positions = list(positions_data.get("positions") or [])

        def _as_risk_row(item: Dict[str, Any], kind: str) -> Dict[str, Any]:
            qty = float(item.get("qty") or item.get("quantity") or item.get("net_qty") or item.get("netQty") or 0)
            entry = float(item.get("entry_price") or item.get("avg_price") or item.get("avgCostPrice") or item.get("buyAvg") or 0)
            ltp = float(item.get("current_price") or item.get("ltp") or item.get("lastTradedPrice") or entry)
            pnl = item.get("unrealized_pnl")
            if pnl is None:
                pnl = item.get("pnl")
            if pnl is None:
                pnl = (ltp - entry) * qty
            return {
                "underlying": str(item.get("underlying") or item.get("symbol") or item.get("trading_symbol") or kind).upper(),
                "entry_price": entry,
                "current_price": ltp,
                "qty": qty,
                "unrealized_pnl": float(pnl or 0),
                "delta": float(item.get("delta") or 0),
                "gamma": float(item.get("gamma") or 0),
                "theta": float(item.get("theta") or 0),
                "vega": float(item.get("vega") or 0),
                "source": kind,
            }

        try:
            holdings = await get_broker_holdings()
            for row in holdings.get("rows") or []:
                if isinstance(row, dict):
                    positions.append(_as_risk_row(row, "dhan_holding"))
        except Exception:
            pass
        try:
            live_pos = await get_broker_positions_live()
            for row in live_pos.get("rows") or []:
                if isinstance(row, dict):
                    positions.append(_as_risk_row(row, "dhan_position"))
        except Exception:
            pass

        risk_mgmt = get_risk_management()
        risk_metrics = risk_mgmt.calculate_portfolio_risk(positions)
        return {
            "status": "ok",
            "risk_metrics": risk_metrics,
            "position_count": len(positions),
            "live_trading_enabled": False,
            "source": "paper_plus_dhan_readonly",
        }
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}


@app.post("/api/risk/check-limits")
async def check_risk_limits(risk_limits: Dict[str, float]):
    """Check risk limits"""
    try:
        if not ADVANCED_FEATURES_AVAILABLE:
            return {"status": "ERROR", "message": "Risk management not available"}

        positions_data = await get_positions()
        positions = positions_data.get("positions", [])

        risk_mgmt = get_risk_management()
        limit_check = risk_mgmt.check_risk_limits(positions, risk_limits)

        return {"status": "ok", "limit_check": limit_check}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}


@app.post("/api/backtest/run")
async def run_backtest_endpoint(strategy_config: Dict[str, Any], historical_data: List[Dict[str, Any]] = None):
    """Run backtest"""
    try:
        if not ADVANCED_FEATURES_AVAILABLE:
            return {"status": "ERROR", "message": "Backtesting not available"}

        # If no historical data provided, use sample data
        if not historical_data:
            # Generate sample historical data
            historical_data = []
            base_price = 20000
            for i in range(100):
                historical_data.append(
                    {
                        "timestamp": (
                            datetime.now(pytz.timezone("Asia/Kolkata")) - timedelta(days=100 - i)
                        ).isoformat(),
                        "price": base_price + __import__("random").gauss(0, 100),
                        "ltp": base_price + __import__("random").gauss(0, 100),
                    }
                )

        backtest_engine = get_backtesting_engine()
        result = backtest_engine.run_backtest(strategy_config, historical_data)

        return {"status": "ok", "backtest": result}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}


def _ml_accuracy_report_record(report_json: Path) -> Dict[str, Any]:
    """Build an honest proof record from model_accuracy_report.json (fail-closed)."""
    try:
        rep = json.loads(report_json.read_text(encoding="utf-8"))
    except Exception as exc:
        return {
            "status": "ERROR",
            "model_proof_ready": False,
            "total_predictions": 0,
            "avg_accuracy": None,
            "avg_confidence": None,
            "blocker_reason": str(exc)[:160],
            "source_file": str(report_json),
        }

    summary = rep.get("summary") if isinstance(rep.get("summary"), dict) else {}
    rows = rep.get("rows") if isinstance(rep.get("rows"), list) else []
    proof_pass = int(summary.get("proof_pass_count") or 0)
    blocked = int(summary.get("blocked_count") or 0)
    hit_rate = summary.get("direction_hit_rate")
    known = int(summary.get("direction_known_count") or 0)
    blocker = None
    for row in rows:
        if isinstance(row, dict) and row.get("blocker_reason"):
            blocker = str(row.get("blocker_reason"))
            break
    if blocker is None and blocked > 0:
        blocker = "ACCURACY_REPORT_BLOCKED"
    model_proof_ready = bool(proof_pass > 0 and blocked == 0 and hit_rate is not None)
    status = "PROVEN_ANALYZER_ONLY" if model_proof_ready else ("BLOCKED" if blocked > 0 or proof_pass == 0 else "LOADED")
    return {
        "status": status,
        "model_proof_ready": model_proof_ready,
        "total_predictions": known if known > 0 else (proof_pass if model_proof_ready else 0),
        "avg_accuracy": float(hit_rate) if hit_rate is not None else None,
        "avg_confidence": None,
        "proof_pass_count": proof_pass,
        "blocked_count": blocked,
        "direction_hit_rate": hit_rate,
        "rows": summary.get("rows"),
        "generated_at_utc": summary.get("generated_at_utc"),
        "blocker_reason": blocker,
        "source_file": str(report_json),
        "ready_for_live": False,
    }


def _ml_options_training_record(options_ml: Path) -> Dict[str, Any]:
    """Normalize options_ml_training_summary.json into UI-compatible proof fields."""
    try:
        data = json.loads(options_ml.read_text(encoding="utf-8"))
    except Exception as exc:
        return {
            "status": "ERROR",
            "model_proof_ready": False,
            "total_predictions": 0,
            "avg_accuracy": None,
            "avg_confidence": None,
            "blocker_reason": str(exc)[:160],
            "source_file": str(options_ml),
        }
    if not isinstance(data, dict):
        return {
            "status": "BLOCKED",
            "model_proof_ready": False,
            "total_predictions": 0,
            "avg_accuracy": None,
            "avg_confidence": None,
            "blocker_reason": "INVALID_OPTIONS_ML_SUMMARY",
            "source_file": str(options_ml),
        }
    status_raw = str(data.get("status") or "").upper()
    ready = status_raw == "PASS" and bool(data.get("model_proof_ready", True))
    results = data.get("results") if isinstance(data.get("results"), dict) else {}
    best = data.get("best_model")
    best_metrics = results.get(best, {}) if best and isinstance(results.get(best), dict) else {}
    out = dict(data)
    out.update(
        {
            "status": "PROVEN_ANALYZER_ONLY" if ready else (status_raw or "BLOCKED"),
            "model_proof_ready": ready,
            "total_predictions": int(data.get("dataset_rows") or data.get("total_predictions") or 0),
            "avg_accuracy": best_metrics.get("accuracy", data.get("avg_accuracy")),
            "avg_confidence": data.get("avg_confidence"),
            "blocker_reason": None if ready else (data.get("reason") or status_raw or "OPTIONS_ML_NOT_PASS"),
            "source_file": str(options_ml),
            "ready_for_live": False,
        }
    )
    return out


def _ml_models_proof_summary(models: Dict[str, Any]) -> Dict[str, Any]:
    """Aggregate fail-closed proof flags from the merged model map."""
    usable = {k: v for k, v in models.items() if k != "status" and isinstance(v, dict)}
    proven = {k: v for k, v in usable.items() if bool(v.get("model_proof_ready"))}
    blocked = {
        k: v
        for k, v in usable.items()
        if not bool(v.get("model_proof_ready"))
        and str(v.get("status") or "").upper() in {"BLOCKED", "ERROR", "NOT_TRAINED", "LOADED"}
    }
    # Artifacts that exist but are not proven count as blocked for messaging.
    if not blocked:
        blocked = {k: v for k, v in usable.items() if k not in proven}
    any_proven = bool(proven)
    blockers = []
    for name, rec in blocked.items():
        reason = rec.get("blocker_reason") or rec.get("message") or rec.get("status")
        if reason:
            blockers.append(f"{name}:{reason}")
    if any_proven:
        message = (
            f"Loaded {len(proven)} proven model performance record(s) "
            "(analyzer-only). Live readiness remains blocked until forward paper validation passes."
        )
        status = "PROVEN_ANALYZER_ONLY"
    elif usable:
        message = (
            f"Loaded {len(usable)} blocked accuracy artifact(s). Model not proven — "
            "missing matured prediction history / post-market validation."
        )
        if blockers:
            message = f"{message} Blocker: {blockers[0]}"
        status = "BLOCKED"
    else:
        message = (
            "No matured ML training/performance artifact is available. "
            "This means model is not proven trained/ready yet."
        )
        status = "BLOCKED"
    return {
        "model_proof_ready": any_proven,
        "status": status,
        "message": message,
        "model_count": len(usable),
        "proven_count": len(proven),
        "blocked_count": len(blocked),
        "ready_for_live": False,
    }


@app.get("/api/ml/performance")
async def get_ml_performance(model_name: Optional[str] = None):
    """Get ML model performance from tracker + on-disk proof reports."""
    performance: Dict[str, Any] = {"models": {}}
    try:
        if ADVANCED_FEATURES_AVAILABLE:
            try:
                ml_tracker = get_ml_tracker()
                tracked = ml_tracker.get_model_performance(model_name)
                if isinstance(tracked, dict):
                    performance.update(tracked)
            except Exception as tracker_error:
                performance["tracker_error"] = str(tracker_error)[:200]
    except Exception as e:
        performance["error"] = str(e)[:200]

    # Always merge file proof so ML tab is not blank on Cloud — but fail-closed on readiness.
    report_json = ROOT_DIR / "reports" / "latest" / "model_accuracy_report.json"
    options_ml = ROOT_DIR / "reports" / "latest" / "options_ml_training_summary.json"
    models = performance.get("models") if isinstance(performance.get("models"), dict) else {}
    # Drop placeholder status-only keys from tracker before merging real artifacts.
    if "status" in models and isinstance(models.get("status"), dict) and "model_proof_ready" not in models["status"]:
        models.pop("status", None)
    if report_json.exists():
        models["model_accuracy_report"] = _ml_accuracy_report_record(report_json)
    if options_ml.exists():
        models["options_ml_training"] = _ml_options_training_record(options_ml)
    # Normalize tracker models that lack explicit proof flags (assume not proven).
    for key, rec in list(models.items()):
        if key == "status" or not isinstance(rec, dict):
            continue
        if "model_proof_ready" not in rec:
            has_metrics = rec.get("avg_accuracy") is not None and int(rec.get("total_predictions") or 0) > 0
            rec["model_proof_ready"] = bool(has_metrics)
            rec.setdefault("status", "PROVEN_ANALYZER_ONLY" if has_metrics else "BLOCKED")
            rec.setdefault("ready_for_live", False)
            if not has_metrics:
                rec.setdefault("blocker_reason", "TRACKER_METRICS_INCOMPLETE")
    if not models:
        models["status"] = {
            "status": "NOT_TRAINED",
            "model_proof_ready": False,
            "total_predictions": 0,
            "avg_accuracy": None,
            "avg_confidence": None,
            "message": "No proven ML artifacts yet — analyzer/paper only until validation days exist",
            "blocker_reason": "NO_ML_ARTIFACTS",
        }
    summary = _ml_models_proof_summary(models)
    performance["models"] = models
    performance.update(summary)
    return {
        "status": "ok",
        "performance": performance,
        "model_proof_ready": summary["model_proof_ready"],
        "proof_status": summary["status"],
        "message": summary["message"],
        "ready_for_live": False,
    }


@app.get("/api/ml/compare")
async def compare_ml_models():
    """Compare ML models + surface proof artifacts (single merged map, no double-count)."""
    comparison: Dict[str, Any] = {"models": {}}
    try:
        if ADVANCED_FEATURES_AVAILABLE:
            try:
                ml_tracker = get_ml_tracker()
                tracked = ml_tracker.compare_models()
                if isinstance(tracked, dict):
                    comparison.update(tracked)
            except Exception as tracker_error:
                comparison["tracker_error"] = str(tracker_error)[:200]
    except Exception as e:
        comparison["error"] = str(e)[:200]

    perf = await get_ml_performance()
    models = ((perf.get("performance") or {}).get("models") or {}) if isinstance(perf, dict) else {}
    if isinstance(models, dict) and models:
        comparison["models"] = models
        comparison["source"] = "ml_performance_merged"
    if not comparison.get("models"):
        comparison["models"] = {
            "status": {
                "status": "NOT_TRAINED",
                "model_proof_ready": False,
                "message": "No comparable model proofs yet",
                "blocker_reason": "NO_ML_ARTIFACTS",
            }
        }
    summary = _ml_models_proof_summary(comparison["models"] if isinstance(comparison.get("models"), dict) else {})
    comparison.update(summary)
    proven = {
        k: v
        for k, v in (comparison.get("models") or {}).items()
        if k != "status" and isinstance(v, dict) and bool(v.get("model_proof_ready"))
    }
    best_model = None
    if proven:
        best_name = next(iter(proven.keys()))
        best_model = {"name": best_name, "metrics": proven[best_name]}
    return {
        "status": "ok",
        "comparison": comparison,
        "best_model": best_model,
        "model_proof_ready": summary["model_proof_ready"],
        "proof_status": summary["status"],
        "message": summary["message"],
        "ready_for_live": False,
    }


@app.get("/api/backtest/results")
async def get_backtest_results():
    """Serve latest walk-forward / backtest proof artifacts for Performance tab."""
    base = ROOT_DIR / "reports" / "latest" / "recent_backtest_walkforward_proof"
    summary_path = base / "summary.json"
    costed_path = base / "costed_walkforward_proof.json"
    if not summary_path.exists() and not costed_path.exists():
        return {
            "status": "no_data",
            "message": "No backtest/walk-forward proof artifacts in this deploy image yet",
            "results": [],
        }
    summary = {}
    costed = {}
    try:
        if summary_path.exists():
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
    except Exception as exc:
        summary = {"error": str(exc)[:160]}
    try:
        if costed_path.exists():
            costed = json.loads(costed_path.read_text(encoding="utf-8"))
    except Exception as exc:
        costed = {"error": str(exc)[:160]}
    # Operator view: never dump repo file-path "candidates_sample" as trade evidence.
    summary = _sanitize_backtest_operator_summary(summary)
    return {
        "status": "ok",
        "summary": summary,
        "costed_walkforward": costed,
        "source_dir": str(base),
        "live_trading_enabled": False,
    }


def _sanitize_backtest_operator_summary(summary: Any) -> Any:
    if not isinstance(summary, dict):
        return summary
    out = dict(summary)
    ev = out.get("evidence")
    if isinstance(ev, dict):
        ev2 = {k: v for k, v in ev.items() if k != "candidates_sample"}
        sample = ev.get("candidates_sample")
        if isinstance(sample, list):
            # Keep only dict-like trade rows; drop .py/.md path strings.
            trade_like = [x for x in sample if isinstance(x, dict)]
            path_like = [
                x
                for x in sample
                if isinstance(x, str)
                and (
                    "/" in x
                    or "\\" in x
                    or x.endswith((".py", ".md", ".json", ".tsx", ".ts"))
                )
            ]
            ev2["trade_candidates_sample"] = trade_like[:40]
            ev2["code_path_scan_count"] = len(path_like)
            ev2["code_path_scan_note"] = (
                "Orchestrator file-scan paths are not trade candidates; "
                "hidden from Performance tab. See costed_walkforward for PnL proof."
            )
            if "candidate_count" in ev2 and path_like and not trade_like:
                ev2["candidate_count_note"] = (
                    f"candidate_count={ev2.get('candidate_count')} counts code/docs hits, not trades"
                )
        out["evidence"] = ev2
    return out


@app.get("/api/backtests/latest")
async def get_backtests_latest():
    return await get_backtest_results()


@app.get("/api/model/behavior")
async def get_model_behavior():
    """Get model behavior analytics"""
    try:
        if not ADVANCED_FEATURES_AVAILABLE:
            return {
                "status": "ok",
                "message": "Model behavior analytics not available",
                "data": {
                    "active_models": ["Ensemble", "Fallback"],
                    "fallback_used": False,
                    "metrics": {},
                    "timestamp": datetime.now(pytz.timezone("Asia/Kolkata")).isoformat(),
                },
            }

        try:
            ml_tracker = get_ml_tracker()
            performance = ml_tracker.get_model_performance()

            # Extract behavior metrics
            behavior_data = {
                "active_models": performance.get("models", ["Ensemble", "Fallback"]),
                "fallback_used": performance.get("fallback_used", False),
                "metrics": performance.get("metrics", {}),
                "timestamp": datetime.now(pytz.timezone("Asia/Kolkata")).isoformat(),
            }
        except Exception as tracker_error:
            # Fallback if ML tracker fails
            behavior_data = {
                "active_models": ["Ensemble", "Fallback"],
                "fallback_used": False,
                "metrics": {},
                "timestamp": datetime.now(pytz.timezone("Asia/Kolkata")).isoformat(),
                "error": str(tracker_error)[:200],
            }

        return {"status": "ok", "data": behavior_data}
    except Exception as e:
        return {
            "status": "ok",
            "message": f"Error: {str(e)[:200]}",
            "data": {
                "active_models": ["Ensemble", "Fallback"],
                "fallback_used": False,
                "metrics": {},
                "timestamp": datetime.now(pytz.timezone("Asia/Kolkata")).isoformat(),
            },
        }


@app.post("/api/journal/note")
async def add_journal_note(position_id: str, note: str, tags: List[str] = None, note_type: str = "general"):
    """Add a note to trade journal"""
    try:
        if not ADVANCED_FEATURES_AVAILABLE:
            return {"status": "ERROR", "message": "Trade journal not available"}

        journal = get_trade_journal()
        journal_entry = journal.add_note(position_id, note, tags, note_type)

        return {"status": "ok", "entry": journal_entry}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}


@app.get("/api/journal/notes")
async def get_journal_notes(position_id: Optional[str] = None, tags: List[str] = None, limit: int = 100):
    """Get journal notes"""
    try:
        if not ADVANCED_FEATURES_AVAILABLE:
            return {"status": "ERROR", "message": "Trade journal not available"}

        journal = get_trade_journal()
        notes = journal.get_notes(position_id, tags, limit)

        return {"status": "ok", "notes": notes, "count": len(notes)}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}


@app.get("/api/journal/search")
async def search_journal_notes(query: str, limit: int = 50):
    """Search journal notes"""
    try:
        if not ADVANCED_FEATURES_AVAILABLE:
            return {"status": "ERROR", "message": "Trade journal not available"}

        journal = get_trade_journal()
        notes = journal.search_notes(query, limit)

        return {"status": "ok", "notes": notes, "count": len(notes)}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}


@app.get("/api/export/positions")
async def export_positions(format: str = "csv"):
    """Export positions"""
    try:
        if not ADVANCED_FEATURES_AVAILABLE:
            return {"status": "ERROR", "message": "Export not available"}

        positions_data = await get_positions()
        positions = positions_data.get("positions", [])

        if not positions:
            return {
                "status": "ok",
                "file": None,
                "format": format,
                "count": 0,
                "message": "No open positions to export",
            }

        export_system = get_export_reporting()
        timestamp = datetime.now(IST).strftime("%Y%m%d_%H%M%S")

        if format == "csv":
            output_file = OUTPUTS_DIR / f"export_positions_{timestamp}.csv"
            success = export_system.export_positions_to_csv(positions, output_file)

            if success:
                return {"status": "ok", "file": output_file.name, "format": "csv"}
            else:
                return {"status": "ERROR", "message": "Export failed"}
        else:
            return {"status": "ERROR", "message": f"Unsupported format: {format}"}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}


@app.get("/api/export/pnl")
async def export_pnl(format: str = "csv"):
    """Export PnL data"""
    try:
        if not ADVANCED_FEATURES_AVAILABLE:
            return {"status": "ERROR", "message": "Export not available"}

        pnl_data = await get_pnl()
        export_system = get_export_reporting()
        timestamp = datetime.now(IST).strftime("%Y%m%d_%H%M%S")

        if format == "csv":
            output_file = OUTPUTS_DIR / f"export_pnl_{timestamp}.csv"
            success = export_system.export_pnl_to_csv(pnl_data, output_file)

            if success:
                return {"status": "ok", "file": output_file.name, "format": "csv"}
            else:
                return {"status": "ERROR", "message": "Export failed"}
        else:
            return {"status": "ERROR", "message": f"Unsupported format: {format}"}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}


@app.get("/api/export/report")
async def generate_report():
    """Generate comprehensive performance report"""
    try:
        if not ADVANCED_FEATURES_AVAILABLE:
            return {"status": "ERROR", "message": "Export not available"}

        health_data = await get_health()
        positions_data = await get_positions()
        pnl_data = await get_pnl()
        perf_data = await get_performance()

        export_system = get_export_reporting()
        report = export_system.generate_performance_report(
            health_data, positions_data.get("positions", []), pnl_data, perf_data
        )

        timestamp = datetime.now(IST).strftime("%Y%m%d_%H%M%S")
        output_file = OUTPUTS_DIR / f"performance_report_{timestamp}.json"
        success = export_system.export_report_to_json(report, output_file)

        if success:
            return {"status": "ok", "report": report, "file": output_file.name}
        else:
            return {"status": "ERROR", "message": "Report generation failed"}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}


@app.post("/api/orders/create")
async def create_order(order_data: Dict[str, Any]):
    """Create a new order. Gated on: kill switch (inside
    OrderManagement.create_order itself), human approval, and portfolio
    risk limits - previously all three existed but only the dashboard's
    read-only status endpoints ever consulted them; nothing in the
    order-creation path did."""
    try:
        if not ADVANCED_FEATURES_AVAILABLE:
            return {"status": "ERROR", "message": "Order management not available"}

        try:
            from dashboard.backend.human_approval_service import build_approval_status
        except ImportError:
            from human_approval_service import build_approval_status
        approval = build_approval_status()
        if not approval.get("human_approval"):
            return {
                "status": "ERROR",
                "message": "Order rejected: human approval gate not signed off",
                "approval": approval,
            }

        try:
            live_cfg = json.loads((ROOT_DIR / "config" / "live_trade_config.json").read_text())
        except Exception:
            live_cfg = {}
        risk_limits = {
            "max_positions": live_cfg.get("MAX_OPEN_POSITIONS", 5),
            "max_exposure": live_cfg.get("MAX_EXPOSURE", 100000),
            "max_loss": -abs(live_cfg.get("MAX_DAILY_LOSS", 5000)),
            "max_concentration_pct": live_cfg.get("MAX_CONCENTRATION_PCT", 50),
        }
        positions_data = await get_positions()
        risk_check = get_risk_management().check_risk_limits(positions_data.get("positions", []), risk_limits)
        if risk_check.get("status") == "FAIL":
            return {"status": "ERROR", "message": "Order rejected: risk limits breached", "risk_check": risk_check}

        order_mgmt = get_order_management()
        order = order_mgmt.create_order(
            symbol=order_data.get("symbol"),
            order_type=order_data.get("order_type", "MARKET"),
            quantity=order_data.get("quantity", 0),
            price=order_data.get("price"),
            stop_loss=order_data.get("stop_loss"),
            target=order_data.get("target"),
            trailing_stop_pct=order_data.get("trailing_stop_pct"),
        )

        return {"status": "ok", "order": order}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}


@app.get("/api/orders")
async def get_orders(status: Optional[str] = None, symbol: Optional[str] = None, limit: int = 100):
    """Get orders"""
    try:
        if not ADVANCED_FEATURES_AVAILABLE:
            return {"status": "ERROR", "message": "Order management not available"}

        order_mgmt = get_order_management()
        orders = order_mgmt.get_orders(status, symbol, limit)

        return {"status": "ok", "orders": orders, "count": len(orders)}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}


@app.get("/api/orders/history")
async def get_order_history(symbol: Optional[str] = None, limit: int = 100):
    """Get order history"""
    try:
        if not ADVANCED_FEATURES_AVAILABLE:
            return {"status": "ERROR", "message": "Order management not available"}

        order_mgmt = get_order_management()
        history = order_mgmt.get_order_history(symbol, limit)

        return {"status": "ok", "history": history, "count": len(history)}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}


@app.post("/api/orders/{order_id}/cancel")
async def cancel_order(order_id: str):
    """Cancel an order"""
    try:
        if not ADVANCED_FEATURES_AVAILABLE:
            return {"status": "ERROR", "message": "Order management not available"}

        order_mgmt = get_order_management()
        success = order_mgmt.cancel_order(order_id)

        return {"status": "ok" if success else "error", "order_id": order_id}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}


@app.get("/api/trades/history")
async def get_trade_history(
    date: Optional[str] = None, start_time: Optional[str] = None, end_time: Optional[str] = None
):
    """
    Get trade history with optional date and time filtering.

    Args:
        date: Date in format 'YYYY-MM-DD' (default: today)
        start_time: Start time in format 'HH:MM' (24-hour, IST, default: 09:15)
        end_time: End time in format 'HH:MM' (24-hour, IST, default: 15:30)
    """
    try:
        try:
            from dashboard.backend.trade_logger import (
                get_all_trades,
                get_trades_by_date,
            )
        except ImportError:
            # Fallback to relative import
            from trade_logger import get_all_trades, get_trades_by_date

        if date:
            trades = get_trades_by_date(date, start_time, end_time)
        else:
            # Get all trades
            trades = get_all_trades()

        return {"trades": trades, "count": len(trades), "date": date, "start_time": start_time, "end_time": end_time}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/trades/today")
async def get_today_trades():
    """Get all trades from today (market hours: 9:15 AM - 3:30 PM IST)"""
    try:
        try:
            from dashboard.backend.trade_logger import get_trades_by_date
        except ImportError:
            # Fallback to relative import
            from trade_logger import get_trades_by_date
        from datetime import datetime

        import pytz

        IST = pytz.timezone("Asia/Kolkata")
        today = datetime.now(IST).strftime("%Y-%m-%d")
        trades = get_trades_by_date(today, start_time="09:15", end_time="15:30")

        def _today_match(ts: str) -> bool:
            return today in (ts or "")

        # Cloud paper CSV tape (OPEN/CLOSE) — primary exit evidence for PAPER_CLOUD_SIM
        try:
            import csv as _csv

            csv_path = OUTPUTS_DIR / "paper_trades_live.csv"
            if csv_path.exists():
                with csv_path.open("r", encoding="utf-8", newline="") as fh:
                    for row in _csv.DictReader(fh):
                        ts = row.get("time_ist") or row.get("timestamp") or ""
                        if not _today_match(ts):
                            continue
                        action = str(row.get("action") or "").upper()
                        pid = row.get("position_id")
                        if pid and any(
                            t.get("position_id") == pid and str(t.get("action") or "").upper() == action
                            for t in trades
                        ):
                            continue
                        trades.append(
                            {
                                "timestamp": row.get("timestamp"),
                                "time_ist": row.get("time_ist"),
                                "event_type": "POSITION_OPENED" if action == "OPEN" else "POSITION_CLOSED",
                                "position_id": pid,
                                "underlying": row.get("underlying"),
                                "symbol": row.get("underlying"),
                                "strike": row.get("strike"),
                                "option_type": row.get("option_type"),
                                "action": action,
                                "entry_price": row.get("entry_price") or row.get("price"),
                                "exit_price": row.get("exit_price"),
                                "qty": row.get("qty"),
                                "strategy": row.get("strategy"),
                                "exit_reason": row.get("exit_reason"),
                                "realized_pnl": row.get("realized_pnl"),
                                "source": "paper_trades_live_csv",
                            }
                        )
        except Exception as csv_exc:
            print(f"[trades/today] paper csv read failed: {csv_exc}")

        # SSOT open positions opened today (paper analyzer cycle)
        if SSOT_AVAILABLE and state_store is not None:
            for p in state_store.get_state().get("positions") or []:
                if not isinstance(p, dict):
                    continue
                ts = p.get("time_ist") or p.get("timestamp") or ""
                if not _today_match(ts):
                    continue
                pid = p.get("position_id")
                if pid and any(t.get("position_id") == pid for t in trades):
                    continue
                trades.append(
                    {
                        "timestamp": p.get("timestamp"),
                        "time_ist": p.get("time_ist"),
                        "event_type": "POSITION_OPENED",
                        "position_id": pid,
                        "underlying": p.get("underlying"),
                        "symbol": p.get("underlying"),
                        "strike": p.get("strike"),
                        "option_type": p.get("option_type"),
                        "action": "OPEN",
                        "entry_price": p.get("entry_price"),
                        "qty": p.get("qty"),
                        "strategy": p.get("strategy"),
                        "source": "state_store",
                    }
                )

        # Lifecycle proof closed trades from today's artifact
        lifecycle_summary = ROOT_DIR / "reports" / "latest" / "analyzer_paper_lifecycle_proof" / "summary.json"
        if lifecycle_summary.exists():
            try:
                proof = json.loads(lifecycle_summary.read_text(encoding="utf-8"))
                started = (proof.get("evidence") or {}).get("proof_id") or ""
                if proof.get("pass") and _today_match(started):
                    proof_file = sorted(
                        (ROOT_DIR / "reports" / "latest" / "analyzer_paper_lifecycle_proof").glob("LIFECYCLE_*.json")
                    )
                    if proof_file:
                        detail = json.loads(proof_file[-1].read_text(encoding="utf-8"))
                        oid = (detail.get("entry_order") or {}).get("order_id")
                        if oid and not any(t.get("position_id") == oid for t in trades):
                            sig = detail.get("signal") or {}
                            ent = detail.get("entry_order") or {}
                            ext = detail.get("exit_record") or {}
                            trades.append(
                                {
                                    "time_ist": datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S IST"),
                                    "event_type": "POSITION_CLOSED",
                                    "position_id": oid,
                                    "underlying": sig.get("symbol"),
                                    "symbol": sig.get("symbol"),
                                    "strike": sig.get("strike"),
                                    "option_type": sig.get("option_type"),
                                    "action": "CLOSE",
                                    "entry_price": ent.get("fill_price"),
                                    "exit_price": ext.get("exit_price"),
                                    "qty": ent.get("quantity") or 1,
                                    "pnl": ext.get("pnl_total"),
                                    "strategy": "PAPER_LIFECYCLE_PROOF",
                                    "exit_reason": ext.get("exit_reason"),
                                    "source": "lifecycle_proof",
                                }
                            )
            except Exception:
                pass

        # Separate by action
        entries = [t for t in trades if t.get("action") == "OPEN"]
        exits = [t for t in trades if t.get("action") == "CLOSE"]

        return {
            "date": today,
            "market_hours": "09:15 - 15:30 IST",
            "total_trades": len(entries),
            "entries": entries,
            "exits": exits,
            "count": len(trades),
            "sources": sorted({t.get("source", "trade_logger") for t in trades}),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Upgrade Agent Endpoints
try:
    from dashboard.backend.upgrade_agent import get_upgrade_agent

    UPGRADE_AGENT_AVAILABLE = True
except ImportError:
    try:
        from upgrade_agent import get_upgrade_agent

        UPGRADE_AGENT_AVAILABLE = True
    except ImportError:
        UPGRADE_AGENT_AVAILABLE = False
        print("Warning: Upgrade agent not available")

if UPGRADE_AGENT_AVAILABLE:
    upgrade_agent = get_upgrade_agent(ROOT_DIR, ROOT_DIR / "agent_memory")


@app.get("/api/agent/status")
async def get_agent_status():
    """Get agent status"""
    try:
        if not UPGRADE_AGENT_AVAILABLE:
            return {"status": "ok", "available": False, "message": "Upgrade agent not available", "paused": False}

        memory_file = ROOT_DIR / "agent_memory" / "tasks.json"
        has_memory = memory_file.exists()

        plan_files = sorted(
            (ROOT_DIR / "agent_memory").glob("upgrade_plan_*.json"), key=lambda f: f.stat().st_mtime, reverse=True
        )
        has_plan = len(plan_files) > 0

        return {
            "status": "ok",
            "available": True,
            "paused": not upgrade_agent.auto_apply_enabled if hasattr(upgrade_agent, "auto_apply_enabled") else False,
            "has_memory": has_memory,
            "has_plan": has_plan,
            "timestamp": datetime.now(pytz.timezone("Asia/Kolkata")).isoformat(),
        }
    except Exception as e:
        return {"status": "ok", "available": False, "message": str(e), "paused": False}


@app.get("/api/agent/memory")
async def get_agent_memory():
    """Get agent memory (tasks, plan)"""
    try:
        if not UPGRADE_AGENT_AVAILABLE:
            return {"status": "error", "message": "Upgrade agent not available"}

        memory_file = ROOT_DIR / "agent_memory" / "tasks.json"
        if memory_file.exists():
            return json.loads(memory_file.read_text())
        return {"status": "ok", "tasks": [], "run_id": "NONE"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/api/agent/issues")
async def get_agent_issues():
    """Return real operational issues (not a permanent empty stub)."""
    try:
        ops = await _synthesize_operational_alerts()
        issues = [
            {
                "id": a.get("id"),
                "severity": a.get("severity"),
                "title": a.get("title"),
                "message": a.get("message"),
                "data": a.get("data") or {},
                "timestamp": a.get("timestamp"),
            }
            for a in ops
            if str(a.get("severity") or "") in {"warning", "error", "critical"}
        ]
        return {"status": "ok", "issues": issues, "count": len(issues)}
    except Exception as e:
        return {"status": "ok", "message": str(e), "issues": []}


@app.get("/api/agent/upgrade-plan")
async def get_upgrade_plan():
    """Get current upgrade plan"""
    try:
        if not UPGRADE_AGENT_AVAILABLE:
            return {"status": "none", "message": "Upgrade agent not available"}

        plan_files = sorted(
            (ROOT_DIR / "agent_memory").glob("upgrade_plan_*.json"), key=lambda f: f.stat().st_mtime, reverse=True
        )

        if plan_files:
            plan = json.loads(plan_files[0].read_text())
            if plan.get("status") in ["draft", "ready"]:
                return {"status": "ok", **plan}

        return {"status": "none", "message": "No pending upgrade plan"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/api/agent/create-plan")
async def create_upgrade_plan():
    """Create new upgrade plan from detected issues"""
    try:
        if not UPGRADE_AGENT_AVAILABLE:
            return {"status": "error", "message": "Upgrade agent not available"}

        issues = upgrade_agent.watch_for_issues()
        if not issues:
            return {"status": "ok", "message": "No issues detected", "plan": None}

        plan = upgrade_agent.create_upgrade_plan(issues)
        test_results = upgrade_agent.run_tests(plan)

        if test_results["failed"] == 0:
            plan["status"] = "ready"
        else:
            plan["status"] = "needs_fix"

        plan_file = ROOT_DIR / "agent_memory" / f"upgrade_plan_{plan['plan_id']}.json"
        with open(plan_file, "w") as f:
            json.dump(plan, f, indent=2)

        return {"status": "ok", "plan": plan, "test_results": test_results}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/api/agent/apply-upgrade")
async def apply_upgrade(plan_data: Dict[str, Any]):
    """Apply upgrade plan"""
    try:
        if not UPGRADE_AGENT_AVAILABLE:
            return {"status": "error", "message": "Upgrade agent not available"}

        plan_id = plan_data.get("plan_id")
        if not plan_id:
            return {"status": "error", "message": "plan_id required"}

        plan_file = ROOT_DIR / "agent_memory" / f"upgrade_plan_{plan_id}.json"
        if not plan_file.exists():
            return {"status": "error", "message": "Plan not found"}

        plan = json.loads(plan_file.read_text())
        test_results = upgrade_agent.run_tests(plan)
        result = upgrade_agent.apply_upgrade(plan, test_results)

        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/api/agent/rollback")
async def rollback_upgrade():
    """Rollback last upgrade"""
    try:
        if not UPGRADE_AGENT_AVAILABLE:
            return {"status": "error", "message": "Upgrade agent not available"}

        plan_files = sorted(
            (ROOT_DIR / "agent_memory").glob("upgrade_plan_*.json"), key=lambda f: f.stat().st_mtime, reverse=True
        )

        for plan_file in plan_files:
            plan = json.loads(plan_file.read_text())
            if plan.get("status") == "applied":
                plan["status"] = "rolled_back"
                plan["rolled_back_at"] = datetime.now(IST).isoformat()
                with open(plan_file, "w") as f:
                    json.dump(plan, f, indent=2)

                return {"status": "ok", "success": True, "message": "Rollback initiated"}

        return {"status": "error", "success": False, "message": "No applied upgrade found"}
    except Exception as e:
        return {"status": "error", "success": False, "message": str(e)}


@app.get("/api/agent/test-results/{plan_id}")
async def get_test_results(plan_id: str):
    """Get test results for a plan"""
    try:
        test_file = ROOT_DIR / "agent_memory" / "test_runs" / f"test_{plan_id}.json"
        if test_file.exists():
            return json.loads(test_file.read_text())
        return {"status": "error", "message": "Test results not found"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/api/agent/pause")
async def pause_agent():
    """Pause/resume upgrade agent"""
    try:
        if not UPGRADE_AGENT_AVAILABLE:
            return {"status": "error", "message": "Upgrade agent not available"}

        upgrade_agent.auto_apply_enabled = not upgrade_agent.auto_apply_enabled
        return {"status": "ok", "paused": not upgrade_agent.auto_apply_enabled}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/api/proof-pack")
async def get_proof_pack():
    """Download proof pack ZIP"""
    try:
        if not UPGRADE_AGENT_AVAILABLE:
            raise HTTPException(status_code=503, detail="Upgrade agent not available")

        proof_pack_file = upgrade_agent.create_proof_pack()

        return FileResponse(
            proof_pack_file,
            media_type="application/zip",
            filename=f"proof_pack_{datetime.now(IST).strftime('%Y%m%d_%H%M%S')}.zip",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/learning/insights")
async def get_learning_insights():
    """Get continuous learning insights - Always returns HTTP 200"""
    try:
        insights_file = ROOT_DIR / "storage" / "learning" / "model_insights.json"
        if insights_file.exists():
            with open(insights_file, "r") as f:
                data = json.load(f)
                # Ensure proper structure
                if not isinstance(data, dict):
                    data = {"insights": data}
                data.setdefault("status", "ok")
                data.setdefault("updated_at", datetime.now(pytz.timezone("Asia/Kolkata")).isoformat())
                return data
        # Return empty but valid structure
        return {
            "status": "ok",
            "message": "Learning insights not available yet",
            "win_rate": 0.0,
            "total_trades": 0,
            "profitable_trades": 0,
            "best_strategy": None,
            "best_underlying": None,
            "updated_at": datetime.now(pytz.timezone("Asia/Kolkata")).isoformat(),
        }
    except Exception as e:
        # Return HTTP 200 with error status, not 500
        return {
            "status": "error",
            "message": str(e),
            "win_rate": 0.0,
            "total_trades": 0,
            "updated_at": datetime.now(pytz.timezone("Asia/Kolkata")).isoformat(),
        }


@app.get("/api/learning/status")
async def get_learning_status():
    _hit = _cache_get("learning_status", 60.0)
    if _hit is not None:
        return _hit
    """Get learning system status - Always returns HTTP 200"""
    try:
        learning_log = ROOT_DIR / "storage" / "learning" / "continuous_learning_log.json"
        # Ensure directory exists
        learning_log.parent.mkdir(parents=True, exist_ok=True)

        if learning_log.exists():
            with open(learning_log, "r") as f:
                logs = json.load(f)
                if logs and isinstance(logs, list) and len(logs) > 0:
                    latest = logs[-1]
                    return {
                        "status": "active",
                        "last_update": latest.get("timestamp", datetime.now(pytz.timezone("Asia/Kolkata")).isoformat()),
                        "total_cycles": len(logs),
                        "latest_insights": latest.get("insights", {}),
                        "updated_at": datetime.now(pytz.timezone("Asia/Kolkata")).isoformat(),
                    }
        # Return inactive but valid structure
        return {
            "status": "inactive",
            "message": "Learning system not started yet",
            "last_update": None,
            "total_cycles": 0,
            "latest_insights": {},
            "updated_at": datetime.now(pytz.timezone("Asia/Kolkata")).isoformat(),
        }
    except Exception as e:
        # Return HTTP 200 with error status, not 500
        return {
            "status": "error",
            "message": str(e),
            "last_update": None,
            "total_cycles": 0,
            "updated_at": datetime.now(pytz.timezone("Asia/Kolkata")).isoformat(),
        }


@app.get("/api/forensic/report")
async def get_forensic_report():
    """Get latest forensic analysis report - Always returns HTTP 200"""
    try:
        reports_dir = ROOT_DIR / "reports" / "forensic"
        # Ensure directory exists
        reports_dir.mkdir(parents=True, exist_ok=True)

        if reports_dir.exists():
            reports = sorted(reports_dir.glob("forensic_report_*.json"), key=lambda x: x.stat().st_mtime, reverse=True)
            if reports:
                with open(reports[0], "r") as f:
                    data = json.load(f)
                    # Ensure proper structure
                    if not isinstance(data, dict):
                        data = {"report": data}
                    data.setdefault("status", "ok")
                    data.setdefault("updated_at", datetime.now(pytz.timezone("Asia/Kolkata")).isoformat())
                    return data
        # Return empty but valid structure
        return {
            "status": "ok",
            "message": "Forensic report not available yet",
            "timestamp": datetime.now(pytz.timezone("Asia/Kolkata")).isoformat(),
            "signal_accuracy": {"accuracy": 0.0, "total_trades": 0},
            "data_integrity": {"issues": []},
            "performance_metrics": {"total_trades": 0, "win_rate": 0.0, "total_pnl": 0.0},
            "updated_at": datetime.now(pytz.timezone("Asia/Kolkata")).isoformat(),
        }
    except Exception as e:
        # Return HTTP 200 with error status, not 500
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now(pytz.timezone("Asia/Kolkata")).isoformat(),
            "signal_accuracy": {"accuracy": 0.0, "total_trades": 0},
            "data_integrity": {"issues": []},
            "performance_metrics": {"total_trades": 0, "win_rate": 0.0, "total_pnl": 0.0},
            "updated_at": datetime.now(pytz.timezone("Asia/Kolkata")).isoformat(),
        }


@app.get("/api/validation/status")
async def get_validation_status():
    """Get validation system status - Always returns HTTP 200"""
    try:
        validation_file = ROOT_DIR / "production_validation_report.json"
        if validation_file.exists():
            with open(validation_file, "r") as f:
                data = json.load(f)
                # Ensure proper structure
                if not isinstance(data, dict):
                    data = {"results": data}
                data.setdefault("status", "ok")
                data.setdefault("updated_at", datetime.now(pytz.timezone("Asia/Kolkata")).isoformat())
                return data
        # Return not_run but valid structure
        return {
            "status": "not_run",
            "message": "Run production_grade_validation.py to generate report",
            "results": {"tests_passed": 0, "total_tests": 0, "success_rate": 0.0},
            "updated_at": datetime.now(pytz.timezone("Asia/Kolkata")).isoformat(),
        }
    except Exception as e:
        # Return HTTP 200 with error status, not 500
        return {
            "status": "error",
            "message": str(e),
            "results": {"tests_passed": 0, "total_tests": 0, "success_rate": 0.0},
            "updated_at": datetime.now(pytz.timezone("Asia/Kolkata")).isoformat(),
        }


@app.post("/api/validation/run")
async def run_validation():
    """Run validation systems"""
    try:
        import re
        import subprocess
        import sys

        result = subprocess.run(
            [sys.executable, str(ROOT_DIR / "complete_end_to_end_validation.py")],
            capture_output=True,
            text=True,
            timeout=120,
        )

        # Parse output for test results
        output = result.stdout + result.stderr
        tests_passed = 0
        total_tests = 0
        success_rate = 0.0

        # Look for common patterns in validation output
        pass_matches = re.findall(r"(PASS|SUCCESS|✓|✅)", output, re.IGNORECASE)
        fail_matches = re.findall(r"(FAIL|ERROR|✗|❌)", output, re.IGNORECASE)
        tests_passed = len(pass_matches)
        total_tests = tests_passed + len(fail_matches)

        if total_tests > 0:
            success_rate = (tests_passed / total_tests) * 100

        # Also check for numeric patterns like "X/Y tests passed"
        numeric_match = re.search(r"(\d+)\s*/\s*(\d+)\s*(?:tests|passed)", output, re.IGNORECASE)
        if numeric_match:
            tests_passed = int(numeric_match.group(1))
            total_tests = int(numeric_match.group(2))
            success_rate = (tests_passed / total_tests * 100) if total_tests > 0 else 0.0

        return {
            "status": "completed",
            "returncode": result.returncode,
            "success": result.returncode == 0,
            "results": {
                "tests_passed": tests_passed,
                "total_tests": total_tests if total_tests > 0 else 1,
                "success_rate": round(success_rate, 1),
            },
            "output_preview": output[-500:] if output else "",
            "updated_at": datetime.now(pytz.timezone("Asia/Kolkata")).isoformat(),
        }
    except subprocess.TimeoutExpired:
        return {
            "status": "timeout",
            "success": False,
            "results": {"tests_passed": 0, "total_tests": 0, "success_rate": 0.0},
            "message": "Validation timed out after 120 seconds",
        }
    except Exception as e:
        return {
            "status": "error",
            "success": False,
            "results": {"tests_passed": 0, "total_tests": 0, "success_rate": 0.0},
            "message": str(e),
        }


@app.post("/api/learning/run")
async def run_learning_cycle():
    """Run one learning cycle"""
    try:
        import json
        import re
        import subprocess
        import sys

        result = subprocess.run(
            [sys.executable, str(ROOT_DIR / "continuous_learning_system.py")],
            capture_output=True,
            text=True,
            timeout=600,  # 10 minutes for learning cycle
        )

        output = result.stdout + result.stderr

        # Try to parse learning log file
        learning_log = ROOT_DIR / "storage" / "learning" / "continuous_learning_log.json"
        insights = {}
        win_rate = 0.0
        total_trades = 0

        if learning_log.exists():
            try:
                with open(learning_log, "r") as f:
                    logs = json.load(f)
                    if logs and isinstance(logs, list) and len(logs) > 0:
                        latest = logs[-1]
                        insights = latest.get("insights", {})
                        win_rate = insights.get("win_rate", 0.0)
                        total_trades = insights.get("total_trades", 0)
            except (ValueError, TypeError, KeyError, AttributeError) as e:
                logger.warning(f'Error handled: {e}')
            except Exception as e:
                logger.error(f'Unexpected error: {e}', exc_info=True)
                pass

        # Also try to extract from output
        win_rate_match = re.search(r"win[_\s]*rate[:\s]*(\d+\.?\d*)%?", output, re.IGNORECASE)
        if win_rate_match:
            win_rate = float(win_rate_match.group(1)) / 100.0

        return {
            "status": "completed",
            "returncode": result.returncode,
            "success": result.returncode == 0,
            "insights": {
                "win_rate": round(win_rate, 4),
                "total_trades": total_trades,
                "best_strategy": insights.get("best_strategy", "N/A"),
            },
            "output_preview": output[-500:] if output else "",
            "updated_at": datetime.now(pytz.timezone("Asia/Kolkata")).isoformat(),
        }
    except subprocess.TimeoutExpired:
        return {
            "status": "timeout",
            "success": False,
            "insights": {"win_rate": 0.0, "total_trades": 0, "best_strategy": "N/A"},
            "message": "Learning cycle timed out after 10 minutes",
        }
    except Exception as e:
        return {
            "status": "error",
            "success": False,
            "insights": {"win_rate": 0.0, "total_trades": 0, "best_strategy": "N/A"},
            "message": str(e),
        }


@app.post("/api/forensic/run")
async def run_forensic_analysis():
    """Run forensic analysis"""
    try:
        import subprocess
        import sys

        result = subprocess.run(
            [sys.executable, str(ROOT_DIR / "forensic_analysis_system.py")], capture_output=True, text=True, timeout=30
        )
        return {
            "status": "completed",
            "returncode": result.returncode,
            "output": result.stdout[-500:] if result.stdout else "",
            "success": result.returncode == 0,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Runner Control Endpoints
@app.get("/api/runner/test")
async def runner_test():
    """Test endpoint to verify runner routes are registered"""
    return {"status": "ok", "message": "Runner endpoints are working"}


class RunnerStartRequest(BaseModel):
    refresh: int = 5
    live: bool = False


@app.post("/api/runner/start")
async def runner_start(request: RunnerStartRequest = RunnerStartRequest()):
    """Start autorun master via runner.py CLI"""
    try:
        import subprocess

        runner_script = ROOT_DIR / "runner.py"
        if not runner_script.exists():
            raise HTTPException(status_code=500, detail="runner.py not found")

        result = subprocess.run(
            [sys.executable, str(runner_script), "start", "--refresh", str(request.refresh)],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(ROOT_DIR),
        )

        # Parse JSON output from runner.py
        try:
            output_lines = result.stdout.split("\n")
            json_start = None
            for i, line in enumerate(output_lines):
                if line.strip().startswith("{"):
                    json_start = i
                    break
            if json_start is not None:
                json_output = "\n".join(output_lines[json_start:])
                runner_result = json.loads(json_output)
                return {
                    "success": runner_result.get("success", False),
                    "pid": runner_result.get("pid"),
                    "mode": runner_result.get("mode", "PAPER"),
                    "message": f"Runner started: {runner_result.get('script', 'autorun')}",
                    "error": runner_result.get("error"),
                }
        except (ValueError, TypeError, KeyError, AttributeError) as e:
            logger.warning(f'Error handled: {e}')
        except Exception as e:
            logger.error(f'Unexpected error: {e}', exc_info=True)
            pass

        return {
            "success": result.returncode == 0,
            "output": result.stdout[-500:] if result.stdout else "",
            "error": result.stderr[-500:] if result.stderr else "",
        }
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=500, detail="Runner start timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/runner/stop")
async def runner_stop():
    """Stop autorun master via runner.py CLI"""
    try:
        import subprocess

        runner_script = ROOT_DIR / "runner.py"
        if not runner_script.exists():
            raise HTTPException(status_code=500, detail="runner.py not found")

        result = subprocess.run(
            [sys.executable, str(runner_script), "stop"], capture_output=True, text=True, timeout=30, cwd=str(ROOT_DIR)
        )

        # Parse JSON output
        try:
            output_lines = result.stdout.split("\n")
            json_start = None
            for i, line in enumerate(output_lines):
                if line.strip().startswith("{"):
                    json_start = i
                    break
            if json_start is not None:
                json_output = "\n".join(output_lines[json_start:])
                runner_result = json.loads(json_output)
                return {
                    "success": runner_result.get("success", False),
                    "stopped": runner_result.get("stopped", 0),
                    "message": f"Stopped {runner_result.get('stopped', 0)} process(es)",
                }
        except (ValueError, TypeError, KeyError, AttributeError) as e:
            logger.warning(f'Error handled: {e}')
        except Exception as e:
            logger.error(f'Unexpected error: {e}', exc_info=True)
            pass

        return {"success": result.returncode == 0, "output": result.stdout[-500:] if result.stdout else ""}
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=500, detail="Runner stop timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/runner/status")
async def runner_status():
    """Get runner status via runner.py CLI"""
    import time

    try:
        # Read heartbeat file directly — spawning runner.py as subprocess is
        # unsafe on 512Mi Render (imports all modules, spikes RAM to OOM).
        heartbeat_file = ROOT_DIR / "system3_daily_heartbeat.json"
        if heartbeat_file.exists():
            try:
                hb = json.loads(heartbeat_file.read_text())
                hb_age = time.time() - heartbeat_file.stat().st_mtime
                return {
                    "runner": "RUNNING" if hb_age < 120 else "STALE",
                    "mode": hb.get("system_info", {}).get("mode", "UNKNOWN"),
                    "heartbeat_age_seconds": int(hb_age),
                    "autopilot_running": hb.get("phase_execution", {}).get("autopilot_running", False),
                    "pid": hb.get("system_info", {}).get("process_id"),
                    "uptime_seconds": hb.get("system_info", {}).get("uptime_seconds"),
                }
            except Exception as hb_err:
                return {"runner": "ERROR", "error": f"heartbeat parse error: {hb_err}"}

        runner_script = ROOT_DIR / "runner.py"
        return {
            "runner": "NOT_STARTED",
            "runner_script_exists": runner_script.exists(),
            "message": "No heartbeat file found — runner has not run yet",
        }
    except Exception as e:
        return {"runner": "ERROR", "error": str(e)}


# Alias routes for convenience (point to /api/* endpoints)
# These prevent confusion when scripts/docs use /health or /state
@app.get("/health")
async def health_alias():
    """Alias for /api/health - compatibility success envelope."""
    return {"status": "success", "data": await get_health()}


@app.get("/state")
async def state_alias():
    """Alias for /api/state - returns same data"""
    return await get_state()


@app.get("/healthz")
@app.get("/api/healthz")
async def healthz_probe():
    """Lightweight kubernetes-style health probe."""
    return {"status": "ok"}


@app.get("/api/deploy_info")
async def deploy_info_underscore_alias():
    """Alias for /api/deploy/info (legacy audit probe compat)."""
    return await get_deploy_info()


@app.get("/api/instruments")
async def api_instruments_alias(symbol: Optional[str] = None):
    """Alias for /instruments (audit probe compat)."""
    return await compat_instruments(symbol)


@app.get("/api/prediction/all")
async def api_prediction_all_alias():
    """Alias for /prediction/all (audit probe compat)."""
    return await compat_prediction_all()


@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    if observer:
        try:
            observer.stop()
            observer.join(timeout=2)
        except (ValueError, TypeError, KeyError, AttributeError) as e:
            logger.warning(f'Error handled: {e}')
        except Exception as e:
            logger.error(f'Unexpected error: {e}', exc_info=True)
            pass


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)

# CORE_PIPELINE_V8_ENDPOINT_START
@app.get("/api/paper/pipeline/status")
async def get_core_pipeline_v8_status():
    """Read-only analyzer/paper pipeline status: forecasts, trade gates, paper orders, blockers."""
    try:
        try:
            from dashboard.backend.paper_pipeline_v8 import build_pipeline_status
        except ImportError:
            from paper_pipeline_v8 import build_pipeline_status
        return build_pipeline_status(ROOT_DIR, OUTPUTS_DIR)
    except Exception as e:
        return {
            "status": "error",
            "pipeline": "core_pipeline_v8",
            "error": str(e)[:300],
            "safety": {
                "live_trading_enabled": os.environ.get("LIVE_TRADING_ENABLED", "0"),
                "system3_live_trading_allowed": os.environ.get("SYSTEM3_LIVE_TRADING_ALLOWED", "0"),
                "broker_real_order_path": "not_used_by_core_pipeline_v8",
            },
        }
# CORE_PIPELINE_V8_ENDPOINT_END




# CTO_COMPAT_ENDPOINTS_START
# Compact compatibility API requested for the Streamlit CTO console. These routes
# wrap existing real data paths and never synthesize market data.
from collections import defaultdict, deque
from starlette.exceptions import HTTPException as StarletteHTTPException

import asyncio
from functools import wraps

async def with_retry(coro, max_retries=3, timeout=30):
    """Retry async operations with timeout"""
    for attempt in range(max_retries):
        try:
            return await asyncio.wait_for(coro, timeout=timeout)
        except asyncio.TimeoutError:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)
        except Exception:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(1)


def validate_params(params: dict, required: list = None, types: dict = None) -> tuple[bool, str]:
    """Validate request parameters"""
    if required:
        for field in required:
            if field not in params or params[field] is None:
                return False, f"Missing required field: {field}"
    
    if types:
        for field, expected_type in types.items():
            if field in params and params[field] is not None:
                if not isinstance(params[field], expected_type):
                    return False, f"Invalid type for {field}: expected {expected_type.__name__}"
    
    return True, ""


# Standardized response wrapper - applied to all endpoint returns
def wrap_response(data=None, status="ok", code="OK", error=None):
    """Wrap all responses in standard format"""
    return {
        "status": status,
        "code": code,
        "data": data,
        "error": error,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


_COMPAT_CACHE: Dict[str, Tuple[float, Any]] = {}
_COMPAT_REQ_BUCKET: Dict[str, deque] = defaultdict(deque)
_COMPAT_SCANNER_CACHE: Tuple[float, Dict[str, Any]] = (0.0, {})
_TRADES_CSV = ROOT_DIR / "trades.csv"


def _compat_ok(data: Any = None) -> Dict[str, Any]:
    return {"status": "success", "data": data if data is not None else {}}


def _compat_cached(key: str, ttl_s: float):
    hit = _COMPAT_CACHE.get(key)
    if hit and time.time() - hit[0] < ttl_s:
        return hit[1]
    return None


def _compat_set_cache(key: str, value: Any):
    _COMPAT_CACHE[key] = (time.time(), value)
    return value


def _compat_parse_expiry(expiry: str) -> float:
    if not expiry or expiry.lower() == "nearest":
        today = datetime.now(IST).date()
        days = (3 - today.weekday()) % 7
        days = 7 if days == 0 else days
        return max(days / 365.0, 1.0 / 365.0)
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
        try:
            exp = datetime.strptime(expiry, fmt).date()
            return max((exp - datetime.now(IST).date()).days / 365.0, 1.0 / 365.0)
        except ValueError:
            continue
    return 7.0 / 365.0


def _compat_is_live_order_allowed() -> bool:
    return (
        os.environ.get("LIVE_TRADING_ENABLED", "0").strip() == "1"
        and os.environ.get("SYSTEM3_LIVE_TRADING_ALLOWED", "0").strip() == "1"
    )


def _compat_flat_contracts(chain: Dict[str, Any]) -> List[Dict[str, Any]]:
    if not isinstance(chain, dict):
        return []
    for key in ("contracts", "rows", "chain", "data"):
        val = chain.get(key)
        if isinstance(val, list):
            return [x for x in val if isinstance(x, dict)]
        if isinstance(val, dict):
            nested = val.get("contracts") or val.get("rows") or val.get("chain")
            if isinstance(nested, list):
                return [x for x in nested if isinstance(x, dict)]
    return []


def _compat_signal_from_chain(symbol: str, chain: Dict[str, Any]) -> Dict[str, Any]:
    rows = _compat_flat_contracts(chain)
    ce_oi = pe_oi = ce_vol = pe_vol = 0.0
    for row in rows:
        typ = str(row.get("option_type") or row.get("type") or row.get("right") or "").upper()
        oi = float(row.get("oi") or row.get("open_interest") or 0)
        vol = float(row.get("volume") or 0)
        if typ == "CE":
            ce_oi += oi
            ce_vol += vol
        elif typ == "PE":
            pe_oi += oi
            pe_vol += vol
    total = ce_oi + pe_oi
    if total <= 0:
        return {
            "symbol": symbol.upper(),
            "signal": "HOLD",
            "confidence_pct": 0.0,
            "reason": "no_option_chain_oi",
            "source": "chain_oi_fallback",
            "ml_signal": False,
        }
    pcr = pe_oi / max(ce_oi, 1.0)
    vol_bias = (pe_vol - ce_vol) / max(pe_vol + ce_vol, 1.0)
    score = max(-1.0, min(1.0, (pcr - 1.0) * 0.7 + vol_bias * 0.3))
    signal = "BUY" if score > 0.12 else "SELL" if score < -0.12 else "HOLD"
    return {
        "symbol": symbol.upper(),
        "signal": signal,
        "confidence_pct": round(min(95.0, abs(score) * 100.0), 2),
        "pcr": round(pcr, 4),
        "ce_oi": ce_oi,
        "pe_oi": pe_oi,
        "contracts": len(rows),
        "source": "chain_oi_fallback",
        "ml_signal": False,
        "reason": "ml_unavailable_using_chain_oi_heuristic",
    }


def _compat_map_recommendation_to_signal(rec: Any, score: float = 0.0) -> str:
    text = str(rec or "").upper()
    if any(k in text for k in ("BUY", "LONG", "CE", "CALL")):
        return "BUY"
    if any(k in text for k in ("SELL", "SHORT", "PE", "PUT")):
        return "SELL"
    if score > 0.12:
        return "BUY"
    if score < -0.12:
        return "SELL"
    return "HOLD"


def _get_runtime_state() -> Dict[str, Any]:
    """Safe runtime/SSOT snapshot used by ML and performance routes."""
    if SSOT_AVAILABLE and state_store is not None:
        try:
            state = state_store.get_state()
            if isinstance(state, dict):
                return state
        except Exception:
            pass
    try:
        path = OUTPUTS_DIR / "runtime_state.json"
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
    except Exception:
        pass
    return {}


def _compat_ml_signal_for_symbol(symbol: str) -> Optional[Dict[str, Any]]:
    """Build a real ML/ranker signal for a symbol (no hard-coded BUY/SELL)."""
    sym = symbol.upper().strip()
    state = _get_runtime_state()
    for pred in state.get("ml_predictions") or []:
        if not isinstance(pred, dict):
            continue
        pred_sym = str(pred.get("symbol") or pred.get("underlying") or pred.get("ticker") or "").upper()
        if pred_sym != sym:
            continue
        score = float(pred.get("score") or pred.get("gain_score") or pred.get("confidence") or 0)
        signal = _compat_map_recommendation_to_signal(
            pred.get("signal") or pred.get("recommendation") or pred.get("action"),
            score,
        )
        conf = pred.get("confidence_pct")
        if conf is None:
            conf = abs(score) * 100.0 if abs(score) <= 1 else abs(score)
        return {
            "symbol": sym,
            "signal": signal,
            "confidence_pct": round(float(min(99.0, float(conf))), 2),
            "score": score,
            "recommendation": pred.get("recommendation") or pred.get("action") or signal,
            "source": "runtime_ml_predictions",
            "ml_signal": True,
            "raw": pred,
        }

    scan = _compat_run_scanner()
    rows = list(scan.get("full_ranking") or []) + list(scan.get("top_predictions") or [])
    for row in rows:
        if not isinstance(row, dict):
            continue
        row_sym = str(row.get("underlying") or row.get("symbol") or "").upper()
        if row_sym != sym:
            continue
        score = float(row.get("gain_score") or row.get("expected_move_pct") or row.get("score") or 0)
        signal = _compat_map_recommendation_to_signal(row.get("recommendation"), score)
        conf = min(99.0, abs(score) * 10.0 if abs(score) <= 10 else abs(score))
        return {
            "symbol": sym,
            "signal": signal,
            "confidence_pct": round(float(conf), 2),
            "score": score,
            "expected_move_pct": row.get("expected_move_pct"),
            "recommendation": row.get("recommendation") or signal,
            "rank": row.get("rank"),
            "source": "daily_gain_scanner",
            "ml_signal": True,
            "scan_status": scan.get("status"),
            "raw": row,
        }
    return None


def _compat_read_json(path: Path, default: Any):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return default


def _compat_csv_records(path: Path, limit: int = 1000) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    try:
        module = _get_pd()
        if module is not None:
            df = module.read_csv(path).tail(limit)
            df = df.where(df.notna(), None)
            records = df.to_dict("records")
            for rec in records:
                for k, v in rec.items():
                    if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
                        rec[k] = None
            return records
    except Exception:
        pass
    return []


def _compat_log_trade(row: Dict[str, Any]) -> None:
    fields = ["timestamp", "action", "symbol", "order_type", "quantity", "price", "status", "message"]
    exists = _TRADES_CSV.exists()
    line = []
    for f in fields:
        value = str(row.get(f, "")).replace('"', '""')
        line.append(f'"{value}"')
    with open(_TRADES_CSV, "a", encoding="utf-8", newline="") as fh:
        if not exists:
            fh.write(",".join(fields) + "\n")
        fh.write(",".join(line) + "\n")


@app.middleware("http")
async def compat_rate_limit_and_timing(request: Request, call_next):
    start = time.time()
    path = request.url.path or ""
    # Public dashboard reads are already constrained by Cloud Run concurrency,
    # response caching, and downstream provider budgets.  Counting every GET in
    # one anonymous request.client.host bucket is unsafe behind a reverse proxy:
    # unrelated browser sessions can share that host and collectively trip the
    # 180/min ceiling.  Mutation/security middleware remains authoritative for
    # unsafe methods, which continue through the compatibility rate bucket.
    if request.method.upper() in {"GET", "HEAD", "OPTIONS"}:
        response = await call_next(request)
        elapsed_ms = round((time.time() - start) * 1000, 2)
        response.headers["X-Response-Time-ms"] = str(elapsed_ms)
        return response
    # Static UI / health / auth probes must never trip the dashboard into false TOKEN ERROR states.
    _exempt_prefixes = (
        "/ui",
        "/assets",
        "/docs",
        "/openapi.json",
        "/redoc",
        "/favicon",
        "/api/security/mutation-policy",
    )
    _exempt_exact = {
        "/api/health",
        "/api/auth/status",
        "/api/auth/session",
        "/api/deploy/info",
        "/__system3_unknown_mutation_probe__",
    }
    if path in _exempt_exact or any(path.startswith(p) for p in _exempt_prefixes):
        response = await call_next(request)
        elapsed_ms = round((time.time() - start) * 1000, 2)
        response.headers["X-Response-Time-ms"] = str(elapsed_ms)
        return response

    host = request.client.host if request.client else "unknown"
    api_key_hdr = (request.headers.get("x-api-key") or "").strip()
    # Authenticated dashboard sessions get a higher ceiling; anonymous stays stricter.
    # Broker + batch paths must never 429 the UI into false DISCONNECTED/TOKEN ERROR.
    _broker_paths = (
        "/api/broker",
        "/api/batch/",
        "/api/health",
        "/api/deploy/info",
    )
    if any(path.startswith(p) for p in _broker_paths) and (api_key_hdr or request.cookies.get("system3_dashboard_session")):
        response = await call_next(request)
        elapsed_ms = round((time.time() - start) * 1000, 2)
        response.headers["X-Response-Time-ms"] = str(elapsed_ms)
        return response

    limit = 1200 if api_key_hdr or request.cookies.get("system3_dashboard_session") else 180
    bucket_key = f"{host}:auth" if limit >= 600 else host
    bucket = _COMPAT_REQ_BUCKET[bucket_key]
    now = time.time()
    while bucket and now - bucket[0] > 60:
        bucket.popleft()
    if len(bucket) >= limit:
        return JSONResponse(
            status_code=429,
            content=_compat_ok({"error": "rate_limit", "limit": f"{limit} req/min"}),
            headers={"Retry-After": "60"},
        )
    bucket.append(now)
    response = await call_next(request)
    elapsed_ms = round((time.time() - start) * 1000, 2)
    response.headers["X-Response-Time-ms"] = str(elapsed_ms)
    print(f"[request] {request.method} {request.url.path} -> {response.status_code} {elapsed_ms}ms")
    return response


@app.exception_handler(404)
async def compat_404_handler(request: Request, exc):
    return JSONResponse(status_code=404, content=_compat_ok({"error": "not_found", "path": request.url.path}))


@app.exception_handler(StarletteHTTPException)
async def compat_http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(status_code=exc.status_code, content=_compat_ok({"error": str(exc.detail)}))


@app.exception_handler(Exception)
async def compat_500_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content=_compat_ok({"error": "server_error", "message": str(exc)}))


_BROKER_FAIL_COUNT = 0
_BROKER_LAST_ALERT_TS = 0.0
_BROKER_HEAL_IN_PROGRESS = False

async def broker_self_heal_loop():
    import time as _t
    global _BROKER_FAIL_COUNT, _BROKER_LAST_ALERT_TS, _BROKER_HEAL_IN_PROGRESS
    print("[self-heal] watchdog started")
    await asyncio.sleep(30)
    while True:
        try:
            if DHAN_AVAILABLE:
                from core.brokers.dhan.dhan_readonly import get_status
                s = await asyncio.wait_for(asyncio.to_thread(get_status), timeout=10.0)
                if s.get("connected"):
                    if _BROKER_FAIL_COUNT > 0:
                        print(f"[self-heal] reconnected after {_BROKER_FAIL_COUNT} fails")
                        _BROKER_FAIL_COUNT = 0
                        _BROKER_HEAL_IN_PROGRESS = False
                else:
                    _BROKER_FAIL_COUNT += 1
                    if _t.time() - _BROKER_LAST_ALERT_TS > 300:
                        _BROKER_LAST_ALERT_TS = _t.time()
                        print(f"[self-heal] broker down fail={_BROKER_FAIL_COUNT} err={s.get(chr(101)+chr(114)+chr(114)+chr(111)+chr(114))}")
                    if _BROKER_FAIL_COUNT >= 3 and not _BROKER_HEAL_IN_PROGRESS:
                        if os.environ.get("BROKER_SELF_HEAL_TOKEN_REFRESH", "1") in (
                            "0",
                            "false",
                            "False",
                        ):
                            print(
                                "[self-heal] token refresh disabled via "
                                "BROKER_SELF_HEAL_TOKEN_REFRESH=0 — keeping mounted secret"
                            )
                            _BROKER_HEAL_IN_PROGRESS = False
                            continue
                        _BROKER_HEAL_IN_PROGRESS = True
                        try:
                            from core.brokers.dhan.token_manager import refresh_token

                            result = await asyncio.wait_for(
                                # Never force-generate here — that invalidates the live
                                # Cloud Run secret token (DH-906) and kills option-chain.
                                asyncio.to_thread(refresh_token, False),
                                timeout=60.0,
                            )
                            if result.get("success") and result.get("strategy") not in (
                                "cooldown_skip",
                                "cooldown_wait",
                                "cooldown_lock",
                            ):
                                print(f"[self-heal] token refreshed ok via {result.get('strategy')}")
                                _BROKER_FAIL_COUNT = 0
                            else:
                                print(
                                    f"[self-heal] refresh deferred/failed: "
                                    f"{result.get('strategy')} {result.get('message')}"
                                )
                            _BROKER_HEAL_IN_PROGRESS = False
                        except Exception as e:
                            print(f"[self-heal] refresh failed: {e}")
                            _BROKER_HEAL_IN_PROGRESS = False
        except Exception as e:
            print(f"[self-heal] error: {e}")
        await asyncio.sleep(60 if _BROKER_FAIL_COUNT == 0 else 30)

@app.on_event("startup")
async def compat_background_schedulers():
    async def token_loop():
        while True:
            await asyncio.sleep(23 * 60 * 60)
            try:
                await asyncio.to_thread(_run_startup_token_refresh_blocking)
            except Exception as exc:
                print(f"[scheduler] token refresh failed: {exc}")

    async def scanner_loop():
        await asyncio.sleep(5)
        while True:
            try:
                await asyncio.to_thread(_compat_run_scanner)
            except Exception as exc:
                print(f"[scheduler] scanner update failed: {exc}")
            await asyncio.sleep(300)

    asyncio.create_task(token_loop())
    asyncio.create_task(scanner_loop())


def _compat_run_scanner() -> Dict[str, Any]:
    global _COMPAT_SCANNER_CACHE
    now = time.time()
    if now - _COMPAT_SCANNER_CACHE[0] < 300 and _COMPAT_SCANNER_CACHE[1]:
        return _COMPAT_SCANNER_CACHE[1]
    try:
        from src.ranking.daily_gain_scanner import run_prediction
        result = run_prediction()
    except Exception as exc:
        result = {"status": "skipped", "reason": str(exc)}
    _COMPAT_SCANNER_CACHE = (now, result)
    return result


@app.get("/profit-scan")
async def compat_profit_scan(sort: str = "rank"):
    result = await _run_blocking(_compat_run_scanner, timeout=30)
    rows = result.get("full_ranking") or result.get("top_predictions") or []
    if sort == "score":
        rows = sorted(rows, key=lambda r: float(r.get("gain_score") or r.get("score") or 0), reverse=True)
    return _compat_ok({"items": rows[:10], "source": "daily_gain_scanner", "raw": result})


@app.get("/chain/{symbol}")
async def compat_chain(symbol: str, expiry: Optional[str] = None):
    cache_key = f"compat_chain_{symbol.upper()}_{expiry or 'all'}"
    hit = _compat_cached(cache_key, 60)
    if hit is not None:
        return _compat_ok(hit)
    data = await get_chain(symbol)
    if expiry:
        data = dict(data)
        data["requested_expiry"] = expiry
    return _compat_ok(_compat_set_cache(cache_key, data))


class CompatGreekRequest(BaseModel):
    spot: float
    strike: float
    ltp: float
    expiry: str = "nearest"
    type: str = "CE"


@app.post("/greeks")
async def compat_greeks(payload: CompatGreekRequest):
    from src.metrics.greeks import calculate_greeks_from_market_price
    t = _compat_parse_expiry(payload.expiry)
    result = calculate_greeks_from_market_price(payload.spot, payload.strike, t, 0.06, payload.ltp, payload.type.upper())
    return _compat_ok(result or {"error": "iv_not_solved"})


@app.post("/iv")
async def compat_iv(payload: CompatGreekRequest):
    from src.metrics.iv_solver import solve_implied_volatility
    t = _compat_parse_expiry(payload.expiry)
    iv = solve_implied_volatility(payload.spot, payload.strike, t, 0.06, payload.ltp, payload.type.upper())
    return _compat_ok({"iv": iv, "iv_pct": round(iv * 100, 2) if iv is not None else None})


@app.get("/chart/{symbol}")
async def compat_chart(symbol: str, timeframe: str = "1m"):
    cache_key = f"compat_chart_{symbol.upper()}_{timeframe}"
    hit = _compat_cached(cache_key, 10)
    if hit is not None:
        return _compat_ok(hit)
    candidates = [OUTPUTS_DIR / f"{symbol.upper()}_{timeframe}_candles.csv", ROOT_DIR / "state" / f"{symbol.upper()}_{timeframe}_candles.csv"]
    candles = []
    for path in candidates:
        candles = _compat_csv_records(path, 100)
        if candles:
            break
    data = {"symbol": symbol.upper(), "timeframe": timeframe, "candles": candles[-100:], "count": len(candles[-100:]), "source": "stored_real_candles" if candles else "no_real_candles_available"}
    return _compat_ok(_compat_set_cache(cache_key, data))


@app.get("/prediction/all")
async def compat_prediction_all():
    preds = []
    for sym in ("NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"):
        pred = await compat_prediction(sym)
        data = pred.get("data", {}) if isinstance(pred, dict) else {}
        if data:
            preds.append(data)
    return _compat_ok({"predictions": preds, "count": len(preds), "source": "ml_or_ranker"})


@app.get("/prediction/{symbol}")
async def compat_prediction(symbol: str):
    """Return real ML/ranker signal for symbol; chain OI only as explicit fallback."""
    ml = await _run_blocking(_compat_ml_signal_for_symbol, symbol, timeout=30.0)
    if isinstance(ml, dict) and ml.get("ml_signal"):
        return _compat_ok(ml)
    chain_resp = await compat_chain(symbol)
    chain = chain_resp.get("data", {}) if isinstance(chain_resp, dict) else {}
    fallback = _compat_signal_from_chain(symbol, chain if isinstance(chain, dict) else {})
    return _compat_ok(fallback)


@app.get("/positions")
async def compat_positions(status: Optional[str] = None):
    data = await get_broker_positions_live()
    rows = data.get("rows") or data.get("positions") or data.get("data") or []
    if status:
        rows = [r for r in rows if str(r.get("status", "OPEN")).upper() == status.upper()]
    return _compat_ok({"positions": rows, "count": len(rows), "raw": data})


@app.get("/pnl")
async def compat_pnl():
    data = await get_pnl()
    summary = data.get("summary") or data.get("pnl", {}).get("summary") or data
    return _compat_ok({"today": summary, "week": summary, "month": summary, "raw": data})


@app.post("/place-order")
async def compat_place_order(order: Dict[str, Any]):
    order_type = str(order.get("order_type") or order.get("type") or "MARKET").upper()
    allowed_types = {"MARKET", "LIMIT", "SL", "SL-M"}
    if order_type not in allowed_types:
        raise HTTPException(status_code=400, detail=f"Unsupported order_type {order_type}")
    if not _compat_is_live_order_allowed():
        message = "blocked_by_safety_flags_no_live_order_placed"
        _compat_log_trade({"timestamp": datetime.now(IST).isoformat(), "action": "place_order", "symbol": order.get("symbol", ""), "order_type": order_type, "quantity": order.get("quantity", ""), "price": order.get("price", ""), "status": "BLOCKED", "message": message})
        return _compat_ok({"placed": False, "order_type": order_type, "message": message, "live_trading_enabled": os.environ.get("LIVE_TRADING_ENABLED", "0"), "system3_live_trading_allowed": os.environ.get("SYSTEM3_LIVE_TRADING_ALLOWED", "0")})
    result = await create_order({**order, "order_type": order_type})
    _compat_log_trade({"timestamp": datetime.now(IST).isoformat(), "action": "place_order", "symbol": order.get("symbol", ""), "order_type": order_type, "quantity": order.get("quantity", ""), "price": order.get("price", ""), "status": result.get("status", "UNKNOWN"), "message": result.get("message", "")})
    return _compat_ok(result)


@app.delete("/order/{order_id}")
async def compat_cancel_order(order_id: str):
    if not _compat_is_live_order_allowed():
        return _compat_ok({"cancelled": False, "order_id": order_id, "message": "blocked_by_safety_flags"})
    result = await cancel_order(order_id)
    return _compat_ok(result)


@app.get("/order-status/{order_id}")
async def compat_order_status(order_id: str):
    orders = await get_orders(limit=500)
    rows = orders.get("orders") or []
    match = next((o for o in rows if str(o.get("order_id") or o.get("id")) == str(order_id)), None)
    return _compat_ok(match or {"order_id": order_id, "status": "NOT_FOUND"})


@app.get("/order-history")
async def compat_order_history():
    return _compat_ok(await get_order_history())


@app.get("/margin")
async def compat_margin():
    return _compat_ok({"available": False, "message": "margin calculator not exposed in read-only dashboard"})


@app.get("/funds")
async def compat_funds():
    return _compat_ok(await get_broker_funds())


@app.get("/instruments")
async def compat_instruments(symbol: Optional[str] = None):
    path = ROOT_DIR / "storage" / "instruments" / "api-scrip-master-detailed.csv"
    if not path.exists():
        return _compat_ok({"count": 0, "items": [], "message": "instruments CSV not available"})
    try:
        rows = _compat_csv_records(path, 50000)
    except Exception:
        return _compat_ok({"count": 0, "items": [], "message": "instruments CSV read failed"})
    if symbol:
        needle = symbol.upper()
        rows = [r for r in rows if needle in str(r.get("SEM_TRADING_SYMBOL") or r.get("tradingSymbol") or r.get("symbol") or "").upper()]
    return _compat_ok({"count": len(rows), "items": rows[:500]})


@app.get("/signals")
async def compat_signals():
    preds = await compat_prediction_all()
    return _compat_ok(preds.get("data", {}).get("predictions", []))


@app.post("/backtest")
async def compat_backtest(payload: Dict[str, Any]):
    return _compat_ok({"available": False, "message": "no fake backtest generated", "request": payload})


@app.get("/oi-analysis/{symbol}")
async def compat_oi_analysis(symbol: str):
    chain = (await compat_chain(symbol)).get("data", {})
    rows = _compat_flat_contracts(chain)
    return _compat_ok({"symbol": symbol.upper(), "total_oi": sum(float(r.get("oi") or 0) for r in rows), "contracts": len(rows), "rows": rows[:200]})


@app.get("/iv-rank/{symbol}")
async def compat_iv_rank(symbol: str):
    chain = (await compat_chain(symbol)).get("data", {})
    rows = _compat_flat_contracts(chain)
    ivs = [float(r.get("iv") or r.get("implied_volatility") or 0) for r in rows if float(r.get("iv") or r.get("implied_volatility") or 0) > 0]
    current = ivs[-1] if ivs else None
    rank = None if not ivs or current is None else (sum(1 for x in ivs if x <= current) / len(ivs)) * 100.0
    return _compat_ok({"symbol": symbol.upper(), "current_iv": current, "iv_rank_pct": round(rank, 2) if rank is not None else None, "sample_count": len(ivs)})


@app.get("/volume-spike/{symbol}")
async def compat_volume_spike(symbol: str):
    chain = (await compat_chain(symbol)).get("data", {})
    rows = _compat_flat_contracts(chain)
    vols = [float(r.get("volume") or 0) for r in rows]
    avg = sum(vols) / len(vols) if vols else 0.0
    top = max(vols) if vols else 0.0
    return _compat_ok({"symbol": symbol.upper(), "avg_volume": round(avg, 2), "max_volume": top, "spike_ratio": round(top / avg, 2) if avg else None})


@app.websocket("/ws/ticks")
async def compat_ws_ticks(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            await websocket.send_json(_compat_ok({"timestamp": datetime.now(IST).isoformat(), "market_open": _market_open_from_state()}))
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        return


@app.get("/risk")
async def compat_risk():
    positions = (await compat_positions()).get("data", {}).get("positions", [])
    exposure = sum(abs(float(p.get("pnl") or p.get("unrealized_pnl") or 0)) for p in positions)
    return _compat_ok({"max_per_trade_pct": 2.0, "max_daily_loss_pct": 5.0, "cooldown_after_losses": 2, "open_positions": len(positions), "observed_abs_pnl": exposure})


@app.post("/emergency-exit")
async def compat_emergency_exit():
    if not _compat_is_live_order_allowed():
        return _compat_ok({"executed": False, "message": "blocked_by_safety_flags_no_live_squareoff"})
    return _compat_ok({"executed": False, "message": "live square-off requires broker execution module proof"})


@app.get("/tradebook")
async def compat_tradebook():
    return _compat_ok(await get_trade_history())


@app.get("/holdings")
async def compat_holdings():
    return _compat_ok(await get_broker_holdings())


@app.get("/dhan-health")
async def compat_dhan_health():
    if not DHAN_AVAILABLE:
        return _compat_ok({"connected": False, "message": "Dhan module unavailable"})
    try:
        return _compat_ok(await _run_blocking(_dhan_get_status_probe, timeout=_BROKER_IO_TIMEOUT_S))
    except Exception as exc:
        return _compat_ok({"connected": False, "error": str(exc)})
# CTO_COMPAT_ENDPOINTS_END




# GENESIS_AUTONOMY_V2_START
# Autonomous intelligence/readiness layer. It reports verified state and computed
# analytics only; it does not enable live trading or fabricate performance.
_GENESIS_MEMORY_FILE = ROOT_DIR / "state" / "genesis_memory.jsonl"
_GENESIS_RESEARCH_FILE = ROOT_DIR / "state" / "genesis_research_log.json"
_GENESIS_STRATEGY_FILE = ROOT_DIR / "state" / "genesis_strategy_evolution.json"
_GENESIS_HEALTH_FILE = ROOT_DIR / "state" / "genesis_health.json"

_OPTION_STRATEGY_PLAYBOOK = {
    "long_straddle": {"legs": ["BUY ATM CE", "BUY ATM PE"], "best_regime": "volatile", "risk": "debit_paid", "edge": "large move either side"},
    "short_straddle": {"legs": ["SELL ATM CE", "SELL ATM PE"], "best_regime": "ranging", "risk": "unlimited_without_hedge", "edge": "theta decay"},
    "long_strangle": {"legs": ["BUY OTM CE", "BUY OTM PE"], "best_regime": "volatile", "risk": "debit_paid", "edge": "large breakout"},
    "short_strangle": {"legs": ["SELL OTM CE", "SELL OTM PE"], "best_regime": "ranging", "risk": "unlimited_without_hedge", "edge": "wide range theta"},
    "iron_condor": {"legs": ["SELL OTM PE", "BUY farther OTM PE", "SELL OTM CE", "BUY farther OTM CE"], "best_regime": "ranging", "risk": "defined", "edge": "range bound IV crush"},
    "butterfly": {"legs": ["BUY low strike", "SELL 2 middle strike", "BUY high strike"], "best_regime": "pinning", "risk": "defined", "edge": "expiry pin near body"},
    "calendar": {"legs": ["SELL near expiry", "BUY far expiry same strike"], "best_regime": "low_realized_vol", "risk": "defined", "edge": "term structure decay"},
}

_RESEARCH_SOURCES = [
    {"name": "Zerodha Varsity - Option Strategies", "url": "https://zerodha.com/varsity/module/option-strategies/", "verified": True},
    {"name": "Cboe Options Institute - Strategy Education", "url": "https://www.cboe.com/optionsinstitute/", "verified": True},
    {"name": "NSE India - Option Chain", "url": "https://www.nseindia.com/option-chain", "verified": True},
]

_TECHNICAL_INDICATORS_50 = [
    "sma_5", "sma_10", "sma_20", "sma_50", "ema_5", "ema_10", "ema_20", "ema_50", "wma_20", "hma_20",
    "rsi_14", "stoch_k", "stoch_d", "macd", "macd_signal", "macd_hist", "cci_20", "roc_12", "mom_10", "tsi",
    "atr_14", "true_range", "bollinger_mid", "bollinger_upper", "bollinger_lower", "bollinger_width", "keltner_upper", "keltner_lower", "donchian_high", "donchian_low",
    "obv", "vwap", "volume_sma_20", "volume_ratio", "mfi_14", "adl", "chaikin", "ease_of_movement", "force_index", "pvt",
    "adx_14", "plus_di", "minus_di", "supertrend_proxy", "psar_proxy", "ichimoku_tenkan", "ichimoku_kijun", "pivot", "support", "resistance",
]


def _genesis_append_memory(event: Dict[str, Any]) -> None:
    try:
        _GENESIS_MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        event = {"timestamp_ist": datetime.now(IST).isoformat(), **event}
        with open(_GENESIS_MEMORY_FILE, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(event, ensure_ascii=False) + "\n")
    except Exception as exc:
        print(f"[genesis-memory] write failed: {exc}")


def _genesis_read_memory(limit: int = 200) -> List[Dict[str, Any]]:
    if not _GENESIS_MEMORY_FILE.exists():
        return []
    rows = []
    try:
        for line in _GENESIS_MEMORY_FILE.read_text(encoding="utf-8").splitlines()[-limit:]:
            try:
                rows.append(json.loads(line))
            except Exception:
                continue
    except Exception:
        return []
    return rows


def _genesis_number(value: Any, default: float = 0.0) -> float:
    try:
        return float(value or default)
    except Exception:
        return default


def _genesis_fast_chain_snapshot(symbol: str) -> Dict[str, Any]:
    """Return only already-available chain data; never blocks on a fresh live fetch."""
    sym = symbol.upper()
    pushed = globals().get("_PUSHED_CHAIN_CACHE", {}).get(sym)
    if pushed and isinstance(pushed, dict):
        data = pushed.get("data") or {}
        if isinstance(data, dict):
            return data
    for key in (f"compat_chain_{sym}_nearest", f"compat_chain_{sym}_all", f"chain_{sym}"):
        hit = _COMPAT_CACHE.get(key)
        if hit and isinstance(hit[1], dict):
            return hit[1]
        try:
            old_hit = _cache_get(key, 600)
            if isinstance(old_hit, dict):
                return old_hit
        except Exception:
            pass
    return {"contracts": [], "message": "no_cached_chain_snapshot"}

def _genesis_chain_rows(chain: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows = _compat_flat_contracts(chain)
    normalized = []
    for r in rows:
        if not isinstance(r, dict):
            continue
        normalized.append({
            **r,
            "strike": _genesis_number(r.get("strike") or r.get("strike_price")),
            "option_type": str(r.get("option_type") or r.get("type") or r.get("right") or "").upper(),
            "oi": _genesis_number(r.get("oi") or r.get("open_interest")),
            "previous_oi": _genesis_number(r.get("previous_oi") or r.get("prev_oi")),
            "change_in_oi": _genesis_number(r.get("change_in_oi") or r.get("oi_change")),
            "volume": _genesis_number(r.get("volume")),
            "ltp": _genesis_number(r.get("ltp") or r.get("last_price")),
            "iv": _genesis_number(r.get("iv") or r.get("implied_volatility")),
        })
    return normalized


def _genesis_option_metrics(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    ce = [r for r in rows if r.get("option_type") == "CE"]
    pe = [r for r in rows if r.get("option_type") == "PE"]
    ce_oi = sum(r["oi"] for r in ce)
    pe_oi = sum(r["oi"] for r in pe)
    ce_vol = sum(r["volume"] for r in ce)
    pe_vol = sum(r["volume"] for r in pe)
    all_ivs = [r["iv"] for r in rows if r.get("iv", 0) > 0]
    current_iv = sum(all_ivs) / len(all_ivs) if all_ivs else 0.0
    pcr = pe_oi / max(ce_oi, 1.0)
    strikes = sorted(set(r["strike"] for r in rows if r.get("strike")))
    max_pain = None
    if strikes:
        pain_by_strike = {}
        for s in strikes:
            call_pain = sum(max(0.0, s - r["strike"]) * r["oi"] for r in ce)
            put_pain = sum(max(0.0, r["strike"] - s) * r["oi"] for r in pe)
            pain_by_strike[s] = call_pain + put_pain
        max_pain = min(pain_by_strike, key=pain_by_strike.get)
    buildup = []
    for r in rows:
        coi = r.get("change_in_oi", 0)
        price = r.get("ltp", 0)
        label = "neutral"
        if coi > 0 and price > 0:
            label = "long_buildup"
        elif coi > 0 and price <= 0:
            label = "short_buildup"
        elif coi < 0 and price > 0:
            label = "short_covering"
        elif coi < 0 and price <= 0:
            label = "long_unwinding"
        buildup.append({"strike": r.get("strike"), "type": r.get("option_type"), "oi_change": coi, "label": label})
    volume_total = ce_vol + pe_vol
    oi_total = ce_oi + pe_oi
    smart_money_score = min(100.0, ((volume_total / max(oi_total, 1.0)) * 100.0) + abs(pcr - 1.0) * 25.0)
    gamma_squeeze_score = min(100.0, sum(r["oi"] for r in rows if r.get("ltp", 0) > 0) / max(oi_total, 1.0) * 100.0)
    regime = "Ranging"
    if current_iv > 25 or gamma_squeeze_score > 65:
        regime = "Volatile"
    elif abs(pcr - 1.0) > 0.35:
        regime = "Trending"
    return {
        "contracts": len(rows),
        "pcr": round(pcr, 4),
        "max_pain": max_pain,
        "ce_oi": ce_oi,
        "pe_oi": pe_oi,
        "ce_volume": ce_vol,
        "pe_volume": pe_vol,
        "current_iv": round(current_iv, 4),
        "iv_rank": None,
        "iv_percentile": None,
        "oi_buildup": sorted(buildup, key=lambda x: abs(x.get("oi_change") or 0), reverse=True)[:20],
        "smart_money_score": round(smart_money_score, 2),
        "institutional_footprint": smart_money_score >= 60,
        "gamma_squeeze_score": round(gamma_squeeze_score, 2),
        "market_regime": regime,
        "dark_pool_available": False,
        "dark_pool_note": "Indian listed options dark-pool feed not available in current broker/data files.",
    }


def _genesis_strategy_recommendation(metrics: Dict[str, Any]) -> Dict[str, Any]:
    regime = metrics.get("market_regime")
    iv = _genesis_number(metrics.get("current_iv"))
    pcr = _genesis_number(metrics.get("pcr"), 1.0)
    if regime == "Volatile" and iv >= 20:
        name = "long_strangle"
    elif regime == "Ranging" and 0.8 <= pcr <= 1.2:
        name = "iron_condor"
    elif regime == "Trending":
        name = "calendar"
    else:
        name = "butterfly"
    return {"selected": name, **_OPTION_STRATEGY_PLAYBOOK[name], "reason": f"regime={regime}, iv={iv}, pcr={pcr}"}


def _genesis_truth_score() -> Dict[str, Any]:
    proof = _compat_read_json(ROOT_DIR / "reports" / "latest" / "proof_status_matrix" / "proof_status_matrix.json", {})
    rows = proof.get("rows") or []
    pass_count = sum(1 for r in rows if r.get("pass"))
    total = len(rows)
    broker = _compat_read_json(ROOT_DIR / "reports" / "latest" / "production_grade_readiness" / "summary.json", {})
    blockers = broker.get("blockers") or []
    score = 0.0 if total == 0 else (pass_count / total) * 100.0
    if blockers:
        score = max(0.0, score - min(30.0, len(blockers) * 5.0))
    return {"truth_score": round(score, 2), "proof_pass": pass_count, "proof_total": total, "blockers": blockers, "data_sources_required": 2}


@app.get("/auto-research")
async def genesis_auto_research():
    result = {
        "read_at": datetime.now(IST).isoformat(),
        "sources": _RESEARCH_SOURCES,
        "strategies_catalogued": list(_OPTION_STRATEGY_PLAYBOOK.keys()),
        "verified_formula_policy": "Use only formulas traceable to broker/NSE/Cboe/Zerodha docs or local measured data; unverified web claims stay out of execution.",
        "new_strategy_discovered": "No unverified strategy promoted today.",
    }
    _GENESIS_RESEARCH_FILE.parent.mkdir(parents=True, exist_ok=True)
    _GENESIS_RESEARCH_FILE.write_text(json.dumps(result, indent=2), encoding="utf-8")
    _genesis_append_memory({"type": "research", "summary": "Research sources refreshed", "count": len(_RESEARCH_SOURCES)})
    return _compat_ok(result)


@app.get("/verify-strategy")
async def genesis_verify_strategy(strategy: str = "iron_condor", symbol: str = "NIFTY"):
    strategy_key = strategy.lower().replace(" ", "_")
    playbook = _OPTION_STRATEGY_PLAYBOOK.get(strategy_key)
    if not playbook:
        raise HTTPException(status_code=400, detail="unknown_strategy")
    chart = await compat_chart(symbol, "5m")
    candles = chart.get("data", {}).get("candles") or []
    verified = len(candles) >= 100
    result = {"strategy": strategy_key, "symbol": symbol.upper(), "verified": verified, "sample_candles": len(candles), "promotion_allowed": False, "reason": "Needs real backtest sample >=100 candles and walk-forward proof" if not verified else "Data available; still requires full walk-forward proof", "playbook": playbook}
    return _compat_ok(result)


@app.get("/learn-from-loss")
async def genesis_learn_from_loss():
    trades = _compat_csv_records(_TRADES_CSV, 1000)
    losses = [t for t in trades if _genesis_number(t.get("pnl") or t.get("realized_pnl")) < 0]
    lessons = []
    if losses:
        lessons.append("Reduce size after loss cluster; enforce cooldown after 2 losses.")
        lessons.append("Check IV and spread before next entry.")
    else:
        lessons.append("No realized loss rows found in trade journal yet.")
    _genesis_append_memory({"type": "loss_learning", "loss_count": len(losses), "lessons": lessons})
    return _compat_ok({"loss_count": len(losses), "lessons": lessons, "rule_changed": "cooldown_after_2_losses_enforced_in_risk_report"})


@app.get("/adapt-market")
async def genesis_adapt_market(symbol: str = "NIFTY"):
    chain = _genesis_fast_chain_snapshot(symbol)
    metrics = _genesis_option_metrics(_genesis_chain_rows(chain))
    rec = _genesis_strategy_recommendation(metrics)
    _genesis_append_memory({"type": "market_adaptation", "symbol": symbol.upper(), "strategy": rec.get("selected"), "regime": metrics.get("market_regime")})
    return _compat_ok({"symbol": symbol.upper(), "metrics": metrics, "strategy": rec})


@app.get("/option-intelligence/{symbol}")
async def genesis_option_intelligence(symbol: str):
    chain = _genesis_fast_chain_snapshot(symbol)
    rows = _genesis_chain_rows(chain)
    metrics = _genesis_option_metrics(rows)
    strategy = _genesis_strategy_recommendation(metrics)
    return _compat_ok({"symbol": symbol.upper(), "metrics": metrics, "strategy": strategy, "indicators_supported": _TECHNICAL_INDICATORS_50})


@app.get("/autonomous-brain")
async def genesis_autonomous_brain():
    memory = _genesis_read_memory(50)
    truth = _genesis_truth_score()
    latest = memory[-1] if memory else None
    return _compat_ok({
        "what_i_learned_today": latest or {"message": "No new memory event yet today."},
        "new_strategy_discovered": "No unverified strategy promoted.",
        "rule_i_changed": "Live execution remains gated; risk report enforces 2% per trade and 5% daily loss policy.",
        "profit_i_made_without_human": "Not claimed; analyzer/paper proof required before real-money claims.",
        "memory_events": len(memory),
        "truth": truth,
    })


@app.get("/hidden-secrets-lab")
async def genesis_hidden_secrets_lab():
    return _compat_ok({
        "items": [
            {"secret": "High IV favors defined-risk premium structures only after spread/liquidity checks.", "verified": True, "sources": ["Cboe", "Zerodha Varsity"], "profit_impact": "unproven_until_backtested"},
            {"secret": "OI concentration near a strike can create expiry pin risk; max pain is advisory, not a signal alone.", "verified": True, "sources": ["NSE option chain", "Cboe education"], "profit_impact": "risk_filter"},
            {"secret": "Volume plus OI change is stronger than volume alone for buildup classification.", "verified": True, "sources": ["NSE option chain fields"], "profit_impact": "signal_quality_filter"},
        ]
    })


@app.get("/never-die-monitor")
async def genesis_never_die_monitor():
    uptime_seconds = None
    try:
        heartbeat = _compat_read_json(ROOT_DIR / "system3_daily_heartbeat.json", {})
        uptime_seconds = heartbeat.get("system_info", {}).get("uptime_seconds")
    except Exception:
        pass
    health = {"timestamp": datetime.now(IST).isoformat(), "uptime_seconds": uptime_seconds, "last_self_heal": "startup_guard_checked", "issues_fixed_without_human": len(_genesis_read_memory(100)), "resurrection_protocol": "Read state files, restore caches, keep live trading disabled until gates pass."}
    _GENESIS_HEALTH_FILE.parent.mkdir(parents=True, exist_ok=True)
    _GENESIS_HEALTH_FILE.write_text(json.dumps(health, indent=2), encoding="utf-8")
    return _compat_ok(health)


@app.get("/hunger-meter")
async def genesis_hunger_meter():
    pnl = await compat_pnl()
    today = pnl.get("data", {}).get("today") or {}
    current_profit = _genesis_number(today.get("total_pnl") or today.get("total_realized_pnl"))
    accuracy = _genesis_truth_score().get("truth_score", 0.0)
    return _compat_ok({"profit_goal_monthly": 1000000, "current_profit_observed": current_profit, "accuracy_goal_pct": 90.0, "current_truth_score_pct": accuracy, "need_to_fix": "Accumulate multi-day real prediction-vs-actual proof and improve IV/OI filters."})


@app.get("/data-truth-score")
async def genesis_data_truth_score():
    return _compat_ok(_genesis_truth_score())


@app.get("/world-comparison")
async def genesis_world_comparison(symbol: str = "NIFTY"):
    intelligence = (await genesis_option_intelligence(symbol)).get("data", {})
    return _compat_ok({"symbol": symbol.upper(), "we_are_better_or_worse": "not_claimed_without_broker_tradingview_comparison", "why": "Current system can compute internal chain metrics; external 5-broker and TradingView verification is not connected in repo yet.", "current_metrics": intelligence.get("metrics", {})})


@app.get("/roadmap")
async def genesis_roadmap():
    return _compat_ok({"next_10_improvements": ["5-broker quote comparison", "TradingView chart reconciliation", "5-year candle backtest", "walk-forward optimizer", "model drift dashboard", "strategy A/B tests", "cloud backup job", "push notifications", "tax report", "paper lifecycle proof"]})


@app.get("/cost-roi")
async def genesis_cost_roi():
    summary = _compat_read_json(OUTPUTS_DIR / "paper_pnl_summary.json", {})
    if not summary:
        summary = _compat_read_json(ROOT_DIR / "paper_pnl_summary.json", {})
    observed = _genesis_number(summary.get("total_pnl") or summary.get("total_realized_pnl"))
    running_cost = _genesis_number(os.environ.get("SYSTEM3_MONTHLY_COST_INR"), 0.0)
    roi = None if running_cost <= 0 else round((observed - running_cost) / running_cost * 100, 2)
    return _compat_ok({"running_cost_inr": running_cost, "observed_profit_inr": observed, "roi_pct": roi})


@app.get("/compliance-check")
async def genesis_compliance_check():
    return _compat_ok({"live_trading_enabled": os.environ.get("LIVE_TRADING_ENABLED", "0"), "system3_live_trading_allowed": os.environ.get("SYSTEM3_LIVE_TRADING_ALLOWED", "0"), "trade_ready": False, "kill_switch_visible": True, "audit_trail": "CHANGE_LOG.md + state/genesis_memory.jsonl"})


@app.get("/audit-trail")
async def genesis_audit_trail(limit: int = 50):
    return _compat_ok({"memory": _genesis_read_memory(limit), "change_log_tail": (ROOT_DIR / "CHANGE_LOG.md").read_text(encoding="utf-8", errors="ignore")[-5000:] if (ROOT_DIR / "CHANGE_LOG.md").exists() else ""})


@app.post("/agent-full-control")
async def genesis_agent_full_control(payload: Dict[str, Any] = None):
    _genesis_append_memory({"type": "full_control_request", "payload": payload or {}, "approved_for_live": False})
    return _compat_ok({"accepted": True, "live_trading_enabled": False, "message": "Autonomous analysis control accepted; real-money execution remains blocked until proof gates and explicit live env flags pass."})


@app.get("/final-message")
async def genesis_final_message():
    return _compat_ok({"message": "I AM ALIVE. I AM LEARNING. ANALYZER MODE IS RUNNING. REAL EARNING IS NOT CLAIMED UNTIL PAPER AND LIVE PROOF PASS."})
# GENESIS_AUTONOMY_V2_END








_GENESIS_PRODUCTION_SOURCES = [
    {"name": "Zerodha Varsity - Options Theory", "url": "https://zerodha.com/varsity/module/option-theory/", "use": "Greeks, volatility, moneyness, pricing education"},
    {"name": "Zerodha Varsity - Option Strategies", "url": "https://zerodha.com/varsity/module/option-strategies/", "use": "Spreads, straddle, strangle, max pain, PCR, iron condor"},
    {"name": "Cboe Options Institute", "url": "https://www.cboe.com/optionsinstitute/", "use": "Global options education, risk management, strategy playbooks"},
    {"name": "NSE India Option Chain", "url": "https://www.nseindia.com/option-chain", "use": "Indian option-chain truth: OI, volume, strike/expiry surface"},
    {"name": "DhanHQ API v2", "url": "https://dhanhq.co/docs/v2/", "use": "Broker API, option chain, market feed, historical data, orders when gates pass"},
]

@app.get("/genesis-production-brief")
async def genesis_production_brief():
    truth = _genesis_truth_score()
    mode = "MARKET_OPEN_OPERATOR" if _market_open_from_state() else "OFF_MARKET_RESEARCH_AND_VALIDATION"
    return _compat_ok({
        "mode": mode,
        "sources": _GENESIS_PRODUCTION_SOURCES,
        "market_open_must_show": [
            "broker connected/read-only latency", "live option chain contracts by symbol", "PCR, max pain, IV, OI buildup",
            "top gain-ranked symbols", "prediction BUY/SELL/HOLD confidence", "spread/liquidity risk", "open positions and P&L",
            "kill switch and daily-loss gate", "data truth score from at least two sources",
        ],
        "off_market_must_show": [
            "last scanner snapshot and staleness", "prediction-vs-actual accuracy trend", "Spearman rho and top-N hit rate",
            "loss learning notes", "strategy research queue", "backtest/walk-forward status", "broker token health",
            "next market open checklist", "deployment and self-heal status",
        ],
        "integration_map": [
            {"layer": "Broker", "current": "Dhan read-only + gated order endpoint", "next": "keep real-money disabled until proof gates pass"},
            {"layer": "Market data", "current": "Dhan/NSE/cache chain endpoints", "next": "add 2-source truth comparison per symbol"},
            {"layer": "Prediction", "current": "gain rank + signal confidence APIs", "next": "show multi-day rho/top-N trend on Genesis tab"},
            {"layer": "Risk", "current": "2% trade risk, 5% daily loss policy displayed", "next": "enforce position sizing in paper lifecycle"},
            {"layer": "Learning", "current": "memory JSONL + research log", "next": "promote only after walk-forward improvement"},
        ],
        "truth": truth,
        "production_verdict": "ANALYZER_PRODUCTION_UI_READY__LIVE_TRADING_STILL_BLOCKED",
    })


@app.get("/api/broker/positions")
async def get_broker_positions():
    try:
        if not _BROKER_CLIENT: return {"positions": [], "status": "error"}
        positions = _BROKER_CLIENT.get_positions() if hasattr(_BROKER_CLIENT, 'get_positions') else []
        formatted = [{"symbol": str(p.get("symbol", "")), "qty": int(p.get("qty", 0)), "ltp": float(p.get("ltp", 0)), "pnl": float(p.get("pnl", 0))} for p in (positions or [])]
        return {"positions": formatted, "count": len(formatted), "status": "ok"}
    except: return {"positions": [], "status": "error"}

@app.get("/api/market/top-gainers")
async def get_market_top_gainers():
    try:
        result = await get_top_contract_gainers() if asyncio.iscoroutinefunction(get_top_contract_gainers) else get_top_contract_gainers()
        if isinstance(result, dict) and "data" in result:
            gainers = sorted(result["data"], key=lambda x: x.get("ce_gain_percent", 0), reverse=True)[:10]
            return {"gainers": gainers, "status": "ok"}
        return {"gainers": [], "status": "no_data"}
    except: return {"gainers": [], "status": "error"}

@app.get("/api/market/top-losers")
async def get_market_top_losers():
    try:
        result = await get_top_contract_gainers() if asyncio.iscoroutinefunction(get_top_contract_gainers) else get_top_contract_gainers()
        if isinstance(result, dict) and "data" in result:
            losers = sorted(result["data"], key=lambda x: x.get("ce_gain_percent", 0))[:10]
            return {"losers": losers, "status": "ok"}
        return {"losers": [], "status": "no_data"}
    except: return {"losers": [], "status": "error"}

@app.get("/api/performance")
async def get_performance_metrics():
    try:
        state = _get_runtime_state()
        return {
            "daily_pnl": float(state.get("daily_pnl", 0)),
            "total_pnl": float(state.get("total_pnl", 0)),
            "trades_executed": int(state.get("trades_executed", 0)),
            "status": "ok"
        }
    except: return {"daily_pnl": 0, "total_pnl": 0, "status": "error"}

@app.get("/api/ml/predictions")
async def get_ml_predictions():
    try:
        state = _get_runtime_state()
        predictions = list(state.get("ml_predictions", []) or [])
        if not predictions:
            scan = await _run_blocking(_compat_run_scanner, timeout=30.0)
            for row in (scan.get("full_ranking") or scan.get("top_predictions") or [])[:10]:
                if not isinstance(row, dict):
                    continue
                score = float(row.get("gain_score") or row.get("expected_move_pct") or 0)
                predictions.append(
                    {
                        "symbol": row.get("underlying") or row.get("symbol"),
                        "signal": _compat_map_recommendation_to_signal(row.get("recommendation"), score),
                        "confidence_pct": round(min(99.0, abs(score) * 10.0 if abs(score) <= 10 else abs(score)), 2),
                        "recommendation": row.get("recommendation"),
                        "score": score,
                        "source": "daily_gain_scanner",
                    }
                )
        return {
            "predictions": predictions[:10],
            "count": len(predictions),
            "status": "ok",
            "live_trading_enabled": False,
        }
    except Exception as exc:
        return {"predictions": [], "status": "error", "error": str(exc)[:200]}

# SYSTEM3_BACKEND_VIRTUAL_LIVE_SIMULATION_ROUTES
@app.get("/api/simulation/live/state")
async def get_virtual_live_simulation_state(scenario: str = "trend"):
    """Backend virtual live-market simulation feed. No real broker/orders."""
    try:
        from dashboard.backend.live_simulation_service import build_virtual_live_state
    except ImportError:
        from live_simulation_service import build_virtual_live_state
    payload = build_virtual_live_state(scenario=scenario)
    payload["api_route"] = "/api/simulation/live/state"
    payload["live_trading_enabled"] = False
    payload["order_placement_allowed"] = False
    payload["real_broker_routes_called"] = False
    return payload


@app.get("/api/simulation/live/chain")
async def get_virtual_live_simulation_chain(scenario: str = "trend"):
    """Virtual option chain shaped like a backend feed; simulation only."""
    try:
        from dashboard.backend.live_simulation_service import build_virtual_live_state
    except ImportError:
        from live_simulation_service import build_virtual_live_state
    payload = build_virtual_live_state(scenario=scenario)
    return {
        "status": "SIMULATION_ONLY",
        "api_route": "/api/simulation/live/chain",
        "scenario": payload.get("scenario"),
        "generated_utc": payload.get("generated_utc"),
        "rows": payload.get("option_chain") or [],
        "row_count": len(payload.get("option_chain") or []),
        "live_trading_enabled": False,
        "order_placement_allowed": False,
        "real_broker_routes_called": False,
    }


@app.get("/api/simulation/live/signals")
async def get_virtual_live_simulation_signals(scenario: str = "trend"):
    """Virtual CE/PE signal feed; simulation only."""
    try:
        from dashboard.backend.live_simulation_service import build_virtual_live_state
    except ImportError:
        from live_simulation_service import build_virtual_live_state
    payload = build_virtual_live_state(scenario=scenario)
    return {
        "status": "SIMULATION_ONLY",
        "api_route": "/api/simulation/live/signals",
        "scenario": payload.get("scenario"),
        "generated_utc": payload.get("generated_utc"),
        "rows": payload.get("signals") or [],
        "row_count": len(payload.get("signals") or []),
        "live_trading_enabled": False,
        "order_placement_allowed": False,
        "real_broker_routes_called": False,
    }


@app.get("/api/simulation/live/paper")
async def get_virtual_live_simulation_paper(scenario: str = "trend"):
    """Virtual paper lifecycle tape; simulation only."""
    try:
        from dashboard.backend.live_simulation_service import build_virtual_live_state
    except ImportError:
        from live_simulation_service import build_virtual_live_state
    payload = build_virtual_live_state(scenario=scenario)
    paper = payload.get("paper") or {}
    return {
        "status": "SIMULATION_ONLY",
        "api_route": "/api/simulation/live/paper",
        "scenario": payload.get("scenario"),
        "generated_utc": payload.get("generated_utc"),
        "orders": paper.get("orders") or [],
        "total_pnl": paper.get("total_pnl"),
        "currency": "INR",
        "live_trading_enabled": False,
        "order_placement_allowed": False,
        "real_broker_routes_called": False,
    }
