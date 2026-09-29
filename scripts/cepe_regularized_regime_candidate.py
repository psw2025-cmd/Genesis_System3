"""Frozen CEPE-NEXT-007 prior-only directional and rare-tail rankings.

The two logistic heads were fit on the 2024-09-27 through 2025-12-31
development block, selected on 2026-Q1, and must be committed before any
2026-Q2 outcome is opened.  Scores use only the two observations available at
the current session close.  They are rankings, not calibrated probabilities,
executable fills, recommendations, or authority to place an order.
"""
from __future__ import annotations

from collections import Counter
import csv
from datetime import date, datetime
from hashlib import sha256
from io import StringIO
from math import isfinite, log, log1p
from statistics import median
from typing import Any


VERSION = "regularized-regime-v3"
SELECTION_COUNT = 10
FEATURE_ORDER = (
    "premium_return",
    "intraday_momentum",
    "close_location",
    "volume",
    "transactions",
    "oi_change",
    "near_expiry",
    "lower_premium",
    "atm_proximity",
    "signed_moneyness",
    "signed_underlying_return",
    "volume_surprise",
    "turnover_per_contract",
    "oi_level",
)
HEADS = {
    "directional": {
        "intercept": -0.29962959274860024,
        "coefficients": {
            "premium_return": 0.3572764058773491,
            "intraday_momentum": 0.31674057376847264,
            "close_location": 0.0525726843914491,
            "volume": -0.09291907008231548,
            "transactions": 0.10584696900393065,
            "oi_change": 0.07691832673540601,
            "near_expiry": -0.29767090401872165,
            "lower_premium": -0.1679356756573878,
            "atm_proximity": 0.15415595629952533,
            "signed_moneyness": -0.10459986772484024,
            "signed_underlying_return": 0.09569600088749793,
            "volume_surprise": -0.01756607795592747,
            "turnover_per_contract": -0.1441899177876584,
            "oi_level": 0.11330736905541013,
        },
    },
    "rare_tail": {
        "intercept": -3.8741081745737356,
        "coefficients": {
            "premium_return": 0.5319846509427568,
            "intraday_momentum": -0.6234557746448749,
            "close_location": 2.0225197189414637,
            "volume": 0.6422895777269116,
            "transactions": 0.5506102879766136,
            "oi_change": -0.13614310781807298,
            "near_expiry": 3.354748770313934,
            "lower_premium": 1.6761165390325548,
            "atm_proximity": 1.532249499919177,
            "signed_moneyness": -3.527966620182274,
            "signed_underlying_return": 0.8289524920227197,
            "volume_surprise": 0.41334783574580414,
            "turnover_per_contract": 0.017473614523446312,
            "oi_level": -1.0154109074997577,
        },
    },
}


def _day(value: str) -> date:
    for pattern in ("%Y-%m-%d", "%d-%b-%Y", "%d-%b-%y", "%d/%m/%Y"):
        try:
            return datetime.strptime(value.strip(), pattern).date()
        except ValueError:
            pass
    raise ValueError("Unknown date format")


def _number(row: dict[str, str], field: str) -> float:
    try:
        value = float(row[field])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(field) from exc
    if not isfinite(value):
        raise ValueError(field)
    return value


def _identity(row: dict[str, Any]) -> tuple[str, str, str, str]:
    return (
        str(row["symbol"]).strip().upper(),
        str(row["expiry"]),
        format(float(row["strike"]), ".4f"),
        str(row["type"]).strip().upper(),
    )


def _percentile_ranks(values: list[float]) -> list[float]:
    size = len(values)
    if not size:
        return []
    order = sorted(range(size), key=lambda index: (values[index], index))
    result = [0.0] * size
    offset = 0
    while offset < size:
        end = offset + 1
        while end < size and values[order[end]] == values[order[offset]]:
            end += 1
        percentile = (((offset + 1) + end) / 2) / size
        for position in range(offset, end):
            result[order[position]] = percentile
        offset = end
    return result


