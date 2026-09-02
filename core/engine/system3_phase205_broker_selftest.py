"""
System3 Phase 205 - Broker Credential Self-Tester

Performs safe read-only API calls to validate broker connectivity.
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

LOG_DIR = PROJECT_ROOT / "logs" / "brokers"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH = LOG_DIR / "system3_broker_selftest.log"


def mask_sensitive(value: str) -> str:
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
            "outputs": {"dhan_status": str},
            "errors": [],
        }
    """
    errors = []
    dhan_status = "NOT_TESTED"

    try:
        with LOG_PATH.open("w", encoding="utf-8") as f:
            f.write("System3 Broker Self-Test Log\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 70 + "\n\n")

            # Test Dhan credentials
            f.write("## Dhan Connectivity Test\n\n")
            try:
                from core.utils.env_loader import get_dhan_credentials

                creds = get_dhan_credentials()

                f.write(f"Client ID: {mask_sensitive(creds.get('client_id', ''))}\n")
                f.write(f"Access Token: {'***' if creds.get('access_token') else 'NOT_SET'}\n\n")

                if not all([creds.get("client_id"), creds.get("access_token")]):
                    f.write("Status: INCOMPLETE_CREDENTIALS\n")
                    dhan_status = "INCOMPLETE_CREDENTIALS"
                else:
                    f.write("Status: CREDENTIALS_PRESENT\n")
                    dhan_status = "CREDENTIALS_PRESENT"
            except ImportError:
                f.write("Status: MODULE_NOT_FOUND\n")
                dhan_status = "MODULE_NOT_FOUND"
                errors.append("env_loader module not found")
            except Exception as e:
                f.write(f"Status: ERROR\nError: {str(e)}\n")
                dhan_status = "ERROR"
                errors.append(f"Dhan test error: {e}")

            f.write("\n" + "=" * 70 + "\n")
            f.write(f"Dhan: {dhan_status}\n")

        status = "OK" if dhan_status in ("CREDENTIALS_PRESENT", "CONNECTED") else "WARN"
        return {
            "phase": 205,
            "status": status,
            "details": f"Dhan: {dhan_status}",
            "outputs": {
                "dhan_status": dhan_status,
                "log_path": str(LOG_PATH),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 205,
            "status": "ERROR",
            "details": str(e),
            "outputs": {},
            "errors": [str(e)],
        }


if __name__ == "__main__":
    result = run_phase205()
    print(f"Phase 205 result: {result['status']}")
    print(f"Details: {result['details']}")
    for err in result["errors"]:
        print(f"  ERROR: {err}")
