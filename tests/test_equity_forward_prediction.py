"""Synthetic chronology and honesty tests; these do not validate alpha."""
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from io import BytesIO
import csv
import io
import json
from pathlib import Path
from zipfile import ZipFile

import pytest

from dashboard.backend.multibagger_outcome import (
    OutcomeLedgerError,
    build_directional_outcome_projection,
    reconcile_directional_reference,
    validate_directional_outcome_projection,
    verify_directional_projection_evidence,
)
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


def outcome_archive(
    trade_date="2026-10-08",
    symbol="AAA",
    isin="INE000A01001",
    close="121",
):
    stamp = trade_date.replace("-", "")
    member = f"BhavCopy_NSE_CM_0_0_0_{stamp}_F_0000.csv"
    row = dict(
        zip(
            FIELDS,
            [
                trade_date,
                trade_date,
                "CM",
                "NSE",
                "STK",
                isin,
                symbol,
                "EQ",
                "F1",
                "120",
                "122",
                "119",
                close,
                "2000000",
            ],
        )
    )
    text = io.StringIO()
    writer = csv.DictWriter(text, fieldnames=FIELDS)
    writer.writeheader()
    writer.writerow(row)
    raw = BytesIO()
    with ZipFile(raw, "w") as archive:
        archive.writestr(member, text.getvalue())
    return (
        raw.getvalue(),
        "https://nsearchives.nseindia.com/content/cm/" + member + ".zip",
    )


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


def retained_sources(args):
    return {
        "equity_source_bytes": args["equity_sources"],
        "index_source_raw": args["index_raw"],
    }


def retained_uris():
    return {
        role: f"snapshots/fixture/{role}.bin"
        for role in (
            "cash",
            "company",
            "etf",
            "actions",
            "index",
            "holiday_calendar",
            "model_spec",
        )
    }


def build_projection(args=None):
    args = args or fixture()
    prediction = build_prediction(**args)
    projection = build_directional_outcome_projection(
        prediction,
        equity_source_bytes=args["equity_sources"],
        index_source_raw=args["index_raw"],
        holiday_calendar_raw=args["holiday_raw"],
        model_spec_raw=args["model_spec_raw"],
        expected_previous_event_hash=args["previous_event_hash"],
        retained_source_uris=retained_uris(),
        now=NOW,
    )
    return args, prediction, projection


def rehash_projection(projection):
    payload = {
        key: value
        for key, value in projection.items()
        if key != "projection_hash"
    }
    projection["projection_hash"] = sha256(json.dumps(
        payload, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode()).hexdigest()


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
        **retained_sources(args),
        holiday_calendar_raw=args["holiday_raw"],
        model_spec_raw=args["model_spec_raw"],
        expected_previous_event_hash=args["previous_event_hash"],
    )["orders_allowed"] is False


def test_builder_requires_explicit_predecessor_anchor():
    args = fixture()
    args.pop("previous_event_hash")
    with pytest.raises(TypeError, match="previous_event_hash"):
        build_prediction(**args)


def test_stored_prediction_requires_external_primary_source_bytes():
    args = fixture()
    result = build_prediction(**args)
    with pytest.raises(ValueError, match="retained equity source bytes required"):
        validate_prediction(
            result,
            now=NOW,
            index_source_raw=args["index_raw"],
            holiday_calendar_raw=args["holiday_raw"],
            model_spec_raw=args["model_spec_raw"],
            expected_previous_event_hash=args["previous_event_hash"],
        )
    with pytest.raises(ValueError, match="retained index source bytes required"):
        validate_prediction(
            result,
            now=NOW,
            equity_source_bytes=args["equity_sources"],
            holiday_calendar_raw=args["holiday_raw"],
            model_spec_raw=args["model_spec_raw"],
            expected_previous_event_hash=args["previous_event_hash"],
        )


@pytest.mark.parametrize("role", ["cash", "company", "etf", "actions"])
def test_stored_prediction_rejects_substituted_equity_source_bytes(role):
    args = fixture()
    result = build_prediction(**args)
    substituted = dict(args["equity_sources"])
    substituted[role] += b"\n"
    with pytest.raises(ValueError, match=rf"{role} retained source bytes mismatch"):
        validate_prediction(
            result,
            now=NOW,
            equity_source_bytes=substituted,
            index_source_raw=args["index_raw"],
            holiday_calendar_raw=args["holiday_raw"],
            model_spec_raw=args["model_spec_raw"],
            expected_previous_event_hash=args["previous_event_hash"],
        )


