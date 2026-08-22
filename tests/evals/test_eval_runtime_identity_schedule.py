"""Eval: runtime identity-safety rotate-daily cadence must match live */5 SSOT."""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
IDENTITY = ROOT / "scripts/gcp_runtime_identity_safety.py"
CONTRACT = ROOT / "dashboard/backend/scheduler_contract.py"
UNITTEST = ROOT / "tests/test_gcp_runtime_identity_safety.py"

LIVE_ROTATE_DAILY = "*/5 * * * *"
STALE_HOURLY = "30 * * * *"


def _assign_value(path: Path, name: str) -> str:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == name:
                    return ast.literal_eval(node.value)
    raise AssertionError(f"{name} not found in {path}")


def test_eval_identity_safety_rotate_daily_matches_live_and_contract():
    identity_schedule = _assign_value(IDENTITY, "EXPECTED_SCHEDULE")
    identity_zone = _assign_value(IDENTITY, "EXPECTED_TIME_ZONE")
    assert identity_schedule == LIVE_ROTATE_DAILY
    assert identity_zone == "Asia/Kolkata"
    assert STALE_HOURLY not in IDENTITY.read_text(encoding="utf-8")

    contract = CONTRACT.read_text(encoding="utf-8")
    assert "genesis-system3-dhan-token-rotate-daily" in contract
    assert f'"{LIVE_ROTATE_DAILY}"' in contract or f"'{LIVE_ROTATE_DAILY}'" in contract

    unit = UNITTEST.read_text(encoding="utf-8")
    assert f'"{LIVE_ROTATE_DAILY}"' in unit
    assert f'"{STALE_HOURLY}"' in unit
    assert "scheduler_config_invalid" in unit
