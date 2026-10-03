"""Build and validate prospective NSE equity PAPER prediction records.

This module deliberately separates a forward research observation from a
qualified signal.  It consumes only source bytes observed before issuance,
uses a fixed deterministic rank, and never places orders.
"""
from __future__ import annotations

import csv
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal, InvalidOperation
from hashlib import sha256
from io import StringIO
import json
import re
from typing import Any
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

from scripts.equity_observation_packet import build_packet


SCHEMA = "equity-forward-paper-prediction-v1"
EVENT_TYPE = "EQUITY_FORWARD_PREDICTION_ISSUED"
GENESIS_HASH = "0" * 64
IST = ZoneInfo("Asia/Kolkata")
INDEX_URL_PREFIX = "https://nsearchives.nseindia.com/content/indices/ind_close_all_"
HOLIDAY_URL = "https://www.nseindia.com/api/holiday-master?type=trading"
EXPECTED_KEYS = {
    "schema",
    "event_type",
    "task_id",
    "evidence_class",
    "prediction_id",
    "issued_at",
    "source_cutoff_at",
    "entry_session_date",
    "due_session_date",
    "due_at",
    "horizon",
    "strategy",
    "counts",
    "prediction",
    "benchmark",
    "source_receipts",
    "action_policy",
    "current_metrics",
    "safety",
    "previous_event_hash",
    "event_hash",
}
_ISIN_RE = re.compile(r"^IN[A-Z0-9]{10}$")
_PREDICTION_ID_RE = re.compile(r"^EQ7D-\d{4}-\d{2}-\d{2}-[A-Z0-9&-]+-V1$")
_EQUITY_SOURCE_ROLES = {"cash", "company", "etf", "actions"}


def _instant(value: Any, field: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid {field}") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field} requires timezone")
    return parsed.astimezone(timezone.utc)


def _decimal(value: Any, field: str, *, positive: bool = False) -> Decimal:
    try:
        result = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError(f"Invalid {field}") from exc
    if not result.is_finite() or (positive and result <= 0):
        raise ValueError(f"Invalid {field}")
    return result


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def _sha(value: Any, field: str) -> str:
    text = str(value).lower()
    if len(text) != 64 or any(char not in "0123456789abcdef" for char in text):
        raise ValueError(f"Invalid {field}")
    return text


def _verify_receipt(raw: bytes, receipt: dict[str, Any], *, url: str) -> datetime:
    parsed = urlsplit(url)
    if (
        parsed.scheme != "https"
        or parsed.hostname not in {"www.nseindia.com", "nsearchives.nseindia.com"}
        or parsed.username
        or parsed.password
        or parsed.fragment
        or parsed.port not in (None, 443)
        or receipt.get("url") != url
        or receipt.get("final_url") != url
        or receipt.get("http_status") != 200
        or receipt.get("raw_sha256") != sha256(raw).hexdigest()
        or receipt.get("bytes") != len(raw)
    ):
        raise ValueError("Official source receipt mismatch")
    return _instant(receipt.get("first_observed_at"), "first_observed_at")


def _percent_rank(values: list[Decimal], value: Decimal) -> Decimal:
    if len(values) == 1:
        return Decimal(1)
    lower = sum(candidate < value for candidate in values)
    equal = sum(candidate == value for candidate in values)
    return (Decimal(lower) + Decimal(equal - 1) / 2) / Decimal(len(values) - 1)


