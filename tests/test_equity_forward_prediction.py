"""Synthetic chronology and honesty tests; these do not validate alpha."""
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from io import BytesIO
import csv
import io
import json
from zipfile import ZipFile

import pytest

from scripts.equity_forward_prediction import (
    GENESIS_HASH,
    HOLIDAY_URL,
    build_prediction,
    validate_prediction,
)
from scripts.equity_instrument_scope import EQUITY_URL, ETF_URL
from scripts.equity_observation_packet import CM_URL


ISSUED = "2026-10-01T12:45:00Z"
NOW = datetime(2026, 10, 1, 13, tzinfo=timezone.utc)
MEMBER = "BhavCopy_NSE_CM_0_0_0_20261001_F_0000.csv"
FIELDS = "TradDt,BizDt,Sgmt,Src,FinInstrmTp,ISIN,TckrSymb,SctySrs,SsnId,OpnPric,HghPric,LwPric,ClsPric,TtlTradgVol".split(",")


def receipt(raw, url, observed="2026-10-01T12:40:00Z"):
    return {
        "url": url,
        "final_url": url,
        "http_status": 200,
        "raw_sha256": sha256(raw).hexdigest(),
        "bytes": len(raw),
        "first_observed_at": observed,
    }


def zipped(rows):
    text = io.StringIO()
    writer = csv.DictWriter(text, fieldnames=FIELDS)
    writer.writeheader()
    writer.writerows(rows)
    raw = BytesIO()
    with ZipFile(raw, "w") as archive:
        archive.writestr(MEMBER, text.getvalue())
    return raw.getvalue()


def fixture():
    rows = [
        dict(zip(FIELDS, ["2026-10-01", "2026-10-01", "CM", "NSE", "STK", "INE000A01001", "AAA", "EQ", "F1", "100", "115", "99", "110", "2000000"])),
        dict(zip(FIELDS, ["2026-10-01", "2026-10-01", "CM", "NSE", "STK", "INE000B01009", "BBB", "EQ", "F1", "100", "106", "99", "105", "3000000"])),
    ]
    cash = zipped(rows)
    company = b"SYMBOL,ISIN NUMBER,SERIES\nAAA,INE000A01001,EQ\nBBB,INE000B01009,EQ\n"
    etf = b"Symbol,ISINNumber\nTRACK,INETRACK\n"
    actions = json.dumps([{"symbol": "ZZZ", "isin": "INE000Z01003", "exDate": "05-Oct-2026", "subject": "Dividend"}]).encode()
    equity_sources = {"cash": cash, "company": company, "etf": etf, "actions": actions}
    action_url = "https://www.nseindia.com/api/corporates-corporateActions?index=equities&from_date=01-10-2026&to_date=09-10-2026"
    equity_receipts = {
        "cash": receipt(cash, CM_URL + MEMBER + ".zip"),
        "company": receipt(company, EQUITY_URL),
        "etf": receipt(etf, ETF_URL),
        "actions": receipt(actions, action_url),
    }
    index = (
        "Index Name,Index Date,Open Index Value,High Index Value,Low Index Value,Closing Index Value\n"
        "Nifty 50,01-10-2026,22000,22200,21900,22100\n"
    ).encode()
    index_url = "https://nsearchives.nseindia.com/content/indices/ind_close_all_01102026.csv"
    holiday = json.dumps({"CM": [{"tradingDate": "02-Oct-2026"}]}).encode()
    model = json.dumps({
        "schema": "equity-forward-experiment-v1",
        "experiment_id": "EQ-FWD-RANK-001",
        "strategy_id": "EQUITY_INTRADAY_MOMENTUM_LIQUIDITY",
        "strategy_version": "1.0.0",
        "status": "EXPLORATORY_FORWARD_ONLY",
        "registered_at": "2026-10-01T12:41:00Z",
        "horizon": {"calendar_days": 7},
        "universe": {"minimum_close_inr": "10", "minimum_close_times_volume_inr": "100000000"},
        "selection": {"score": "0.5*intraday_return_percent_rank + 0.5*liquidity_proxy_percent_rank"},
    }, sort_keys=True).encode()
    return dict(
        equity_sources=equity_sources,
        equity_receipts=equity_receipts,
        index_raw=index,
        index_receipt=receipt(index, index_url),
        holiday_raw=holiday,
        holiday_receipt=receipt(holiday, HOLIDAY_URL),
        model_spec_raw=model,
        issued_at=ISSUED,
        now=NOW,
        previous_event_hash=GENESIS_HASH,
    )


def test_builds_one_unqualified_forward_paper_prediction():
    args = fixture()
    result = build_prediction(**args)
    assert result["prediction"]["symbol"] == "AAA"
    assert result["prediction"]["direction"] == "POSITIVE"
    assert result["prediction"]["entry_reference_close"] == "110"
    assert result["prediction"]["entry_reference_is_executable_fill"] is False
    assert result["prediction"]["adjusted_entry_price"] is None
    assert result["prediction"]["expected_return_range"] is None
    assert result["counts"]["screened_candidates"] == 2
    assert result["counts"]["qualified_current_candidates"] == 0
    assert result["counts"]["forward_predictions"] == 1
    assert result["due_session_date"] == "2026-10-08"
    assert validate_prediction(
        result,
        now=NOW,
        holiday_calendar_raw=args["holiday_raw"],
        model_spec_raw=args["model_spec_raw"],
        expected_previous_event_hash=args["previous_event_hash"],
    )["orders_allowed"] is False


