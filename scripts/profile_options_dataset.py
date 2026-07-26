#!/usr/bin/env python3
"""Profile NSE/Dhan option datasets into deterministic numerical JSON proof."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def pick(columns: list[str], candidates: list[str]) -> str | None:
    exact = {column.lower(): column for column in columns}
    for candidate in candidates:
        if candidate.lower() in exact:
            return exact[candidate.lower()]
    return None


def counts(series: pd.Series, limit: int = 50) -> dict[str, int]:
    values = series.fillna("<NULL>").astype(str).str.strip().replace("", "<EMPTY>")
    return {str(key): int(value) for key, value in values.value_counts(dropna=False).head(limit).items()}


def profile_frame(frame: pd.DataFrame) -> dict:
    columns = list(frame.columns)
    instrument_col = pick(columns, ["FinInstrmTp", "INSTRUMENT", "Instrument", "instrument"])
    symbol_col = pick(columns, ["TckrSymb", "SYMBOL", "Symbol", "symbol", "underlying"])
    option_col = pick(columns, ["OptnTp", "OptTp", "OPTION_TYP", "OptionType", "option_type"])
    expiry_col = pick(columns, ["XpryDt", "EXPIRY_DT", "Expiry", "expiry", "expiry_date"])
    strike_col = pick(columns, ["StrkPric", "STRIKE_PR", "Strike", "strike"])
    volume_col = pick(columns, ["TtlTradgVol", "CONTRACTS", "Volume", "volume"])
    oi_col = pick(columns, ["OpnIntrst", "OPEN_INT", "OI", "oi"])
    date_col = pick(columns, ["TradDt", "TIMESTAMP", "timestamp", "trade_date"])

    option_mask = pd.Series(False, index=frame.index)
    if option_col:
        option_values = frame[option_col].fillna("").astype(str).str.upper().str.strip()
        option_mask = option_values.isin({"CE", "PE", "CALL", "PUT"})
    instrument_values = frame[instrument_col].fillna("").astype(str).str.upper().str.strip() if instrument_col else pd.Series("", index=frame.index)
    option_mask = option_mask | instrument_values.str.contains("OPT", regex=False) | instrument_values.isin({"IDO", "STO"})
    index_option_mask = option_mask & (instrument_values.str.contains("IDX", regex=False) | instrument_values.str.contains("INDEX", regex=False) | instrument_values.isin({"IDO"}))
    stock_option_mask = option_mask & (instrument_values.str.contains("STK", regex=False) | instrument_values.str.contains("STOCK", regex=False) | instrument_values.isin({"STO"}))

    result = {
        "rows": int(len(frame)),
        "columns": int(len(columns)),
        "column_names": columns,
        "detected_columns": {
            "instrument": instrument_col, "symbol": symbol_col, "option_type": option_col,
            "expiry": expiry_col, "strike": strike_col, "volume": volume_col,
            "open_interest": oi_col, "trade_date": date_col,
        },
        "option_rows": int(option_mask.sum()),
        "index_option_rows": int(index_option_mask.sum()),
        "stock_option_rows": int(stock_option_mask.sum()),
        "unclassified_option_rows": int((option_mask & ~index_option_mask & ~stock_option_mask).sum()),
        "instrument_counts": counts(frame[instrument_col]) if instrument_col else {},
        "option_type_counts": counts(frame.loc[option_mask, option_col]) if option_col else {},
        "distinct_symbols": int(frame[symbol_col].nunique(dropna=True)) if symbol_col else None,
        "distinct_option_symbols": int(frame.loc[option_mask, symbol_col].nunique(dropna=True)) if symbol_col else None,
        "top_option_symbols_by_rows": counts(frame.loc[option_mask, symbol_col], 25) if symbol_col else {},
        "distinct_expiries": int(frame.loc[option_mask, expiry_col].nunique(dropna=True)) if expiry_col else None,
        "distinct_strikes": int(pd.to_numeric(frame.loc[option_mask, strike_col], errors="coerce").nunique(dropna=True)) if strike_col else None,
        "positive_volume_rows": int((pd.to_numeric(frame[volume_col], errors="coerce") > 0).sum()) if volume_col else None,
        "positive_oi_rows": int((pd.to_numeric(frame[oi_col], errors="coerce") > 0).sum()) if oi_col else None,
        "date_min": str(frame[date_col].min()) if date_col else None,
        "date_max": str(frame[date_col].max()) if date_col else None,
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.input.suffix == ".parquet":
        frame = pd.read_parquet(args.input)
    else:
        frame = pd.read_csv(args.input, low_memory=False)
    result = profile_frame(frame)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