def _index_reference(raw: bytes, receipt: dict[str, Any], session: date) -> tuple[dict, datetime]:
    url = f"{INDEX_URL_PREFIX}{session.strftime('%d%m%Y')}.csv"
    observed = _verify_receipt(raw, receipt, url=url)
    reader = csv.DictReader(StringIO(raw.decode("utf-8-sig")))
    required = {
        "Index Name",
        "Index Date",
        "Open Index Value",
        "High Index Value",
        "Low Index Value",
        "Closing Index Value",
    }
    if not required.issubset(reader.fieldnames or []):
        raise ValueError("Unsupported index schema")
    matches = [row for row in reader if row["Index Name"] == "Nifty 50"]
    if len(matches) != 1 or matches[0]["Index Date"] != session.strftime("%d-%m-%Y"):
        raise ValueError("Nifty 50 session row missing or duplicated")
    row = matches[0]
    values = {
        key: _decimal(row[key], key, positive=True)
        for key in (
            "Open Index Value",
            "High Index Value",
            "Low Index Value",
            "Closing Index Value",
        )
    }
    if not values["Low Index Value"] <= min(
        values["Open Index Value"], values["Closing Index Value"]
    ) <= max(
        values["Open Index Value"], values["Closing Index Value"]
    ) <= values["High Index Value"]:
        raise ValueError("Inconsistent Nifty 50 OHLC")
    return {
        "name": "Nifty 50",
        "entry_session_date": session.isoformat(),
        "entry_reference_close": str(values["Closing Index Value"]),
        "price_basis": "UNADJUSTED_EXCHANGE_REFERENCE",
        "source_sha256": sha256(raw).hexdigest(),
        "source_url": url,
    }, observed


def _cm_holidays(raw: bytes) -> set[date]:
    try:
        payload = json.loads(raw)
        rows = payload["CM"]
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        raise ValueError("Unsupported CM holiday source") from exc
    if not isinstance(rows, list) or not rows:
        raise ValueError("Empty CM holiday source")
    holidays = set()
    for row in rows:
        try:
            holidays.add(datetime.strptime(row["tradingDate"], "%d-%b-%Y").date())
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("Invalid CM holiday row") from exc
    return holidays


def _due_session(
    raw: bytes, receipt: dict[str, Any], *, entry: date, calendar_days: int
) -> tuple[date, datetime]:
    observed = _verify_receipt(raw, receipt, url=HOLIDAY_URL)
    holidays = _cm_holidays(raw)
    result = entry + timedelta(days=calendar_days)
    while result.weekday() >= 5 or result in holidays:
        result += timedelta(days=1)
    return result, observed


def _model(raw: bytes) -> tuple[dict[str, Any], str]:
    try:
        model = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError("Invalid model specification") from exc
    required = {
        "schema": "equity-forward-experiment-v1",
        "experiment_id": "EQ-FWD-RANK-001",
        "strategy_id": "EQUITY_INTRADAY_MOMENTUM_LIQUIDITY",
        "strategy_version": "1.0.0",
        "status": "EXPLORATORY_FORWARD_ONLY",
    }
    if not isinstance(model, dict) or any(model.get(k) != v for k, v in required.items()):
        raise ValueError("Unsupported model specification")
    if model.get("selection", {}).get("score") != "0.5*intraday_return_percent_rank + 0.5*liquidity_proxy_percent_rank":
        raise ValueError("Model score changed")
    return model, sha256(raw).hexdigest()


def _select_candidate(packet: dict[str, Any], model: dict[str, Any]) -> dict[str, Any]:
    """Replay the frozen screen and rank from an authenticated source packet."""
    minimum_close = _decimal(
        model["universe"]["minimum_close_inr"],
        "minimum_close",
        positive=True,
    )
    minimum_liquidity = _decimal(
        model["universe"]["minimum_close_times_volume_inr"],
        "minimum_liquidity",
        positive=True,
    )
    candidates = []
    for row in packet["observations"]:
        close = _decimal(row["close"], "close", positive=True)
        opening = _decimal(row["open"], "open", positive=True)
        volume = Decimal(row["volume"])
        intraday_return = close / opening - 1
        liquidity = close * volume
        if (
            row["action_review"]["action_count"] == 0
            and close >= minimum_close
            and liquidity >= minimum_liquidity
            and intraday_return > 0
        ):
            candidates.append((row, intraday_return, liquidity))
    if not candidates:
        raise ValueError("No exploratory candidate")
    momenta = [row[1] for row in candidates]
    liquidities = [row[2] for row in candidates]
    ranked = []
    for observation, momentum, liquidity in candidates:
        momentum_rank = _percent_rank(momenta, momentum)
        liquidity_rank = _percent_rank(liquidities, liquidity)
        score = (momentum_rank + liquidity_rank) / 2
        ranked.append(
            (
                score,
                observation["symbol"],
                observation["isin"],
                observation,
                momentum,
                liquidity,
                momentum_rank,
                liquidity_rank,
            )
        )
    ranked.sort(key=lambda row: (-row[0], row[1], row[2]))
    (
        score,
        symbol,
        isin,
        selected,
        momentum,
        liquidity,
        momentum_rank,
        liquidity_rank,
    ) = ranked[0]
    features = {
        "open": selected["open"],
        "close": selected["close"],
        "volume": selected["volume"],
        "intraday_return": str(momentum.quantize(Decimal("0.0000000001"))),
        "close_times_volume_inr": str(liquidity.quantize(Decimal("0.01"))),
        "intraday_return_percent_rank": str(
            momentum_rank.quantize(Decimal("0.0000000001"))
        ),
        "liquidity_proxy_percent_rank": str(
            liquidity_rank.quantize(Decimal("0.0000000001"))
        ),
        "selection_score": str(score.quantize(Decimal("0.0000000001"))),
        "source_row_sha256": selected["canonical_source_row_sha256"],
    }
    return {
        "screened_candidates": len(candidates),
        "symbol": symbol,
        "isin": isin,
        "selected": selected,
        "features": features,
    }


