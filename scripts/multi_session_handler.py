"""
Multi-Session Handler - Manages paper trading across multiple days
Handles session continuity, data persistence, and multi-day tracking
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import pytz

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


class MultiSessionHandler:
    """Handles multi-day paper trading sessions."""

    def __init__(self):
        """Initialize multi-session handler."""
        self.ist = pytz.timezone("Asia/Kolkata")
        self.session_file = ROOT_DIR / "storage" / "multi_session_state.json"
        self.archive_dir = ROOT_DIR / "storage" / "archive"
        self.archive_dir.mkdir(parents=True, exist_ok=True)

    def get_current_session_id(self):
        """Get current session ID (date-based)."""
        now = datetime.now(self.ist)
        return now.strftime("%Y%m%d")

    def load_session_state(self):
        """Load multi-session state."""
        if self.session_file.exists():
            try:
                return json.load(open(self.session_file))
            except:
                pass

        # Initialize new state
        return {
            "sessions": {},
            "total_days": 0,
            "total_trades_all_sessions": 0,
            "total_pnl_all_sessions": 0.0,
            "last_session_date": None,
        }

    def save_session_state(self, state):
        """Save multi-session state."""
        json.dump(state, open(self.session_file, "w"), indent=2)

    def archive_daily_session(self, session_date):
        """Archive a daily session."""
        archive_path = self.archive_dir / f"session_{session_date}"
        archive_path.mkdir(parents=True, exist_ok=True)

        # Copy current outputs
        files_to_archive = [
            "outputs/pnl_live.json",
            "outputs/positions_live.json",
            "outputs/paper_trades_live.csv",
        ]

        for file_path in files_to_archive:
            src = ROOT_DIR / file_path
            if src.exists():
                dst = archive_path / Path(file_path).name
                try:
                    import shutil

                    shutil.copy2(src, dst)
                except:
                    pass

        return archive_path

    def update_multi_session_state(self):
        """Update multi-session state with current session data."""
        state = self.load_session_state()
        session_id = self.get_current_session_id()
        now = datetime.now(self.ist)

        # Load current session PnL
        pnl_file = ROOT_DIR / "outputs" / "pnl_live.json"
        if pnl_file.exists():
            try:
                pnl = json.load(open(pnl_file))

                # Update or create session record
                if session_id not in state["sessions"]:
                    state["sessions"][session_id] = {
                        "date": session_id,
                        "start_time": now.isoformat(),
                        "total_trades": 0,
                        "total_pnl": 0.0,
                        "win_rate": 0.0,
                    }
                    state["total_days"] = len(state["sessions"])

                # Update session data
                state["sessions"][session_id].update(
                    {
                        "last_update": now.isoformat(),
                        "total_trades": pnl.get("total_trades", 0),
                        "total_pnl": pnl.get("total_pnl", 0.0),
                        "win_rate": pnl.get("win_rate", 0.0),
                        "realized_pnl": pnl.get("total_realized_pnl", 0.0),
                        "unrealized_pnl": pnl.get("total_unrealized_pnl", 0.0),
                    }
                )

                # Update totals
                state["total_trades_all_sessions"] = sum(s.get("total_trades", 0) for s in state["sessions"].values())
                state["total_pnl_all_sessions"] = sum(s.get("total_pnl", 0.0) for s in state["sessions"].values())
                state["last_session_date"] = session_id

                self.save_session_state(state)
                return state
            except Exception as e:
                print(f"  [WARN] Failed to update session state: {e}")

        return state

    def get_multi_session_summary(self):
        """Get summary of all sessions."""
        state = self.load_session_state()

        return {
            "total_days": state.get("total_days", 0),
            "total_trades": state.get("total_trades_all_sessions", 0),
            "total_pnl": state.get("total_pnl_all_sessions", 0.0),
            "sessions": state.get("sessions", {}),
            "last_session": state.get("last_session_date"),
        }

    def should_reset_daily(self):
        """Check if we should reset for a new day."""
        state = self.load_session_state()
        current_session = self.get_current_session_id()
        last_session = state.get("last_session_date")

        if last_session and last_session != current_session:
            return True
        return False

    def reset_for_new_day(self):
        """Reset for a new trading day."""
        state = self.load_session_state()
        last_session = state.get("last_session_date")

        if last_session:
            # Archive previous day
            self.archive_daily_session(last_session)
            print(f"  [OK] Archived previous session: {last_session}")

        # Clear current session files (optional)
        # This allows fresh start each day
        return True


def main():
    """Test multi-session handler."""
    handler = MultiSessionHandler()

    print("\n" + "=" * 80)
    print("  MULTI-SESSION HANDLER TEST")
    print("=" * 80 + "\n")

    # Update state
    state = handler.update_multi_session_state()

    # Get summary
    summary = handler.get_multi_session_summary()

    print("Multi-Session Summary:")
    print(f"  Total Days: {summary['total_days']}")
    print(f"  Total Trades (All Sessions): {summary['total_trades']}")
    print(f"  Total PnL (All Sessions): Rs {summary['total_pnl']:.2f}")
    print(f"  Current Session: {handler.get_current_session_id()}")
    print(f"  Last Session: {summary['last_session']}")

    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    main()
