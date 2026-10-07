"""Replay the official NSE F&O source used by the locked CE/PE delivery.

This validator deliberately reads the retained ZIP.  Receipt values are not
trusted as measurements: hashes, the CSV member, contract identity, row counts,
missingness and the mechanical liquidity screen are recomputed from bytes.
"""
from __future__ import annotations

import csv
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from hashlib import sha1, sha256
import io
import json
from pathlib import Path
import re
from typing import Any
from urllib.parse import urlsplit
import zipfile


SCHEMA = "cepe-delivery-source-v1"
TASK_ID = "CEPE-SOURCE-024"
SOURCE_DATE = "2026-10-07"
TARGET_OPEN_AT = "2026-10-08T09:15:00+05:30"
ARCHIVE_URL = (
    "https://nsearchives.nseindia.com/content/fo/"
    "BhavCopy_NSE_FO_0_0_0_20261007_F_0000.csv.zip"
)
RAW_PATH = "research/evidence/cepe/raw/fo_20261007.zip"
MEMBER = "BhavCopy_NSE_FO_0_0_0_20261007_F_0000.csv"
ZIP_SHA256 = "676932c7a62c953cd1a82c277a4bb040ace5cd593c661dac4b9030a49c1801df"
CSV_SHA256 = "54774919d0962f213ed6ac3b482c9e4321af3815a421544ed162e26a96d1e2dd"
GIT_BLOB_SHA = "641068354baed06b3080e8125e56ff8a198c2ebd"
CALENDAR_URL = "https://nsearchives.nseindia.com/content/circulars/FAOP71777.pdf"
CALENDAR_SHA256 = "5a2079cd78b2e6b536ef0d28300e63b645721bed22cc82a91facf5945f3296ea"
EXPECTED_HEADER = [
    "TradDt", "BizDt", "Sgmt", "Src", "FinInstrmTp", "FinInstrmId", "ISIN",
    "TckrSymb", "SctySrs", "XpryDt", "FininstrmActlXpryDt", "StrkPric",
    "OptnTp", "FinInstrmNm", "OpnPric", "HghPric", "LwPric", "ClsPric",
    "LastPric", "PrvsClsgPric", "UndrlygPric", "SttlmPric", "OpnIntrst",
    "ChngInOpnIntrst", "TtlTradgVol", "TtlTrfVal", "TtlNbOfTxsExctd",
    "SsnId", "NewBrdLotQty", "Rmks", "Rsvd1", "Rsvd2", "Rsvd3", "Rsvd4",
]
EXPECTED_TOP_LEVEL = {
    "schema", "task_id", "lane", "evidence_as_of", "source_session_date",
    "target_open_at", "target_session", "delivery_lock", "retrievals",
    "official_archive", "mechanical_universe", "feature_registry",
    "forward_state", "gate_status", "interpretation",
    "opening_price_is_executable_fill", "fees_slippage_applied",
    "real_money_ready", "live_trading_enabled", "orders_allowed",
}
FEATURE_IDS = {
    "exact_contract_identity", "option_close", "option_ohl", "prior_close",
    "traded_volume", "open_interest", "change_in_open_interest",
    "underlying_price", "settlement_price", "board_lot_quantity",
    "close_volume_liquidity_screen", "implied_volatility",
    "greeks_delta_gamma_theta_vega", "bid_ask_spread", "fees_and_slippage",
}
NUMERIC_FIELDS = (
    "OpnPric", "HghPric", "LwPric", "ClsPric", "PrvsClsgPric",
    "UndrlygPric", "SttlmPric", "OpnIntrst", "ChngInOpnIntrst",
    "TtlTradgVol", "NewBrdLotQty",
)


def _instant(value: Any, field: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid {field}") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field} must include timezone")
    return parsed


def _sha(value: Any, length: int, field: str) -> str:
    text = str(value).lower()
    if not re.fullmatch(rf"[0-9a-f]{{{length}}}", text):
        raise ValueError(f"Invalid {field}")
    return text


