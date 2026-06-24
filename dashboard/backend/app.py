"""
System3 Ultra Dashboard Backend
FastAPI service for real-time system monitoring and control
"""

import asyncio
import hashlib
import json
import os
import re
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytz

IST = pytz.timezone("Asia/Kolkata")

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
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

try:
    import pandas as pd
except ImportError:
    pd = None
    print("Warning: pandas not available")
import sqlite3

import numpy as np

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

app = FastAPI(title="System3 Ultra Dashboard API")


# Rate limiting middleware to prevent excessive API calls
@app.middleware("http")
async def rate_limit_middleware(request, call_next):
    """Add small delay to throttle external API calls and prevent rate limiting"""
    import time

    # Small delay to prevent rapid-fire requests (especially during startup)
    # This helps avoid Angel One rate limits
    time.sleep(0.1)
    response = await call_next(request)
    return response


# Initialize SSOT (Single Source of Truth)
if SSOT_AVAILABLE:
    state_store = get_state_store(OUTPUTS_DIR)
    # Sync from existing files on startup
    state_store.sync_from_files()
else:
    state_store = None

# Warm instruments master — sync from Dhan CDN if stale, then load cache
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

# CORS - explicit allow-list only. Wildcard origins + credentials is an open
# CORS misconfiguration (any site can read authenticated responses).
# Override/extend via ALLOWED_ORIGINS env var (comma-separated).
_default_allowed_origins = [
    "https://genesis-system3-backend.onrender.com",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "null",  # Electron file:// pages send Origin: null
]
_env_allowed_origins = os.environ.get("ALLOWED_ORIGINS", "")
_allowed_origins = [o.strip() for o in _env_allowed_origins.split(",") if o.strip()] or _default_allowed_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


_DASHBOARD_DIR = ROOT_DIR / "dashboard"


# Root route - helpful message
@app.api_route("/", methods=["GET", "HEAD"])
async def root():
    base_url = os.environ.get("PUBLIC_BACKEND_URL", "https://genesis-system3-backend.onrender.com").rstrip("/")
    dashboard_url = os.environ.get("PUBLIC_DASHBOARD_URL", base_url).rstrip("/")
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
            "dashboard": "/ui",
        },
    }


@app.get("/ui", include_in_schema=False)
@app.get("/ui/", include_in_schema=False)
async def serve_dashboard_index():
    f = _DASHBOARD_DIR / "index.html"
    if f.exists():
        return FileResponse(str(f), media_type="text/html", headers=_NO_CACHE_HEADERS)
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

    state = state_store.get_state()
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
            except:
                continue
    except Exception as e:
        print(f"Error reading state history: {e}")

    return {"history": history, "count": len(history), "limit": limit}


@app.get("/api/broker/status")
async def get_broker_status():
    """Get broker connection status. Uses Dhan broker (read-only, analyzer mode)."""
    try:
        from core.brokers.dhan.dhan_readonly import get_status as _dhan_status
        status = await asyncio.wait_for(asyncio.to_thread(_dhan_status), timeout=5)
        if SSOT_AVAILABLE and state_store is not None:
            state_store.update_state({"broker": status})
        return status
    except Exception as _e:
        return {
            "connected": False,
            "name": "dhan",
            "status": "error",
            "error": str(_e)[:200],
            "error_type": "DHAN_STATUS_ERROR",
            "latency_ms": None,
            "last_ok": None,
        }


@app.get("/api/broker/dhan/status")
async def get_dhan_broker_status():
    """Dhan read-only broker status. Never returns access token. No live trading."""
    try:
        from core.brokers.dhan.dhan_readonly import get_status as dhan_get_status
        status = await asyncio.wait_for(asyncio.to_thread(dhan_get_status), timeout=5)
        if SSOT_AVAILABLE and state_store is not None:
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
        return {
            "broker": "dhan",
            "mode": "ANALYZER",
            "connected": False,
            "live_trading_enabled": False,
            "order_placement_allowed": False,
            "credentials_present": False,
            "error": str(exc)[:200],
        }


