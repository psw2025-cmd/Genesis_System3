import json

from dashboard.backend.lifetime_research_engine import (
    compute_metrics,
    run_lifetime_research,
    select_champion,
    walk_forward_windows,
    OutcomeRow,
)


def _row(i, strategy="S1", symbol="NIFTY", side="CE", ret=0.02):
    return OutcomeRow(ts=f"2026-01-{i:02d}T09:15:00+05:30", symbol=symbol, side=side, strategy=strategy, return_pct=ret, source="test")


def test_walk_forward_has_no_future_leakage():
    rows = [_row(i) for i in range(1, 61)]
    windows = walk_forward_windows(rows, train_size=20, test_size=10)

    assert windows
    for train, test in windows:
        assert train[-1].ts < test[0].ts
        assert len(train) == 20
        assert len(test) == 10


def test_metrics_pass_for_positive_strategy():
    rows = [_row(i, ret=0.03 if i % 3 else -0.005) for i in range(1, 41)]
    m = compute_metrics(rows, {"min_test_rows": 10, "min_hit_rate": 0.55, "min_profit_factor": 1.15, "min_expectancy": 0.001, "max_drawdown_pct": 0.20, "min_avg_trade_return": 0.001})

    assert m.passed is True
    assert m.expectancy > 0
    assert m.profit_factor > 1


def test_metrics_block_bad_strategy():
    rows = [_row(i, ret=-0.02) for i in range(1, 41)]
    m = compute_metrics(rows)

    assert m.passed is False
    assert "HIT_RATE_BELOW_GATE" in m.blockers
    assert "EXPECTANCY_BELOW_GATE" in m.blockers


def test_select_champion_blocks_when_live_env_not_safe(monkeypatch):
    monkeypatch.setenv("LIVE_TRADING_ENABLED", "1")
    good = compute_metrics([_row(i, ret=0.03 if i % 3 else -0.005) for i in range(1, 41)], {"min_test_rows": 10, "min_expectancy": 0.001, "min_avg_trade_return": 0.001})

    decision = select_champion([good])

    assert decision.status == "BLOCKED"
    assert decision.champion is None
    assert "LIVE_TRADING_ENV_NOT_SAFE_FOR_RESEARCH" in decision.blockers


def test_run_lifetime_research_writes_reports(tmp_path, monkeypatch):
    monkeypatch.setenv("LIVE_TRADING_ENABLED", "0")
    ledger = tmp_path / "state" / "paper_pipeline_v8" / "closed_paper_trade_ledger.jsonl"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for i in range(1, 91):
        rows.append({"created_utc": f"2026-01-{(i % 28) + 1:02d}T09:15:00+05:30", "underlying": "NIFTY", "option_side": "CE", "strategy": "S1", "return_pct": 0.03 if i % 4 else -0.005})
    ledger.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")

    result = run_lifetime_research(tmp_path, {"min_train_rows": 20, "min_test_rows": 10, "min_walk_forward_windows": 2, "min_expectancy": 0.001, "min_avg_trade_return": 0.001})

    assert result["status"] == "CHAMPION_SELECTED"
    assert result["champion"]["symbol"] == "NIFTY"
    assert (tmp_path / "reports" / "latest" / "lifetime_research_engine" / "summary.json").exists()
