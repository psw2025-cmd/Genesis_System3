"""Human approval gate — read-only status for live enablement ladder."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[2]
GATE_FILE = ROOT / "config" / "human_approval_gate.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load_human_approval() -> Dict[str, Any]:
    if not GATE_FILE.exists():
        return {
            "approved": False,
            "approved_by": None,
            "approved_utc": None,
            "scope": None,
            "live_trading_env_flip_authorized": False,
            "technical_gates_still_required": [],
            "note": "Human approval not recorded",
        }
    try:
        data = json.loads(GATE_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {"approved": False}
    except Exception:
        return {"approved": False, "note": "Human approval file unreadable"}


def build_approval_status() -> Dict[str, Any]:
    gate = load_human_approval()
    approved = bool(gate.get("approved"))
    tech_gates: List[str] = list(gate.get("technical_gates_still_required") or [])
    return {
        "generated_utc": _utc_now(),
        "human_approval": approved,
        "approved_by": gate.get("approved_by"),
        "approved_utc": gate.get("approved_utc"),
        "scope": gate.get("scope"),
        "live_trading_enabled": False,
        "live_trading_env_flip_authorized": bool(gate.get("live_trading_env_flip_authorized")),
        "dashboard_status": "PASS" if approved else "PEND",
        "dashboard_reason": (
            f"Owner approved — {gate.get('approved_by', 'owner')}"
            if approved
            else "Required before live"
        ),
        "technical_gates_still_required": tech_gates,
        "technical_gates_pending_count": len(tech_gates),
        "production_ready_for_real_money": False,
        "note": gate.get("note"),
    }