@app.get("/api/broker/truth")
async def get_broker_truth():
    """Multi-validated broker trader truth — holdings, positions, funds."""
    try:
        from dashboard.backend.broker_truth_validator import build_broker_truth_report
    except ImportError:
        from broker_truth_validator import build_broker_truth_report
    return build_broker_truth_report()


@app.get("/api/broker/holdings")
async def get_broker_holdings():
    """Dhan equity holdings — read-only. No orders."""
    try:
        from core.brokers.dhan.dhan_payload_normalizer import (
            normalize_holding_row,
            normalize_holdings_payload,
        )
        from core.brokers.dhan.dhan_readonly import get_holdings

        result = get_holdings()
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
    try:
        from core.brokers.dhan.dhan_payload_normalizer import (
            normalize_funds_payload,
            normalize_funds_row,
        )
        from core.brokers.dhan.dhan_readonly import get_funds

        result = get_funds()
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


@app.get("/api/broker/positions/live")
async def get_broker_positions_live():
    """Dhan open positions — read-only. No orders."""
    try:
        from core.brokers.dhan.dhan_payload_normalizer import (
            normalize_position_row,
            normalize_positions_payload,
        )
        from core.brokers.dhan.dhan_readonly import get_positions

        result = get_positions()
        raw_rows = normalize_positions_payload(result.get("data"))
        normalized = [normalize_position_row(r) for r in raw_rows]
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


@app.get("/api/portfolio/unified")
async def get_unified_portfolio():
    """Paper + broker read-only portfolio truth. Never enables live trading."""
    try:
        from dashboard.backend.portfolio_truth_service import build_unified_portfolio
    except ImportError:
        from portfolio_truth_service import build_unified_portfolio
    return build_unified_portfolio(OUTPUTS_DIR)


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
        except:
            pass

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
        except:
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
            except:
                pass

        # Check market status
        market_status = "unknown"
        data_source = "unknown"
        if MARKET_DETECTION_AVAILABLE:
            try:
                market_status = get_market_status()
                data_source = "synthetic" if not is_market_open() else "real"
            except:
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


@app.get("/api/gain_rank")
async def get_gain_rank(refresh: bool = False):
    """Latest gain rank predictions and 14-day history from gain_rank_history.json."""
    try:
        if not GAIN_RANK_FILE.exists():
            return {"status": "no_data", "latest": None, "history": [], "is_today": False, "stale": True}
        history = json.loads(GAIN_RANK_FILE.read_text())
        if not isinstance(history, list):
            history = []
        today = datetime.now(IST).strftime("%Y-%m-%d")
        today_entry = next((e for e in reversed(history) if e.get("date") == today), None)
        latest = today_entry or (history[-1] if history else None)
        stale = latest is None or latest.get("date") != today
        market_open = False
        if SSOT_AVAILABLE and state_store is not None:
            market_open = bool((state_store.get_state().get("market") or {}).get("is_open"))
        if (refresh or stale) and market_open:
            try:
                from scripts.daily_gain_rank_and_validate import run_ranking

                run_ranking(top_n=5)
                history = json.loads(GAIN_RANK_FILE.read_text())
                if not isinstance(history, list):
                    history = []
                today_entry = next((e for e in reversed(history) if e.get("date") == today), None)
                latest = today_entry or (history[-1] if history else None)
                stale = latest is None or latest.get("date") != today
            except Exception as rank_err:
                return {
                    "status": "ok",
                    "latest": latest,
                    "history": history[-14:],
                    "total_days": len(history),
                    "is_today": not stale,
                    "stale": stale,
                    "rank_refresh_error": str(rank_err)[:200],
                }
        return {
            "status": "ok",
            "latest": latest,
            "history": history[-14:],
            "total_days": len(history),
            "is_today": not stale,
            "stale": stale,
            "latest_date": (latest or {}).get("date"),
        }
    except Exception as e:
        return {"status": "error", "error": str(e), "latest": None, "history": [], "is_today": False, "stale": True}


