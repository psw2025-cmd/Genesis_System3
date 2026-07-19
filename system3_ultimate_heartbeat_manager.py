"""
system3_ultimate_heartbeat_manager.py
--------------------------------------
Provides UltimateHeartbeatManager — the single writer for system3_daily_heartbeat.json.
Used by system3_autorun_master.py to prove the master process is alive.

Heartbeat JSON structure:
{
    "_last_updated": "<ISO timestamp>",
    "timestamp": "<ISO timestamp>",
    "status": "running",
    "pid": <int>,
    "phase": "<str>",
    "system_info": { "timestamp": "<ISO timestamp>", "pid": <int> }
}
"""

import json
import os
import traceback
from datetime import datetime
from pathlib import Path


class UltimateHeartbeatManager:
    """
    Single-writer heartbeat manager for System3 autorun master.

    Writes a timestamped JSON file at ROOT/system3_daily_heartbeat.json every call
    to update_heartbeat(). Thread-safe via atomic write (temp file + replace).
    """

    def __init__(
        self,
        heartbeat_path: str | Path | None = None,
        phase: str = "autorun_master",
    ):
        root = Path(__file__).parent.absolute()
        self.heartbeat_path = Path(heartbeat_path) if heartbeat_path else root / "system3_daily_heartbeat.json"
        self.phase = phase
        self.pid = os.getpid()

        # Ensure parent directory exists
        self.heartbeat_path.parent.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def update_heartbeat(self) -> bool:
        """
        Write (or atomically update) the heartbeat JSON file.

        Returns:
            True  — write succeeded
            False — write failed (caller should count failures)
        """
        try:
            now_iso = datetime.now().isoformat()
            payload = {
                "_last_updated": now_iso,
                "timestamp": now_iso,
                "status": "running",
                "pid": self.pid,
                "phase": self.phase,
                "system_info": {
                    "timestamp": now_iso,
                    "pid": self.pid,
                },
            }

            # Merge with existing keys so other writers (dashboard, etc.) aren't clobbered
            if self.heartbeat_path.exists():
                try:
                    with self.heartbeat_path.open("r", encoding="utf-8") as f:
                        existing = json.load(f)
                    existing.update(payload)
                    payload = existing
                except Exception:
                    # If the file is corrupt just overwrite it
                    pass

            # Atomic write: write to .tmp then rename
            tmp_path = self.heartbeat_path.with_suffix(".tmp")
            with tmp_path.open("w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
            tmp_path.replace(self.heartbeat_path)
            return True

        except Exception:  # noqa: BLE001
            traceback.print_exc()
            return False

    # ------------------------------------------------------------------
    # Convenience helpers (used by some phase modules)
    # ------------------------------------------------------------------

    def read_heartbeat(self) -> dict:
        """Return current heartbeat dict, or empty dict on failure."""
        try:
            if self.heartbeat_path.exists():
                with self.heartbeat_path.open("r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def is_stale(self, threshold_seconds: float = 240.0) -> bool:
        """Return True if the heartbeat has not been updated recently."""
        data = self.read_heartbeat()
        ts_str = data.get("_last_updated") or data.get("timestamp")
        if not ts_str:
            return True
        try:
            last = datetime.fromisoformat(ts_str)
            return (datetime.now() - last).total_seconds() > threshold_seconds
        except Exception:
            return True

    def mark_phase(self, phase: str) -> bool:
        """Update the 'phase' field in the heartbeat file without a full write cycle."""
        self.phase = phase
        return self.update_heartbeat()


# ---------------------------------------------------------------------------
# Quick self-test when run directly
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    mgr = UltimateHeartbeatManager()
    ok = mgr.update_heartbeat()
    print(f"[UltimateHeartbeatManager] update_heartbeat() -> {'OK' if ok else 'FAILED'}")
    print(f"[UltimateHeartbeatManager] is_stale(10s) -> {mgr.is_stale(10)}")
    print(f"[UltimateHeartbeatManager] heartbeat written to: {mgr.heartbeat_path}")
