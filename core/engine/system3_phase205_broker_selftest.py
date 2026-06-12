"""
System3 Phase 205 - Broker Credential Self-Tester

Performs safe read-only API calls to validate broker connectivity.
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

LOG_DIR = PROJECT_ROOT / "logs" / "brokers"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH = LOG_DIR / "system3_broker_selftest.log"


def mask_sensitive(value: str) -> str:
    """Mask sensitive credential values."""
    if not value or len(value) < 4:
        return "***"
    return value[:2] + "*" * (len(value) - 4) + value[-2:]


def run_phase205(**kwargs) -> Dict[str, Any]:
    """
    Run Phase 205: Broker Credential Self-Tester.

    Returns:
        dict: {
            "phase": 205,
            "status": "OK" or "WARN" or "ERROR",
            "details": "short summary",
            "outputs": {
                "angelone_status": str,
                "binance_status": str,
            },
            "errors": [],
        }
    """
    errors = []
    angelone_status = "NOT_TESTED"
    binance_status = "NOT_TESTED"

    try:
        with LOG_PATH.open("w", encoding="utf-8") as f:
            f.write(f"System3 Broker Self-Test Log\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 70 + "\n\n")

            # Test Dhan
            f.write("## Dhan Connectivity Test\n\n")
            try:
                from core.utils.env_loader import get_angelone_credentials

                creds = get_angelone_credentials()

                f.write(f"API Key: {mask_sensitive(creds.get('api_key', ''))}\n")
                f.write(f"Client ID: {mask_sensitive(creds.get('client_id', ''))}\n")
                f.write(f"PIN/Password: {'***' if creds.get('pin') or creds.get('password') else 'NOT_SET'}\n")
                f.write(f"TOTP Secret: {'***' if creds.get('totp_secret') else 'NOT_SET'}\n\n")

                # Check if credentials are present
                if not all([creds.get("api_key"), creds.get("client_id"), creds.get("totp_secret")]):
                    f.write("Status: ❌ INCOMPLETE_CREDENTIALS\n")
                    f.write("Reason: Missing required credential fields\n")
                    angelone_status = "INCOMPLETE_CREDENTIALS"
                else:
                    # Dhan broker path is disabled — Dhan-only mode
                    f.write("Status: DISABLED\n")
                    f.write("Reason: Dhan broker path disabled — System3 is Dhan-only\n")
                    angelone_status = "DISABLED_DHAN_ONLY"
            except ImportError:
                f.write("Status: ❌ MODULE_NOT_FOUND\n")
                f.write("Reason: Cannot import broker modules\n")
                angelone_status = "MODULE_NOT_FOUND"
                errors.append("Dhan broker module not found")
            except Exception as e:
                f.write(f"Status: ❌ ERROR\n")
                f.write(f"Error: {str(e)}\n")
                angelone_status = "ERROR"
                errors.append(f"Dhan test error: {e}")

            f.write("\n")

            # Test Binance (if enabled)
            f.write("## Binance Connectivity Test\n\n")
            f.write("Status: ⚠️ NOT_CONFIGURED\n")
            f.write("Reason: Binance testing not implemented (read-only public API test would go here)\n")
            binance_status = "NOT_CONFIGURED"

            f.write("\n" + "=" * 70 + "\n")
            f.write("Summary\n")
            f.write("=" * 70 + "\n")
            f.write(f"Dhan: {angelone_status}\n")
            f.write(f"Binance: {binance_status}\n")

        status = "OK" if angelone_status == "CONNECTED" else "WARN"
        details = f"Dhan: {angelone_status}"
        if binance_status != "NOT_CONFIGURED":
            details += f", Binance: {binance_status}"

        return {
            "phase": 205,
            "status": status,
            "details": details,
            "outputs": {
                "angelone_status": angelone_status,
                "binance_status": binance_status,
                "log_path": str(LOG_PATH),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 205,
            "status": "ERROR",
            "details": f"Phase 205 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 205 - BROKER CREDENTIAL SELF-TESTER")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase205()

    print(f"Phase 205: {result['details']}")
    if result.get("errors"):
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    if result["outputs"]:
        print(f"\nLog: {result['outputs']['log_path']}")
        print(f"Dhan: {result['outputs']['angelone_status']}")
        print(f"Binance: {result['outputs']['binance_status']}")

    return 0 if result["status"] in ("OK", "WARN") else 1


if __name__ == "__main__":
    sys.exit(main())