@pytest.mark.parametrize(
    "path,value,match",
    [
        (("source_cutoff_at",), "2026-10-01T12:46:00Z", "chronology"),
        (("counts", "qualified_current_candidates"), 1, "overstate"),
        (("prediction", "expected_return_range"), [1, 2], "range"),
        (("prediction", "entry_reference_is_executable_fill"), True, "executable"),
        (("safety", "orders_allowed"), True, "Unsafe"),
    ],
)
def test_stored_record_fails_closed(path, value, match):
    args = fixture()
    result = build_prediction(**args)
    target = result
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    with pytest.raises(ValueError, match=match):
        validate_prediction(
            result,
            now=NOW,
            holiday_calendar_raw=args["holiday_raw"],
            model_spec_raw=args["model_spec_raw"],
        )


def test_event_and_feature_hashes_are_immutable():
    args = fixture()
    result = build_prediction(**args)
    result["prediction"]["features"]["volume"] += 1
    with pytest.raises(ValueError, match="Feature hash"):
        validate_prediction(
            result,
            now=NOW,
            holiday_calendar_raw=args["holiday_raw"],
            model_spec_raw=args["model_spec_raw"],
        )
    args = fixture()
    result = build_prediction(**args)
    result["prediction"]["symbol"] = "BBB"
    with pytest.raises(ValueError, match="identity|event hash"):
        validate_prediction(
            result,
            now=NOW,
            holiday_calendar_raw=args["holiday_raw"],
            model_spec_raw=args["model_spec_raw"],
        )


