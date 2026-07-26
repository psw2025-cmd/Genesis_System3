#!/usr/bin/env python3
"""Stream-profile every NSE F&O Parquet partition with bounded memory.

Only required columns are read from each partition. Arrow strings, dictionary
columns and pandas categoricals are normalized before missing-value handling.
Every file error is preserved in the output and makes the command fail.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq

from scripts.profile_options_dataset import pick


CANDIDATES = {
    "instrument": ["FinInstrmTp", "INSTRUMENT", "Instrument", "instrument"],
    "symbol": ["TckrSymb", "SYMBOL", "Symbol", "symbol", "underlying"],
    "option_type": ["OptnTp", "OptTp", "OPTION_TYP", "OptionType", "option_type"],
    "expiry": ["XpryDt", "EXPIRY_DT", "Expiry", "expiry", "expiry_date"],
    "strike": ["StrkPric", "STRIKE_PR", "Strike", "strike"],
    "volume": ["TtlTradgVol", "CONTRACTS", "Volume", "volume"],
    "oi": ["OpnIntrst", "OPEN_INT", "OI", "oi"],
    "trade_date": ["TradDt", "TIMESTAMP", "timestamp", "trade_date"],
}


def safe_text(series: pd.Series) -> pd.Series:
    return series.astype("string").fillna("").str.strip()


def add_counts(target: Counter[str], series: pd.Series) -> None:
    values = safe_text(series).replace("", "<EMPTY>")
    target.update({str(key): int(value) for key, value in values.value_counts(dropna=False).items()})


def selected_columns(path: Path) -> dict[str, str | None]:
    names = list(pq.ParquetFile(path).schema_arrow.names)
    return {name: pick(names, candidates) for name, candidates in CANDIDATES.items()}


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
    file_errors: list[dict[str, str]] = []
    peak_partition_rows = 0
    columns_read_total = 0

    for path in files:
        try:
            mapping = selected_columns(path)
            columns = sorted({column for column in mapping.values() if column})
            frame = pd.read_parquet(path, columns=columns)
            columns_read_total += len(columns)
            peak_partition_rows = max(peak_partition_rows, len(frame))

            instrument_col = mapping["instrument"]
            symbol_col = mapping["symbol"]
            option_col = mapping["option_type"]
            expiry_col = mapping["expiry"]
            strike_col = mapping["strike"]
            volume_col = mapping["volume"]
            oi_col = mapping["oi"]
            date_col = mapping["trade_date"]

            instrument = (
                safe_text(frame[instrument_col]).str.upper()
                if instrument_col else pd.Series("", index=frame.index, dtype="string")
            )
            option_values = (
                safe_text(frame[option_col]).str.upper()
                if option_col else pd.Series("", index=frame.index, dtype="string")
            )
            option_mask = (
                option_values.isin({"CE", "PE", "CALL", "PUT"})
                | instrument.str.contains("OPT", regex=False, na=False)
                | instrument.isin({"IDO", "STO"})
            )
            index_mask = option_mask & (
                instrument.str.contains("IDX", regex=False, na=False)
                | instrument.str.contains("INDEX", regex=False, na=False)
                | instrument.isin({"IDO"})
            )
            stock_mask = option_mask & (
                instrument.str.contains("STK", regex=False, na=False)
                | instrument.str.contains("STOCK", regex=False, na=False)
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
                option_symbols.update(value for value in safe_text(frame.loc[option_mask, symbol_col]) if value)
            if expiry_col:
                expiries.update(value for value in safe_text(frame.loc[option_mask, expiry_col]) if value)
            if strike_col:
                strikes.update(
                    pd.to_numeric(frame.loc[option_mask, strike_col], errors="coerce").dropna().astype(float)
                )
            if volume_col:
                positive_volume_rows += int((pd.to_numeric(frame[volume_col], errors="coerce") > 0).sum())
            if oi_col:
                positive_oi_rows += int((pd.to_numeric(frame[oi_col], errors="coerce") > 0).sum())
            if date_col and not frame.empty:
                date_text = safe_text(frame[date_col])
                if not date_text.empty:
                    date_values.extend([str(date_text.min()), str(date_text.max())])
        except Exception as exc:
            file_errors.append({
                "path": str(path),
                "error": f"{type(exc).__name__}: {exc}",
            })

    result = {
        "status": "PASS" if not file_errors else "FAIL",
        "files": len(files),
        "files_profiled": len(files) - len(file_errors),
        "file_errors": len(file_errors),
        "file_error_samples": file_errors[:50],
        "bytes": total_bytes,
        "rows": total_rows,
        "option_rows": option_rows,
        "index_option_rows": index_rows,
        "stock_option_rows": stock_rows,
        "futures_rows": futures_rows,
        "unclassified_option_rows": unclassified_rows,
        "distinct_option_symbols": len(option_symbols),
        "distinct_expiries": len(expiries),
        "distinct_strikes": len(strikes),
        "positive_volume_rows": positive_volume_rows,
        "positive_oi_rows": positive_oi_rows,
        "instrument_counts": dict(instrument_counts.most_common()),
        "option_type_counts": dict(option_type_counts.most_common()),
        "date_min": min(date_values) if date_values else None,
        "date_max": max(date_values) if date_values else None,
        "yearly": dict(sorted(yearly.items())),
        "peak_partition_rows": peak_partition_rows,
        "average_columns_read_per_file": columns_read_total / len(files) if files else 0.0,
        "all_columns_loaded": False,
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = profile_archive(args.data_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
