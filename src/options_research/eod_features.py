"""Normalize legacy/UDiFF NSE option files and generate future-return features."""
from __future__ import annotations

import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

FEATURE_COLUMNS = [
    "open_close_return", "range_pct", "settle_gap_pct", "log_volume", "log_oi",
    "oi_change_ratio", "moneyness_pct", "days_to_expiry", "sqrt_days_to_expiry",
    "prev_close_return", "prev_volume_change", "prev_oi_change", "underlying_return",
    "option_is_call", "instrument_is_index", "weekday_sin", "weekday_cos",
    "month_sin", "month_cos",
]
KEY_COLUMNS = ["symbol", "expiry", "strike", "option_type", "instrument"]


def pick(columns: Iterable[str], *candidates: str) -> str | None:
    mapping = {str(column).lower(): str(column) for column in columns}
    return next((mapping[c.lower()] for c in candidates if c.lower() in mapping), None)


def file_trade_date(path: Path) -> pd.Timestamp:
    match = re.search(r"(20\d{6})", path.name)
    if not match:
        raise ValueError(f"date not found in {path.name}")
    return pd.Timestamp(datetime.strptime(match.group(1), "%Y%m%d").date())


def normalize_options(frame: pd.DataFrame, path: Path) -> pd.DataFrame:
    cols = list(frame.columns)
    names = {
        "instrument": pick(cols, "FinInstrmTp", "INSTRUMENT"),
        "symbol": pick(cols, "TckrSymb", "SYMBOL"),
        "expiry": pick(cols, "XpryDt", "EXPIRY_DT"),
        "strike": pick(cols, "StrkPric", "STRIKE_PR"),
        "option_type": pick(cols, "OptnTp", "OPTION_TYP"),
        "open": pick(cols, "OpnPric", "OPEN"),
        "high": pick(cols, "HghPric", "HIGH"),
        "low": pick(cols, "LwPric", "LOW"),
        "close": pick(cols, "ClsPric", "CLOSE"),
        "settle": pick(cols, "SttlmPric", "SETTLE_PR"),
        "underlying_price": pick(cols, "UndrlygPric"),
        "volume": pick(cols, "TtlTradgVol", "CONTRACTS"),
        "oi": pick(cols, "OpnIntrst", "OPEN_INT"),
        "change_oi": pick(cols, "ChngInOpnIntrst", "CHG_IN_OI"),
        "trade_date": pick(cols, "TradDt", "TIMESTAMP"),
    }
    mandatory = ["instrument", "symbol", "expiry", "strike", "option_type", "open", "high", "low", "close", "volume", "oi"]
    missing = [name for name in mandatory if not names[name]]
    if missing:
        raise ValueError(f"{path.name} missing normalized columns {missing}")
    out = pd.DataFrame(index=frame.index)
    for name, column in names.items():
        if column:
            out[name] = frame[column]
    instrument = out["instrument"].fillna("").astype(str).str.upper().str.strip()
    side = out["option_type"].fillna("").astype(str).str.upper().str.strip()
    mask = side.isin({"CE", "PE", "CALL", "PUT"}) | instrument.isin({"IDO", "STO", "OPTIDX", "OPTSTK"})
    out = out.loc[mask].copy()
    out["instrument"] = instrument.loc[mask].replace({"IDO": "OPTIDX", "STO": "OPTSTK"})
    out["option_type"] = side.loc[mask].replace({"CALL": "CE", "PUT": "PE"})
    out["symbol"] = out["symbol"].fillna("").astype(str).str.upper().str.strip()
    out["expiry"] = pd.to_datetime(out["expiry"], errors="coerce", dayfirst=True).dt.normalize()
    for column in ["strike", "open", "high", "low", "close", "settle", "underlying_price", "volume", "oi", "change_oi"]:
        out[column] = pd.to_numeric(out[column], errors="coerce") if column in out else np.nan
    if names["trade_date"]:
        out["trade_date"] = pd.to_datetime(out["trade_date"], errors="coerce", dayfirst=True).dt.normalize()
    else:
        out["trade_date"] = file_trade_date(path)
    out["trade_date"] = out["trade_date"].fillna(file_trade_date(path))
    out = out.dropna(subset=["symbol", "expiry", "strike", "option_type", "open", "high", "low", "close"])
    out = out[(out["symbol"] != "") & (out["close"] > 0) & (out[["open", "high", "low"]] >= 0).all(axis=1)]
    return out.sort_values(KEY_COLUMNS).drop_duplicates(KEY_COLUMNS, keep="last").reset_index(drop=True)


