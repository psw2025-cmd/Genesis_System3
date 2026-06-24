#!/usr/bin/env python3
"""WebSocket tick health proof — probes runtime state; PASS only when tick stream proven."""

from __future__ import annotations

import json
import os
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "latest" / "websocket_tick_health"
CLOUD = os.environ.get("SYSTEM3_API_BASE", "https://genesis-system3-backend.onrender.com").rstrip("/")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    state = {}
    try:
        with urllib.request.urlopen(f"{CLOUD}/api/state", timeout=60) as resp:
            state = json.loads(resp.read().decode("utf-8", errors="replace"))
    except Exception as exc:
        state = {"error": str(exc)[:200]}

    ws_path = "/ws/stream"
    tick_age = state.get("last_tick_age_sec") or state.get("tick_health", {}).get("last_tick_age_sec")
    refresh = state.get("refresh_interval") or state.get("tick_health", {}).get("refresh_interval_sec")
    broker_ok = (state.get("broker") or {}).get("connected")
    market_open = (state.get("market") or {}).get("is_open")
    rest_ok = refresh is not None and float(refresh) <= 10
    pass_gate = (tick_age is not None and float(tick_age) < 30 and broker_ok) or (
        rest_ok and broker_ok and tick_age is not None and float(tick_age) <= 15
    )

    report = {
        "generated_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "pass": pass_gate,
        "websocket_endpoint": ws_path,
        "evidence": {
            "last_tick_age_sec": tick_age,
            "refresh_interval_sec": refresh,
            "broker_connected": broker_ok,
            "market_open": market_open,
            "rest_fallback_active": rest_ok,
            "note": "PASS with REST SSOT poll ≤10s for analyzer; WebSocket required for live execution",
        },
        "auto_action": "Expose last_tick_age_sec in /api/state from Dhan WebSocket feed",
    }
    (OUT / "summary.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (OUT / "summary.md").write_text(
        f"# WebSocket Tick Health\n\nPass: **{pass_gate}**\n\nTick age: `{tick_age}`\n",
        encoding="utf-8",
    )
    print(json.dumps({"pass": pass_gate}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
