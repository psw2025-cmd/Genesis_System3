"""Contracts, planning, safety, and storage helpers for options research."""
from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Iterator, Sequence

import pandas as pd

REQUIRED_DATA = ["open", "high", "low", "close", "iv", "volume", "strike", "oi", "spot"]
TRUTHY = {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Underlying:
    symbol: str
    security_id: str
    instrument: str
    exchange_segment: str = "NSE_FNO"


@dataclass(frozen=True)
class RollingRequest:
    underlying: Underlying
    from_date: date
    to_date: date
    expiry_flag: str
    expiry_code: int
    strike: str
    option_type: str
    interval: str

    @property
    def key(self) -> str:
        raw = "|".join([
            self.underlying.exchange_segment, self.underlying.symbol, self.underlying.security_id,
            self.underlying.instrument, self.from_date.isoformat(), self.to_date.isoformat(),
            self.expiry_flag, str(self.expiry_code), self.strike, self.option_type, self.interval,
        ])
        return hashlib.sha256(raw.encode()).hexdigest()

    def payload(self) -> dict:
        return {
            "exchangeSegment": self.underlying.exchange_segment,
            "interval": self.interval,
            "securityId": int(self.underlying.security_id),
            "instrument": self.underlying.instrument,
            "expiryFlag": self.expiry_flag,
            "expiryCode": self.expiry_code,
            "strike": self.strike,
            "drvOptionType": self.option_type,
            "requiredData": REQUIRED_DATA,
            "fromDate": self.from_date.isoformat(),
            "toDate": self.to_date.isoformat(),
        }


def ensure_analyzer_only() -> None:
    for name in ("LIVE_TRADING_ENABLED", "SYSTEM3_LIVE_TRADING_ALLOWED"):
        if str(os.getenv(name, "0")).strip().lower() in TRUTHY:
            raise RuntimeError(f"{name} must remain disabled")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def month_chunks(start: date, end: date, days: int = 30) -> Iterator[tuple[date, date]]:
    current = start
    while current < end:
        following = min(end, current + timedelta(days=days))
        yield current, following
        current = following


def relative_strikes(instrument: str, expiry_code: int = 0) -> list[str]:
    width = 10 if instrument == "OPTIDX" and expiry_code == 0 else 3
    values = ["ATM"]
    for step in range(1, width + 1):
        values.extend([f"ATM+{step}", f"ATM-{step}"])
    return values


def build_plan(
    universe: Sequence[Underlying], start: date, end: date, interval: str = "1",
    expiry_codes: Sequence[int] = (0, 1, 2),
) -> list[RollingRequest]:
    plan: list[RollingRequest] = []
    for underlying in universe:
        flags = ("WEEK", "MONTH") if underlying.instrument == "OPTIDX" else ("MONTH",)
        for chunk_start, chunk_end in month_chunks(start, end):
            for flag in flags:
                for expiry_code in expiry_codes:
                    for strike in relative_strikes(underlying.instrument, expiry_code):
                        for side in ("CALL", "PUT"):
                            plan.append(RollingRequest(
                                underlying, chunk_start, chunk_end, flag, expiry_code, strike, side, interval,
                            ))
    return plan


def flatten_rolling_response(request: RollingRequest, payload: dict) -> pd.DataFrame:
    side = "ce" if request.option_type == "CALL" else "pe"
    series = (payload.get("data") or {}).get(side) or {}
    rows: list[dict] = []
    for index, timestamp in enumerate(series.get("timestamp") or []):
        row = {
            "timestamp": int(timestamp),
            "underlying": request.underlying.symbol,
            "security_id": request.underlying.security_id,
            "instrument": request.underlying.instrument,
            "exchange_segment": request.underlying.exchange_segment,
            "expiry_flag": request.expiry_flag,
            "expiry_code": request.expiry_code,
            "strike_offset": request.strike,
            "option_type": request.option_type,
            "interval_min": int(request.interval),
        }
        for field in REQUIRED_DATA:
            values = series.get(field) or []
            row[field] = values[index] if index < len(values) else None
        rows.append(row)
    return pd.DataFrame(rows)


def write_frame(frame: pd.DataFrame, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        frame.to_parquet(path, index=False, compression="zstd")
        return path
    except (ImportError, ValueError):
        fallback = path.with_suffix(".csv.gz")
        frame.to_csv(fallback, index=False, compression="gzip")
        return fallback
