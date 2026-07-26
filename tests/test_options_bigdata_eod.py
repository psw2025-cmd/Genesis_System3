from pathlib import Path

import numpy as np
import pandas as pd

from src.options_research.eod_features import FEATURE_COLUMNS, generate_features, normalize_options
from src.options_research.eod_model import evaluate, split_files


def udiff_day(day: str, close: float) -> pd.DataFrame:
    return pd.DataFrame({
        "TradDt": [day, day], "FinInstrmTp": ["STO", "IDF"],
        "TckrSymb": ["RELIANCE", "NIFTY"], "XpryDt": ["30-Jul-2026", "30-Jul-2026"],
        "StrkPric": [1500, 0], "OptnTp": ["CE", "XX"],
        "OpnPric": [close - 1, 25000], "HghPric": [close + 2, 25100],
        "LwPric": [close - 2, 24900], "ClsPric": [close, 25050],
        "SttlmPric": [close, 25050], "UndrlygPric": [1505, 25050],
        "OpnIntrst": [1000, 500], "ChngInOpnIntrst": [100, 10], "TtlTradgVol": [200, 100],
    })


def test_normalize_udiff_filters_futures(tmp_path: Path):
    path = tmp_path / "20260724_fo.parquet"
    result = normalize_options(udiff_day("2026-07-24", 100.0), path)
    assert len(result) == 1
    assert result.iloc[0]["instrument"] == "OPTSTK"
    assert result.iloc[0]["option_type"] == "CE"
    assert str(result.iloc[0]["trade_date"].date()) == "2026-07-24"


def test_normalize_legacy_schema(tmp_path: Path):
    path = tmp_path / "20200102_fo.parquet"
    frame = pd.DataFrame({
        "INSTRUMENT": ["OPTIDX"], "SYMBOL": ["NIFTY"], "EXPIRY_DT": ["30-JAN-2020"],
        "STRIKE_PR": [12000], "OPTION_TYP": ["PE"], "OPEN": [100], "HIGH": [110],
        "LOW": [90], "CLOSE": [105], "SETTLE_PR": [105], "CONTRACTS": [1000],
        "OPEN_INT": [5000], "CHG_IN_OI": [200], "TIMESTAMP": ["02-JAN-2020"],
    })
    result = normalize_options(frame, path)
    assert len(result) == 1
    assert result.iloc[0]["instrument"] == "OPTIDX"
    assert result.iloc[0]["option_type"] == "PE"
    assert str(result.iloc[0]["trade_date"].date()) == "2020-01-02"


def test_generate_features_uses_next_open_and_conservative_exit(tmp_path: Path):
    data_root = tmp_path / "data"
    feature_root = tmp_path / "features"
    year = data_root / "nse_fo_eod" / "2026"
    year.mkdir(parents=True)
    for day, close in [("2026-07-22", 100.0), ("2026-07-23", 110.0), ("2026-07-24", 121.0)]:
        pd.DataFrame(udiff_day(day, close)).to_parquet(year / f"{day.replace('-', '')}_fo.parquet", index=False)
    stats = generate_features(data_root, feature_root, base_cost_bps=0)
    files = sorted(feature_root.glob("**/*.parquet"))
    assert stats["archive_files"] == 3
    assert stats["feature_files"] == 2
    assert stats["entry_rule"] == "NEXT_SESSION_OPEN"
    assert stats["future_fill_filter_used_for_candidate_selection"] is False
    first = pd.read_parquet(files[0])
    assert len(first) == 1
    expected = 110.0 / 109.0 - 1.0
    assert abs(first.iloc[0]["gross_return"] - expected) < 1e-12
    assert first.iloc[0]["target_fillable"] == 1
    assert set(FEATURE_COLUMNS).issubset(first.columns)


def test_generate_features_keeps_signal_but_marks_next_session_no_fill(tmp_path: Path):
    data_root = tmp_path / "data"
    feature_root = tmp_path / "features"
    year = data_root / "nse_fo_eod" / "2026"
    year.mkdir(parents=True)
    first = udiff_day("2026-07-22", 100.0)
    second = udiff_day("2026-07-23", 110.0)
    second.loc[0, "TtlTradgVol"] = 0
    first.to_parquet(year / "20260722_fo.parquet", index=False)
    second.to_parquet(year / "20260723_fo.parquet", index=False)
    stats = generate_features(data_root, feature_root, base_cost_bps=80)
    feature = pd.read_parquet(next(feature_root.glob("**/*.parquet")))
    assert len(feature) == 1
    assert feature.iloc[0]["target_fillable"] == 0
    assert feature.iloc[0]["gross_return"] == 0
    assert feature.iloc[0]["target_net_return"] == 0
    assert stats["next_no_fill_rows"] == 1


def make_feature_file(path: Path, day: str, symbols=("AAA", "BBB", "CCC")):
    rows = []
    for index, symbol in enumerate(symbols):
        row = {column: 0.01 * (index + 1) for column in FEATURE_COLUMNS}
        row.update({
            "symbol": symbol, "expiry": pd.Timestamp("2027-01-01"), "strike": 100 + index,
            "option_type": "CE", "instrument": "OPTSTK", "trade_date": pd.Timestamp(day),
            "gross_return": 0.02 * (index + 1), "target_net_return": 0.02 * (index + 1) - 0.008,
            "target_positive": 1, "target_fillable": 1,
            "close": 10, "volume": 100, "oi": 1000,
        })
        rows.append(row)
    pd.DataFrame(rows).to_parquet(path, index=False)


def test_split_has_one_day_embargo(tmp_path: Path):
    root = tmp_path / "features"
    root.mkdir()
    dates = pd.bdate_range("2026-01-01", periods=40)
    for day in dates:
        make_feature_file(root / f"{day:%Y%m%d}_features.parquet", str(day.date()))
    train, valid, test, split = split_files(root, embargo_days=1)
    assert len(train) == split.train_days
    assert len(valid) == split.validation_days
    assert len(test) == split.test_days
    assert pd.Timestamp(split.validation_start) > pd.Timestamp(split.train_end)
    assert pd.Timestamp(split.test_start) > pd.Timestamp(split.validation_end)


class IdentityScaler:
    def transform(self, values):
        return values


class FirstFeatureRegressor:
    def predict(self, values):
        return values[:, 0]


class FixedClassifier:
    def predict_proba(self, values):
        probability = np.clip(0.5 + values[:, 0], 0, 1)
        return np.column_stack([1 - probability, probability])


def test_evaluate_selects_distinct_underlyings(tmp_path: Path):
    path = tmp_path / "20260102_features.parquet"
    make_feature_file(path, "2026-01-02")
    result = evaluate([path], IdentityScaler(), FirstFeatureRegressor(), FixedClassifier(), top_k=2, costs=[80.0])
    assert result["days"] == 1
    assert result["trades"] == 2
    assert result["distinct_traded_symbols"] == 2