def _replay_receipt(stored: dict[str, Any]) -> dict[str, Any]:
    """Restore the builder receipt fields after authenticating stored metadata."""
    return {
        "url": stored["url"],
        "final_url": stored["url"],
        "http_status": 200,
        "raw_sha256": stored["sha256"],
        "bytes": stored["bytes"],
        "first_observed_at": stored["first_observed_at"],
    }


def build_prediction(
    *,
    equity_sources: dict[str, bytes],
    equity_receipts: dict[str, dict[str, Any]],
    index_raw: bytes,
    index_receipt: dict[str, Any],
    holiday_raw: bytes,
    holiday_receipt: dict[str, Any],
    model_spec_raw: bytes,
    issued_at: str,
    previous_event_hash: str,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Build one deterministic exploratory prediction from current-session sources."""
    issued = _instant(issued_at, "issued_at")
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None or current.utcoffset() is None or issued > current.astimezone(timezone.utc):
        raise ValueError("issued_at cannot be in the future")
    model, model_sha = _model(model_spec_raw)
    model_registered = _instant(model.get("registered_at"), "model registered_at")
    if model_registered > issued:
        raise ValueError("Model specification registered after prediction issue")
    packet = build_packet(
        equity_sources,
        equity_receipts,
        as_of=issued.isoformat(),
        now=current,
    )
    entry = date.fromisoformat(packet["trade_date"])
    if issued.astimezone(IST).date() != entry or issued.astimezone(IST).time() < time(15, 30):
        raise ValueError("Prediction must use a completed same-day cash session")
    benchmark, index_observed = _index_reference(index_raw, index_receipt, entry)
    due, holiday_observed = _due_session(
        holiday_raw,
        holiday_receipt,
        entry=entry,
        calendar_days=model["horizon"]["calendar_days"],
    )
    source_times = [
        _instant(receipt["first_observed_at"], "first_observed_at")
        for receipt in equity_receipts.values()
    ] + [index_observed, holiday_observed]
    cutoff = max(source_times)
    if cutoff > issued:
        raise ValueError("Prediction source observed after issuance")

    selection = _select_candidate(packet, model)
    symbol = selection["symbol"]
    isin = selection["isin"]
    selected = selection["selected"]
    features = selection["features"]
    due_at = datetime.combine(due, time(15, 30), IST).astimezone(timezone.utc)
    source_receipts = {
        role: {
            "url": receipt["url"],
            "first_observed_at": _instant(receipt["first_observed_at"], "first_observed_at").isoformat(),
            "sha256": receipt["raw_sha256"],
            "bytes": receipt["bytes"],
        }
        for role, receipt in {
            **equity_receipts,
            "index": index_receipt,
            "holiday_calendar": holiday_receipt,
        }.items()
    }
    payload = {
        "schema": SCHEMA,
        "event_type": EVENT_TYPE,
        "task_id": "EQ-ADJUST-008",
        "evidence_class": "EXPLORATORY_FORWARD_PAPER_PREDICTION",
        "prediction_id": f"EQ7D-{entry.isoformat()}-{symbol}-V1",
        "issued_at": issued.isoformat(),
        "source_cutoff_at": cutoff.isoformat(),
        "entry_session_date": entry.isoformat(),
        "due_session_date": due.isoformat(),
        "due_at": due_at.isoformat(),
        "horizon": {
            "calendar_days": model["horizon"]["calendar_days"],
            "outcome_reference": "OFFICIAL_CLOSE_FIRST_CM_SESSION_ON_OR_AFTER_CALENDAR_HORIZON",
        },
        "strategy": {
            "experiment_id": model["experiment_id"],
            "strategy_id": model["strategy_id"],
            "strategy_version": model["strategy_version"],
            "model_spec_sha256": model_sha,
            "qualification_status": "EXPLORATORY_NOT_GATE_QUALIFIED",
        },
        "counts": {
            "source_company_eq_observations": packet["company_eq_observation_count"],
            "screened_candidates": selection["screened_candidates"],
            "selected_candidates": 1,
            "qualified_current_candidates": 0,
            "forward_predictions": 1,
            "matured_outcomes": 0,
            "positive_forecasts": 1,
            "negative_forecasts": 0,
        },
        "prediction": {
            "symbol": symbol,
            "isin": isin,
            "series": "EQ",
            "direction": "POSITIVE",
            "entry_reference_close": selected["close"],
            "entry_reference_is_executable_fill": False,
            "price_basis": "UNADJUSTED_EXCHANGE_REFERENCE",
            "adjusted_entry_price": None,
            "expected_return_range": None,
            "calibrated_probability": None,
            "features": features,
            "feature_hash": sha256(_canonical(features)).hexdigest(),
            "forward_evaluation_status": "PENDING",
        },
        "benchmark": benchmark,
        "source_receipts": source_receipts,
        "action_policy": {
            "capture_interval_start": packet["action_scope"]["start"],
            "capture_interval_end": packet["action_scope"]["end"],
            "selected_action_count_at_issue": selected["action_review"]["action_count"],
            "complete_action_coverage_at_issue": False,
            "maturity_recheck_required": True,
            "score_if_action_or_identity_change": "NOT_PROVEN_UNTIL_ADJUSTMENT_RESOLVED",
        },
        "current_metrics": {
            "valid_outcomes": 0,
            "oos_days": 0,
            "directional_accuracy": None,
            "top_decile_precision": None,
            "sharpe": None,
            "max_drawdown": None,
            "deflated_sharpe_probability": None,
            "benchmark_excess_return": None,
            "calibration_error": None,
            "target_gaps": {
                "valid_outcomes": 100,
                "oos_days": 60,
                "directional_accuracy": None,
                "top_decile_precision": None,
                "sharpe": None,
                "max_drawdown": None,
                "deflated_sharpe_probability": None,
            },
        },
        "safety": {
            "retrospective": False,
            "catalyst_feature_included": False,
            "real_money_ready": False,
            "live_trading_enabled": False,
            "orders_allowed": False,
        },
        "previous_event_hash": _sha(previous_event_hash, "previous_event_hash"),
    }
    payload["event_hash"] = sha256(_canonical(payload)).hexdigest()
    validate_prediction(
        payload,
        now=current,
        equity_source_bytes=equity_sources,
        index_source_raw=index_raw,
        holiday_calendar_raw=holiday_raw,
        model_spec_raw=model_spec_raw,
        expected_previous_event_hash=previous_event_hash,
    )
    return payload


def validate_prediction(
    payload: dict[str, Any],
    *,
    now: datetime | None = None,
    equity_source_bytes: dict[str, bytes] | None = None,
    index_source_raw: bytes | None = None,
    holiday_calendar_raw: bytes | None = None,
    model_spec_raw: bytes | None = None,
    expected_previous_event_hash: str | None = None,
) -> dict[str, Any]:
    """Fail closed if a stored forward record overstates its evidence."""
    if not isinstance(payload, dict) or set(payload) != EXPECTED_KEYS:
        raise ValueError("Prediction record fields do not match locked schema")
    if payload["schema"] != SCHEMA or payload["event_type"] != EVENT_TYPE:
        raise ValueError("Unsupported prediction schema or event")
    if payload["task_id"] != "EQ-ADJUST-008" or payload["evidence_class"] != "EXPLORATORY_FORWARD_PAPER_PREDICTION":
        raise ValueError("Invalid task or evidence class")
    issued = _instant(payload["issued_at"], "issued_at")
    cutoff = _instant(payload["source_cutoff_at"], "source_cutoff_at")
    due = _instant(payload["due_at"], "due_at")
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None or current.utcoffset() is None:
        raise ValueError("now requires timezone")
    current_utc = current.astimezone(timezone.utc)
    if issued > current_utc:
        raise ValueError("Prediction issue is in the future")
    if not cutoff <= issued < due:
        raise ValueError("Invalid source/issue/outcome chronology")
    entry_day = date.fromisoformat(payload["entry_session_date"])
    due_day = date.fromisoformat(payload["due_session_date"])
    issued_local = issued.astimezone(IST)
    if issued_local.date() != entry_day or issued_local.time() < time(15, 30):
        raise ValueError("Prediction must be issued after the completed entry-session close")
    due_local = due.astimezone(IST)
    if due_local.date() != due_day or due_local.time() != time(15, 30):
        raise ValueError("Invalid due close timestamp")
    if due_day < entry_day + timedelta(days=7):
        raise ValueError("Invalid due session")

    horizon = payload["horizon"]
    if set(horizon) != {"calendar_days", "outcome_reference"} or horizon != {
        "calendar_days": 7,
        "outcome_reference": "OFFICIAL_CLOSE_FIRST_CM_SESSION_ON_OR_AFTER_CALENDAR_HORIZON",
    }:
        raise ValueError("Horizon contract changed")
    if not _PREDICTION_ID_RE.fullmatch(str(payload["prediction_id"])):
        raise ValueError("Invalid prediction id")

    strategy = payload["strategy"]
    if set(strategy) != {
        "experiment_id",
        "strategy_id",
        "strategy_version",
        "model_spec_sha256",
        "qualification_status",
    }:
        raise ValueError("Strategy fields changed")
    if (
        strategy["experiment_id"] != "EQ-FWD-RANK-001"
        or strategy["strategy_id"] != "EQUITY_INTRADAY_MOMENTUM_LIQUIDITY"
        or strategy["strategy_version"] != "1.0.0"
        or strategy["qualification_status"] != "EXPLORATORY_NOT_GATE_QUALIFIED"
    ):
        raise ValueError("Exploratory strategy was promoted")
    _sha(strategy["model_spec_sha256"], "model_spec_sha256")
    if not isinstance(model_spec_raw, bytes) or not model_spec_raw:
        raise ValueError("Registered model specification bytes required")
    retained_model, retained_model_sha = _model(model_spec_raw)
    if retained_model_sha != strategy["model_spec_sha256"]:
        raise ValueError("Model specification retained bytes mismatch")
    if _instant(retained_model.get("registered_at"), "model registered_at") > issued:
        raise ValueError("Model specification registered after prediction issue")

    counts = payload["counts"]
    if set(counts) != {
        "source_company_eq_observations",
        "screened_candidates",
        "selected_candidates",
        "qualified_current_candidates",
        "forward_predictions",
        "matured_outcomes",
        "positive_forecasts",
        "negative_forecasts",
    }:
        raise ValueError("Prediction count fields changed")
    expected_counts = {
        "selected_candidates": 1,
        "qualified_current_candidates": 0,
        "forward_predictions": 1,
        "matured_outcomes": 0,
        "positive_forecasts": 1,
        "negative_forecasts": 0,
    }
    if any(counts.get(key) != value for key, value in expected_counts.items()):
        raise ValueError("Prediction counts overstate the evidence")
    if (
        type(counts["source_company_eq_observations"]) is not int
        or type(counts["screened_candidates"]) is not int
        or not 1 <= counts["screened_candidates"] <= counts["source_company_eq_observations"]
    ):
        raise ValueError("Invalid source or screening counts")

    prediction = payload["prediction"]
    if set(prediction) != {
        "symbol",
        "isin",
        "series",
        "direction",
        "entry_reference_close",
        "entry_reference_is_executable_fill",
        "price_basis",
        "adjusted_entry_price",
        "expected_return_range",
        "calibrated_probability",
        "features",
        "feature_hash",
        "forward_evaluation_status",
    }:
        raise ValueError("Prediction fields changed")
    symbol = str(prediction.get("symbol", ""))
    if not symbol or symbol != symbol.upper() or not _ISIN_RE.fullmatch(str(prediction.get("isin", ""))):
        raise ValueError("Invalid prediction identity")
    if payload["prediction_id"] != f"EQ7D-{entry_day.isoformat()}-{symbol}-V1":
        raise ValueError("Prediction id does not bind identity")
    if prediction.get("series") != "EQ":
        raise ValueError("Prediction series changed")
    _decimal(prediction.get("entry_reference_close"), "entry_reference_close", positive=True)
    if prediction.get("direction") != "POSITIVE" or prediction.get("forward_evaluation_status") != "PENDING":
        raise ValueError("Unsupported prediction state")
    if prediction.get("expected_return_range") is not None or prediction.get("calibrated_probability") is not None:
        raise ValueError("Uncalibrated prediction cannot claim range or probability")
    if prediction.get("adjusted_entry_price") is not None or prediction.get("price_basis") != "UNADJUSTED_EXCHANGE_REFERENCE":
        raise ValueError("Raw entry reference mislabeled as adjusted")
    if prediction.get("entry_reference_is_executable_fill") is not False:
        raise ValueError("Closing reference cannot be an executable fill")
    features = prediction.get("features")
    if not isinstance(features, dict) or set(features) != {
        "open",
        "close",
        "volume",
        "intraday_return",
        "close_times_volume_inr",
        "intraday_return_percent_rank",
        "liquidity_proxy_percent_rank",
        "selection_score",
        "source_row_sha256",
    }:
        raise ValueError("Feature fields changed")
    _sha(features["source_row_sha256"], "source_row_sha256")
    if prediction.get("feature_hash") != sha256(_canonical(features)).hexdigest():
        raise ValueError("Feature hash mismatch")
    if features["close"] != prediction["entry_reference_close"]:
        raise ValueError("Feature close does not bind entry reference")
    if type(features["volume"]) is not int or features["volume"] <= 0:
        raise ValueError("Invalid feature volume")
    feature_open = _decimal(features["open"], "open", positive=True)
    feature_close = _decimal(features["close"], "close", positive=True)
    feature_return = _decimal(
        features["intraday_return"], "intraday_return", positive=True
    )
    feature_liquidity = _decimal(
        features["close_times_volume_inr"],
        "close_times_volume_inr",
        positive=True,
    )
    selection_score = _decimal(
        features["selection_score"], "selection_score", positive=True
    )
    ranks = {}
    for field in (
        "intraday_return_percent_rank",
        "liquidity_proxy_percent_rank",
    ):
        rank = _decimal(features[field], field)
        if not Decimal(0) <= rank <= Decimal(1):
            raise ValueError(f"Invalid {field}")
        ranks[field] = rank
    expected_return = (feature_close / feature_open - 1).quantize(
        Decimal("0.0000000001")
    )
    expected_liquidity = (feature_close * features["volume"]).quantize(
        Decimal("0.01")
    )
    expected_score = (
        (
            ranks["intraday_return_percent_rank"]
            + ranks["liquidity_proxy_percent_rank"]
        )
        / 2
    ).quantize(Decimal("0.0000000001"))
    if (
        feature_return != expected_return
        or feature_liquidity != expected_liquidity
        or abs(selection_score - expected_score) > Decimal("0.0000000001")
    ):
        raise ValueError("Feature arithmetic mismatch")

    benchmark = payload["benchmark"]
    if set(benchmark) != {
        "name",
        "entry_session_date",
        "entry_reference_close",
        "price_basis",
        "source_sha256",
        "source_url",
    }:
        raise ValueError("Benchmark fields changed")
    if (
        benchmark["name"] != "Nifty 50"
        or benchmark["entry_session_date"] != entry_day.isoformat()
        or benchmark["price_basis"] != "UNADJUSTED_EXCHANGE_REFERENCE"
    ):
        raise ValueError("Benchmark contract changed")
    _decimal(benchmark["entry_reference_close"], "benchmark_close", positive=True)
    _sha(benchmark["source_sha256"], "benchmark_source_sha256")

    source_receipts = payload["source_receipts"]
    if not isinstance(source_receipts, dict) or set(source_receipts) != {
        "cash",
        "company",
        "etf",
        "actions",
        "index",
        "holiday_calendar",
    }:
        raise ValueError("Source receipt roles changed")
    observed_times = []
    for role, receipt in source_receipts.items():
        if not isinstance(receipt, dict) or set(receipt) != {
            "url",
            "first_observed_at",
            "sha256",
            "bytes",
        }:
            raise ValueError("Source receipt fields changed")
        parsed_url = urlsplit(str(receipt["url"]))
        if (
            parsed_url.scheme != "https"
            or parsed_url.hostname not in {"www.nseindia.com", "nsearchives.nseindia.com"}
            or parsed_url.username
            or parsed_url.password
            or parsed_url.fragment
            or parsed_url.port not in (None, 443)
        ):
            raise ValueError("Unapproved stored source URL")
        observed_times.append(_instant(receipt["first_observed_at"], "first_observed_at"))
        _sha(receipt["sha256"], f"{role}_source_sha256")
        if type(receipt["bytes"]) is not int or receipt["bytes"] <= 0:
            raise ValueError("Invalid stored source size")
    if max(observed_times) != cutoff or max(observed_times) > issued:
        raise ValueError("Stored source cutoff mismatch")
    if (
        benchmark["source_sha256"] != source_receipts["index"]["sha256"]
        or benchmark["source_url"] != source_receipts["index"]["url"]
    ):
        raise ValueError("Benchmark source receipt mismatch")

    if (
        not isinstance(equity_source_bytes, dict)
        or set(equity_source_bytes) != _EQUITY_SOURCE_ROLES
    ):
        raise ValueError("Exact retained equity source bytes required")
    replay_receipts = {}
    for role in sorted(_EQUITY_SOURCE_ROLES):
        raw = equity_source_bytes[role]
        receipt = source_receipts[role]
        if (
            not isinstance(raw, bytes)
            or not raw
            or sha256(raw).hexdigest() != receipt["sha256"]
            or len(raw) != receipt["bytes"]
        ):
            raise ValueError(f"{role} retained source bytes mismatch")
        replay_receipts[role] = _replay_receipt(receipt)
    replay_packet = build_packet(
        equity_source_bytes,
        replay_receipts,
        as_of=issued.isoformat(),
        now=current_utc,
    )
    replay_selection = _select_candidate(replay_packet, retained_model)
    if (
        replay_packet["trade_date"] != entry_day.isoformat()
        or counts["source_company_eq_observations"]
        != replay_packet["company_eq_observation_count"]
        or counts["screened_candidates"]
        != replay_selection["screened_candidates"]
    ):
        raise ValueError("Prediction counts do not match retained source replay")
    if (
        prediction["symbol"] != replay_selection["symbol"]
        or prediction["isin"] != replay_selection["isin"]
        or prediction["features"] != replay_selection["features"]
        or prediction["entry_reference_close"]
        != replay_selection["selected"]["close"]
    ):
        raise ValueError("Prediction does not match retained source replay")

    if not isinstance(index_source_raw, bytes) or not index_source_raw:
        raise ValueError("Exact retained index source bytes required")
    index_receipt = source_receipts["index"]
    if (
        sha256(index_source_raw).hexdigest() != index_receipt["sha256"]
        or len(index_source_raw) != index_receipt["bytes"]
    ):
        raise ValueError("index retained source bytes mismatch")
    replay_benchmark, replay_index_observed = _index_reference(
        index_source_raw,
        _replay_receipt(index_receipt),
        entry_day,
    )
    if (
        replay_benchmark != benchmark
        or replay_index_observed
        != _instant(index_receipt["first_observed_at"], "first_observed_at")
    ):
        raise ValueError("Benchmark does not match retained index replay")

    calendar_receipt = source_receipts["holiday_calendar"]
    if calendar_receipt["url"] != HOLIDAY_URL:
        raise ValueError("Holiday calendar source changed")
    if not isinstance(holiday_calendar_raw, bytes) or not holiday_calendar_raw:
        raise ValueError("Official holiday calendar bytes required")
    if (
        sha256(holiday_calendar_raw).hexdigest() != calendar_receipt["sha256"]
        or len(holiday_calendar_raw) != calendar_receipt["bytes"]
    ):
        raise ValueError("Holiday calendar retained bytes mismatch")
    expected_due = entry_day + timedelta(days=horizon["calendar_days"])
    holidays = _cm_holidays(holiday_calendar_raw)
    while expected_due.weekday() >= 5 or expected_due in holidays:
        expected_due += timedelta(days=1)
    if due_day != expected_due:
        raise ValueError("Due session does not match retained official calendar")

    action_policy = payload["action_policy"]
    if set(action_policy) != {
        "capture_interval_start",
        "capture_interval_end",
        "selected_action_count_at_issue",
        "complete_action_coverage_at_issue",
        "maturity_recheck_required",
        "score_if_action_or_identity_change",
    }:
        raise ValueError("Action policy fields changed")
    if (
        action_policy["selected_action_count_at_issue"] != 0
        or action_policy["complete_action_coverage_at_issue"] is not False
        or action_policy["maturity_recheck_required"] is not True
        or action_policy["score_if_action_or_identity_change"] != "NOT_PROVEN_UNTIL_ADJUSTMENT_RESOLVED"
    ):
        raise ValueError("Corporate-action maturity recheck required")
    if not (
        date.fromisoformat(action_policy["capture_interval_start"]) <= entry_day
        and due_day <= date.fromisoformat(action_policy["capture_interval_end"])
    ):
        raise ValueError("Action capture does not cover the requested horizon")
    if (
        action_policy["capture_interval_start"]
        != replay_packet["action_scope"]["start"]
        or action_policy["capture_interval_end"]
        != replay_packet["action_scope"]["end"]
        or action_policy["selected_action_count_at_issue"]
        != replay_selection["selected"]["action_review"]["action_count"]
    ):
        raise ValueError("Action policy does not match retained source replay")

    metrics = payload["current_metrics"]
    metric_fields = {
        "valid_outcomes",
        "oos_days",
        "directional_accuracy",
        "top_decile_precision",
        "sharpe",
        "max_drawdown",
        "deflated_sharpe_probability",
        "benchmark_excess_return",
        "calibration_error",
        "target_gaps",
    }
    if set(metrics) != metric_fields or metrics["valid_outcomes"] != 0 or metrics["oos_days"] != 0:
        raise ValueError("Current metric fields overstate evidence")
    pending_metrics = metric_fields - {"valid_outcomes", "oos_days", "target_gaps"}
    if any(metrics[field] is not None for field in pending_metrics):
        raise ValueError("Pending record cannot contain performance metrics")
    if metrics["target_gaps"] != {
        "valid_outcomes": 100,
        "oos_days": 60,
        "directional_accuracy": None,
        "top_decile_precision": None,
        "sharpe": None,
        "max_drawdown": None,
        "deflated_sharpe_probability": None,
    }:
        raise ValueError("Research gate gaps changed")

    safety = payload["safety"]
    if set(safety) != {
        "retrospective",
        "catalyst_feature_included",
        "real_money_ready",
        "live_trading_enabled",
        "orders_allowed",
    } or any(safety.values()):
        raise ValueError("Unsafe prediction flags")
    stored_previous_hash = _sha(
        payload["previous_event_hash"], "previous_event_hash"
    )
    if expected_previous_event_hash is None:
        raise ValueError("Trusted previous event hash evidence required")
    expected_previous_hash = _sha(
        expected_previous_event_hash, "expected_previous_event_hash"
    )
    if stored_previous_hash != expected_previous_hash:
        raise ValueError("Previous event hash does not match trusted predecessor")
    stored_hash = _sha(payload["event_hash"], "event_hash")
    unhashed = {key: value for key, value in payload.items() if key != "event_hash"}
    if stored_hash != sha256(_canonical(unhashed)).hexdigest():
        raise ValueError("Prediction event hash mismatch")
    return {
        "status": "FORWARD_PAPER_PREDICTION_SEALED",
        "prediction_id": payload["prediction_id"],
        "symbol": prediction["symbol"],
        "due_session_date": payload["due_session_date"],
        "screened_candidates": counts["screened_candidates"],
        "qualified_current_candidates": 0,
        "forward_predictions": 1,
        "matured_outcomes": 0,
        "event_hash": stored_hash,
        "real_money_ready": False,
        "orders_allowed": False,
    }
