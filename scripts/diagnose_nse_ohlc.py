#!/usr/bin/env python3
"""Print exact traded NSE rows whose OHLC ordering is inconsistent."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def pick(frame: pd.DataFrame, names: tuple[str, ...]) -> str:
    mapping = {str(column).lower(): str(column) for column in frame.columns}
    for name in names:
        if name.lower() in mapping:
            return mapping[name.lower()]
    raise KeyError(names)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    frame = pd.read_parquet(args.input)
    open_col = pick(frame, ("open", "OpnPric", "OPEN"))
    high_col = pick(frame, ("high", "HghPric", "HIGH"))
    low_col = pick(frame, ("low", "LwPric", "LOW"))
    close_col = pick(frame, ("close", "ClsPric", "CLOSE"))
    volume_col = pick(frame, ("volume", "TtlTradgVol", "CONTRACTS"))
    ohlc = frame[[open_col, high_col, low_col, close_col]].apply(pd.to_numeric, errors="coerce")
    ohlc.columns = ["open", "high", "low", "close"]
    volume = pd.to_numeric(frame[volume_col], errors="coerce").fillna(0)
    complete = (volume > 0) & ohlc.notna().all(axis=1) & (ohlc > 0).all(axis=1)
    invalid = complete & (
        (ohlc["high"] < ohlc[["open", "close", "low"]].max(axis=1))
        | (ohlc["low"] > ohlc[["open", "close", "high"]].min(axis=1))
    )
    columns = [
        name for name in (
            "TradDt", "FinInstrmTp", "TckrSymb", "XpryDt", "StrkPric", "OptnTp",
            open_col, high_col, low_col, close_col, volume_col, "OpnIntrst", "UndrlygPric",
        ) if name in frame.columns
    ]
    rows = frame.loc[invalid, columns].copy()
    payload = {
        "input": str(args.input),
        "rows": int(len(frame)),
        "traded_complete_rows": int(complete.sum()),
        "invalid_rows": int(invalid.sum()),
        "invalid_samples": rows.head(100).where(pd.notna(rows), None).to_dict(orient="records"),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