def test_stored_prediction_rejects_substituted_index_source_bytes():
    args = fixture()
    result = build_prediction(**args)
    with pytest.raises(ValueError, match="index retained source bytes mismatch"):
        validate_prediction(
            result,
            now=NOW,
            equity_source_bytes=args["equity_sources"],
            index_source_raw=args["index_raw"] + b"\n",
            holiday_calendar_raw=args["holiday_raw"],
            model_spec_raw=args["model_spec_raw"],
            expected_previous_event_hash=args["previous_event_hash"],
        )


def test_rehashed_fabricated_cash_receipt_fails_external_replay():
    args = fixture()
    result = build_prediction(**args)
    result["source_receipts"]["cash"].update(
        url="https://nsearchives.nseindia.com/content/cm/fabricated.zip",
        sha256="f" * 64,
        bytes=1,
    )
    rehash(result)
    with pytest.raises(ValueError, match="cash retained source bytes mismatch"):
        validate_prediction(
            result,
            now=NOW,
            **retained_sources(args),
            holiday_calendar_raw=args["holiday_raw"],
            model_spec_raw=args["model_spec_raw"],
            expected_previous_event_hash=args["previous_event_hash"],
        )


def test_rehashed_row_or_benchmark_substitution_fails_source_replay():
    args = fixture()
    result = build_prediction(**args)
    result["prediction"]["features"]["source_row_sha256"] = "f" * 64
    result["prediction"]["feature_hash"] = sha256(
        json.dumps(
            result["prediction"]["features"],
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode()
    ).hexdigest()
    rehash(result)
    with pytest.raises(ValueError, match="retained source replay"):
        validate_prediction(
            result,
            now=NOW,
            **retained_sources(args),
            holiday_calendar_raw=args["holiday_raw"],
            model_spec_raw=args["model_spec_raw"],
            expected_previous_event_hash=args["previous_event_hash"],
        )

    result = build_prediction(**args)
    result["benchmark"]["entry_reference_close"] = "99999"
    rehash(result)
    with pytest.raises(ValueError, match="retained index replay"):
        validate_prediction(
            result,
            now=NOW,
            **retained_sources(args),
            holiday_calendar_raw=args["holiday_raw"],
            model_spec_raw=args["model_spec_raw"],
            expected_previous_event_hash=args["previous_event_hash"],
        )


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
            **retained_sources(args),
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
            **retained_sources(args),
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
            **retained_sources(args),
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
            **retained_sources(args),
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
            **retained_sources(args),
            holiday_calendar_raw=args["holiday_raw"],
            model_spec_raw=args["model_spec_raw"],
        )

    result["previous_event_hash"] = "1" * 64
    rehash(result)
    with pytest.raises(ValueError, match="trusted predecessor"):
        validate_prediction(
            result,
            now=NOW,
            **retained_sources(args),
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
            **retained_sources(args),
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
            **retained_sources(args),
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
            **retained_sources(args),
            holiday_calendar_raw=args["holiday_raw"],
        )
    with pytest.raises(ValueError, match="retained bytes mismatch"):
        validate_prediction(
            result,
            now=NOW,
            **retained_sources(args),
            holiday_calendar_raw=args["holiday_raw"],
            model_spec_raw=args["model_spec_raw"] + b"\n",
        )
    result["strategy"]["model_spec_sha256"] = "0" * 64
    rehash(result)
    with pytest.raises(ValueError, match="retained bytes mismatch"):
        validate_prediction(
            result,
            now=NOW,
            **retained_sources(args),
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
            **retained_sources(args),
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
            **retained_sources(args),
            model_spec_raw=args["model_spec_raw"],
        )
    with pytest.raises(ValueError, match="retained bytes mismatch"):
        validate_prediction(
            result,
            now=NOW,
            **retained_sources(args),
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
            **retained_sources(args),
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
            **retained_sources(args),
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


def test_direction_only_projection_preserves_pending_honest_state():
    _, prediction, projection = build_projection()
    assert projection["prediction_event_hash"] == prediction["event_hash"]
    assert projection["forecast_kind"] == "DIRECTION_ONLY"
    assert projection["forecast_direction"] == "POSITIVE"
    assert projection["predicted_return_pct"] is None
    assert projection["expected_return_range"] is None
    assert projection["calibrated_probability"] is None
    assert projection["adjusted_entry_price"] is None
    assert projection["adjustment_status"] == "PENDING_MATURITY_RECHECK"
    assert projection["adjustment_basis"] is None
    assert projection["outcome_status"] == "PENDING"
    assert projection["reference_prices_are_executable_fills"] is False
    assert projection["performance_metrics_available"] is False
    assert projection["real_money_ready"] is False
    assert projection["live_trading_enabled"] is False
    assert projection["order_placement_allowed"] is False
    status = validate_directional_outcome_projection(projection)
    assert status["status"] == (
        "DIRECTIONAL_FORECAST_PROJECTED_PENDING_MATURITY"
    )
    assert status["matured_outcomes"] == 0
    assert status["predicted_return_pct"] is None


@pytest.mark.parametrize(
    "mutate,match",
    [
        (
            lambda row: row.update(predicted_return_pct=20),
            "NUMERIC_FORECAST_INVENTED",
        ),
        (
            lambda row: row.update(
                reference_prices_are_executable_fills=True
            ),
            "REFERENCE_PRICES_ARE_EXECUTABLE_FILLS_INVALID",
        ),
        (
            lambda row: row.update(performance_metrics_available=True),
            "PERFORMANCE_METRICS_AVAILABLE_INVALID",
        ),
        (
            lambda row: row.update(adjustment_basis="assumed-none"),
            "ADJUSTMENT_BASIS_PREMATURE",
        ),
    ],
)
def test_rehashed_direction_projection_rejects_invented_claims(mutate, match):
    _, _, projection = build_projection()
    mutate(projection)
    rehash_projection(projection)
    with pytest.raises(OutcomeLedgerError, match=match):
        validate_directional_outcome_projection(projection)


def test_direction_projection_rejects_substituted_source_and_predecessor():
    args = fixture()
    prediction = build_prediction(**args)
    substituted = dict(args["equity_sources"])
    substituted["cash"] += b"\n"
    with pytest.raises(OutcomeLedgerError, match="cash retained source bytes"):
        build_directional_outcome_projection(
            prediction,
            equity_source_bytes=substituted,
            index_source_raw=args["index_raw"],
            holiday_calendar_raw=args["holiday_raw"],
            model_spec_raw=args["model_spec_raw"],
            expected_previous_event_hash=args["previous_event_hash"],
            retained_source_uris=retained_uris(),
            now=NOW,
        )
    with pytest.raises(OutcomeLedgerError, match="trusted predecessor"):
        build_directional_outcome_projection(
            prediction,
            equity_source_bytes=args["equity_sources"],
            index_source_raw=args["index_raw"],
            holiday_calendar_raw=args["holiday_raw"],
            model_spec_raw=args["model_spec_raw"],
            expected_previous_event_hash="1" * 64,
            retained_source_uris=retained_uris(),
            now=NOW,
        )


def test_direction_projection_rejects_missing_or_traversing_source_uri():
    args = fixture()
    prediction = build_prediction(**args)
    missing = retained_uris()
    missing.pop("model_spec")
    with pytest.raises(OutcomeLedgerError, match="URI_ROLES"):
        build_directional_outcome_projection(
            prediction,
            equity_source_bytes=args["equity_sources"],
            index_source_raw=args["index_raw"],
            holiday_calendar_raw=args["holiday_raw"],
            model_spec_raw=args["model_spec_raw"],
            expected_previous_event_hash=args["previous_event_hash"],
            retained_source_uris=missing,
            now=NOW,
        )
    traversing = retained_uris()
    traversing["cash"] = "snapshots/fixture/../cash.zip"
    with pytest.raises(OutcomeLedgerError, match="SNAPSHOT_URI_INVALID"):
        build_directional_outcome_projection(
            prediction,
            equity_source_bytes=args["equity_sources"],
            index_source_raw=args["index_raw"],
            holiday_calendar_raw=args["holiday_raw"],
            model_spec_raw=args["model_spec_raw"],
            expected_previous_event_hash=args["previous_event_hash"],
            retained_source_uris=traversing,
            now=NOW,
        )


def test_direction_projection_rechecks_all_retained_source_bytes(tmp_path):
    args, _, projection = build_projection()
    raw_by_role = {
        **args["equity_sources"],
        "index": args["index_raw"],
        "holiday_calendar": args["holiday_raw"],
        "model_spec": args["model_spec_raw"],
    }
    for role, raw in raw_by_role.items():
        path = tmp_path / projection["source_bindings"][role]["snapshot_uri"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    verify_directional_projection_evidence(
        projection,
        evidence_root=tmp_path,
    )
    cash_path = (
        tmp_path / projection["source_bindings"]["cash"]["snapshot_uri"]
    )
    cash_path.write_bytes(cash_path.read_bytes() + b"\n")
    with pytest.raises(OutcomeLedgerError, match="HASH_OR_SIZE_MISMATCH"):
        verify_directional_projection_evidence(
            projection,
            evidence_root=tmp_path,
        )


def directional_outcome(close="121"):
    raw, url = outcome_archive(close=close)
    return {
        "symbol": "AAA",
        "isin": "INE000A01001",
        "price_as_of_at": "2026-10-08T10:00:00+00:00",
        "source_exchange_published_at": None,
        "source_first_observed_at": "2026-10-08T10:05:00+00:00",
        "reference_close": close,
        "source": "NSE",
        "source_url": url,
        "source_hash": sha256(raw).hexdigest(),
        "source_snapshot": raw,
        "source_snapshot_uri": "snapshots/fixture/outcome_cash.zip",
        "price_basis": "UNADJUSTED_EXCHANGE_REFERENCE",
    }


def test_directional_reference_replays_raw_close_without_scoring_outcome():
    args, _, projection = build_projection()
    result = reconcile_directional_reference(
        projection,
        directional_outcome(),
        entry_source_snapshot=args["equity_sources"]["cash"],
        now=datetime(2026, 10, 8, 10, 6, tzinfo=timezone.utc),
    )
    assert result["status"] == (
        "RAW_REFERENCE_OBSERVED_ADJUSTMENT_REVIEW_PENDING"
    )
    assert result["raw_actual_return_pct"] == 10.0
    assert result["raw_reference_direction"] == "POSITIVE"
    assert result["predicted_return_pct"] is None
    assert result["actual_return_pct"] is None
    assert result["absolute_error_pp"] is None
    assert result["direction_correct"] is None
    assert result["matured_outcomes"] == 0
    assert result["adjustment_basis"] is None
    assert result["source_availability_status"] == (
        "FIRST_OBSERVED_ONLY_EXCHANGE_PUBLICATION_NOT_PROVEN"
    )
    assert result["reference_prices_are_executable_fills"] is False
    assert result["performance_metrics_available"] is False
    assert result["real_money_ready"] is False
    assert result["order_placement_allowed"] is False


def test_directional_reference_rejects_before_exact_horizon():
    args, _, projection = build_projection()
    result = reconcile_directional_reference(
        projection,
        directional_outcome(),
        entry_source_snapshot=args["equity_sources"]["cash"],
        now=datetime(2026, 10, 7, 14, 0, tzinfo=timezone.utc),
    )
    assert result == {"status": "NOT_PROVEN", "reason": "OUTCOME_NOT_MATURED"}


@pytest.mark.parametrize(
    "mutate,reason",
    [
        (
            lambda row: row.update(reference_close="999"),
            "OUTCOME_PRICE_EVIDENCE_MISMATCH",
        ),
        (
            lambda row: row.update(price_as_of_at="2026-10-09T10:00:00+00:00"),
            "OUTCOME_HORIZON_MISMATCH",
        ),
        (
            lambda row: row.update(
                source_first_observed_at="2026-10-08T09:59:00+00:00"
            ),
            "OUTCOME_SOURCE_TIME_ORDER_INVALID",
        ),
        (
            lambda row: row.update(adjustment_basis="assumed-none"),
            "OUTCOME_FIELDS_INVALID",
        ),
    ],
)
def test_directional_reference_rejects_unbound_or_premature_claims(
    mutate,
    reason,
):
    args, _, projection = build_projection()
    outcome = directional_outcome()
    mutate(outcome)
    result = reconcile_directional_reference(
        projection,
        outcome,
        entry_source_snapshot=args["equity_sources"]["cash"],
        now=datetime(2026, 10, 8, 10, 6, tzinfo=timezone.utc),
    )
    assert result == {"status": "NOT_PROVEN", "reason": reason}


def test_directional_reference_rejects_unproven_exchange_publication_time():
    args, _, projection = build_projection()
    outcome = directional_outcome()
    outcome["source_exchange_published_at"] = (
        "2026-10-08T10:01:00+00:00"
    )
    result = reconcile_directional_reference(
        projection,
        outcome,
        entry_source_snapshot=args["equity_sources"]["cash"],
        now=datetime(2026, 10, 8, 10, 6, tzinfo=timezone.utc),
    )
    assert result == {
        "status": "NOT_PROVEN",
        "reason": "OUTCOME_EXCHANGE_PUBLICATION_TIME_NOT_PROVEN",
    }


def test_directional_reference_rejects_replaced_entry_bytes():
    _, _, projection = build_projection()
    result = reconcile_directional_reference(
        projection,
        directional_outcome(),
        entry_source_snapshot=b"replaced",
        now=datetime(2026, 10, 8, 10, 6, tzinfo=timezone.utc),
    )
    assert result == {
        "status": "NOT_PROVEN",
        "reason": "ENTRY_SNAPSHOT_HASH_OR_SIZE_MISMATCH",
    }


def test_real_molbio_direction_only_prediction_projects_without_magnitude():
    root = Path(__file__).resolve().parents[1]
    raw_root = root / "research/evidence/equity/raw/2026-10-01-forward"
    prediction = json.loads(
        (
            root
            / "research/forward/equity/2026-10-01/"
            "2026-10-01_equity_forward_prediction.json"
        ).read_text(encoding="utf-8")
    )
    equity_sources = {
        "cash": (raw_root / "cm_20261001.zip").read_bytes(),
        "company": (raw_root / "EQUITY_L.csv").read_bytes(),
        "etf": (raw_root / "eq_etfseclist.csv").read_bytes(),
        "actions": (raw_root / "corporate_actions.json").read_bytes(),
    }
    index_raw = (raw_root / "index_close_20261001.csv").read_bytes()
    holiday_raw = (raw_root / "trading_holidays.json").read_bytes()
    model_raw = (
        root / "research/experiments/equity_forward_rank_v1.json"
    ).read_bytes()
    retained_source_uris = {
        "cash": (
            "research/evidence/equity/raw/2026-10-01-forward/"
            "cm_20261001.zip"
        ),
        "company": (
            "research/evidence/equity/raw/2026-10-01-forward/EQUITY_L.csv"
        ),
        "etf": (
            "research/evidence/equity/raw/2026-10-01-forward/"
            "eq_etfseclist.csv"
        ),
        "actions": (
            "research/evidence/equity/raw/2026-10-01-forward/"
            "corporate_actions.json"
        ),
        "index": (
            "research/evidence/equity/raw/2026-10-01-forward/"
            "index_close_20261001.csv"
        ),
        "holiday_calendar": (
            "research/evidence/equity/raw/2026-10-01-forward/"
            "trading_holidays.json"
        ),
        "model_spec": (
            "research/evidence/equity/raw/2026-10-01-forward/"
            "equity_forward_rank_v1.json"
        ),
    }
    kwargs = dict(
        equity_source_bytes=equity_sources,
        index_source_raw=index_raw,
        holiday_calendar_raw=holiday_raw,
        model_spec_raw=model_raw,
        expected_previous_event_hash=GENESIS_HASH,
        retained_source_uris=retained_source_uris,
        now=datetime(2026, 10, 7, 9, 30, tzinfo=timezone.utc),
    )
    projection = build_directional_outcome_projection(
        prediction,
        **kwargs,
    )
    duplicate = build_directional_outcome_projection(
        prediction,
        **kwargs,
    )
    assert projection == duplicate
    assert projection["prediction_event_hash"] == (
        "91912ef5ef5264cdff60fd06449f355fcd4bfcedc6b743e46c7b6ded7236744f"
    )
    assert projection["symbol"] == "MOLBIO"
    assert projection["isin"] == "INE869T01028"
    assert projection["forecast_direction"] == "POSITIVE"
    assert projection["entry_reference_close"] == "1513.10"
    assert projection["predicted_return_pct"] is None
    assert projection["due_at"] == "2026-10-08T10:00:00+00:00"
    assert projection["outcome_status"] == "PENDING"
    verify_directional_projection_evidence(
        projection,
        evidence_root=root,
    )
