"""
System3 Ultra Dashboard Backend
FastAPI service for real-time system monitoring and control
"""

import os
import sys
import json
import asyncio
import hashlib
import re
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import pytz

IST = pytz.timezone("Asia/Kolkata")

# CRITICAL: Add project root to Python path FIRST, before any core module imports
# This allows the backend to import core.brokers.angel_one.broker and other core modules
ROOT_DIR = Path(__file__).parent.parent.parent.resolve()  # Use resolve() to get absolute path
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
# Also add src for utils
if str(ROOT_DIR / "src") not in sys.path:
    sys.path.insert(0, str(ROOT_DIR / "src"))

# Try to import broker module at module level (with error handling)
# This ensures the import path is correct and module is available
BROKER_AVAILABLE = False
AngelOneBroker = None
try:
    from core.brokers.angel_one.broker import AngelOneBroker

    BROKER_AVAILABLE = True
    print(f"[Backend] Broker module imported successfully from {ROOT_DIR}")
except ImportError as e:
    print(f"[Backend] Warning: Could not import broker module: {e}")
    print(f"[Backend] ROOT_DIR: {ROOT_DIR}")
    print(f"[Backend] sys.path[0:3]: {sys.path[0:3]}")
except Exception as e:
    print(f"[Backend] Warning: Error importing broker module: {e}")

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
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
    from utils.market_hours import is_market_open, get_market_status

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
        generate_synthetic_qc_data,
        generate_synthetic_signal_data,
        generate_synthetic_perf_data,
    )

    SYNTHETIC_DATA_AVAILABLE = True
except ImportError:
    try:
        # Try relative import
        from synthetic_data_generator import (
            generate_synthetic_chain_data,
            generate_synthetic_health_data,
            generate_synthetic_qc_data,
            generate_synthetic_signal_data,
            generate_synthetic_perf_data,
        )

        SYNTHETIC_DATA_AVAILABLE = True
    except ImportError:
        SYNTHETIC_DATA_AVAILABLE = False
        print("Warning: Synthetic data generator not available")

# Import performance predictor and live validator
try:
    from dashboard.backend.performance_predictor import get_performance_predictor
    from dashboard.backend.live_profit_validator import get_live_validator

    PERFORMANCE_PREDICTOR_AVAILABLE = True
except ImportError:
    try:
        from performance_predictor import get_performance_predictor
        from live_profit_validator import get_live_validator

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
    from dashboard.backend.risk_management import get_risk_management
    from dashboard.backend.backtesting import get_backtesting_engine
    from dashboard.backend.ml_performance_tracking import get_ml_tracker
    from dashboard.backend.trade_journal import get_trade_journal
    from dashboard.backend.export_reporting import get_export_reporting
    from dashboard.backend.order_management import get_order_management

    ADVANCED_FEATURES_AVAILABLE = True
except ImportError:
    try:
        from advanced_charting import get_advanced_charting
        from advanced_filtering import get_advanced_filtering
        from risk_management import get_risk_management
        from backtesting import get_backtesting_engine
        from ml_performance_tracking import get_ml_tracker
        from trade_journal import get_trade_journal
        from export_reporting import get_export_reporting
        from order_management import get_order_management

        ADVANCED_FEATURES_AVAILABLE = True
    except ImportError:
        ADVANCED_FEATURES_AVAILABLE = False
        print("Warning: Advanced features not available")

# Try to import watchdog (optional)
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler

    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    Observer = None
    FileSystemEventHandler = None
    print("Warning: watchdog not available - file watching disabled")

ROOT_DIR = Path(__file__).parent.parent.parent
OUTPUTS_DIR = ROOT_DIR / "outputs"
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

# CORS - allow localhost and local network IPs
# For development: allow all origins (change to specific list in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root route - helpful message
@app.get("/")
async def root():
    public_base_url = os.environ.get("PUBLIC_BASE_URL", "http://localhost:8000").rstrip("/")
    dashboard_url = os.environ.get("PUBLIC_DASHBOARD_URL", "http://localhost:3000").rstrip("/")
    return {
        "message": "System3 Ultra Dashboard API",
        "status": "running",
        "dashboard_url": dashboard_url,
        "api_docs": f"{public_base_url}/docs",
        "health": f"{public_base_url}/api/health",
        "state": f"{public_base_url}/api/state",
    }


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
    if state_store:
        state = state_store.get_state()
        return state
    else:
        raise HTTPException(status_code=503, detail="State store not available")


# Get state history
@app.get("/api/state/history")
async def get_state_history(limit: int = 100):
    """Get SSOT state history (time series). Useful for tracking state changes over time."""
    if state_store:
        return state_store.get_history(limit=limit)
    return []
