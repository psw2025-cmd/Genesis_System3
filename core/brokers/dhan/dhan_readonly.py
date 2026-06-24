"""
DhanHQ Read-Only / Analyzer-Only Broker Adapter
================================================
SAFETY CONTRACT:
- No order placement, modification, or cancellation.
- No live trading of any kind.
- Access token only — never printed or logged.
- Profile endpoint used for connectivity check.
"""

import logging
import os
import sys
import time

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Load env (picks up .secrets/dhan.env via env_loader's path list)
try:
    from core.utils.env_loader import get_dhan_credentials
    _ENV_LOADED_VIA = "core.utils.env_loader"
except ImportError:
    # Fallback: load .secrets/dhan.env directly
    from dotenv import load_dotenv
    _secrets_path = os.path.join(ROOT_DIR, ".secrets", "dhan.env")
    _sys3_env = os.getenv("SYSTEM3_ENV_FILE", "")
    for _p in [_sys3_env, _secrets_path]:
        if _p and os.path.exists(_p):
            load_dotenv(_p, override=False)
            break

    def get_dhan_credentials():
        return {
            "client_id": os.getenv("DHAN_CLIENT_ID", "").strip(),
            "access_token": os.getenv("DHAN_ACCESS_TOKEN", "").strip(),
        }
    _ENV_LOADED_VIA = "dotenv-fallback"

try:
    import requests as _requests
    _REQUESTS_OK = True
except ImportError:
    _requests = None
    _REQUESTS_OK = False

_DHAN_SDK_OK = False
_dhanhq_class = None
_DhanContext = None
try:
    import dhanhq as _pkg
    from dhanhq import dhanhq as _dhanhq_class
    from dhanhq.dhan_context import DhanContext as _DhanContext
    _DHAN_SDK_OK = True
except Exception:
    pass

_LIVE_TRADING_BLOCKED_MSG = (
    "LIVE_TRADING_BLOCKED: Dhan adapter is read-only/analyzer-only. "
    "Order placement is permanently disabled."
)

_DHAN_PROFILE_URL = "https://api.dhan.co/v2/profile"
_DHAN_FUNDS_URL = "https://api.dhan.co/v2/fundlimit"
_DHAN_POSITIONS_URL = "https://api.dhan.co/v2/positions"
_DHAN_HOLDINGS_URL = "https://api.dhan.co/v2/holdings"
_DHAN_ORDERS_URL = "https://api.dhan.co/v2/orders"

# Broker status endpoint is polled every 10s by the dashboard.  Auto-refresh
# must therefore be rate-limited so an expired/missing token does not trigger
# repeated login attempts or TOTP churn on every UI poll.
_STATUS_REFRESH_COOLDOWN_S = int(os.getenv("DHAN_STATUS_REFRESH_COOLDOWN_S", "300") or "300")
_LAST_STATUS_REFRESH_ATTEMPT_AT = 0.0

logger = logging.getLogger("dhan_readonly")


def _mask(value: str, keep: int = 4) -> str:
    """Mask a string, showing only the last `keep` chars."""
    if not value:
        return "<empty>"
    return f"{'*' * max(0, len(value) - keep)}{value[-keep:]}"


def _env_truthy(name: str, default: str = "0") -> bool:
    return os.getenv(name, default).strip().lower() in ("1", "true", "yes", "on")


def _env_falsey(name: str, default: str = "0") -> bool:
    return os.getenv(name, default).strip().lower() in ("0", "false", "no", "off", "")


def _status_auto_refresh_enabled() -> bool:
    """
    Safe default: enabled only for read-only broker status checks.
    Disable with DHAN_STATUS_AUTO_REFRESH=0 if needed.
    """
    if not _env_truthy("DHAN_STATUS_AUTO_REFRESH", "1"):
        return False

    # Never allow this read-only adapter to be used as a live-trading bypass.
    # The refresh is only for profile/fund/position reads in ANALYZER/PAPER mode.
    if not _env_falsey("LIVE_TRADING_ENABLED", "0"):
        return False
    if not _env_falsey("SYSTEM3_LIVE_TRADING_ALLOWED", "0"):
        return False

    return True


def _safe_refresh_token_for_status(reason: str) -> dict:
    """
    Refresh Dhan token from the web backend process when dashboard broker status
    detects an expired/missing token.  Returns only safe metadata; never returns
    or logs the raw access token.
    """
    global _LAST_STATUS_REFRESH_ATTEMPT_AT

    meta = {
        "attempted": False,
        "success": False,
        "reason": reason,
        "cooldown_s": _STATUS_REFRESH_COOLDOWN_S,
    }

    if not _status_auto_refresh_enabled():
        meta["skipped"] = "AUTO_REFRESH_DISABLED_OR_LIVE_GATE"
        return meta

    now = time.time()
    elapsed = now - _LAST_STATUS_REFRESH_ATTEMPT_AT
    if _LAST_STATUS_REFRESH_ATTEMPT_AT and elapsed < _STATUS_REFRESH_COOLDOWN_S:
        meta["skipped"] = "COOLDOWN"
        meta["cooldown_remaining_s"] = int(_STATUS_REFRESH_COOLDOWN_S - elapsed)
        return meta

    _LAST_STATUS_REFRESH_ATTEMPT_AT = now
    meta["attempted"] = True

    try:
        from core.brokers.dhan.token_manager import refresh_token

        # Expired/missing dashboard token needs a fresh generate attempt first.
        # renew_token can fail once the token is already fully expired.
        force_generate = reason in ("CONFIG_MISSING", "TOKEN_EXPIRED_OR_INVALID")
        result = refresh_token(force_generate=force_generate)
        meta["success"] = bool(result.get("success"))
        meta["strategy"] = result.get("strategy")
        meta["message"] = str(result.get("message", ""))[:160]
        meta["token_value_printed"] = False
        return meta
    except Exception as exc:
        meta["error_type"] = type(exc).__name__
        meta["message"] = str(exc)[:160]
        meta["token_value_printed"] = False
        return meta


def get_dhan_credentials_masked() -> dict:
    """Return credential presence info — never the actual values."""
    creds = get_dhan_credentials()
    cid = creds.get("client_id", "")
    tok = creds.get("access_token", "")
    return {
        "client_id_present": bool(cid),
        "client_id_length": len(cid),
        "client_id_masked": _mask(cid, 3) if cid else "<missing>",
        "access_token_present": bool(tok),
        "access_token_length": len(tok),
        "access_token_masked": _mask(tok, 6) if tok else "<missing>",
        "token_value_printed": False,
    }


def create_dhan_client():
    """
    Create and return a dhanhq SDK client instance.
    Uses DhanContext(client_id, access_token) → dhanhq(ctx) pattern.
    Returns None if credentials are missing or SDK unavailable.
    Raises RuntimeError if SDK is installed but credentials are missing.
    """
    creds = get_dhan_credentials()
    client_id = creds.get("client_id", "")
    access_token = creds.get("access_token", "")

    if not client_id or not access_token:
        return None

    if not _DHAN_SDK_OK or _DhanContext is None or _dhanhq_class is None:
        return None

    try:
        ctx = _DhanContext(client_id, access_token)
        client = _dhanhq_class(ctx)
        return client
    except Exception as exc:
        logger.warning("DhanHQ SDK client creation failed: %s", type(exc).__name__)
        return None


def _rest_get(url: str, access_token: str, client_id: str, timeout: int = 10) -> dict:
    """Raw REST GET to Dhan API — returns parsed JSON or raises."""
    if not _REQUESTS_OK or _requests is None:
        raise RuntimeError("requests library not available")
    headers = {
        "access-token": access_token,
        "client-id": client_id,
        "Content-Type": "application/json",
    }
    resp = _requests.get(url, headers=headers, timeout=timeout)
    resp.raise_for_status()
    return resp.json()


def get_profile() -> dict:
    """
    Fetch profile from Dhan API.
    Tries SDK first; falls back to REST.
    Returns a safe dict — never includes raw token.
    """
    creds = get_dhan_credentials()
    client_id = creds.get("client_id", "")
    access_token = creds.get("access_token", "")

    if not client_id or not access_token:
        return {"success": False, "error": "CONFIG_MISSING", "data": None}

    # Try SDK first
    client = create_dhan_client()
    if client is not None:
        try:
            result = client.get_profile() if hasattr(client, "get_profile") else None
            if result is not None:
                return {"success": True, "source": "sdk", "data": _safe_profile(result)}
        except Exception as exc:
            logger.debug("SDK profile fetch failed (%s), trying REST", type(exc).__name__)

    # REST fallback
    try:
        data = _rest_get(_DHAN_PROFILE_URL, access_token, client_id)
        return {"success": True, "source": "rest", "data": _safe_profile(data)}
    except Exception as exc:
        err = str(exc)
        if "401" in err or "Unauthorized" in err.lower():
            return {"success": False, "error": "TOKEN_EXPIRED_OR_INVALID", "data": None}
        if "403" in err or "Forbidden" in err.lower():
            return {"success": False, "error": "ACCESS_FORBIDDEN", "data": None}
        return {"success": False, "error": f"NETWORK_ERROR: {type(exc).__name__}", "data": None}


def _safe_profile(raw: dict) -> dict:
    """Return only non-sensitive profile fields."""
    if not isinstance(raw, dict):
        return {}
    safe_keys = {
        "dhanClientId", "clientName", "email", "segment",
        "exchangeSegment", "status", "message", "httpStatus",
    }
    return {k: v for k, v in raw.items() if k in safe_keys}


def get_funds() -> dict:
    """Fetch fund limits (read-only)."""
    creds = get_dhan_credentials()
    client_id = creds.get("client_id", "")
    access_token = creds.get("access_token", "")
    if not client_id or not access_token:
        return {"success": False, "error": "CONFIG_MISSING", "data": None}

    client = create_dhan_client()
    if client is not None and hasattr(client, "get_fund_limits"):
        try:
            return {"success": True, "source": "sdk", "data": client.get_fund_limits()}
        except Exception:
            pass

    try:
        data = _rest_get(_DHAN_FUNDS_URL, access_token, client_id)
        return {"success": True, "source": "rest", "data": data}
    except Exception as exc:
        return {"success": False, "error": str(exc)[:200], "data": None}


def get_positions() -> dict:
    """Fetch open positions (read-only)."""
    creds = get_dhan_credentials()
    client_id = creds.get("client_id", "")
    access_token = creds.get("access_token", "")
    if not client_id or not access_token:
        return {"success": False, "error": "CONFIG_MISSING", "data": None}

    client = create_dhan_client()
    if client is not None and hasattr(client, "get_positions"):
        try:
            return {"success": True, "source": "sdk", "data": client.get_positions()}
        except Exception:
            pass

    try:
        data = _rest_get(_DHAN_POSITIONS_URL, access_token, client_id)
        return {"success": True, "source": "rest", "data": data}
    except Exception as exc:
        return {"success": False, "error": str(exc)[:200], "data": None}


def get_holdings() -> dict:
    """Fetch equity holdings (read-only)."""
    creds = get_dhan_credentials()
    client_id = creds.get("client_id", "")
    access_token = creds.get("access_token", "")
    if not client_id or not access_token:
        return {"success": False, "error": "CONFIG_MISSING", "data": None}

    client = create_dhan_client()
    if client is not None and hasattr(client, "get_holdings"):
        try:
            return {"success": True, "source": "sdk", "data": client.get_holdings()}
        except Exception:
            pass

    try:
        data = _rest_get(_DHAN_HOLDINGS_URL, access_token, client_id)
        return {"success": True, "source": "rest", "data": data}
    except Exception as exc:
        return {"success": False, "error": str(exc)[:200], "data": None}


def get_orders_readonly() -> dict:
    """Fetch order book (read-only — no placement)."""
    creds = get_dhan_credentials()
    client_id = creds.get("client_id", "")
    access_token = creds.get("access_token", "")
    if not client_id or not access_token:
        return {"success": False, "error": "CONFIG_MISSING", "data": None}

    client = create_dhan_client()
    if client is not None and hasattr(client, "get_order_list"):
        try:
            return {"success": True, "source": "sdk", "data": client.get_order_list()}
        except Exception:
            pass

    try:
        data = _rest_get(_DHAN_ORDERS_URL, access_token, client_id)
        return {"success": True, "source": "rest", "data": data}
    except Exception as exc:
        return {"success": False, "error": str(exc)[:200], "data": None}


def get_status() -> dict:
    """
    Full broker status check. Safe for API responses.
    Never includes raw access token.
    """
    refresh_meta = {"attempted": False, "success": False}
    masked = get_dhan_credentials_masked()

    if not masked["client_id_present"]:
        return {
            "broker": "dhan",
            "mode": "ANALYZER",
            "connected": False,
            "live_trading_enabled": False,
            "order_placement_allowed": False,
            "credentials_present": False,
            "client_id_present": False,
            "access_token_present": masked["access_token_present"],
            "error": "CONFIG_MISSING",
            "auto_refresh": refresh_meta,
            "sdk_available": _DHAN_SDK_OK,
            "env_source": _ENV_LOADED_VIA,
        }

    if not masked["access_token_present"]:
        refresh_meta = _safe_refresh_token_for_status("CONFIG_MISSING")
        masked = get_dhan_credentials_masked()
        if not masked["access_token_present"]:
            return {
                "broker": "dhan",
                "mode": "ANALYZER",
                "connected": False,
                "live_trading_enabled": False,
                "order_placement_allowed": False,
                "credentials_present": False,
                "client_id_present": True,
                "access_token_present": False,
                "error": "CONFIG_MISSING",
                "auto_refresh": refresh_meta,
                "sdk_available": _DHAN_SDK_OK,
                "env_source": _ENV_LOADED_VIA,
            }

    t0 = time.time()
    profile_result = get_profile()
    latency_ms = int((time.time() - t0) * 1000)

    connected = profile_result.get("success", False)
    error = None if connected else profile_result.get("error", "UNKNOWN")

    if not connected and error == "TOKEN_EXPIRED_OR_INVALID":
        refresh_meta = _safe_refresh_token_for_status(error)
        if refresh_meta.get("success"):
            t0 = time.time()
            profile_result = get_profile()
            latency_ms = int((time.time() - t0) * 1000)
            connected = profile_result.get("success", False)
            error = None if connected else profile_result.get("error", "UNKNOWN")

    return {
        "broker": "dhan",
        "mode": "ANALYZER",
        "connected": connected,
        "live_trading_enabled": False,
        "order_placement_allowed": False,
        "credentials_present": bool(masked["client_id_present"] and masked["access_token_present"]),
        "client_id_present": masked["client_id_present"],
        "access_token_present": masked["access_token_present"],
        "latency_ms": latency_ms,
        "error": error,
        "auto_refresh": refresh_meta,
        "sdk_available": _DHAN_SDK_OK,
        "env_source": _ENV_LOADED_VIA,
    }


# ── BLOCKED ORDER METHODS ──────────────────────────────────────────────────────

class DhanReadOnly:
    """
    Safe wrapper around DhanHQ for use as an analyzer-only broker object.
    All read methods delegate to module-level functions.
    All write methods raise RuntimeError.
    """

    def get_profile(self) -> dict:
        return get_profile()

    def get_funds(self) -> dict:
        return get_funds()

    def get_positions(self) -> dict:
        return get_positions()

    def get_holdings(self) -> dict:
        return get_holdings()

    def get_orders_readonly(self) -> dict:
        return get_orders_readonly()

    def get_status(self) -> dict:
        return get_status()

    def get_dhan_credentials_masked(self) -> dict:
        return get_dhan_credentials_masked()

    # ── BLOCKED ──────────────────────────────────────────────────────────────

    def place_order(self, *args, **kwargs):
        raise RuntimeError(_LIVE_TRADING_BLOCKED_MSG)

    def modify_order(self, *args, **kwargs):
        raise RuntimeError(_LIVE_TRADING_BLOCKED_MSG)

    def cancel_order(self, *args, **kwargs):
        raise RuntimeError(_LIVE_TRADING_BLOCKED_MSG)

    def place_super_order(self, *args, **kwargs):
        raise RuntimeError(_LIVE_TRADING_BLOCKED_MSG)

    def modify_super_order(self, *args, **kwargs):
        raise RuntimeError(_LIVE_TRADING_BLOCKED_MSG)

    def cancel_super_order(self, *args, **kwargs):
        raise RuntimeError(_LIVE_TRADING_BLOCKED_MSG)

    def place_forever(self, *args, **kwargs):
        raise RuntimeError(_LIVE_TRADING_BLOCKED_MSG)

    def modify_forever(self, *args, **kwargs):
        raise RuntimeError(_LIVE_TRADING_BLOCKED_MSG)

    def cancel_forever(self, *args, **kwargs):
        raise RuntimeError(_LIVE_TRADING_BLOCKED_MSG)

    def place_slice_order(self, *args, **kwargs):
        raise RuntimeError(_LIVE_TRADING_BLOCKED_MSG)

    def kill_switch(self, *args, **kwargs):
        raise RuntimeError(_LIVE_TRADING_BLOCKED_MSG)
