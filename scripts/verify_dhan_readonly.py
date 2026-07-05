#!/usr/bin/env python3
"""
Dhan Read-Only Broker Verification Script
==========================================
Safe to run in GitHub Codespace.
Prints credential presence info only — never prints token values.
Exits 0 only if not configured (CONFIG_MISSING) OR fully verified.
Exits 1 if token present but profile verification fails.
"""

import os
import sys
import time
import traceback

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

print(f"ROOT: {ROOT}")

# ── Determine env file ────────────────────────────────────────────────────────
_candidates = [
    os.getenv("SYSTEM3_ENV_FILE", ""),
    os.path.join(ROOT, ".secrets", "dhan.env"),
    os.path.join(ROOT, "config", ".env"),
    "/etc/secrets/.env",
]
ENV_FILE_USED = "<none>"
for _p in _candidates:
    if _p and os.path.exists(_p):
        ENV_FILE_USED = _p
        break
print(f"ENV_FILE_USED: {ENV_FILE_USED}")

# ── Load env ──────────────────────────────────────────────────────────────────
try:
    from dotenv import load_dotenv

    if ENV_FILE_USED != "<none>":
        load_dotenv(ENV_FILE_USED, override=False)
except ImportError:
    print("WARNING: python-dotenv not installed; relying on shell env only")

# ── Credential presence check ─────────────────────────────────────────────────
DHAN_CLIENT_ID = os.getenv("DHAN_CLIENT_ID", "").strip()
DHAN_ACCESS_TOKEN = os.getenv("DHAN_ACCESS_TOKEN", "").strip()

print(f"DHAN_CLIENT_ID_PRESENT: {'YES' if DHAN_CLIENT_ID else 'NO'}")
print(f"DHAN_CLIENT_ID_LENGTH: {len(DHAN_CLIENT_ID)}")
print(f"DHAN_ACCESS_TOKEN_PRESENT: {'YES' if DHAN_ACCESS_TOKEN else 'NO'}")
print(f"DHAN_ACCESS_TOKEN_LENGTH: {len(DHAN_ACCESS_TOKEN)}")
print("TOKEN_VALUE_PRINTED: NO")

if not DHAN_CLIENT_ID or not DHAN_ACCESS_TOKEN:
    print("DHAN_STATUS: CONFIG_MISSING")
    print("LIVE_TRADING_ENABLED: false")
    print("ORDER_PLACEMENT_TESTED: NO")
    print(
        "\nACTION_REQUIRED: Run the hidden-input terminal command from the "
        "integration guide to write .secrets/dhan.env"
    )
    sys.exit(0)

# ── dhanhq import check ───────────────────────────────────────────────────────
try:
    import inspect

    import dhanhq as _pkg
    from dhanhq import dhanhq as _dhanhq_class
    from dhanhq.dhan_context import DhanContext as _DhanContext

    _sdk_sig = str(inspect.signature(_dhanhq_class))
    print(f"DHANHQ_IMPORT: PASS")
    print(f"DHAN_SDK_SIGNATURE: {_sdk_sig}")
    DHAN_SDK_OK = True
except ImportError as exc:
    print(f"DHANHQ_IMPORT: FAIL ({exc})")
    print("DHAN_SDK_SIGNATURE: N/A")
    DHAN_SDK_OK = False
    _DhanContext = None
    _dhanhq_class = None

# ── Import adapter ────────────────────────────────────────────────────────────
ADAPTER_OK = False
try:
    from core.brokers.dhan.dhan_readonly import (
        _LIVE_TRADING_BLOCKED_MSG,
        get_dhan_credentials_masked,
        get_profile,
        get_status,
    )

    ADAPTER_OK = True
except Exception as exc:
    print(f"ADAPTER_IMPORT: FAIL — {exc}")
    traceback.print_exc()

# ── Masked credentials ────────────────────────────────────────────────────────
if ADAPTER_OK:
    masked = get_dhan_credentials_masked()
    print(f"CLIENT_ID_MASKED: {masked['client_id_masked']}")
    print(f"TOKEN_MASKED: {masked['access_token_masked']}")

# ── Profile check ─────────────────────────────────────────────────────────────
PROFILE_PASS = False
PROFILE_ERROR = None

if ADAPTER_OK:
    print("\n--- Dhan Profile Check ---")
    t0 = time.time()
    try:
        result = get_profile()
        latency_ms = int((time.time() - t0) * 1000)

        if result.get("success"):
            print(f"DHAN_PROFILE_CHECK: PASS (source={result.get('source', '?')}, latency={latency_ms}ms)")
            safe_data = result.get("data", {})
            # Print only non-sensitive fields
            if isinstance(safe_data, dict):
                for k in ("dhanClientId", "clientName", "segment", "status", "message"):
                    if k in safe_data:
                        print(f"  {k}: {safe_data[k]}")
            PROFILE_PASS = True
        else:
            PROFILE_ERROR = result.get("error", "UNKNOWN")
            print(f"DHAN_PROFILE_CHECK: FAIL — {PROFILE_ERROR}")

    except Exception as exc:
        PROFILE_ERROR = f"{type(exc).__name__}: {exc}"
        print(f"DHAN_PROFILE_CHECK: FAIL — {PROFILE_ERROR}")
else:
    print("DHAN_PROFILE_CHECK: SKIP (adapter not loaded)")
    PROFILE_ERROR = "ADAPTER_IMPORT_FAILED"

# ── Blocked order placement safety test ───────────────────────────────────────
ORDER_BLOCK_OK = False
if ADAPTER_OK:
    try:
        from core.brokers.dhan.dhan_readonly import DhanReadOnly

        _ro = DhanReadOnly()
        try:
            _ro.place_order(test=True)
            print("ORDER_BLOCK_TEST: FAIL — place_order did NOT raise")
        except RuntimeError as _rte:
            if "LIVE_TRADING_BLOCKED" in str(_rte):
                print("ORDER_BLOCK_TEST: PASS — place_order correctly raises RuntimeError")
                ORDER_BLOCK_OK = True
            else:
                print(f"ORDER_BLOCK_TEST: UNEXPECTED_ERROR — {_rte}")
    except Exception as exc:
        print(f"ORDER_BLOCK_TEST: FAIL — {exc}")

# ── Final summary ─────────────────────────────────────────────────────────────
print("\n=== SUMMARY ===")
if PROFILE_PASS:
    print("DHAN_STATUS: connected")
else:
    print(f"DHAN_STATUS: disconnected ({PROFILE_ERROR or 'UNKNOWN'})")
print("LIVE_TRADING_ENABLED: false")
print("ORDER_PLACEMENT_TESTED: NO")
print(f"ORDER_PLACEMENT_BLOCKED: {'YES' if ORDER_BLOCK_OK else 'NOT_VERIFIED'}")
print("TOKEN_VALUE_PRINTED: NO")

# Exit code
if not PROFILE_PASS:
    print(f"\nVERIFICATION_RESULT: FAIL\n" f"REASON: Token present but profile check failed — {PROFILE_ERROR}")
    sys.exit(1)

print("\nVERIFICATION_RESULT: PASS")
sys.exit(0)