@app.get("/api/scanner/top_contract_gainers")
async def get_top_contract_gainers(top_n: int = 5):
    """
    Live market scanner: highest % gain CE and PE per index segment.
    Segments: NIFTY, BANKNIFTY, FINNIFTY, MIDCPNIFTY.
    """
    try:
        from dashboard.backend.contract_gain_scanner import (
            build_top_contract_gainers_report,
        )

        report = build_top_contract_gainers_report(top_n=min(max(top_n, 1), 20))
        report["status"] = "ok" if report.get("segments_implemented", 0) > 0 else "no_data"
        return report
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)[:300],
            "segments": ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY"],
            "segments_implemented": 0,
            "by_segment": {},
        }


@app.get("/api/scanner/equity_options")
async def get_equity_options_scanner(top_n: int = 10, priority_only: bool = False):
    """Equity (stock) F&O universe + OPTSTK top CE/PE from bhavcopy."""
    try:
        from dashboard.backend.equity_option_scanner import build_equity_options_report

        return build_equity_options_report(top_n=min(max(top_n, 1), 50), priority_only=priority_only)
    except Exception as e:
        return {"status": "error", "error": str(e)[:300]}


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
    """Spearman rho trend from market_validations/*.json (last 14 days). Handles both field names."""
    try:
        if not VALIDATION_DIR.exists():
            return {"status": "no_data", "trend": [], "retrain_needed": RETRAIN_FLAG.exists()}
        files = sorted(VALIDATION_DIR.glob("market_validation_*.json"))[-14:]
        trend = []
        for f in files:
            try:
                d = json.loads(f.read_text())
                rho = d.get("rank_correlation_spearman") or d.get("spearman_correlation")
                trend.append(
                    {
                        "date": d.get("date", f.stem.replace("market_validation_", "")),
                        "rho": round(rho, 4) if rho is not None else None,
                        "hit_rate": d.get("hit_rate"),
                        "status": d.get("status", "UNKNOWN"),
                        "predicted": d.get("predicted_ranking", []),
                        "actual": d.get("actual_ranking", []),
                    }
                )
            except Exception:
                continue
        avg_rho = None
        rhos = [e["rho"] for e in trend if e["rho"] is not None]
        if rhos:
            avg_rho = round(sum(rhos) / len(rhos), 4)
        return {
            "status": "ok",
            "trend": trend,
            "avg_rho": avg_rho,
            "retrain_needed": RETRAIN_FLAG.exists(),
            "days_available": len(trend),
        }
    except Exception as e:
        return {"status": "error", "error": str(e), "trend": [], "retrain_needed": False}


@app.get("/api/auto_gates")
async def get_auto_gates(refresh: bool = False):
    """Runtime-driven production/prediction/profit blocker gates (replaces static dashboard proof matrix)."""
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

# File watcher for real-time updates
# Store the event loop for use in file watcher thread
_main_loop = None


def set_event_loop(loop):
    """Store the main event loop for file watcher"""
    global _main_loop
    _main_loop = loop


class OutputFileHandler(FileSystemEventHandler):
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
            except:
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


