"""Opening a paper position cannot reset realized performance evidence."""
import json

from dashboard.backend.paper_pipeline_v8 import _pipeline_paths, _update_positions_and_pnl


def _order(order_id):
    return {
        "position_id": "PV8-" + order_id,
        "paper_order_id": order_id,
        "underlying": "NIFTY",
        "contract_symbol": "NIFTY-CE",
        "qty": 25,
        "entry_price": 100.0,
        "created_utc": "2026-11-06T10:00:00+00:00",
    }


def test_new_paper_order_preserves_existing_realized_history(tmp_path):
    paths = _pipeline_paths(tmp_path)
    paths["pnl_summary"].parent.mkdir(parents=True, exist_ok=True)
    paths["pnl_summary"].write_text(json.dumps({
        "total_trades": 12, "winning_trades": 7, "losing_trades": 5,
        "win_rate": 58.333, "total_realized_pnl": -425.0,
    }))
    _update_positions_and_pnl(tmp_path, _order("one"))
    result = json.loads(paths["pnl_summary"].read_text())
    assert result["total_trades"] == 12
    assert result["winning_trades"] == 7
    assert result["total_realized_pnl"] == -425.0
    assert result["total_pnl"] is None
    assert result["verification_status"] == "NOT_VERIFIED"
    _update_positions_and_pnl(tmp_path, _order("one"))
    assert json.loads(paths["positions"].read_text())["open_count"] == 1


def test_new_paper_order_without_close_evidence_does_not_claim_zero_win_rate(tmp_path):
    _update_positions_and_pnl(tmp_path, _order("first"))
    result = json.loads(_pipeline_paths(tmp_path)["pnl_summary"].read_text())
    assert result["total_trades"] is None
    assert result["win_rate"] is None
    assert result["total_realized_pnl"] is None
    assert result["total_unrealized_pnl"] is None
    assert result["open_positions"] == 1
