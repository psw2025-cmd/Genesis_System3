#!/usr/bin/env python3
"""Stream-profile every NSE F&O Parquet partition without loading the archive at once."""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import pandas as pd

from scripts.profile_options_dataset import pick


def add_counts(target: Counter[str], series: pd.Series) -> None:
    values = series.fillna("<NULL>").astype(str).str.strip().replace("", "<EMPTY>")
    target.update({str(key): int(value) for key, value in values.value_counts(dropna=False).items()})


def profile_archive(data_root: Path) -> dict:
    files = sorted(data_root.glob("nse_fo_eod/**/*.parquet"))
    if not files:
        raise FileNotFoundError(f"no NSE F&O parquet files under {data_root}")

    instrument_counts: Counter[str] = Counter()
    option_type_counts: Counter[str] = Counter()
    option_symbols: set[str] = set()
    expiries: set[str] = set()
    strikes: set[float] = set()
    yearly: dict[str, dict[str, int]] = {}
    total_rows = option_rows = index_rows = stock_rows = futures_rows = 0
    positive_volume_rows = positive_oi_rows = unclassified_rows = 0
    total_bytes = 0
    date_values: list[str] = []

    for path in files:
        frame = pd.read_parquet(path)
        columns = list(frame.columns)
        instrument_col = pick(columns, ["FinInstrmTp", "INSTRUMENT", "Instrument", "instrument"])
        symbol_col = pick(columns, ["TckrSymb", "SYMBOL", "Symbol", "symbol", "underlying"])
        option_col = pick(columns, ["OptnTp", "OptTp", "OPTION_TYP", "OptionType", "option_type"])
        expiry_col = pick(columns, ["XpryDt", "EXPIRY_DT", "Expiry", "expiry", "expiry_date"])
        strike_col = pick(columns, ["StrkPric", "STRIKE_PR", "Strike", "strike"])
        volume_col = pick(columns, ["TtlTradgVol", "CONTRACTS", "Volume", "volume"])
        oi_col = pick(columns, ["OpnIntrst", "OPEN_INT", "OI", "oi"])
        date_col = pick(columns, ["TradDt", "TIMESTAMP", "timestamp", "trade_date"])

        instrument = (
            frame[instrument_col].fillna("").astype(str).str.upper().str.strip()
            if instrument_col else pd.Series("", index=frame.index)
        )
        option_values = (
            frame[option_col].fillna("").astype(str).str.upper().str.strip()
            if option_col else pd.Series("", index=frame.index)
        )
        option_mask = (
            option_values.isin({"CE", "PE", "CALL", "PUT"})
            | instrument.str.contains("OPT", regex=False)
            | instrument.isin({"IDO", "STO"})
        )
        index_mask = option_mask & (
            instrument.str.contains("IDX", regex=False)
            | instrument.str.contains("INDEX", regex=False)
            | instrument.isin({"IDO"})
        )
        stock_mask = option_mask & (
            instrument.str.contains("STK", regex=False)
            | instrument.str.contains("STOCK", regex=False)
            | instrument.isin({"STO"})
        )
        future_mask = ~option_mask

        rows = len(frame)
        opts = int(option_mask.sum())
        idx = int(index_mask.sum())
        stk = int(stock_mask.sum())
        fut = int(future_mask.sum())
        unclassified = int((option_mask & ~index_mask & ~stock_mask).sum())
        year = path.parent.name if path.parent.name.isdigit() else "UNKNOWN"
        year_stat = yearly.setdefault(year, {"files": 0, "rows": 0, "option_rows": 0, "bytes": 0})
        year_stat["files"] += 1
        year_stat["rows"] += rows
        year_stat["option_rows"] += opts
        year_stat["bytes"] += path.stat().st_size

        total_rows += rows
        option_rows += opts
        index_rows += idx
        stock_rows += stk
        futures_rows += fut
        unclassified_rows += unclassified
        total_bytes += path.stat().st_size
        if instrument_col:
            add_counts(instrument_counts, frame[instrument_col])
        if option_col:
            add_counts(option_type_counts, frame.loc[option_mask, option_col])
        if symbol_col:
            option_symbols.update(frame.loc[option_mask, symbol_col].dropna().astype(str).str.strip())
        if expiry_col:
            expiries.update(frame.loc[option_mask, expiry_col].dropna().astype(str).str.strip())
        if strike_col:
            strikes.update(pd.to_numeric(frame.loc[option_mask, strike_col], errors="coerce").dropna().astype(float))
        if volume_col:
            positive_volume_rows += int((pd.to_numeric(frame[volume_col], errors="coerce") > 0).sum())
        if oi_col:
            positive_oi_rows += int((pd.to_numeric(frame[oi_col], errors="coerce") > 0).sum())
        if date_col and not frame.empty:
            date_values.extend([str(frame[date_col].min()), str(frame[date_col].max())])

    return {
        "files": len(files),
        "bytes": total_bytes,
        "rows": total_rows,
        "option_rows": option_rows,
        "index_option_rows": index_rows,
        "stock_option_rows": stock_rows,
        "futures_rows": futures_rows,
        "unclassified_option_rows": unclassified_rows,
        "distinct_option_symbols": len({value for value in option_symbols if value}),
        "distinct_expiries": len({value for value in expiries if value}),
        "distinct_strikes": len(strikes),
        "positive_volume_rows": positive_volume_rows,
        "positive_oi_rows": positive_oi_rows,
        "instrument_counts": dict(instrument_counts.most_common()),
        "option_type_counts": dict(option_type_counts.most_common()),
        "date_min": min(date_values) if date_values else None,
        "date_max": max(date_values) if date_values else None,
        "yearly": dict(sorted(yearly.items())),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = profile_archive(args.data_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
