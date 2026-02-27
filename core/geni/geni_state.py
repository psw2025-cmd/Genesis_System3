"""
System3 GENI - State Management

Manages high-level GENI system state persistence.
"""

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional, List
from datetime import datetime

from .geni_config import GENI_STATE_FILE


@dataclass
class GeniState:
    """GENI system state representation."""

    timestamp: str
    env_ok: bool
    validation_passed: bool
    last_validation_summary: str
    live_loop_running: bool
    pending_issues: List[str]

    @classmethod
    def default(cls) -> "GeniState":
        """Create a default state."""
        return cls(
            timestamp=datetime.now().isoformat(),
            env_ok=False,
            validation_passed=False,
            last_validation_summary="No validation run yet",
            live_loop_running=False,
            pending_issues=[],
        )


def load_state(path: Optional[Path] = None) -> GeniState:
    """
    Load GENI state from file.

    Args:
        path: Optional path to state file (defaults to GENI_STATE_FILE)

    Returns:
        GeniState object (default if file missing/corrupt)
    """
    if path is None:
        path = GENI_STATE_FILE

    if not path.exists():
        return GeniState.default()

    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        return GeniState(
            timestamp=data.get("timestamp", datetime.now().isoformat()),
            env_ok=data.get("env_ok", False),
            validation_passed=data.get("validation_passed", False),
            last_validation_summary=data.get("last_validation_summary", ""),
            live_loop_running=data.get("live_loop_running", False),
            pending_issues=data.get("pending_issues", []),
        )
    except Exception:
        # If file is corrupt, return default state
        return GeniState.default()


def save_state(state: GeniState, path: Optional[Path] = None) -> None:
    """
    Save GENI state to file.

    Args:
        state: GeniState to save
        path: Optional path to state file (defaults to GENI_STATE_FILE)
    """
    if path is None:
        path = GENI_STATE_FILE

    # Update timestamp
    state.timestamp = datetime.now().isoformat()

    # Ensure directory exists
    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with path.open("w", encoding="utf-8") as f:
            json.dump(asdict(state), f, indent=2, ensure_ascii=False)
    except Exception as e:
        # Log error but don't crash
        print(f"[GENI][WARN] Failed to save state: {e}")
