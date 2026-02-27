"""
Angel One Index Options - Real Data Capture Starter

Logs Monday start-time and creates minimal recorder.
SAFE MODE ONLY - Read-only logging, no execution.
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, Any

PROJECT_ROOT = Path(__file__).parent.parent.parent
LEARNING_DIR = PROJECT_ROOT / "storage" / "learning"
CAPTURE_LOG_CSV = LEARNING_DIR / "real_data_capture_log.csv"

LEARNING_DIR.mkdir(parents=True, exist_ok=True)


def start_real_data_capture() -> Dict[str, Any]:
    """
    Start real data capture session.

    Logs Monday start-time and creates minimal recorder.
    Does NOT start any automated processes.

    Returns:
        Dict with capture session info
    """
    print("=== ANGEL ONE INDEX OPTIONS - REAL DATA CAPTURE STARTER ===")
    print("[INFO] SAFE MODE - Logging only, no execution\n")

    session = {
        "session_id": f"session_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
        "start_time": datetime.utcnow().isoformat(),
        "status": "STARTED",
        "mode": "SAFE",
        "auto_execute": False,
        "auto_pnl": False,
    }

    # Log to CSV
    try:
        import pandas as pd

        log_row = {
            "session_id": session["session_id"],
            "start_time": session["start_time"],
            "status": session["status"],
            "mode": session["mode"],
        }

        if CAPTURE_LOG_CSV.exists():
            df = pd.read_csv(CAPTURE_LOG_CSV)
            df = pd.concat([df, pd.DataFrame([log_row])], ignore_index=True)
        else:
            df = pd.DataFrame([log_row])

        df.to_csv(CAPTURE_LOG_CSV, index=False)
        print(f"[LOG] Capture session started: {session['session_id']}")
        print(f"[LOG] Start time: {session['start_time']}")
        print(f"[LOG] Mode: {session['mode']}")
        print(f"[LOG] Logged to: {CAPTURE_LOG_CSV}")

    except Exception as e:
        print(f"[ERROR] Failed to log capture session: {e}")
        session["status"] = "ERROR"
        session["error"] = str(e)

    return session


def get_capture_status() -> Dict[str, Any]:
    """
    Get current capture status (read-only).

    Returns:
        Dict with capture status
    """
    if not CAPTURE_LOG_CSV.exists():
        return {
            "status": "NO_SESSIONS",
            "message": "No capture sessions logged",
        }

    try:
        import pandas as pd

        df = pd.read_csv(CAPTURE_LOG_CSV)
        if df.empty:
            return {
                "status": "EMPTY",
                "message": "Capture log is empty",
            }

        latest = df.iloc[-1]
        return {
            "status": "ACTIVE",
            "latest_session": latest.to_dict(),
            "total_sessions": len(df),
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "error": str(e),
        }


def main() -> None:
    """Main entry point."""
    print("Starting real data capture session...\n")
    session = start_real_data_capture()

    if session["status"] == "STARTED":
        print("\n✅ Real data capture session started successfully")
        print("⚠️  Note: This only logs the session. No automated processes started.")
    else:
        print(f"\n❌ Failed to start capture session: {session.get('error', 'Unknown error')}")


if __name__ == "__main__":
    main()
