"""Eval: scanner cards must not invent SL/target or model confidence (Gmail M033/M034)."""

from __future__ import annotations

from pathlib import Path

SIGNALS = (
    Path(__file__).resolve().parents[2]
    / "dashboard"
    / "frontend"
    / "src"
    / "components"
    / "Signals.tsx"
)


def test_signals_scanner_card_is_observation_only():
    text = SIGNALS.read_text(encoding="utf-8")
    assert "REAL CANDIDATE EVIDENCE" not in text
    assert "SCANNER OBSERVATION" in text
    assert "ltp * 0.8" not in text
    assert "ltp * 1.3" not in text
    assert "Math.abs(gain)" not in text
    assert "candidate ? 'PASS'" not in text
    assert "confidence: 0," in text