def _snapshot(raw: bytes, trade_day: date) -> list[dict[str, str]]:
    try:
        reader = csv.DictReader(StringIO(raw.decode("utf-8-sig")))
    except UnicodeDecodeError as exc:
        raise ValueError("Bhavcopy is not UTF-8 CSV") from exc
    required = {
        "TradDt", "TckrSymb", "XpryDt", "StrkPric", "OptnTp", "OpnPric",
        "HghPric", "LwPric", "ClsPric", "PrvsClsgPric", "UndrlygPric",
        "OpnIntrst", "ChngInOpnIntrst", "TtlTradgVol", "TtlTrfVal",
        "TtlNbOfTxsExctd", "NewBrdLotQty",
    }
    if not required <= set(reader.fieldnames or ()):
        raise ValueError("Unsupported bhavcopy schema")
    rows: list[dict[str, str]] = []
    identities: set[tuple[str, str, str, str]] = set()
    for row in reader:
        if row.get("OptnTp") not in {"CE", "PE"}:
            continue
        if _day(row["TradDt"]) != trade_day:
            raise ValueError("Trade date differs from requested date")
        key = _identity(
            {
                "symbol": row["TckrSymb"],
                "expiry": _day(row["XpryDt"]).isoformat(),
                "strike": _number(row, "StrkPric"),
                "type": row["OptnTp"],
            }
        )
        if key in identities:
            raise ValueError("Duplicate contract row")
        identities.add(key)
        rows.append(row)
    return rows


