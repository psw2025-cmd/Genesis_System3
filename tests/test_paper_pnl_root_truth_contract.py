import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "paper_pnl_summary.json"


def test_root_pnl_fallback_never_exposes_synthetic_fixture_as_production_truth():
    data = json.loads(SUMMARY.read_text(encoding="utf-8"))

    assert data["total_trades"] == 0
    assert data["winning_trades"] == 0
    assert data["losing_trades"] == 0
    assert data["total_realized_pnl"] == 0.0
    assert data["total_unrealized_pnl"] == 0.0
    assert data["total_pnl"] == 0.0
    assert data["open_positions"] == 0
    assert data["verification_status"] == "NO_VERIFIED_TRADES"
    assert data["is_fixture"] is False
    assert data["data_source"] == "none"
    text = SUMMARY.read_text(encoding="utf-8").lower()
    assert "synthetic trades" not in text
    assert "feb 1 2026" not in text


def test_fixture_history_remains_confined_to_tests_directory():
    fixture = ROOT / "tests" / "fixtures" / "paper_closed_trades_feb2026.json"
    assert fixture.exists()
    assert fixture.is_file()