def enrich_day(day: pd.DataFrame, prior: pd.DataFrame | None) -> pd.DataFrame:
    out = day.copy()
    out["open_close_return"] = out["close"] / out["open"].replace(0, np.nan) - 1
    out["range_pct"] = (out["high"] - out["low"]) / out["open"].replace(0, np.nan)
    out["settle_gap_pct"] = out["settle"].fillna(out["close"]) / out["close"] - 1
    out["log_volume"] = np.log1p(out["volume"].clip(lower=0))
    out["log_oi"] = np.log1p(out["oi"].clip(lower=0))
    out["oi_change_ratio"] = out["change_oi"].fillna(0) / out["oi"].replace(0, np.nan)
    out["moneyness_pct"] = np.where(
        out["underlying_price"].gt(0),
        np.where(out["option_type"] == "CE", (out["underlying_price"] - out["strike"]) / out["underlying_price"], (out["strike"] - out["underlying_price"]) / out["underlying_price"]),
        0.0,
    )
    out["days_to_expiry"] = (out["expiry"] - out["trade_date"]).dt.days.astype(float)
    out["sqrt_days_to_expiry"] = np.sqrt(out["days_to_expiry"].clip(lower=0))
    out["option_is_call"] = (out["option_type"] == "CE").astype(float)
    out["instrument_is_index"] = (out["instrument"] == "OPTIDX").astype(float)
    weekday, month = out["trade_date"].dt.weekday, out["trade_date"].dt.month
    out["weekday_sin"], out["weekday_cos"] = np.sin(2 * np.pi * weekday / 7), np.cos(2 * np.pi * weekday / 7)
    out["month_sin"], out["month_cos"] = np.sin(2 * np.pi * month / 12), np.cos(2 * np.pi * month / 12)
    for column in ["prev_close_return", "prev_volume_change", "prev_oi_change", "underlying_return"]:
        out[column] = 0.0
    if prior is not None and not prior.empty:
        lag = prior[KEY_COLUMNS + ["close", "volume", "oi", "underlying_price"]].rename(columns={
            "close": "lag_close", "volume": "lag_volume", "oi": "lag_oi", "underlying_price": "lag_underlying_price",
        })
        out = out.merge(lag, on=KEY_COLUMNS, how="left", validate="one_to_one")
        out["prev_close_return"] = out["close"] / out["lag_close"].replace(0, np.nan) - 1
        out["prev_volume_change"] = out["volume"] / out["lag_volume"].replace(0, np.nan) - 1
        out["prev_oi_change"] = out["oi"] / out["lag_oi"].replace(0, np.nan) - 1
        out["underlying_return"] = out["underlying_price"] / out["lag_underlying_price"].replace(0, np.nan) - 1
    return out.replace([np.inf, -np.inf], np.nan)


def generate_features(data_root: Path, feature_root: Path, base_cost_bps: float) -> dict:
    files = sorted(data_root.glob("nse_fo_eod/**/*.parquet"), key=file_trade_date)
    if len(files) < 3:
        raise ValueError("at least 3 archive sessions required")
    prior_raw = prior_enriched = None
    stats: Counter[str] = Counter()
    for path in files:
        current_raw = normalize_options(pd.read_parquet(path), path)
        current_enriched = enrich_day(current_raw, prior_raw)
        stats["archive_files"] += 1
        stats["input_option_rows"] += len(current_raw)
        if prior_enriched is not None:
            next_values = current_raw[KEY_COLUMNS + ["close", "volume"]].rename(columns={"close": "next_close", "volume": "next_volume"})
            matched = prior_enriched.merge(next_values, on=KEY_COLUMNS, how="inner", validate="one_to_one")
            stats["matched_contract_rows"] += len(matched)
            matched["gross_return"] = matched["next_close"] / matched["close"] - 1
            matched["target_net_return"] = matched["gross_return"] - base_cost_bps / 10000.0
            matched["target_positive"] = (matched["target_net_return"] > 0).astype(np.int8)
            tradable = matched[
                (matched["close"] > 1) & (matched["next_close"] > 0) & (matched["volume"] > 0)
                & (matched["next_volume"] > 0) & (matched["oi"] > 0) & (matched["days_to_expiry"] >= 1)
            ].replace([np.inf, -np.inf], np.nan).dropna(subset=FEATURE_COLUMNS + ["gross_return", "target_net_return"])
            stats["tradable_feature_rows"] += len(tradable)
            stats["filtered_feature_rows"] += len(matched) - len(tradable)
            if not tradable.empty:
                trade_date = pd.Timestamp(tradable["trade_date"].iloc[0])
                output = feature_root / str(trade_date.year) / f"{trade_date:%Y%m%d}_features.parquet"
                output.parent.mkdir(parents=True, exist_ok=True)
                columns = KEY_COLUMNS + ["trade_date"] + FEATURE_COLUMNS + ["gross_return", "target_net_return", "target_positive", "close", "volume", "oi"]
                tradable[columns].to_parquet(output, index=False, compression="zstd")
                stats["feature_files"] += 1
        prior_raw, prior_enriched = current_raw, current_enriched
    return {**dict(stats), "base_cost_bps": base_cost_bps}