@pytest.mark.parametrize(
    "field,value",
    [
        ("intraday_return", "9.0000000000"),
        ("close_times_volume_inr", "1.00"),
        ("selection_score", "0.0100000000"),
    ],
)
def test_rehashed_fabricated_feature_arithmetic_fails_closed(field, value):
    args = fixture()
    result = build_prediction(**args)
    features = result["prediction"]["features"]
    features[field] = value
    result["prediction"]["feature_hash"] = sha256(json.dumps(
        features, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode()).hexdigest()
    rehash(result)
    with pytest.raises(ValueError, match="Feature arithmetic mismatch"):
        validate_prediction(
            result,
            now=NOW,
            holiday_calendar_raw=args["holiday_raw"],
            model_spec_raw=args["model_spec_raw"],
        )


def rehash(result):
    payload = {key: value for key, value in result.items() if key != "event_hash"}
    result["event_hash"] = sha256(json.dumps(
        payload, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode()).hexdigest()


def test_stored_prediction_requires_trusted_predecessor_anchor():
    args = fixture()
    result = build_prediction(**args)
    with pytest.raises(ValueError, match="previous event hash evidence required"):
        validate_prediction(
            result,
            now=NOW,
            holiday_calendar_raw=args["holiday_raw"],
            model_spec_raw=args["model_spec_raw"],
        )

    result["previous_event_hash"] = "1" * 64
    rehash(result)
    with pytest.raises(ValueError, match="trusted predecessor"):
        validate_prediction(
            result,
            now=NOW,
            holiday_calendar_raw=args["holiday_raw"],
            model_spec_raw=args["model_spec_raw"],
            expected_previous_event_hash=GENESIS_HASH,
        )


@pytest.mark.parametrize(
    "mutate,match",
    [
        (lambda row: row["prediction"].update(broker_order="BUY"), "Prediction fields"),
        (lambda row: row["source_receipts"].update(secret_feed={}), "receipt roles"),
        (lambda row: row["source_receipts"]["cash"].update(url="https://example.com/a"), "source URL"),
        (lambda row: row["current_metrics"].update(directional_accuracy=1), "performance metrics"),
        (lambda row: row["action_policy"].update(maturity_recheck_required=False), "recheck"),
    ],
)
def test_rehashed_hidden_claims_and_source_changes_fail_closed(mutate, match):
    args = fixture()
    result = build_prediction(**args)
    mutate(result)
    rehash(result)
    with pytest.raises(ValueError, match=match):
        validate_prediction(
            result,
            now=NOW,
            holiday_calendar_raw=args["holiday_raw"],
            model_spec_raw=args["model_spec_raw"],
        )


@pytest.mark.parametrize(
    "mutate,match",
    [
        (
            lambda row: row.update(due_at="2026-10-08T03:45:00+00:00"),
            "due close timestamp",
        ),
        (
            lambda row: row.update(
                due_session_date="2026-10-09",
                due_at="2026-10-09T10:00:00+00:00",
            ),
            "retained official calendar",
        ),
    ],
)
def test_rehashed_horizon_timestamp_or_session_substitution_fails_closed(
    mutate,
    match,
):
    args = fixture()
    result = build_prediction(**args)
    mutate(result)
    rehash(result)
    with pytest.raises(ValueError, match=match):
        validate_prediction(
            result,
            now=NOW,
            holiday_calendar_raw=args["holiday_raw"],
            model_spec_raw=args["model_spec_raw"],
        )


def test_stored_prediction_requires_exact_registered_model_bytes():
    args = fixture()
    result = build_prediction(**args)
    with pytest.raises(ValueError, match="model specification bytes required"):
        validate_prediction(
            result,
            now=NOW,
            holiday_calendar_raw=args["holiday_raw"],
        )
    with pytest.raises(ValueError, match="retained bytes mismatch"):
        validate_prediction(
            result,
            now=NOW,
            holiday_calendar_raw=args["holiday_raw"],
            model_spec_raw=args["model_spec_raw"] + b"\n",
        )
    result["strategy"]["model_spec_sha256"] = "0" * 64
    rehash(result)
    with pytest.raises(ValueError, match="retained bytes mismatch"):
        validate_prediction(
            result,
            now=NOW,
            holiday_calendar_raw=args["holiday_raw"],
            model_spec_raw=args["model_spec_raw"],
        )


def test_model_registration_after_issue_fails_builder_and_stored_record():
    args = fixture()
    result = build_prediction(**args)
    future_model = json.loads(args["model_spec_raw"])
    future_model["registered_at"] = "2026-10-01T12:46:00Z"
    future_raw = json.dumps(future_model, sort_keys=True).encode()
    with pytest.raises(ValueError, match="registered after prediction issue"):
        build_prediction(**{**args, "model_spec_raw": future_raw})
    result["strategy"]["model_spec_sha256"] = sha256(future_raw).hexdigest()
    rehash(result)
    with pytest.raises(ValueError, match="registered after prediction issue"):
        validate_prediction(
            result,
            now=NOW,
            holiday_calendar_raw=args["holiday_raw"],
            model_spec_raw=future_raw,
        )


def test_stored_prediction_requires_exact_retained_calendar_bytes():
    args = fixture()
    result = build_prediction(**args)
    with pytest.raises(ValueError, match="calendar bytes required"):
        validate_prediction(
            result,
            now=NOW,
            model_spec_raw=args["model_spec_raw"],
        )
    with pytest.raises(ValueError, match="retained bytes mismatch"):
        validate_prediction(
            result,
            now=NOW,
            holiday_calendar_raw=b'{"CM":[]}',
            model_spec_raw=args["model_spec_raw"],
        )


def test_stored_prediction_cannot_validate_before_issuance():
    args = fixture()
    result = build_prediction(**args)
    with pytest.raises(ValueError, match="issue is in the future"):
        validate_prediction(
            result,
            now=datetime(2026, 9, 30, 12, tzinfo=timezone.utc),
            holiday_calendar_raw=args["holiday_raw"],
            model_spec_raw=args["model_spec_raw"],
        )


@pytest.mark.parametrize(
    "issued_at,now,match",
    [
        (
            "2026-10-07T12:45:00+00:00",
            datetime(2026, 10, 2, 0, tzinfo=timezone.utc),
            "issue is in the future",
        ),
        (
            "2026-10-02T12:45:00+00:00",
            datetime(2026, 10, 2, 13, tzinfo=timezone.utc),
            "completed entry-session close",
        ),
    ],
)
def test_rehashed_issuance_must_be_observed_and_bind_entry_session(
    issued_at,
    now,
    match,
):
    args = fixture()
    result = build_prediction(**args)
    result["issued_at"] = issued_at
    rehash(result)
    with pytest.raises(ValueError, match=match):
        validate_prediction(
            result,
            now=now,
            holiday_calendar_raw=args["holiday_raw"],
            model_spec_raw=args["model_spec_raw"],
        )


def test_rejects_source_observed_after_issue_and_wrong_hash():
    args = fixture()
    args["index_receipt"]["first_observed_at"] = "2026-10-01T12:46:00Z"
    with pytest.raises(ValueError, match="after issuance"):
        build_prediction(**args)
    args = fixture()
    args["holiday_receipt"]["raw_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="receipt mismatch"):
        build_prediction(**args)


def test_selected_symbol_with_future_action_is_excluded():
    args = fixture()
    actions = json.dumps([{"symbol": "AAA", "isin": "INE000A01001", "exDate": "05-Oct-2026", "subject": "Dividend"}]).encode()
    args["equity_sources"]["actions"] = actions
    args["equity_receipts"]["actions"].update(raw_sha256=sha256(actions).hexdigest(), bytes=len(actions))
    result = build_prediction(**args)
    assert result["prediction"]["symbol"] == "BBB"


def test_holiday_rolls_due_session_forward():
    args = fixture()
    holiday = json.dumps({"CM": [{"tradingDate": "08-Oct-2026"}]}).encode()
    args["holiday_raw"] = holiday
    args["holiday_receipt"] = receipt(holiday, HOLIDAY_URL)
    result = build_prediction(**args)
    assert result["due_session_date"] == "2026-10-09"