# API Endpoints
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

            # Check Dhan first — takes priority when DHAN credentials are present
            _dhan_cid = os.getenv("DHAN_CLIENT_ID", "").strip()
            _dhan_tok = os.getenv("DHAN_ACCESS_TOKEN", "").strip()
            if _dhan_cid and _dhan_tok:
                try:
                    from core.brokers.dhan.dhan_readonly import (
                        get_status as _dhan_get_status,
                    )

                    _dhan_result = _dhan_get_status()
                    if _dhan_result.get("connected"):
                        broker_connected = True
                        broker_status_str = "connected"
                        broker_name = "dhan"
                        mode = "PAPER"
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
                    "data_source": "live",
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
            return {
                "status": "ok",
                "mode": "PAPER",
                "broker_status": "connected",
                "market_status": market_status_str,
                "data_source": "live",
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
                "qc_status": "PASS",
                "qc_failures": [],
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
            data_source = ssot_state.get("data_source", "live")
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
            except:
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
                    "data_source": "live",
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


@app.get("/api/underlyings")
async def get_underlyings():
    """Return list of underlyings for dynamic chain/validator use."""
    return {"underlyings": DEFAULT_UNDERLYINGS}


@app.get("/api/chain/{underlying}")
async def get_chain(underlying: str):
    """Get option chain for specific underlying"""
    try:
        # Check market status first
        market_is_open = False
        if MARKET_DETECTION_AVAILABLE:
            try:
                market_is_open, reason = is_market_open()
            except:
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
                if chain_file.exists() and pd is not None:
                    try:
                        df = pd.read_csv(chain_file)
                        if "underlying" in df.columns and "spot_price" in df.columns:
                            filtered = df[df["underlying"].astype(str).str.upper() == underlying.upper()]
                            if not filtered.empty:
                                spot_vals = pd.to_numeric(filtered["spot_price"], errors="coerce").dropna()
                                if not spot_vals.empty:
                                    spot_price = float(spot_vals.iloc[0])
                    except:
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
                    "data_source": "live",
                    "status": "NOT_READY",
                    "message": "BROKER_NOT_READY - Real chain data unavailable",
                }

        # Market closed — prefer Dhan snapshot, never label MARKET_OPEN
        if not market_is_open:
            try:
                from core.data.datasource_manager import DataSourceManager
                from dashboard.backend.chain_adapter import fetch_chain_for_api

                _dsm = DataSourceManager()
                _closed = fetch_chain_for_api(_dsm, underlying.upper())
                if _closed and _closed.get("contracts"):
                    _closed["status"] = "MARKET_CLOSED"
                    _closed["message"] = "Market closed — last available chain snapshot"
                    return _closed
            except Exception:
                pass

        # ALWAYS try Dhan P0 first when market is open (or as fallback)
        # chain_raw_live.csv on Render is from repo clone — may be months old
        # DSM → dhan_option_chain_parser → live Greeks, OI change, bid/ask
        try:
            from core.data.datasource_manager import DataSourceManager
            from dashboard.backend.chain_adapter import fetch_chain_for_api

            _dsm = DataSourceManager()
            _live = fetch_chain_for_api(_dsm, underlying.upper())
            if _live and _live.get("contracts") and len(_live["contracts"]) >= 5:
                _live["status"] = "MARKET_OPEN" if market_is_open else "MARKET_CLOSED"
                _live["source_priority"] = "dhan_p0_live"
                return _live
            else:
                print(
                    f"[chain/{underlying}] DSM returned empty/small ({len((_live or {}).get('contracts', []))} contracts) — using CSV fallback"
                )
        except Exception as _dsm_err:
            print(f"[chain/{underlying}] DSM failed: {_dsm_err} — using CSV fallback")

        # CSV fallback (only reached if Dhan P0 fails)
        chain_file = OUTPUTS_DIR / "chain_raw_live.csv"
        if not chain_file.exists():
            # Try Dhan Data API directly
            try:
                from core.data.datasource_manager import DataSourceManager
                from dashboard.backend.chain_adapter import fetch_chain_for_api

                _dsm = DataSourceManager()
                _chain_result = fetch_chain_for_api(_dsm, underlying.upper())
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
                except:
                    pass

            # Calculate PCR
            pcr = 1.0
            if "oi" in filtered_rows[0] and "option_type" in filtered_rows[0]:
                try:
                    pe_oi = sum(float(row.get("oi", 0)) for row in filtered_rows if row.get("option_type") == "PE")
                    ce_oi = sum(float(row.get("oi", 0)) for row in filtered_rows if row.get("option_type") == "CE")
                    pcr = float(pe_oi / ce_oi) if ce_oi > 0 else 1.0
                except:
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
                        except:
                            contract[key] = value
                contracts.append(contract)

            return {
                "underlying": underlying,
                "spot": float(spot),
                "pcr": float(pcr),
                "contracts": contracts[:1000],
                "total_contracts": len(contracts),
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
            except:
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

        chain_status = "MARKET_OPEN" if market_is_open else "MARKET_CLOSED"
        return {
            "underlying": underlying,
            "spot": float(spot),
            "pcr": float(pcr),
            "contracts": contracts[:1000],
            "total_contracts": len(contracts),
            "data_source": "real",
            "status": chain_status,
            "message": "Cached chain CSV" if not market_is_open else "Live chain data",
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
            except:
                pass

        # REAL_ONLY MODE: Never use synthetic data
        if not market_is_open and not REAL_ONLY and SYNTHETIC_DATA_AVAILABLE:
            signal = generate_synthetic_signal_data()
            signal["data_source"] = "synthetic"
            return signal

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
                    "data_source": "live",
                    "confidence": 0,
                }

        # Market is open - use real data
        signal_file = OUTPUTS_DIR / "top_trade_signal.json"
        if not signal_file.exists():
            return {"action": "NO_TRADE", "reason": "Signal file not found", "data_source": "real"}

        data = json.loads(signal_file.read_text())
        data["data_source"] = "real"
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
            except:
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
            except:
                summary = {}
        # Also try pnl_live.json as authoritative source
        pnl_live = OUTPUTS_DIR / "pnl_live.json"
        if pnl_live.exists() and not summary.get("total_trades"):
            try:
                live = json.loads(pnl_live.read_text())
                if live.get("total_trades", 0) > 0:
                    summary = live
            except:
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
                except:
                    # If parsing fails, add current timestamp
                    processed_item["timestamp"] = datetime.now(IST).isoformat()
            else:
                # No timestamp - add current one
                processed_item["timestamp"] = datetime.now(IST).isoformat()
            processed_history.append(processed_item)

        if not processed_history:
            for session_file in [
                ROOT_DIR / "tests" / "fixtures" / "paper_closed_trades_feb2026.json",
                ROOT_DIR / "storage" / "paper" / "closed_trades_feb2026.json",
            ]:
                if not session_file.exists():
                    continue
                try:
                    session = json.loads(session_file.read_text(encoding="utf-8"))
                    processed_history = session.get("trades", [])
                    if summary and not summary.get("data_source"):
                        summary["data_source"] = session.get("data_source", "paper_simulation")
                    if processed_history:
                        break
                except Exception:
                    pass

        try:
            from core.brokers.dhan.nse_option_symbol import enrich_option_rows

            session_expiry = None
            if not processed_history:
                pass
            else:
                session_expiry = processed_history[0].get("expiry_date")
            processed_history = enrich_option_rows(processed_history, default_expiry=session_expiry)
        except Exception:
            pass

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
            except:
                pass

        # REAL_ONLY MODE: Never use synthetic data
        if not market_is_open and not REAL_ONLY and SYNTHETIC_DATA_AVAILABLE:
            synthetic_perf = generate_synthetic_perf_data()
            return {"status": "OK", "current": synthetic_perf, "history": [], "data_source": "synthetic"}

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
                    "data_source": "live",
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
        except:
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
    """Get paper trading data (combines positions and PnL)"""
    try:
        positions_data = await get_positions()
        pnl_data = await get_pnl()

        return {"positions": positions_data, "pnl": pnl_data}
    except Exception as e:
        return {"status": "ERROR", "reason": str(e), "positions": {}, "pnl": {}}


@app.post("/api/positions/{position_id}/close")
async def close_position(position_id: str):
    """Manually close a position (for trader control)"""
    try:
        positions_file = OUTPUTS_DIR / "positions_live.json"
        if not positions_file.exists():
            raise HTTPException(status_code=404, detail="Positions file not found")

        data = json.loads(positions_file.read_text())
        positions = data.get("positions", [])

        # Find position
        position = None
        for pos in positions:
            if str(pos.get("position_id", "")) == position_id:
                position = pos
                break

        if not position:
            raise HTTPException(status_code=404, detail=f"Position {position_id} not found")

        # Mark as closed (system will handle actual closing in next cycle)
        position["status"] = "CLOSED"
        position["exit_reason"] = "MANUAL_CLOSE"
        position["exit_price"] = position.get("current_price", position.get("entry_price", 0))

        # Save updated positions
        data["positions"] = [p for p in positions if p.get("status") != "CLOSED"]
        data["open_count"] = len(data["positions"])

        with open(positions_file, "w") as f:
            json.dump(data, f, indent=2, default=str)

        return {"status": "success", "message": f"Position {position_id} marked for closure"}
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
                                except:
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
    # Check if market is open before accepting connection
    if MARKET_DETECTION_AVAILABLE:
        is_open, reason = is_market_open()
        if not is_open:
            # Reject connection outside market hours
            await websocket.close(code=1008, reason=f"Market closed: {reason}")
            return

    await websocket.accept()
    active_connections.append(websocket)

    try:
        # Send initial data
        try:
            health_file = OUTPUTS_DIR / "health.json"
            if health_file.exists():
                health_data = json.loads(health_file.read_text())
                await websocket.send_json(
                    {
                        "type": "health_update",
                        "data": health_data,
                        "timestamp": datetime.now(pytz.timezone("Asia/Kolkata")).isoformat(),
                    }
                )
        except (WebSocketDisconnect, ConnectionError):
            # Client disconnected, exit gracefully
            raise
        except Exception:
            # Other errors, continue
            pass

        # Send periodic updates
        last_health_send = 0
        last_positions_send = 0
        last_pnl_send = 0
        last_heartbeat_send = 0

        while True:
            await asyncio.sleep(1)  # Check every second

            now = datetime.now(pytz.timezone("Asia/Kolkata")).timestamp()

            # Send health update every 3 seconds
            if now - last_health_send >= 3:
                try:
                    health_file = OUTPUTS_DIR / "health.json"
                    if health_file.exists():
                        health_data = json.loads(health_file.read_text())
                        await websocket.send_json(
                            {
                                "type": "health_update",
                                "data": health_data,
                                "timestamp": datetime.now(pytz.timezone("Asia/Kolkata")).isoformat(),
                            }
                        )
                    last_health_send = now
                except (WebSocketDisconnect, ConnectionError):
                    # Client disconnected, exit gracefully
                    raise
                except Exception:
                    # Other errors, continue
                    pass

            # Send positions update every 3 seconds
            if now - last_positions_send >= 3:
                try:
                    positions_file = OUTPUTS_DIR / "positions_live.json"
                    if positions_file.exists():
                        positions_data = json.loads(positions_file.read_text())
                        await websocket.send_json(
                            {
                                "type": "positions_update",
                                "data": positions_data,
                                "timestamp": datetime.now(pytz.timezone("Asia/Kolkata")).isoformat(),
                            }
                        )
                    last_positions_send = now
                except (WebSocketDisconnect, ConnectionError):
                    # Client disconnected, exit gracefully
                    raise
                except Exception:
                    # Other errors, continue
                    pass

            # Send PnL update every 5 seconds
            if now - last_pnl_send >= 5:
                try:
                    pnl_file = OUTPUTS_DIR / "paper_pnl_summary.json"
                    if pnl_file.exists():
                        pnl_data = json.loads(pnl_file.read_text())
                        await websocket.send_json(
                            {
                                "type": "pnl_update",
                                "data": pnl_data,
                                "timestamp": datetime.now(pytz.timezone("Asia/Kolkata")).isoformat(),
                            }
                        )
                    last_pnl_send = now
                except (WebSocketDisconnect, ConnectionError):
                    # Client disconnected, exit gracefully
                    raise
                except Exception:
                    # Other errors, continue
                    pass

            # Send heartbeat every 10 seconds (more reliable than modulo)
            if now - last_heartbeat_send >= 10:
                try:
                    await websocket.send_json(
                        {"type": "heartbeat", "timestamp": datetime.now(pytz.timezone("Asia/Kolkata")).isoformat()}
                    )
                    last_heartbeat_send = now
                except (WebSocketDisconnect, ConnectionError):
                    # Client disconnected, exit gracefully
                    raise
                except Exception:
                    # Other errors, continue
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

                # Fetch live chains for all index symbols
                chains = []
                for sym in ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]:
                    try:
                        ch = await get_chain(sym)
                        if ch and ch.get("contracts"):
                            chains.append(ch)
                    except Exception:
                        continue

                if chains:
                    engine.step(chains, max_open=3)
                    print(
                        f"[paper-loop] tick: {len(engine.open_positions)} open, {len(engine.closed_positions)} closed"
                    )

            await _asyncio.sleep(60)  # tick every 60s
        except Exception as e:
            print(f"[paper-loop] error (continuing): {e}")
            await _asyncio.sleep(60)


