"""Eval: Positions must treat fractional win_rate as a percent (Gmail P08)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
POSITIONS = ROOT / "dashboard" / "frontend" / "src" / "components" / "Positions.tsx"
UTILS = ROOT / "dashboard" / "frontend" / "src" / "lib" / "utils.ts"


def test_positions_uses_shared_fraction_to_percent_helper():
    positions = POSITIONS.read_text(encoding="utf-8")
    utils = UTILS.read_text(encoding="utf-8")
    assert "export function asPct" in utils
    assert "Math.abs(n) <= 1 ? n * 100 : n" in utils
    assert "asPct(summary.win_rate)" in positions
    assert "Number(summary.win_rate ?? 0)" not in positions
