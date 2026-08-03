import numpy as np
import pandas as pd

from scripts.options_research_train_backtest import build_features, chronological_split, evaluate_ranked


def fixture_rows(days=20, bars=80):
    rows = []
    base = pd.Timestamp("2026-01-01 09:15", tz="Asia/Kolkata")
    for d in range(days):
        for symbol_index, symbol in enumerate(["AAA", "BBB", "CCC", "DDD"]):
            for side_index, side in enumerate(["CALL", "PUT"]):
                for i in range(bars):
                    ts = base + pd.Timedelta(days=d, minutes=i)
                    spot = 100 + symbol_index * 10 + d * 0.2 + i * 0.01
                    close = 5 + symbol_index + side_index * 0.2 + 0.02 * i + np.sin(i / 8 + symbol_index) * 0.1
                    rows.append({
                        "timestamp": int(ts.tz_convert("UTC").timestamp()), "underlying": symbol,
                        "security_id": str(100 + symbol_index), "exchange_segment": "NSE_FNO",
                        "instrument": "OPTSTK", "option_type": side, "expiry_flag": "MONTH", "expiry_code": 0,
                        "strike_offset": "ATM", "open": close, "high": close + 0.1,
                        "low": close - 0.1, "close": close, "volume": 1000 + i,
                        "oi": 5000 + i * 2, "iv": 0.2 + i * 0.0001,
                        "strike": round(spot), "spot": spot,
                    })
    return pd.DataFrame(rows)


def test_future_target_is_shifted_not_same_row():
    raw = fixture_rows(days=2, bars=50)
    features = build_features(raw, horizon_bars=5, round_trip_cost_bps=0)
    sample = features.iloc[0]
    mask = (
        (raw["underlying"] == sample["underlying"])
        & (raw["option_type"] == sample["option_type"])
        & (raw["strike_offset"] == sample["strike_offset"])
    )
    group = raw[mask].sort_values("timestamp").reset_index(drop=True)
    ts_epoch = int(sample["timestamp"].tz_convert("UTC").timestamp())
    loc = int(group.index[group["timestamp"] == ts_epoch][0])
    expected = group.iloc[loc + 5]["close"] / group.iloc[loc]["close"] - 1
    assert abs(sample["target_net_return"] - expected) < 1e-12
    assert sample["target_timestamp"] > sample["timestamp"]


def test_chronological_split_has_embargo_and_no_label_crossing():
    features = build_features(fixture_rows(), horizon_bars=5, round_trip_cost_bps=10)
    train, valid, test, split = chronological_split(features, embargo_days=1)
    assert train["timestamp"].max() < valid["timestamp"].min()
    assert valid["timestamp"].max() < test["timestamp"].min()
    assert train["target_timestamp"].max().floor("D") <= split.train_end
    assert valid["target_timestamp"].max().floor("D") <= split.validation_end
    assert split.validation_start > split.train_end
    assert split.test_start > split.validation_end


def test_ranked_evaluation_selects_one_contract_per_underlying():
    features = build_features(fixture_rows(), horizon_bars=5, round_trip_cost_bps=0)
    subset = features.copy()
    pred = subset["target_net_return"].to_numpy()
    prob = np.clip(0.5 + pred, 0, 1)
    metrics = evaluate_ranked(subset, pred, prob, top_k=2, decision_time="10:00")
    assert metrics["trades"] == metrics["test_days"] * 2
    assert metrics["unique_traded_underlyings"] <= 4
    assert metrics["median_daily_spearman"] > 0.99
