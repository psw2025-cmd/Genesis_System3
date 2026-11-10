"""Backtest dashboard must never certify hardcoded performance."""
from dashboard.backend.backtest_service import BACKTEST_STRATEGIES, get_backtest_results


def test_backtest_results_fail_closed_without_independent_evidence():
    result = get_backtest_results()
    assert result["status"] == "NOT_VERIFIED"
    assert result["passed"] is False
    assert result["verification_status"] == "NOT_VERIFIED"
    assert result["data_mode"] == "NO_VERIFIED_BACKTEST"
    assert result["summary"]["net_pnl"] is None
    assert result["summary"]["win_rate"] is None
    assert result["summary"]["total_trades"] is None
    assert result["summary"]["passed"] is False
    assert result["equity_curve"] == []
    assert result["recent_trades"] == []
    assert result["cloud_artifacts"] is None
    assert result["run_id"] is None
    assert result["git_sha"] is None
    assert result["governance"]["order_placement_allowed"] is False
    assert BACKTEST_STRATEGIES == []