def _refresh_spot_prices_blocking() -> None:
    """Synchronous network + CSV I/O — only ever called via asyncio.to_thread
    from background_data_refresh, never inline in the async loop. This used
    to run directly inside an `async def` task on the single uvicorn event
    loop: up to 5 sequential HTTP calls (5s timeout each) plus pandas CSV
    read/write, all blocking the entire server (every request, every other
    background task) for up to ~25s out of every 30s cycle.
    """
    symbols = {
        "NIFTY": "^NSEI",
        "BANKNIFTY": "^NSEBANK",
        "FINNIFTY": "^NSEFINNIFTY",
        "MIDCPNIFTY": "^NSEMIDCP",
        "SENSEX": "^BSESN",
    }

    import requests

    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})

    for underlying, yahoo_symbol in symbols.items():
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{yahoo_symbol}"
            response = session.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if "chart" in data and "result" in data["chart"]:
                    result = data["chart"]["result"][0]
                    meta = result.get("meta", {})
                    ltp = meta.get("regularMarketPrice")
                    if ltp and pd is not None:
                        # Update chain CSV
                        chain_file = OUTPUTS_DIR / "chain_raw_live.csv"
                        if chain_file.exists():
                            try:
                                df = pd.read_csv(chain_file)
                                if "underlying" in df.columns and "spot_price" in df.columns:
                                    mask = df["underlying"].astype(str).str.upper() == underlying.upper()
                                    if mask.any():
                                        df.loc[mask, "spot_price"] = ltp
                                        df.to_csv(chain_file, index=False)
                            except Exception:
                                pass
        except Exception:
            pass


