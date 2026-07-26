"""Normalize NSE options and generate leakage-safe next-session execution targets."""
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
MIN_PREMIUM = 10.0
MIN_VOLUME = 100.0
MIN_OI = 500.0
MIN_DAYS_TO_EXPIRY = 2.0
MAX_DAYS_TO_EXPIRY = 45.0
STOP_LOSS_PCT = 0.30
TAKE_PROFIT_PCT = 0.60


def pick(columns: Iterable[str], *candidates: str) -> str | None:
    mapping = {str(column).lower(): str(column) for column in columns}
    return next((mapping[c.lower()] for c in candidates if c.lower() in mapping), None)


def file_trade_date(path: Path) -> pd.Timestamp:
    match = re.search(r"(20\d{6})", path.name)
    if not match:
        raise ValueError(f"date not found in {path.name}")
    return pd.Timestamp(datetime.strptime(match.group(1), "%Y%m%d").date())


def parse_mixed_dates(series: pd.Series) -> pd.Series:
    """Parse ISO dates first and legacy NSE DD-MON-YYYY dates second."""
    raw = series.astype("string").fillna("").str.strip()
    parsed = pd.to_datetime(raw, format="%Y-%m-%d", errors="coerce")
    remaining = parsed.isna()
    if remaining.any():
        parsed.loc[remaining] = pd.to_datetime(raw.loc[remaining], format="%d-%b-%Y", errors="coerce")
    remaining = parsed.isna()
    if remaining.any():
        parsed.loc[remaining] = pd.to_datetime(raw.loc[remaining], errors="coerce", dayfirst=True)
    return parsed


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
    instrument = out["instrument"].astype("string").fillna("").str.upper().str.strip()
    side = out["option_type"].astype("string").fillna("").str.upper().str.strip()
    mask = side.isin({"CE", "PE", "CALL", "PUT"}) | instrument.isin({"IDO", "STO", "OPTIDX", "OPTSTK"})
    raw_option_rows = int(mask.sum())
    out = out.loc[mask].copy()
    out["instrument"] = instrument.loc[mask].replace({"IDO": "OPTIDX", "STO": "OPTSTK"})
    out["option_type"] = side.loc[mask].replace({"CALL": "CE", "PUT": "PE"})
    out["symbol"] = out["symbol"].astype("string").fillna("").str.upper().str.strip()
    out["expiry"] = parse_mixed_dates(out["expiry"]).dt.normalize()
    for column in ["strike", "open", "high", "low", "close", "settle", "underlying_price", "volume", "oi", "change_oi"]:
        out[column] = pd.to_numeric(out[column], errors="coerce") if column in out else np.nan
    if names["trade_date"]:
        out["trade_date"] = parse_mixed_dates(out["trade_date"]).dt.normalize()
    else:
        out["trade_date"] = file_trade_date(path)
    out["trade_date"] = out["trade_date"].fillna(file_trade_date(path))
    out = out.dropna(subset=["symbol", "expiry", "strike", "option_type", "open", "high", "low", "close"])
    out = out[(out["symbol"] != "") & (out["close"] > 0) & (out[["open", "high", "low"]] >= 0).all(axis=1)]

    traded = out["volume"].fillna(0) > 0
    complete_positive = (out[["open", "high", "low", "close"]] > 0).all(axis=1)
    valid_ordering = (
        (out["high"] >= out[["open", "close", "low"]].max(axis=1))
        & (out["low"] <= out[["open", "close", "high"]].min(axis=1))
    )
    invalid_traded = traded & ~(complete_positive & valid_ordering)
    no_trade_rows = int((~traded).sum())
    invalid_traded_rows = int(invalid_traded.sum())
    out = out.loc[~invalid_traded].copy()
    out = out.sort_values(KEY_COLUMNS).drop_duplicates(KEY_COLUMNS, keep="last").reset_index(drop=True)
    out.attrs.update({
        "raw_option_rows": raw_option_rows,
        "normalized_option_rows": int(len(out)),
        "no_trade_option_rows": no_trade_rows,
        "quarantined_invalid_traded_option_rows": invalid_traded_rows,
    })
    return out


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
    lag_features = ["prev_close_return", "prev_volume_change", "prev_oi_change", "underlying_return"]
    for column in lag_features:
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
    out = out.replace([np.inf, -np.inf], np.nan)
    out[lag_features] = out[lag_features].fillna(0.0).clip(lower=-10.0, upper=10.0)
    out["moneyness_pct"] = out["moneyness_pct"].fillna(0.0).clip(lower=-5.0, upper=5.0)
    return out


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
        stats["raw_option_rows"] += int(current_raw.attrs.get("raw_option_rows", len(current_raw)))
        stats["input_option_rows"] += len(current_raw)
        stats["no_trade_option_rows"] += int(current_raw.attrs.get("no_trade_option_rows", 0))
        stats["quarantined_invalid_traded_option_rows"] += int(
            current_raw.attrs.get("quarantined_invalid_traded_option_rows", 0)
        )
        if prior_enriched is not None:
            next_values = current_raw[KEY_COLUMNS + ["open", "high", "low", "close", "volume"]].rename(columns={
                "open": "next_open", "high": "next_high", "low": "next_low",
                "close": "next_close", "volume": "next_volume",
            })
            matched = prior_enriched.merge(next_values, on=KEY_COLUMNS, how="left", validate="one_to_one")
            next_contract = matched["next_close"].notna()
            valid_next_prices = matched[["next_open", "next_high", "next_low", "next_close"]].fillna(0).gt(0).all(axis=1)
            fillable = next_contract & valid_next_prices & matched["next_volume"].fillna(0).gt(0)
            entry = matched["next_open"]
            stop = entry * (1.0 - STOP_LOSS_PCT)
            target = entry * (1.0 + TAKE_PROFIT_PCT)
            exit_price = np.where(
                matched["next_low"].le(stop),
                stop,
                np.where(matched["next_high"].ge(target), target, matched["next_close"]),
            )
            matched["target_fillable"] = fillable.astype(np.int8)
            matched["gross_return"] = np.where(fillable, exit_price / entry - 1.0, 0.0)
            matched["target_net_return"] = np.where(
                fillable, matched["gross_return"] - base_cost_bps / 10000.0, 0.0
            )
            matched["target_positive"] = (matched["target_net_return"] > 0).astype(np.int8)

            signal_liquid = (
                matched["close"].ge(MIN_PREMIUM)
                & matched["volume"].ge(MIN_VOLUME)
                & matched["oi"].ge(MIN_OI)
                & matched["days_to_expiry"].between(MIN_DAYS_TO_EXPIRY, MAX_DAYS_TO_EXPIRY)
            )
            candidate = matched.loc[signal_liquid].replace([np.inf, -np.inf], np.nan)
            tradable = candidate.dropna(subset=FEATURE_COLUMNS + ["close", "volume", "oi"])

            stats["prior_contract_rows"] += len(matched)
            stats["matched_next_contract_rows"] += int(next_contract.sum())
            stats["unmatched_next_contract_rows"] += int((~next_contract).sum())
            stats["signal_liquid_rows"] += int(signal_liquid.sum())
            stats["next_fillable_rows"] += int((signal_liquid & fillable).sum())
            stats["next_no_fill_rows"] += int((signal_liquid & ~fillable).sum())
            stats["tradable_feature_rows"] += len(tradable)
            stats["filtered_feature_rows"] += len(matched) - len(tradable)
            if not tradable.empty:
                trade_date = pd.Timestamp(tradable["trade_date"].iloc[0])
                output = feature_root / str(trade_date.year) / f"{trade_date:%Y%m%d}_features.parquet"
                output.parent.mkdir(parents=True, exist_ok=True)
                columns = KEY_COLUMNS + ["trade_date"] + FEATURE_COLUMNS + [
                    "gross_return", "target_net_return", "target_positive", "target_fillable",
                    "close", "volume", "oi",
                ]
                tradable[columns].to_parquet(output, index=False, compression="zstd")
                stats["feature_files"] += 1
        prior_raw, prior_enriched = current_raw, current_enriched
    return {
        **dict(stats),
        "base_cost_bps": base_cost_bps,
        "entry_rule": "NEXT_SESSION_OPEN",
        "stop_loss_pct": STOP_LOSS_PCT,
        "take_profit_pct": TAKE_PROFIT_PCT,
        "same_bar_stop_before_target": True,
        "minimum_premium": MIN_PREMIUM,
        "minimum_volume": MIN_VOLUME,
        "minimum_open_interest": MIN_OI,
        "minimum_days_to_expiry": MIN_DAYS_TO_EXPIRY,
        "maximum_days_to_expiry": MAX_DAYS_TO_EXPIRY,
        "future_fill_filter_used_for_candidate_selection": False,
    }
