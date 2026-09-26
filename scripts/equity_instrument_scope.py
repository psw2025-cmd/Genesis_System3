"""Prospective company/ETF identity checks from captured official NSE masters.

A current undated master cannot establish historical universe membership.
These receipts qualify classification only; they never qualify a forecast.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from io import StringIO
import json

EQUITY_URL = "https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv"
ETF_URL = "https://nsearchives.nseindia.com/content/equities/eq_etfseclist.csv"
VERSION = "nse-company-etf-snapshot-v1"


def _time(value: str) -> datetime:
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None or result.utcoffset() is None:
        raise ValueError("Require an explicit observation/issue timezone")
    return result.astimezone(timezone.utc)


def _read(raw: bytes, receipt: dict, url: str, columns: set[str]) -> list[dict]:
    if receipt.get("url") != url or receipt.get("raw_sha256") != sha256(raw).hexdigest():
        raise ValueError("Official source URL or exact raw hash mismatch")
    _time(receipt["first_observed_at"])
    reader = csv.DictReader(StringIO(raw.decode("utf-8-sig")))
    if not columns.issubset({x.strip() for x in (reader.fieldnames or [])}):
        raise ValueError("Unsupported master schema")
    rows = [{k.strip(): v.strip() for k, v in row.items()} for row in reader]
    if not rows:
        raise ValueError("Empty instrument master")
    return rows


@dataclass(frozen=True)
class InstrumentSnapshot:
    company_eq: frozenset[tuple[str, str]]
    other_company_series: frozenset[tuple[str, str]]
    etfs: frozenset[tuple[str, str]]
    available_at: datetime
    oldest_observation_at: datetime
    receipt_sha256: str

    def classify(self, symbol: str, isin: str, *, issued_at: str) -> str:
        issue = _time(issued_at)
        if issue < self.available_at:
            return "NOT_PROVEN_SOURCE_NOT_YET_OBSERVED"
        # An explicit operational freshness policy, not an exchange validity claim.
        if issue - self.oldest_observation_at > timedelta(hours=24):
            return "NOT_PROVEN_REFRESH_REQUIRED"
        key = (symbol.strip(), isin.strip())
        if key in self.etfs:
            return "ETF_EXCLUDED"
        if key in self.company_eq:
            return "COMPANY_EQ_IDENTITY_MATCHED"
        if key in self.other_company_series:
            return "COMPANY_NON_EQ_SERIES_EXCLUDED"
        return "NOT_PROVEN_UNKNOWN_IDENTITY"


def capture(equity_raw: bytes, etf_raw: bytes, *, equity_receipt: dict,
            etf_receipt: dict) -> InstrumentSnapshot:
    company = _read(equity_raw, equity_receipt, EQUITY_URL, {"SYMBOL", "ISIN NUMBER", "SERIES"})
    etfs = _read(etf_raw, etf_receipt, ETF_URL, {"Symbol", "ISINNumber"})
    groups = [set(), set(), set()]
    seen = set()
    for rows, symbol_key, isin_key, fixed_group in (
        (company, "SYMBOL", "ISIN NUMBER", None), (etfs, "Symbol", "ISINNumber", 2)
    ):
        for row in rows:
            key = (row[symbol_key], row[isin_key])
            if not all(key) or key in seen:
                raise ValueError("Missing, duplicate or conflicting instrument identity")
            seen.add(key)
            group = fixed_group if fixed_group is not None else (0 if row["SERIES"] == "EQ" else 1)
            groups[group].add(key)
    observed = [_time(x["first_observed_at"]) for x in (equity_receipt, etf_receipt)]
    # Bind both original receipts including capture times into an immutable digest.
    digest = sha256(json.dumps({"version": VERSION, "equity": equity_receipt, "etf": etf_receipt},
                              sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return InstrumentSnapshot(*(frozenset(x) for x in groups), max(observed), min(observed), digest)