async def background_data_refresh():
    """Background task to refresh spot prices every 30 seconds"""
    while True:
        try:
            await asyncio.wait_for(asyncio.to_thread(_refresh_spot_prices_blocking), timeout=25)
        except asyncio.TimeoutError:
            print("[background_data_refresh] spot-price refresh exceeded 25s timeout (continuing)")
        except Exception as e:
            print(f"[background_data_refresh] error (continuing): {e}")
        await asyncio.sleep(30)  # Refresh every 30 seconds


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


@app.on_event("startup")
async def startup():
    """Store event loop on startup and start background tasks"""
    set_event_loop(asyncio.get_running_loop())

    # Attempt token refresh at startup using PIN+TOTP (non-fatal — cloud mode).
    # Fired as a background task (never awaited here) so a slow/hung Dhan
    # auth call cannot delay or block the server from accepting requests.
    _pin = os.environ.get("DHAN_PIN", "").strip()
    _totp = os.environ.get("DHAN_TOTP_SECRET", "").strip()
    if _pin and _totp:
        asyncio.create_task(_startup_token_refresh_task())
    else:
        if not os.environ.get("DHAN_ACCESS_TOKEN"):
            print("[startup] DHAN_PIN/DHAN_TOTP_SECRET not set — token refresh skipped")

    # Start background data refresh
    asyncio.create_task(background_data_refresh())

    # Start cloud paper trading loop (PAPER ONLY — generates live paper trades)
    asyncio.create_task(cloud_paper_trading_loop())

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
                except:
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
                except:
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
            except:
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
    """Get recent alerts"""
    try:
        if not ALERTS_AVAILABLE:
            return {"status": "ERROR", "message": "Alerts system not available", "alerts": []}

        alerts_system = get_alerts_system()
        alerts = alerts_system.get_recent_alerts(limit)

        return {"status": "ok", "alerts": alerts, "count": len(alerts)}
    except Exception as e:
        return {"status": "ERROR", "message": str(e), "alerts": []}


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
    """Get portfolio risk metrics"""
    try:
        if not ADVANCED_FEATURES_AVAILABLE:
            return {"status": "ERROR", "message": "Risk management not available"}

        positions_data = await get_positions()
        positions = positions_data.get("positions", [])

        risk_mgmt = get_risk_management()
        risk_metrics = risk_mgmt.calculate_portfolio_risk(positions)

        return {"status": "ok", "risk_metrics": risk_metrics}
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
async def filter_option_chain_endpoint(underlying: str, filters: Dict[str, Any]):
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
async def filter_positions_endpoint(filters: Dict[str, Any]):
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
                        "price": base_price + np.random.normal(0, 100),
                        "ltp": base_price + np.random.normal(0, 100),
                    }
                )

        backtest_engine = get_backtesting_engine()
        result = backtest_engine.run_backtest(strategy_config, historical_data)

        return {"status": "ok", "backtest": result}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}