def _canonical(payload: dict[str, Any]) -> bytes:
    return json.dumps(
        payload, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def _git_blob_sha(raw: bytes) -> str:
    header = f"blob {len(raw)}\0".encode("ascii")
    return sha1(header + raw).hexdigest()


def _safe_file(repo_root: Path, relative: Any) -> Path:
    text = str(relative)
    if text != RAW_PATH or Path(text).is_absolute() or ".." in Path(text).parts:
        raise ValueError("Raw ZIP path is not the locked safe repository path")
    root = repo_root.resolve()
    candidate = (root / text).resolve()
    if root not in candidate.parents or not candidate.is_file():
        raise ValueError("Retained raw ZIP is missing or outside the repository")
    return candidate


def _decimal(value: str, field: str) -> Decimal:
    try:
        return Decimal(value)
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"Invalid numeric source field: {field}") from exc


def _read_and_measure(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    if len(raw) != 1_086_658:
        raise ValueError("Retained ZIP byte count changed")
    if sha256(raw).hexdigest() != ZIP_SHA256:
        raise ValueError("Retained ZIP SHA-256 changed")
    if _git_blob_sha(raw) != GIT_BLOB_SHA:
        raise ValueError("Retained ZIP Git blob SHA changed")

    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            if archive.namelist() != [MEMBER]:
                raise ValueError("ZIP member set changed")
            member_info = archive.getinfo(MEMBER)
            csv_bytes = archive.read(MEMBER)
    except zipfile.BadZipFile as exc:
        raise ValueError("Retained source is not a valid ZIP") from exc
    if member_info.file_size != 6_378_435 or len(csv_bytes) != 6_378_435:
        raise ValueError("CSV member byte count changed")
    if sha256(csv_bytes).hexdigest() != CSV_SHA256:
        raise ValueError("CSV member SHA-256 changed")

    stream = io.TextIOWrapper(io.BytesIO(csv_bytes), encoding="utf-8-sig", newline="")
    reader = csv.DictReader(stream)
    if reader.fieldnames != EXPECTED_HEADER:
        raise ValueError("CSV header changed")
    rows = list(reader)
    if any(None in row for row in rows):
        raise ValueError("CSV contains overflow columns")
    if any(set(row) != set(EXPECTED_HEADER) for row in rows):
        raise ValueError("CSV row shape changed")

    instrument_types: dict[str, int] = {}
    for row in rows:
        kind = row["FinInstrmTp"]
        instrument_types[kind] = instrument_types.get(kind, 0) + 1
    identifiers = [row["FinInstrmId"] for row in rows]
    options = [row for row in rows if row["FinInstrmTp"] in {"IDO", "STO"}]
    keys = [
        (row["TckrSymb"], row["XpryDt"], row["StrkPric"], row["OptnTp"])
        for row in options
    ]
    missing = {
        field: sum(not row[field].strip() for row in options)
        for field in NUMERIC_FIELDS
    }
    zeros = {
        field: sum(
            bool(row[field].strip()) and _decimal(row[field], field) == 0
            for row in options
        )
        for field in NUMERIC_FIELDS
    }
    positive_volume = sum(
        _decimal(row["TtlTradgVol"], "TtlTradgVol") > 0 for row in options
    )
    screen_rows = [
        row for row in options
        if _decimal(row["ClsPric"], "ClsPric") >= 1
        and _decimal(row["TtlTradgVol"], "TtlTradgVol") >= 100
    ]
    return {
        "zip_bytes": len(raw),
        "zip_sha256": sha256(raw).hexdigest(),
        "git_blob_sha": _git_blob_sha(raw),
        "member": MEMBER,
        "csv_bytes": len(csv_bytes),
        "csv_sha256": sha256(csv_bytes).hexdigest(),
        "source_rows": len(rows),
        "instrument_type_rows": instrument_types,
        "trade_dates": sorted({row["TradDt"] for row in rows}),
        "business_dates": sorted({row["BizDt"] for row in rows}),
        "segments": sorted({row["Sgmt"] for row in rows}),
        "sources": sorted({row["Src"] for row in rows}),
        "sessions": sorted({row["SsnId"] for row in rows}),
        "unique_instrument_ids": len(set(identifiers)),
        "duplicate_rows_by_instrument_id": len(identifiers) - len(set(identifiers)),
        "option_rows": len(options),
        "ce_rows": sum(row["OptnTp"] == "CE" for row in options),
        "pe_rows": sum(row["OptnTp"] == "PE" for row in options),
        "unique_exact_contract_keys": len(set(keys)),
        "duplicate_exact_contract_rows": len(keys) - len(set(keys)),
        "option_symbols": len({row["TckrSymb"] for row in options}),
        "option_expiries": len({row["XpryDt"] for row in options}),
        "minimum_expiry": min(row["XpryDt"] for row in options),
        "maximum_expiry": max(row["XpryDt"] for row in options),
        "positive_volume_rows": positive_volume,
        "zero_volume_rows": len(options) - positive_volume,
        "close_ge_1_and_volume_ge_100_rows": len(screen_rows),
        "screen_symbols": len({row["TckrSymb"] for row in screen_rows}),
        "missing": missing,
        "zeros": zeros,
    }


def validate(payload: dict[str, Any], repo_root: Path = Path(".")) -> dict[str, Any]:
    """Return byte-replayed measurements or reject provenance inflation."""
    if not isinstance(payload, dict) or set(payload) != EXPECTED_TOP_LEVEL:
        raise ValueError("Delivery-source fields do not match the locked schema")
    if payload["schema"] != SCHEMA or payload["task_id"] != TASK_ID:
        raise ValueError("Unsupported delivery-source schema or task")
    if payload["lane"] != "CEPE_NEXT_OPEN":
        raise ValueError("CE/PE evidence cannot be mixed with another lane")

    try:
        source_day = date.fromisoformat(str(payload["source_session_date"]))
    except (TypeError, ValueError) as exc:
        raise ValueError("Invalid source_session_date") from exc
    evidence_at = _instant(payload["evidence_as_of"], "evidence_as_of")
    target_open = _instant(payload["target_open_at"], "target_open_at")
    if source_day.isoformat() != SOURCE_DATE or payload["target_open_at"] != TARGET_OPEN_AT:
        raise ValueError("Source or target session changed")
    if not source_day < target_open.date() or not evidence_at < target_open:
        raise ValueError("Source and target sessions are not chronological")

    target = payload["target_session"]
    target_fields = {
        "segment", "calendar_source_url", "calendar_source_sha256",
        "calendar_source_first_observed_at", "calendar_source_published_date",
        "calendar_source_circular", "intervening_official_holidays",
        "next_eligible_session_date", "opening_time_basis",
    }
    if not isinstance(target, dict) or set(target) != target_fields:
        raise ValueError("Target-session evidence is incomplete")
    calendar = urlsplit(str(target["calendar_source_url"]))
    if (
        target["segment"] != "FO" or target["calendar_source_url"] != CALENDAR_URL
        or calendar.scheme != "https" or calendar.hostname != "nsearchives.nseindia.com"
        or calendar.username or calendar.password or calendar.fragment
        or calendar.port not in (None, 443)
    ):
        raise ValueError("Target-session source is not the exact official NSE circular")
    if _sha(target["calendar_source_sha256"], 64, "calendar source") != CALENDAR_SHA256:
        raise ValueError("Target-session calendar hash changed")
    if not _instant(target["calendar_source_first_observed_at"], "calendar observation") < evidence_at:
        raise ValueError("Calendar was not observed before this receipt")
    if (
        target["calendar_source_published_date"] != "2025-12-12"
        or target["calendar_source_circular"] != "NSE/FAOP/71777"
        or target["intervening_official_holidays"] != []
        or target["next_eligible_session_date"] != "2026-10-08"
        or target["opening_time_basis"] != "REGULAR_SESSION_ASSUMPTION_NOT_EXECUTABLE_FILL"
    ):
        raise ValueError("Target-session chronology or basis changed")

    delivery = payload["delivery_lock"]
    delivery_fields = {
        "task_id", "report_date", "decision", "subject", "recipient",
        "sent_at", "gmail_message_id", "sent_history_count_exact",
        "durable_record_url", "source_observed_before_send",
        "qualified_candidates_at_send", "second_email_allowed",
    }
    if not isinstance(delivery, dict) or set(delivery) != delivery_fields:
        raise ValueError("Delivery lock is incomplete")
    sent_at = _instant(delivery["sent_at"], "sent_at")
    if (
        delivery["task_id"] != "CEPE-DELIVERY-023"
        or delivery["report_date"] != SOURCE_DATE
        or delivery["decision"] != "NO_VERIFIED_SIGNAL"
        or delivery["subject"] != "[Genesis System3 CE/PE] 7 Oct 2026 — NO VERIFIED SIGNAL"
        or delivery["recipient"] != "warghade2012@gmail.com"
        or delivery["sent_at"] != "2026-10-07T20:07:10+05:30"
        or delivery["gmail_message_id"] != "1a116cbffe37ba90"
        or delivery["sent_history_count_exact"] != 1
        or delivery["durable_record_url"] != "https://github.com/psw2025-cmd/Genesis_System3/pull/472#issuecomment-6040287777"
        or delivery["source_observed_before_send"] is not True
        or delivery["qualified_candidates_at_send"] != 0
        or delivery["second_email_allowed"] is not False
    ):
        raise ValueError("Exactly-once delivery lock changed")

    retrievals = payload["retrievals"]
    if not isinstance(retrievals, list) or len(retrievals) != 3:
        raise ValueError("Exactly three successful retrieval observations are required")
    expected_roles = [
        "PRE_DELIVERY_FIRST_SUCCESS", "POST_DELIVERY_INDEPENDENT_REPEAT_1",
        "POST_DELIVERY_INDEPENDENT_REPEAT_2",
    ]
    observed_times: list[datetime] = []
    for index, item in enumerate(retrievals):
        if not isinstance(item, dict):
            raise ValueError("Retrieval observation must be an object")
        required = {
            "role", "request_started_at", "observed_at", "http_status",
            "response_bytes", "response_sha256", "content_type",
            "byte_identical_to_first_success",
        }
        if set(item) != required:
            raise ValueError("Retrieval observation fields changed")
        observed = _instant(item["observed_at"], "observed_at")
        if index == 0:
            if item["request_started_at"] is not None:
                raise ValueError("Uncaptured first request start must remain null")
            started = observed
        else:
            started = _instant(item["request_started_at"], "request_started_at")
        if started > observed:
            raise ValueError("Retrieval request ends before it starts")
        observed_times.append(observed)
        if (
            item["role"] != expected_roles[index] or item["http_status"] != 200
            or item["response_bytes"] != 1_086_658
            or _sha(item["response_sha256"], 64, "response_sha256") != ZIP_SHA256
            or item["content_type"] != "application/zip"
            or item["byte_identical_to_first_success"] is not (index > 0)
        ):
            raise ValueError("Retrieval identity or byte proof changed")
    if observed_times != sorted(observed_times) or evidence_at != observed_times[-1]:
        raise ValueError("Retrieval timeline or evidence_as_of changed")
    if not observed_times[0] < sent_at < observed_times[1] < observed_times[2] < target_open:
        raise ValueError("Source/delivery/repeat chronology is invalid")

    archive = payload["official_archive"]
    archive_fields = {
        "url", "zip_bytes", "zip_sha256", "raw_zip_path", "raw_zip_git_blob_sha",
        "server_date_header", "server_last_modified_header", "server_etag",
        "exchange_publication_time", "header_time_is_exchange_dissemination_time",
        "member", "member_timestamp_used_as_availability_proof", "csv_bytes",
        "csv_sha256", "csv_header", "source_rows", "instrument_type_rows",
        "trade_date", "business_date", "segment", "source", "session",
        "unique_instrument_ids", "duplicate_rows_by_instrument_id",
    }
    if not isinstance(archive, dict) or set(archive) != archive_fields:
        raise ValueError("Official archive metadata is incomplete")
    parsed = urlsplit(str(archive["url"]))
    if (
        archive["url"] != ARCHIVE_URL or parsed.scheme != "https"
        or parsed.hostname != "nsearchives.nseindia.com" or parsed.username
        or parsed.password or parsed.fragment or parsed.port not in (None, 443)
    ):
        raise ValueError("Archive URL is not the exact official NSE source")
    if archive["exchange_publication_time"] is not None:
        raise ValueError("HTTP metadata cannot invent exchange dissemination time")
    if archive["header_time_is_exchange_dissemination_time"] is not False:
        raise ValueError("HTTP header was promoted to dissemination time")
    if archive["member_timestamp_used_as_availability_proof"] is not False:
        raise ValueError("ZIP member timestamp cannot prove availability")
    server_date = _instant(archive["server_date_header"], "server date")
    server_modified = _instant(archive["server_last_modified_header"], "last-modified")
    repeat_started = _instant(retrievals[-1]["request_started_at"], "repeat start")
    if not repeat_started <= server_date <= observed_times[-1]:
        raise ValueError("Server date is not bound to the repeat request")
    if not server_modified < observed_times[0]:
        raise ValueError("Last-modified chronology changed")
    if archive["server_etag"] != 'W/"1086658-1791378242804"':
        raise ValueError("Server ETag changed")

    measured = _read_and_measure(_safe_file(repo_root, archive["raw_zip_path"]))
    archive_expected = {
        "zip_bytes": measured["zip_bytes"], "zip_sha256": measured["zip_sha256"],
        "raw_zip_git_blob_sha": measured["git_blob_sha"], "member": measured["member"],
        "csv_bytes": measured["csv_bytes"], "csv_sha256": measured["csv_sha256"],
        "csv_header": EXPECTED_HEADER, "source_rows": measured["source_rows"],
        "instrument_type_rows": measured["instrument_type_rows"],
        "trade_date": SOURCE_DATE, "business_date": SOURCE_DATE, "segment": "FO",
        "source": "NSE", "session": "F1",
        "unique_instrument_ids": measured["unique_instrument_ids"],
        "duplicate_rows_by_instrument_id": measured["duplicate_rows_by_instrument_id"],
    }
    for field, expected in archive_expected.items():
        if archive[field] != expected:
            raise ValueError(f"Archive measurement changed: {field}")
    if (
        measured["trade_dates"] != [SOURCE_DATE]
        or measured["business_dates"] != [SOURCE_DATE]
        or measured["segments"] != ["FO"] or measured["sources"] != ["NSE"]
        or measured["sessions"] != ["F1"]
    ):
        raise ValueError("CSV date/source/segment/session identity changed")

    universe = payload["mechanical_universe"]
    universe_fields = {
        "option_rows", "ce_rows", "pe_rows", "unique_exact_contract_keys",
        "duplicate_exact_contract_rows", "option_symbols", "option_expiries",
        "minimum_expiry", "maximum_expiry", "positive_volume_rows",
        "zero_volume_rows", "close_ge_1_and_volume_ge_100_rows", "screen_symbols",
        "screen_is_prediction", "screen_is_strategy_qualification",
    }
    if not isinstance(universe, dict) or set(universe) != universe_fields:
        raise ValueError("Mechanical universe fields changed")
    for field in universe_fields - {"screen_is_prediction", "screen_is_strategy_qualification"}:
        if universe[field] != measured[field]:
            raise ValueError(f"Mechanical universe measurement changed: {field}")
    if universe["screen_is_prediction"] is not False or universe["screen_is_strategy_qualification"] is not False:
        raise ValueError("Mechanical screen was promoted to a forecast")

    features = payload["feature_registry"]
    if not isinstance(features, list) or len(features) != len(FEATURE_IDS):
        raise ValueError("Feature registry is incomplete")
    by_id = {item.get("feature_id"): item for item in features if isinstance(item, dict)}
    if set(by_id) != FEATURE_IDS or len(by_id) != len(features):
        raise ValueError("Feature registry is duplicated or incomplete")
    feature_fields = {
        "feature_id", "source_fields", "available", "source_observed_at",
        "missing_count", "zero_count", "transformation", "version", "reason",
        "promotion_status",
    }
    unavailable = {
        "implied_volatility", "greeks_delta_gamma_theta_vega", "bid_ask_spread",
        "fees_and_slippage",
    }
    numeric_mapping = {
        "option_close": "ClsPric", "prior_close": "PrvsClsgPric",
        "traded_volume": "TtlTradgVol", "open_interest": "OpnIntrst",
        "change_in_open_interest": "ChngInOpnIntrst", "underlying_price": "UndrlygPric",
        "settlement_price": "SttlmPric", "board_lot_quantity": "NewBrdLotQty",
    }
    for feature_id, feature in by_id.items():
        if set(feature) != feature_fields or not feature["reason"]:
            raise ValueError(f"Feature metadata is incomplete: {feature_id}")
        if _instant(feature["source_observed_at"], "feature source") != observed_times[0]:
            raise ValueError("Feature timestamp is not point-in-time bound")
        if feature["version"] != SCHEMA:
            raise ValueError("Feature version changed")
        if feature_id in unavailable:
            if (
                feature["available"] is not False or feature["missing_count"] != measured["option_rows"]
                or feature["zero_count"] is not None
                or feature["transformation"] != "NOT_AVAILABLE_IN_SOURCE"
                or feature["promotion_status"] != "MISSING_NOT_IMPUTED"
            ):
                raise ValueError("Unavailable feature was silently imputed")
        elif feature["available"] is not True or feature["missing_count"] != 0:
            raise ValueError("Available feature missingness changed")
        if feature_id in numeric_mapping:
            field = numeric_mapping[feature_id]
            if feature["zero_count"] != measured["zeros"][field]:
                raise ValueError(f"Feature zero count changed: {feature_id}")
        if feature_id == "option_ohl" and feature["zero_count"] != measured["zeros"]["OpnPric"]:
            raise ValueError("Option OHL zero count changed")

    forward = payload["forward_state"]
    forward_fields = {
        "qualified_candidates", "issued_contract_forecasts", "matured_forward_outcomes",
        "positive_forecasts", "negative_forecasts", "expected_premium_move_range",
        "uncertainty", "source_backfilled_into_prior_decision",
        "historical_screen_promoted_to_forecast",
    }
    if not isinstance(forward, dict) or set(forward) != forward_fields:
        raise ValueError("Forward state fields changed")
    if any(forward[field] != 0 for field in (
        "qualified_candidates", "issued_contract_forecasts", "matured_forward_outcomes",
        "positive_forecasts", "negative_forecasts",
    )):
        raise ValueError("Source receipt cannot fabricate a forward forecast")
    if forward["expected_premium_move_range"] is not None or forward["uncertainty"] != "NOT_PROVEN":
        raise ValueError("Unqualified source cannot create a premium range")
    if forward["source_backfilled_into_prior_decision"] is not False or forward["historical_screen_promoted_to_forecast"] is not False:
        raise ValueError("Historical source was backfilled or promoted")

    gates = payload["gate_status"]
    expected_targets = {
        "minimum_oos_trades": 100, "minimum_oos_days": 60,
        "minimum_directional_accuracy": 0.65, "minimum_top_decile_precision": 0.70,
        "minimum_sharpe": 2.5, "maximum_drawdown": 0.10,
        "minimum_deflated_sharpe_probability": 0.95,
    }
    if not isinstance(gates, dict) or any(gates.get(k) != v for k, v in expected_targets.items()):
        raise ValueError("Project gate thresholds changed")
    if gates.get("valid_forward_trades") != 0 or gates.get("valid_forward_days") != 0:
        raise ValueError("Forward sample was fabricated")
    if gates.get("trade_gap") != 100 or gates.get("day_gap") != 60:
        raise ValueError("Forward sample gaps changed")
    if gates.get("instrument_horizon_definition") != {
        "instrument": "NSE_FO_OPTION_EXACT_SYMBOL_EXPIRY_STRIKE_SIDE",
        "entry_reference": "2026-10-07_OFFICIAL_CLOSE_NOT_EXECUTABLE_FILL",
        "outcome_reference": "2026-10-08_OFFICIAL_OPEN_NOT_EXECUTABLE_FILL",
        "distribution": "FULL_UNCAPPED_NEXT_OPEN_MULTIPLE_WITH_3X_10X_20X_30X_COUNTS",
    }:
        raise ValueError("Instrument or horizon definition changed")
    if gates.get("frozen_q2_baseline") != {
        "directional_accuracy": 0.586441,
        "minimum_directional_accuracy": 0.65,
        "gap_percentage_points": 6.3559,
        "valid_outcome_days": 59,
        "minimum_oos_days": 60,
        "day_gap": 1,
        "top_decile_precision": None,
        "cost_aware_sharpe": None,
        "max_drawdown": None,
        "deflated_sharpe_probability": None,
        "status": "TARGET_FAIL",
    }:
        raise ValueError("Frozen Q2 baseline or numerical gap changed")
    if not gates.get("hypothesis") or not gates.get("next_experiment"):
        raise ValueError("Gap-loop hypothesis or next experiment is missing")
    for field in (
        "directional_accuracy", "top_decile_precision", "sharpe", "max_drawdown",
        "deflated_sharpe_probability", "benchmark_excess", "calibration_error",
    ):
        if gates.get(field) is not None:
            raise ValueError("Unevaluated metrics must remain null")
    if gates.get("strategy_promoted") is not False or gates.get("frozen_test_retuned") is not False:
        raise ValueError("Unevaluated strategy cannot be promoted or retuned")

    for field in (
        "opening_price_is_executable_fill", "fees_slippage_applied", "real_money_ready",
        "live_trading_enabled", "orders_allowed",
    ):
        if payload[field] is not False:
            raise ValueError(f"Unsafe or dishonest flag: {field}")
    if payload["interpretation"] != "OFFICIAL_SOURCE_BYTES_RETAINED_NO_FORECAST_ISSUED":
        raise ValueError("Evidence interpretation changed")

    return {
        "task_id": TASK_ID,
        "status": "OFFICIAL_PRE_DELIVERY_SOURCE_RETAINED_AND_REPLAYED",
        "source_session_date": SOURCE_DATE,
        "target_open_at": target_open.isoformat(),
        "first_successfully_observed_at": observed_times[0].isoformat(),
        "zip_sha256": measured["zip_sha256"],
        "csv_sha256": measured["csv_sha256"],
        "source_rows": measured["source_rows"],
        "option_rows": measured["option_rows"],
        "mechanically_screened_observations": measured["close_ge_1_and_volume_ge_100_rows"],
        "qualified_candidates": 0,
        "issued_contract_forecasts": 0,
        "matured_forward_outcomes": 0,
        "second_email_allowed": False,
        "receipt_sha256": sha256(_canonical(payload)).hexdigest(),
        "orders_allowed": False,
    }
