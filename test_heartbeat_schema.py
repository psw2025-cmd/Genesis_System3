#!/usr/bin/env python3
"""
Schema guard for system3_daily_heartbeat.json
Ensures required sections are present and version is 2.0.0.
Run standalone or via test runner.
"""

from __future__ import annotations

import json
from pathlib import Path

from system3_ultimate_heartbeat_manager import REQUIRED_SECTIONS

HEARTBEAT_PATH = Path("system3_daily_heartbeat.json")
EXPECTED_VERSION = "2.0.0"


def test_heartbeat_schema():
    assert HEARTBEAT_PATH.exists(), f"Heartbeat file missing: {HEARTBEAT_PATH}"
    data = json.loads(HEARTBEAT_PATH.read_text(encoding="utf-8"))

    assert data.get("_version") == EXPECTED_VERSION, "Heartbeat version mismatch"

    missing = [s for s in REQUIRED_SECTIONS if s not in data]
    assert not missing, f"Missing heartbeat sections: {missing}"

    # Spot-check timestamp presence
    assert data.get("_last_updated") or data.get("system_info", {}).get("timestamp"), "Missing heartbeat timestamp"


if __name__ == "__main__":
    test_heartbeat_schema()
    print("✅ heartbeat schema OK")
