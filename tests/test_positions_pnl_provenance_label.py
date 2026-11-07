"""Paper positions must not present unreconciled returns as verified net performance."""
from pathlib import Path

def test_positions_unverified_pnl_labels():
    root=Path(__file__).resolve().parents[1]
    ui=(root/"dashboard/frontend/src/components/Positions.tsx").read_text()
    assert "PAPER NET P&L · REPORTED / UNVERIFIED" in ui
    assert "PAPER WIN RATE · REPORTED / UNVERIFIED" in ui
    assert "matched to opening and closing fills, charges, and ledger evidence" in ui
    assert "Real Dhan positions are read-only" in ui
    assert "setActiveTab('broker')" in ui
