import pandas as pd

from scripts.profile_options_dataset import profile_frame


def test_profile_counts_stock_and_index_options():
    frame = pd.DataFrame({
        "FinInstrmTp": ["OPTIDX", "OPTIDX", "OPTSTK", "FUTIDX"],
        "TckrSymb": ["NIFTY", "NIFTY", "RELIANCE", "NIFTY"],
        "OptnTp": ["CE", "PE", "CE", "XX"],
        "XpryDt": ["2026-07-30"] * 4,
        "StrkPric": [25000, 25000, 1500, 0],
        "TtlTradgVol": [10, 20, 30, 40],
        "OpnIntrst": [100, 200, 300, 400],
        "TradDt": ["2026-07-24"] * 4,
    })
    result = profile_frame(frame)
    assert result["rows"] == 4
    assert result["option_rows"] == 3
    assert result["index_option_rows"] == 2
    assert result["stock_option_rows"] == 1
    assert result["distinct_option_symbols"] == 2
    assert result["option_type_counts"] == {"CE": 2, "PE": 1}