def rank(
    prior: bytes,
    current: bytes,
    prior_day: date,
    current_day: date,
    following_day: date,
) -> dict[str, Any]:
    """Return frozen top-ten rankings without accepting any future snapshot."""
    if not prior_day < current_day < following_day:
        raise ValueError("Session dates must be increasing")
    prior_rows = _snapshot(prior, prior_day)
    current_rows = _snapshot(current, current_day)

    prior_underlying: dict[str, list[float]] = {}
    prior_volume: dict[tuple[str, str, str, str], float] = {}
    for row in prior_rows:
        symbol = row["TckrSymb"].strip().upper()
        try:
            underlying = _number(row, "UndrlygPric")
            volume = _number(row, "TtlTradgVol")
            key = _identity(
                {
                    "symbol": symbol,
                    "expiry": _day(row["XpryDt"]).isoformat(),
                    "strike": _number(row, "StrkPric"),
                    "type": row["OptnTp"],
                }
            )
        except ValueError:
            continue
        if underlying > 0:
            prior_underlying.setdefault(symbol, []).append(underlying)
        if volume > 0:
            prior_volume[key] = volume
    underlying_reference = {
        symbol: median(values) for symbol, values in prior_underlying.items()
    }

    eligible: list[dict[str, Any]] = []
    rejected: Counter[str] = Counter()
    for row in current_rows:
        try:
            expiry = _day(row["XpryDt"])
            opening = _number(row, "OpnPric")
            high = _number(row, "HghPric")
            low = _number(row, "LwPric")
            close = _number(row, "ClsPric")
            previous_close = _number(row, "PrvsClsgPric")
            underlying = _number(row, "UndrlygPric")
            open_interest = _number(row, "OpnIntrst")
            oi_change = _number(row, "ChngInOpnIntrst")
            volume = _number(row, "TtlTradgVol")
            transfer_value = _number(row, "TtlTrfVal")
            transactions = _number(row, "TtlNbOfTxsExctd")
            lot_size = _number(row, "NewBrdLotQty")
            strike = _number(row, "StrkPric")
        except ValueError:
            rejected["MISSING_OR_INVALID_FEATURE"] += 1
            continue
        if expiry < following_day:
            rejected["EXPIRED_BEFORE_OUTCOME"] += 1
            continue
        if not (
            opening > 0
            and high > low >= 0
            and low <= opening <= high
            and low <= close <= high
        ):
            rejected["INVALID_PRICE_RANGE"] += 1
            continue
        if not (
            close >= 5
            and previous_close > 0
            and underlying > 0
            and volume >= 1000
            and open_interest > 0
            and transfer_value > 0
            and transactions > 0
            and lot_size > 0
            and strike > 0
        ):
            rejected["PRIOR_QUALITY_OR_LIQUIDITY_FILTER"] += 1
            continue

        item = {
            "symbol": row["TckrSymb"].strip().upper(),
            "expiry": expiry.isoformat(),
            "strike": format(strike, ".4f"),
            "type": row["OptnTp"],
            "previous_close": close,
        }
        key = _identity(item)
        side = 1.0 if item["type"] == "CE" else -1.0
        prior_underlying_value = underlying_reference.get(item["symbol"])
        signed_underlying_return = (
            side * log(underlying / prior_underlying_value)
            if prior_underlying_value and prior_underlying_value > 0
            else 0.0
        )
        previous_volume = prior_volume.get(key)
        volume_surprise = (
            log1p(volume) - log1p(previous_volume)
            if previous_volume and previous_volume > 0
            else 0.0
        )
        moneyness = log(strike / underlying)
        item["feature_values"] = {
            "premium_return": max(-3.0, min(3.0, log(close / previous_close))),
            "intraday_momentum": max(-3.0, min(3.0, log(close / opening))),
            "close_location": (close - low) / (high - low),
            "volume": log1p(volume),
            "transactions": log1p(transactions),
            "oi_change": max(-2.0, min(2.0, oi_change / open_interest)),
            "near_expiry": -log1p((expiry - following_day).days),
            "lower_premium": -log(close),
            "atm_proximity": -abs(moneyness),
            "signed_moneyness": -moneyness if item["type"] == "CE" else moneyness,
            "signed_underlying_return": signed_underlying_return,
            "volume_surprise": max(-5.0, min(5.0, volume_surprise)),
            "turnover_per_contract": log1p(transfer_value / volume),
            "oi_level": log1p(open_interest),
        }
        item["feature_missingness"] = {
            "prior_underlying": prior_underlying_value is None,
            "prior_exact_contract_volume": previous_volume is None,
        }
        eligible.append(item)

    for feature in FEATURE_ORDER:
        percentiles = _percentile_ranks(
            [item["feature_values"][feature] for item in eligible]
        )
        for item, percentile in zip(eligible, percentiles):
            item.setdefault("feature_percentiles", {})[feature] = percentile

    selected: dict[str, list[dict[str, Any]]] = {}
    for head, frozen in HEADS.items():
        for item in eligible:
            item.setdefault("scores", {})[head] = frozen["intercept"] + sum(
                frozen["coefficients"][feature]
                * item["feature_percentiles"][feature]
                for feature in FEATURE_ORDER
            )
        ordered = sorted(
            eligible,
            key=lambda item: (-item["scores"][head], _identity(item)),
        )
        selected[head] = ordered[:SELECTION_COUNT]

    return {
        "version": VERSION,
        "prior_day": prior_day.isoformat(),
        "current_day": current_day.isoformat(),
        "following_day": following_day.isoformat(),
        "prior_sha256": sha256(prior).hexdigest(),
        "current_sha256": sha256(current).hexdigest(),
        "eligible": eligible,
        "selected": selected,
        "selection_count_per_head": SELECTION_COUNT,
        "rejected": dict(rejected),
        "feature_order": FEATURE_ORDER,
        "feature_availability": {
            "archived_bhavcopy_fields": "MEASURED",
            "implied_volatility": "NOT_AVAILABLE_ZERO_COVERAGE",
            "greeks": "NOT_AVAILABLE_ZERO_COVERAGE",
        },
        "score_interpretation": "LINEAR_LOGIT_RANK_ONLY_NOT_CALIBRATED_PROBABILITY",
        "expected_multiple": None,
        "expected_range": None,
        "forward_issued": False,
        "opening_fill_proven": False,
        "orders_allowed": False,
    }