@app.get("/api/ml/performance")
async def get_ml_performance(model_name: Optional[str] = None):
    """Get ML model performance"""
    try:
        if not ADVANCED_FEATURES_AVAILABLE:
            return {"status": "ok", "performance": {"models": {}, "message": "ML tracking not available"}}

        try:
            ml_tracker = get_ml_tracker()
            performance = ml_tracker.get_model_performance(model_name)

            return {"status": "ok", "performance": performance if performance else {"models": {}}}
        except Exception as tracker_error:
            # Fallback if ML tracker fails
            return {
                "status": "ok",
                "performance": {"models": {}, "message": f"ML tracker error: {str(tracker_error)[:200]}"},
            }
    except Exception as e:
        return {"status": "ok", "performance": {"models": {}, "message": f"Error: {str(e)[:200]}"}}


@app.get("/api/ml/compare")
async def compare_ml_models():
    """Compare ML models"""
    try:
        if not ADVANCED_FEATURES_AVAILABLE:
            return {"status": "ok", "comparison": {"models": {}, "message": "ML tracking not available"}}

        try:
            ml_tracker = get_ml_tracker()
            comparison = ml_tracker.compare_models()

            return {"status": "ok", "comparison": comparison if comparison else {"models": {}}}
        except Exception as tracker_error:
            # Fallback if ML tracker fails
            return {
                "status": "ok",
                "comparison": {"models": {}, "message": f"ML tracker error: {str(tracker_error)[:200]}"},
            }
    except Exception as e:
        return {"status": "ok", "comparison": {"models": {}, "message": f"Error: {str(e)[:200]}"}}


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
    """Create a new order"""
    try:
        if not ADVANCED_FEATURES_AVAILABLE:
            return {"status": "ERROR", "message": "Order management not available"}

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
    """Get detected issues - returns immediately with empty array"""
    try:
        if not UPGRADE_AGENT_AVAILABLE:
            return {"status": "ok", "message": "Upgrade agent not available", "issues": []}

        # Return immediately - issue detection is handled by other systems
        # This endpoint is kept for API compatibility but returns instantly
        return {"status": "ok", "issues": []}
    except Exception as e:
        # Return empty array on any error to prevent blocking
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
            except:
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
        except:
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
        except:
            pass

        return {"success": result.returncode == 0, "output": result.stdout[-500:] if result.stdout else ""}
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=500, detail="Runner stop timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/runner/status")
async def runner_status():
    """Get runner status via runner.py CLI"""
    try:
        import subprocess
        import time

        runner_script = ROOT_DIR / "runner.py"
        if not runner_script.exists():
            return {"runner": "ERROR", "error": "runner.py not found"}

        result = subprocess.run(
            [sys.executable, str(runner_script), "status"],
            capture_output=True,
            text=True,
            timeout=10,
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
                status_data = json.loads(json_output)
                return status_data
        except Exception as parse_err:
            # If parsing fails, try heartbeat fallback
            pass

        # Fallback: try to read heartbeat directly
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
                pass

        return {"runner": "STOPPED", "error": "Could not parse status"}
    except Exception as e:
        return {"runner": "ERROR", "error": str(e)}


# Alias routes for convenience (point to /api/* endpoints)
# These prevent confusion when scripts/docs use /health or /state
@app.get("/health")
async def health_alias():
    """Alias for /api/health - returns same data"""
    return await get_health()


@app.get("/state")
async def state_alias():
    """Alias for /api/state - returns same data"""
    return await get_state()


@app.get("/healthz")
async def healthz_alias():
    """Alias for /api/health (kubernetes-style) - returns same data"""
    return await get_health()


@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    if observer:
        try:
            observer.stop()
            observer.join(timeout=2)
        except:
            pass


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
