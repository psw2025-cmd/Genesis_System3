from dashboard.backend.profit_governor import (
    BLOCK_ACCURACY,
    BLOCK_NO_DHAN_QUOTE,
    BLOCK_SPREAD,
    select_best_paper_trade,
    summarize_outcomes,
)


def test_summarize_outcomes_expectancy():
    stats = summarize_outcomes([
        {"underlying": "NIFTY", "option_side": "CE", "pnl_pct": 0.20},
        {"underlying": "NIFTY", "option_side": "CE", "pnl_pct": -0.10},
        {"underlying": "NIFTY", "option_side": "CE", "pnl_pct": 0.30},
    ])

    row = stats["NIFTY::CE"]
    assert row["samples"] == 3
    assert round(row["hit_rate"], 4) == 0.6667
    assert row["expectancy"] > 0


def test_selects_highest_positive_expectancy_real_dhan_candidate():
    candidates = [
        {
            "underlying": "NIFTY", "option_side": "CE", "ltp": 100, "data_source": "dhan", "source_priority": "dhan_p0_live",
            "oi": 1000, "volume": 500, "top_bid_price": 99, "top_ask_price": 100.5, "confidence": 0.70, "expectancy": 0.05,
        },
        {
            "underlying": "BANKNIFTY", "option_side": "PE", "ltp": 200, "data_source": "dhan", "source_priority": "dhan_p0_live",
            "oi": 1000, "volume": 500, "top_bid_price": 198, "top_ask_price": 201, "confidence": 0.80, "expectancy": 0.09,
        },
    ]

    decision = select_best_paper_trade(candidates, [], gates={"min_expectancy": 0.01})

    assert decision.status == "SELECTED"
    assert decision.selected["underlying"] == "BANKNIFTY"
    assert decision.selected["entry_exit"]["stop_loss"] < decision.selected["entry_exit"]["entry_price"]
    assert decision.selected["entry_exit"]["target"] > decision.selected["entry_exit"]["entry_price"]


def test_blocks_non_dhan_candidate_even_if_expectancy_high():
    candidates = [
        {
            "underlying": "NIFTY", "option_side": "CE", "ltp": 100, "data_source": "csv_fallback", "source_priority": "csv_fallback",
            "oi": 999999, "volume": 999999, "confidence": 0.99, "expectancy": 9.0,
        }
    ]

    decision = select_best_paper_trade(candidates, [])

    assert decision.status == "BLOCKED"
    assert decision.blocked[0]["reason"] == BLOCK_NO_DHAN_QUOTE


def test_blocks_wide_spread_candidate():
    candidates = [
        {
            "underlying": "NIFTY", "option_side": "CE", "ltp": 100, "data_source": "dhan", "source_priority": "dhan_p0_live",
            "oi": 1000, "volume": 500, "top_bid_price": 80, "top_ask_price": 120, "confidence": 0.90, "expectancy": 0.10,
        }
    ]

    decision = select_best_paper_trade(candidates, [], gates={"max_spread_pct": 8.0})

    assert decision.status == "BLOCKED"
    assert decision.blocked[0]["reason"] == BLOCK_SPREAD


def test_history_accuracy_gate_blocks_bad_symbol_after_min_samples():
    candidates = [
        {
            "underlying": "NIFTY", "option_side": "CE", "ltp": 100, "data_source": "dhan", "source_priority": "dhan_p0_live",
            "oi": 1000, "volume": 500, "top_bid_price": 99, "top_ask_price": 100.5, "confidence": 0.90, "expectancy": 0.20,
        }
    ]
    outcomes = [{"underlying": "NIFTY", "option_side": "CE", "pnl_pct": -0.05} for _ in range(10)]

    decision = select_best_paper_trade(candidates, outcomes, gates={"min_samples": 10, "min_hit_rate": 0.55})

    assert decision.status == "BLOCKED"
    assert decision.blocked[0]["reason"] == BLOCK_ACCURACY
