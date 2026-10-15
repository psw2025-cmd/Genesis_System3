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

import scripts.equity_durable_publication as durable_publication
import scripts.equity_directional_maturity as maturity_module
import scripts.issue_equity_forward_paper as issue_module
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
    INDEX_API_URL,
    build_prediction,
    validate_prediction,
)
from scripts.equity_directional_maturity import (
    ISSUANCE_MANIFEST_GENESIS_HASH,
    MATURITY_LEDGER_GENESIS_HASH,
    PUBLICATION_RECEIPT_GENESIS_HASH,
    MaturityObservationError,
    _canonical_maturity_ledger_event,
    append_external_publication_receipt,
    append_issuance_artifact_manifest,
    append_maturity_observation,
    build_maturity_observation,
    build_maturity_observation_event,
    github_publication_comment_body,
    publication_collision_uri_for,
    publish_github_attestation_and_retain,
    publish_prospective_issuance,
    read_external_publication_receipts,
    read_issuance_artifact_manifest,
    read_maturity_observation_ledger,
    validate_maturity_observation,
    verify_external_publication_receipts,
    verify_issuance_artifact_manifest,
    verify_maturity_evidence,
    verify_maturity_observation_chain,
    verify_publication_collision_evidence,
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


def all_indices_payload(timestamp="01-Oct-2026 15:30"):
    return {
        "timestamp": timestamp,
        "data": [
            {
                "index": "NIFTY 50",
                "indexSymbol": "NIFTY 50",
                "open": 22020,
                "high": 22120,
                "low": 21980,
                "last": 22100,
                "previousClose": 22000,
                "variation": 100,
                "percentChange": 0.45,
            }
        ],
    }


def with_all_indices(args, payload=None):
    raw = json.dumps(payload or all_indices_payload()).encode()
    args["index_raw"] = raw
    args["index_receipt"] = receipt(raw, INDEX_API_URL)
    return args


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


def test_builds_from_official_all_indices_close_fallback():
    args = with_all_indices(fixture())
    result = build_prediction(**args)
    assert result["benchmark"]["entry_reference_close"] == "22100"
    assert result["benchmark"]["source_url"] == INDEX_API_URL
    assert validate_prediction(
        result,
        now=NOW,
        **retained_sources(args),
        holiday_calendar_raw=args["holiday_raw"],
        model_spec_raw=args["model_spec_raw"],
        expected_previous_event_hash=args["previous_event_hash"],
    )["orders_allowed"] is False


@pytest.mark.parametrize(
    ("case", "message"),
    [
        ("stale_date", "requested session close"),
        ("not_close", "requested session close"),
        ("duplicate", "missing or duplicated"),
        ("variation", "change arithmetic"),
        ("percent", "change arithmetic"),
    ],
)
def test_all_indices_fallback_fails_closed(case, message):
    payload = all_indices_payload()
    if case == "stale_date":
        payload["timestamp"] = "30-Sep-2026 15:30"
    elif case == "not_close":
        payload["timestamp"] = "01-Oct-2026 15:29"
    elif case == "duplicate":
        payload["data"].append(deepcopy(payload["data"][0]))
    elif case == "variation":
        payload["data"][0]["variation"] = 99.99
    else:
        payload["data"][0]["percentChange"] = 0.46
    with pytest.raises(ValueError, match=message):
        build_prediction(**with_all_indices(fixture(), payload))


def test_capture_falls_back_after_exact_archive_404(monkeypatch):
    entry = datetime(2026, 10, 13, tzinfo=timezone.utc).date()
    holiday = json.dumps(
        {"CM": [{"tradingDate": "20-Oct-2026"}]}
    ).encode()
    successful = b"official-source"
    fallback = json.dumps(
        all_indices_payload("13-Oct-2026 15:30")
    ).encode()
    archive_url = (
        "https://nsearchives.nseindia.com/content/indices/"
        "ind_close_all_13102026.csv"
    )

    def fake_fetch(url, *, opener=None):
        del opener
        if url == HOLIDAY_URL:
            return issue_module.Capture(holiday, receipt(holiday, url))
        if url == archive_url:
            result = receipt(b"not found", url)
            result["http_status"] = 404
            return issue_module.Capture(b"not found", result)
        if url == INDEX_API_URL:
            return issue_module.Capture(fallback, receipt(fallback, url))
        return issue_module.Capture(successful, receipt(successful, url))

    monkeypatch.setattr(issue_module, "_source_opener", object)
    monkeypatch.setattr(issue_module, "_fetch", fake_fetch)
    captures, attempts, due = issue_module._capture_sources(entry)
    assert captures["index"].raw == fallback
    assert captures["index"].receipt["url"] == INDEX_API_URL
    assert attempts[0]["http_status"] == 404
    assert attempts[0]["retained_file"] is None
    assert due.isoformat() == "2026-10-21"


def test_issue_rejects_before_close_before_network(monkeypatch, tmp_path):
    monkeypatch.setattr(
        issue_module,
        "_utc_now",
        lambda: datetime(2026, 10, 13, 9, 59, tzinfo=timezone.utc),
    )

    def unexpected_capture(_entry):
        raise AssertionError("network capture must not run before close")

    monkeypatch.setattr(issue_module, "_capture_sources", unexpected_capture)
    with pytest.raises(ValueError, match="completed NSE cash session"):
        issue_module.issue(
            datetime(2026, 10, 13, tzinfo=timezone.utc).date(),
            evidence_root=tmp_path,
        )


def test_issue_retains_exact_unavailable_source_without_forecast(
    monkeypatch, tmp_path
):
    entry = datetime(2026, 10, 14, tzinfo=timezone.utc).date()
    url = (
        CM_URL
        + "BhavCopy_NSE_CM_0_0_0_20261014_F_0000.csv.zip"
    )
    raw = b"official 404 response"
    failed_receipt = receipt(raw, url)
    failed_receipt["http_status"] = 404
    failed_receipt["content_type"] = "text/html;charset=UTF-8"
    failed_receipt["first_observed_at"] = (
        "2026-10-14T10:29:19.785239+00:00"
    )
    failure = issue_module.OfficialSourceUnavailable(
        "cash", issue_module.Capture(raw, failed_receipt)
    )
    monkeypatch.setattr(
        issue_module,
        "_utc_now",
        lambda: datetime(2026, 10, 14, 10, 30, tzinfo=timezone.utc),
    )
    monkeypatch.setattr(
        issue_module, "_load_captured_sources", lambda *_: None
    )

    def unavailable(_entry):
        raise failure

    monkeypatch.setattr(issue_module, "_capture_sources", unavailable)
    with pytest.raises(
        issue_module.OfficialSourceUnavailable,
        match="Official source was not captured exactly",
    ):
        issue_module.issue(entry, evidence_root=tmp_path)

    attempt_dir = tmp_path / (
        "research/evidence/equity/raw/2026-10-14-forward/"
        "availability_attempts"
    )
    records = list(attempt_dir.glob("*.json"))
    responses = list(attempt_dir.glob("*.response"))
    assert len(records) == 1
    assert len(responses) == 1
    assert responses[0].read_bytes() == raw
    record = json.loads(records[0].read_bytes())
    assert record["schema_version"] == (
        "nse-equity-source-availability-attempt-v1"
    )
    assert record["source_role"] == "cash"
    assert record["receipt"]["http_status"] == 404
    assert record["response_sha256"] == sha256(raw).hexdigest()
    assert record["forecast_issued"] is False
    assert record["live_trading_enabled"] is False
    assert record["orders_allowed"] is False
    assert not list((tmp_path / "research/forward").rglob("*.json"))
    assert not list((tmp_path / "research/forward").rglob("*.ndjson"))


def test_issue_creates_artifact_parent_before_atomic_publish(
    monkeypatch, tmp_path
):
    entry = datetime(2026, 10, 13, tzinfo=timezone.utc).date()
    due = datetime(2026, 10, 21, tzinfo=timezone.utc).date()
    roles = {
        "cash": CM_URL + "BhavCopy_NSE_CM_0_0_0_20261013_F_0000.csv.zip",
        "company": EQUITY_URL,
        "etf": ETF_URL,
        "actions": "https://www.nseindia.com/api/corporates-corporateActions?index=equities&from_date=13-10-2026&to_date=21-10-2026",
        "holiday_calendar": HOLIDAY_URL,
        "index": INDEX_API_URL,
    }
    captures = {
        role: issue_module.Capture(b"x", receipt(b"x", url))
        for role, url in roles.items()
    }
    model_path = tmp_path / issue_module.MODEL_SPEC_URI
    model_path.parent.mkdir(parents=True)
    model_path.write_bytes(b"model")
    monkeypatch.setattr(
        issue_module,
        "_utc_now",
        lambda: datetime(2026, 10, 13, 16, 0, tzinfo=timezone.utc),
    )
    monkeypatch.setattr(
        issue_module,
        "_load_captured_sources",
        lambda *_: (captures, [{"http_status": 404}], due),
    )
    monkeypatch.setattr(
        issue_module,
        "read_issuance_artifact_manifest",
        lambda *_args, **_kwargs: [{"prediction_event_hash": "1" * 64}],
    )
    prediction = {
        "prediction_id": "EQ7D-2026-10-13-AAA-V1",
        "issued_at": "2026-10-13T16:00:00+00:00",
        "source_cutoff_at": "2026-10-13T15:59:00+00:00",
        "due_at": "2026-10-21T10:00:00+00:00",
        "prediction": {
            "symbol": "AAA",
            "isin": "INE000A01001",
            "entry_reference_close": "100",
        },
        "benchmark": {"entry_reference_close": "22000"},
        "counts": {"qualified_current_candidates": 0},
        "event_hash": "2" * 64,
    }
    monkeypatch.setattr(
        issue_module, "build_prediction", lambda **_kwargs: prediction
    )
    monkeypatch.setattr(
        issue_module,
        "build_directional_outcome_projection",
        lambda *_args, **_kwargs: {"projection_hash": "3" * 64},
    )
    monkeypatch.setattr(
        issue_module,
        "_guard_remote_prediction_identity",
        lambda *_args, **_kwargs: None,
    )

    def fake_publish(_path, **kwargs):
        del kwargs
        assert (
            tmp_path / "research/forward/equity/2026-10-13"
        ).is_dir()
        return {"event_hash": "4" * 64}

    monkeypatch.setattr(
        issue_module, "publish_prospective_issuance", fake_publish
    )
    result = issue_module.issue(entry, evidence_root=tmp_path)
    assert result["orders_allowed"] is False
    assert result["issuance_manifest_event_hash"] == "4" * 64


def test_remote_namespace_guard_retains_conflict_without_forecast(
    monkeypatch, tmp_path
):
    entry = datetime(2026, 10, 14, tzinfo=timezone.utc).date()
    prediction = {
        "prediction_id": "EQ7D-2026-10-14-AAA-V1",
        "event_hash": "2" * 64,
        "due_at": "2026-10-21T10:00:00+00:00",
        "counts": {
            "source_company_eq_observations": 10,
            "screened_candidates": 2,
            "selected_candidates": 1,
            "qualified_current_candidates": 0,
            "forward_predictions": 1,
            "positive_forecasts": 1,
            "negative_forecasts": 0,
            "matured_outcomes": 0,
        },
    }
    projection = {"projection_hash": "3" * 64}
    attestation = {
        "schema_version": "equity-publication-attestation-v1",
        "prediction_id": prediction["prediction_id"],
        "issuance_manifest_event_hash": "a" * 64,
        "prediction_event_hash": "b" * 64,
        "projection_hash": "c" * 64,
        "registered_at": "2026-10-14T10:00:00+00:00",
        "due_at": prediction["due_at"],
        "execution_mode": "ANALYZE_PAPER",
        "market_validation_claimed": False,
        "live_trading_enabled": False,
        "order_placement_allowed": False,
    }
    body = "GENESIS_SYSTEM3_EQUITY_PUBLICATION_V1\n" + json.dumps(
        attestation,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )
    comment_id = 123456
    comment_url = (
        "https://api.github.com/repos/psw2025-cmd/Genesis_System3/"
        f"issues/comments/{comment_id}"
    )
    source = {
        "id": comment_id,
        "url": comment_url,
        "issue_url": (
            "https://api.github.com/repos/psw2025-cmd/"
            "Genesis_System3/issues/471"
        ),
        "html_url": (
            "https://github.com/psw2025-cmd/Genesis_System3/"
            f"pull/471#issuecomment-{comment_id}"
        ),
        "user": {"login": "psw2025-cmd", "type": "User", "id": 1},
        "author_association": "OWNER",
        "created_at": "2026-10-14T10:01:00Z",
        "updated_at": "2026-10-14T10:01:00Z",
        "body": body,
    }
    page_url = issue_module._publication_comment_page_url(1)
    payloads = {
        page_url: json.dumps([source]).encode("utf-8"),
        comment_url: json.dumps(source).encode("utf-8"),
    }

    class Response:
        def __init__(self, url):
            self.status = 200
            self.url = url
            self.headers = {"Content-Type": "application/json; charset=utf-8"}

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def geturl(self):
            return self.url

        def read(self, limit):
            raw = payloads[self.url]
            assert len(raw) < limit
            return raw

    class Opener:
        def open(self, request, timeout):
            assert timeout == 30
            return Response(request.full_url)

    monkeypatch.setattr(
        issue_module,
        "_utc_now",
        lambda: datetime(2026, 10, 14, 10, 2, tzinfo=timezone.utc),
    )
    with pytest.raises(
        issue_module.RemotePredictionIdentityOccupied,
        match="no forecast issued",
    ):
        issue_module._guard_remote_prediction_identity(
            tmp_path,
            entry,
            prediction,
            projection,
            opener=Opener(),
        )

    attempt_dir = tmp_path / (
        "research/evidence/equity/raw/2026-10-14-forward/"
        "remote_namespace_attempts"
    )
    records = []
    for path in attempt_dir.glob("*.json"):
        value = json.loads(path.read_bytes())
        if value.get("schema_version") == (
            "equity-remote-namespace-attempt-v1"
        ):
            records.append(value)
    assert len(records) == 1
    record = records[0]
    assert record["remote_identity_status"] == (
        "REMOTE_PREDICTION_ID_COLLISION_NOT_ISSUED"
    )
    assert record["remote_comment_count"] == 1
    assert record["forecast_issued"] is False
    assert record["retained_prediction_count"] == 0
    assert record["effective_forward_oos_eligible_count"] == 0
    assert record["live_trading_enabled"] is False
    assert record["orders_allowed"] is False
    snapshot = tmp_path / record["remote_comments"][0]["snapshot_uri"]
    assert json.loads(snapshot.read_bytes()) == source
    assert not (tmp_path / "research/forward").exists()


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


def maturity_sources(args):
    outcome_cash, outcome_url = outcome_archive()
    index = (
        "Index Name,Index Date,Open Index Value,High Index Value,"
        "Low Index Value,Closing Index Value\n"
        "Nifty 50,08-10-2026,22100,22300,22000,22210\n"
    ).encode()
    sources = {
        "outcome_cash": outcome_cash,
        "company": args["equity_sources"]["company"],
        "etf": args["equity_sources"]["etf"],
        "actions": args["equity_sources"]["actions"],
        "index": index,
    }
    urls = {
        "outcome_cash": outcome_url,
        "company": EQUITY_URL,
        "etf": ETF_URL,
        "actions": args["equity_receipts"]["actions"]["url"],
        "index": (
            "https://nsearchives.nseindia.com/content/indices/"
            "ind_close_all_08102026.csv"
        ),
    }
    receipts = {}
    for offset, role in enumerate(sorted(sources)):
        receipts[role] = receipt(
            sources[role],
            urls[role],
            observed=f"2026-10-08T10:{5 + offset:02d}:00Z",
        )
        receipts[role]["exchange_published_at"] = None
    uris = {
        role: f"research/evidence/test-maturity/{role}.bin"
        for role in sources
    }
    return sources, receipts, uris


def test_directional_maturity_binds_sources_without_premature_scoring(tmp_path):
    args, prediction, projection = build_projection()
    sources, receipts, uris = maturity_sources(args)
    result = build_maturity_observation(
        prediction,
        projection,
        entry_source_snapshot=args["equity_sources"]["cash"],
        outcome_close="121",
        source_bytes=sources,
        source_receipts=receipts,
        source_snapshot_uris=uris,
        now=datetime(2026, 10, 8, 10, 15, tzinfo=timezone.utc),
    )
    assert result["identity_review"]["classification"] == (
        "COMPANY_EQ_IDENTITY_MATCHED"
    )
    assert result["corporate_action_review"]["action_count"] == 0
    assert result["corporate_action_review"][
        "requested_interval_covered"
    ] is True
    assert result["corporate_action_review"][
        "complete_action_coverage"
    ] is False
    assert result["raw_reference"]["raw_actual_return_pct"] == 10.0
    assert result["raw_reference"]["raw_reference_direction"] == "POSITIVE"
    assert result["raw_reference"]["direction_correct"] is None
    assert result["benchmark_raw_reference"]["raw_return_pct"] == (
        0.497738
    )
    assert result["benchmark_raw_reference"][
        "raw_unadjusted_equity_excess_pp"
    ] == 9.502262
    assert result["counts"]["raw_reference_observations"] == 1
    assert result["counts"]["matured_adjusted_outcomes"] == 0
    assert "POINT_IN_TIME_MATURITY_IDENTITY_NOT_PROVEN" in result[
        "final_outcome_blockers"
    ]
    assert "COMPLETE_CORPORATE_ACTION_COVERAGE_NOT_PROVEN" in result[
        "final_outcome_blockers"
    ]
    assert validate_maturity_observation(result)["orders_allowed"] is False

    for role, raw in sources.items():
        path = tmp_path / uris[role]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    verify_maturity_evidence(result, evidence_root=tmp_path)
    index_path = tmp_path / uris["index"]
    index_path.write_bytes(index_path.read_bytes() + b"\n")
    with pytest.raises(
        MaturityObservationError,
        match="INDEX_RETAINED_HASH_OR_SIZE_MISMATCH",
    ):
        verify_maturity_evidence(result, evidence_root=tmp_path)


def test_directional_maturity_rejects_invented_publication_time():
    args, prediction, projection = build_projection()
    sources, receipts, uris = maturity_sources(args)
    receipts["outcome_cash"]["exchange_published_at"] = (
        "2026-10-08T10:01:00Z"
    )
    with pytest.raises(
        MaturityObservationError,
        match="OFFICIAL_SOURCE_RECEIPT_MISMATCH",
    ):
        build_maturity_observation(
            prediction,
            projection,
            entry_source_snapshot=args["equity_sources"]["cash"],
            outcome_close="121",
            source_bytes=sources,
            source_receipts=receipts,
            source_snapshot_uris=uris,
            now=datetime(2026, 10, 8, 10, 15, tzinfo=timezone.utc),
        )


def test_directional_maturity_record_cannot_claim_adjusted_outcome():
    args, prediction, projection = build_projection()
    sources, receipts, uris = maturity_sources(args)
    result = build_maturity_observation(
        prediction,
        projection,
        entry_source_snapshot=args["equity_sources"]["cash"],
        outcome_close="121",
        source_bytes=sources,
        source_receipts=receipts,
        source_snapshot_uris=uris,
        now=datetime(2026, 10, 8, 10, 15, tzinfo=timezone.utc),
    )
    result["raw_reference"]["direction_correct"] = True
    payload = {
        key: value for key, value in result.items() if key != "record_hash"
    }
    result["record_hash"] = sha256(
        json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode()
    ).hexdigest()
    with pytest.raises(
        MaturityObservationError,
        match="RAW_REFERENCE_SEMANTICS_INVALID",
    ):
        validate_maturity_observation(result)


@pytest.mark.parametrize(
    ("path", "value", "message"),
    [
        (
            ("raw_reference", "raw_actual_return_pct"),
            999999.0,
            "RAW_REFERENCE_RETURN_INVALID",
        ),
        (
            ("raw_reference", "raw_reference_direction"),
            "NEGATIVE",
            "RAW_REFERENCE_DIRECTION_INVALID",
        ),
        (
            ("benchmark_raw_reference", "raw_return_pct"),
            999999.0,
            "BENCHMARK_RETURN_INVALID",
        ),
        (
            (
                "benchmark_raw_reference",
                "raw_unadjusted_equity_excess_pp",
            ),
            999999.0,
            "BENCHMARK_EXCESS_INVALID",
        ),
        (
            ("identity_review", "snapshot_digest"),
            "0" * 64,
            "IDENTITY_SNAPSHOT_DIGEST_MISMATCH",
        ),
        (
            ("corporate_action_review", "status"),
            "ACTION_OR_IDENTITY_REVIEW_REQUIRED",
            "ACTION_REVIEW_SEMANTICS_INVALID",
        ),
        (
            ("source_cutoff_at",),
            "2026-10-08T10:00:00+00:00",
            "SOURCE_CUTOFF_MISMATCH",
        ),
        (
            ("final_outcome_blockers",),
            ["EXCHANGE_PUBLICATION_TIME_NOT_PROVEN"],
            "FINAL_OUTCOME_BLOCKERS_INVALID",
        ),
        (
            ("raw_reference", "hidden_performance_claim"),
            True,
            "RAW_REFERENCE_FIELDS_INVALID",
        ),
    ],
)
def test_directional_maturity_rejects_rehashed_nested_semantic_mutations(
    path,
    value,
    message,
):
    args, prediction, projection = build_projection()
    sources, receipts, uris = maturity_sources(args)
    result = build_maturity_observation(
        prediction,
        projection,
        entry_source_snapshot=args["equity_sources"]["cash"],
        outcome_close="121",
        source_bytes=sources,
        source_receipts=receipts,
        source_snapshot_uris=uris,
        now=datetime(2026, 10, 8, 10, 15, tzinfo=timezone.utc),
    )
    target = result
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    payload = {
        key: item
        for key, item in result.items()
        if key != "record_hash"
    }
    result["record_hash"] = sha256(
        json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode()
    ).hexdigest()
    with pytest.raises(MaturityObservationError, match=message):
        validate_maturity_observation(result)


def test_directional_maturity_revalidates_matching_action_event():
    args, prediction, projection = build_projection()
    sources, receipts, uris = maturity_sources(args)
    actions = json.dumps(
        [
            {
                "symbol": "AAA",
                "isin": "INE000A01001",
                "exDate": "05-Oct-2026",
                "subject": "Dividend",
            }
        ]
    ).encode()
    sources["actions"] = actions
    receipts["actions"].update(
        raw_sha256=sha256(actions).hexdigest(),
        bytes=len(actions),
    )
    result = build_maturity_observation(
        prediction,
        projection,
        entry_source_snapshot=args["equity_sources"]["cash"],
        outcome_close="121",
        source_bytes=sources,
        source_receipts=receipts,
        source_snapshot_uris=uris,
        now=datetime(2026, 10, 8, 10, 15, tzinfo=timezone.utc),
    )
    assert result["corporate_action_review"]["action_count"] == 1
    assert (
        "CORPORATE_ACTION_OR_IDENTITY_ADJUSTMENT_REQUIRED"
        in result["final_outcome_blockers"]
    )
    assert validate_maturity_observation(result)["orders_allowed"] is False


def retain_anchor_artifacts(
    tmp_path,
    args,
    prediction,
    projection,
    *,
    suffix="",
):
    retain_projection_sources(tmp_path, args, projection)
    prediction_uri = (
        "research/forward/equity/test/"
        f"prediction{suffix}.json"
    )
    projection_uri = (
        "research/forward/equity/test/"
        f"projection{suffix}.json"
    )
    prediction_path = tmp_path / prediction_uri
    projection_path = tmp_path / projection_uri
    prediction_path.parent.mkdir(parents=True, exist_ok=True)
    prediction_bytes = json.dumps(
        prediction, sort_keys=True, indent=2
    ).encode("utf-8")
    projection_bytes = json.dumps(
        projection, sort_keys=True, indent=2
    ).encode("utf-8")
    manifest_uri = (
        "research/forward/equity/test/"
        f"issuance_manifest{suffix}.ndjson"
    )
    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setattr(
            maturity_module,
            "_system_utc_now",
            lambda: datetime(
                2026, 10, 1, 13, 1, tzinfo=timezone.utc
            ),
        )
        publish_prospective_issuance(
            tmp_path / manifest_uri,
            prediction_bytes=prediction_bytes,
            projection_bytes=projection_bytes,
            prediction_uri=prediction_uri,
            projection_uri=projection_uri,
            evidence_root=tmp_path,
        )
    return (
        manifest_uri,
        prediction_path,
        projection_path,
    )


def publication_receipt_uri_for(manifest_uri):
    return manifest_uri.replace(
        "issuance_manifest", "publication_receipts"
    )


def publication_source_uri_for(manifest_uri):
    return manifest_uri.replace(
        "issuance_manifest", "publication_comment"
    ).replace(".ndjson", ".json")


def github_comment_response(
    manifest_event,
    *,
    created_at="2026-10-01T13:02:00Z",
    updated_at=None,
    body=None,
    comment_id=6123456789,
):
    return {
        "id": comment_id,
        "url": (
            "https://api.github.com/repos/psw2025-cmd/"
            f"Genesis_System3/issues/comments/{comment_id}"
        ),
        "html_url": (
            "https://github.com/psw2025-cmd/Genesis_System3/"
            f"pull/471#issuecomment-{comment_id}"
        ),
        "issue_url": (
            "https://api.github.com/repos/psw2025-cmd/"
            "Genesis_System3/issues/471"
        ),
        "user": {
            "login": "psw2025-cmd",
            "id": 176781239,
            "type": "User",
        },
        "created_at": created_at,
        "updated_at": updated_at or created_at,
        "author_association": "OWNER",
        "body": body or github_publication_comment_body(manifest_event),
    }


def retain_publication_receipt(
    tmp_path,
    manifest_uri,
    *,
    created_at="2026-10-01T13:02:00Z",
    updated_at=None,
    body=None,
    observed_at=datetime(2026, 10, 1, 13, 3, tzinfo=timezone.utc),
):
    manifest_event = read_issuance_artifact_manifest(
        manifest_uri, evidence_root=tmp_path
    )[0]
    source_uri = publication_source_uri_for(manifest_uri)
    source_path = tmp_path / source_uri
    source_path.write_text(
        json.dumps(
            github_comment_response(
                manifest_event,
                created_at=created_at,
                updated_at=updated_at,
                body=body,
            ),
            sort_keys=True,
            indent=2,
        ),
        encoding="utf-8",
    )
    receipt_uri = publication_receipt_uri_for(manifest_uri)
    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setattr(
            maturity_module,
            "_system_utc_now",
            lambda: observed_at,
        )
        event = append_external_publication_receipt(
            tmp_path / receipt_uri,
            source_uri,
            issuance_manifest_uri=manifest_uri,
            evidence_root=tmp_path,
        )
    return receipt_uri, source_path, event


def retain_publication_collision(
    tmp_path,
    receipt_uri,
    receipt_event,
    canonical_source_path,
    *,
    detected_at="2026-10-01T13:05:00Z",
):
    canonical_source = json.loads(
        canonical_source_path.read_text(encoding="utf-8")
    )
    conflict = deepcopy(canonical_source)
    conflict["id"] += 1
    old_id = str(canonical_source["id"])
    new_id = str(conflict["id"])
    conflict["url"] = conflict["url"].replace(old_id, new_id)
    conflict["html_url"] = conflict["html_url"].replace(old_id, new_id)
    conflict["created_at"] = "2026-10-01T13:01:00Z"
    conflict["updated_at"] = conflict["created_at"]
    prefix, encoded = conflict["body"].split("\n", 1)
    attestation = json.loads(encoded)
    attestation["projection_hash"] = "f" * 64
    conflict["body"] = prefix + "\n" + json.dumps(
        attestation, sort_keys=True, separators=(",", ":")
    )
    conflict_uri = canonical_source_path.relative_to(tmp_path).as_posix()
    conflict_uri = conflict_uri.replace(
        "publication_comment", "publication_conflict"
    )
    conflict_path = tmp_path / conflict_uri
    conflict_raw = json.dumps(
        conflict, sort_keys=True, indent=2
    ).encode("utf-8")
    conflict_path.write_bytes(conflict_raw)
    canonical_raw = canonical_source_path.read_bytes()
    collision_uri = publication_collision_uri_for(receipt_uri)
    record = {
        "schema_version": "equity-publication-identity-collision-v1",
        "event_type": "EQUITY_PUBLICATION_IDENTITY_COLLISION_REVIEWED",
        "repository": "psw2025-cmd/Genesis_System3",
        "pull_request_number": 471,
        "detected_at": detected_at,
        "collisions": [
            {
                "prediction_id": receipt_event["prediction_id"],
                "canonical_receipt_event_hash": receipt_event["event_hash"],
                "comments": [
                    {
                        "comment_id": canonical_source["id"],
                        "snapshot_uri": canonical_source_path.relative_to(
                            tmp_path
                        ).as_posix(),
                        "source_sha256": sha256(canonical_raw).hexdigest(),
                        "source_size_bytes": len(canonical_raw),
                    },
                    {
                        "comment_id": conflict["id"],
                        "snapshot_uri": conflict_uri,
                        "source_sha256": sha256(conflict_raw).hexdigest(),
                        "source_size_bytes": len(conflict_raw),
                    },
                ],
                "status": "REMOTE_IDENTITY_COLLISION_NOT_FORWARD_OOS",
                "effective_forward_oos_eligible": False,
            }
        ],
        "market_validation_claimed": False,
        "performance_metrics_available": False,
        "real_money_ready": False,
        "live_trading_enabled": False,
        "order_placement_allowed": False,
    }
    record["record_hash"] = sha256(
        json.dumps(
            record,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()
    collision_path = tmp_path / collision_uri
    collision_path.write_text(
        json.dumps(record, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    return collision_uri, collision_path, conflict_path, record


def retain_projection_sources(tmp_path, args, projection):
    (tmp_path / "research/forward/equity/test").mkdir(
        parents=True, exist_ok=True
    )
    projection_sources = {
        **args["equity_sources"],
        "index": args["index_raw"],
        "holiday_calendar": args["holiday_raw"],
        "model_spec": args["model_spec_raw"],
    }
    for role, raw in projection_sources.items():
        path = tmp_path / projection["source_bindings"][role][
            "snapshot_uri"
        ]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)


def retained_maturity_case(tmp_path):
    args, prediction, projection = build_projection()
    sources, receipts, uris = maturity_sources(args)
    observation = build_maturity_observation(
        prediction,
        projection,
        entry_source_snapshot=args["equity_sources"]["cash"],
        outcome_close="121",
        source_bytes=sources,
        source_receipts=receipts,
        source_snapshot_uris=uris,
        now=datetime(2026, 10, 8, 10, 15, tzinfo=timezone.utc),
    )
    for role, raw in sources.items():
        path = tmp_path / uris[role]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    observation_uri = (
        "research/forward/equity/test/"
        "directional_maturity_observation.json"
    )
    observation_bytes = json.dumps(
        observation,
        sort_keys=True,
        indent=2,
    ).encode("utf-8")
    observation_path = tmp_path / observation_uri
    observation_path.parent.mkdir(parents=True, exist_ok=True)
    observation_path.write_bytes(observation_bytes)
    anchor_artifacts, prediction_path, projection_path = (
        retain_anchor_artifacts(
            tmp_path,
            args,
            prediction,
            projection,
        )
    )
    retain_publication_receipt(tmp_path, anchor_artifacts)
    return (
        observation,
        observation_bytes,
        observation_uri,
        observation_path,
        anchor_artifacts,
        prediction_path,
        projection_path,
    )


def test_issuance_manifest_seals_exact_artifact_bytes_before_maturity(
    tmp_path,
):
    args, prediction, projection = build_projection()
    manifest_uri, prediction_path, projection_path = (
        retain_anchor_artifacts(
            tmp_path, args, prediction, projection
        )
    )
    events = read_issuance_artifact_manifest(
        manifest_uri, evidence_root=tmp_path
    )
    assert len(events) == 1
    event = events[0]
    assert event["previous_hash"] == ISSUANCE_MANIFEST_GENESIS_HASH
    assert event["pre_maturity_registered"] is True
    assert event["registration_status"] == "PRE_MATURITY_REGISTERED"
    assert event["prediction_file_sha256"] == sha256(
        prediction_path.read_bytes()
    ).hexdigest()
    assert event["projection_file_sha256"] == sha256(
        projection_path.read_bytes()
    ).hexdigest()
    status = verify_issuance_artifact_manifest(
        events, evidence_root=tmp_path
    )
    assert status["pre_maturity_registration_count"] == 1
    assert status["historical_after_maturity_registration_count"] == 0
    assert status["order_placement_allowed"] is False


def test_issuance_manifest_marks_late_registration_not_proven(tmp_path):
    args, prediction, projection = build_projection()
    _, prediction_path, projection_path = retain_anchor_artifacts(
        tmp_path, args, prediction, projection
    )
    manifest_uri = (
        "research/forward/equity/test/late_issuance_manifest.ndjson"
    )
    event = append_issuance_artifact_manifest(
        tmp_path / manifest_uri,
        prediction_uri=str(prediction_path.relative_to(tmp_path)),
        projection_uri=str(projection_path.relative_to(tmp_path)),
        registered_at=datetime(
            2026, 10, 9, 10, 0, tzinfo=timezone.utc
        ),
        evidence_root=tmp_path,
    )
    assert event["pre_maturity_registered"] is False
    assert event["registration_status"] == (
        "HISTORICAL_AFTER_MATURITY_REGISTRATION_NOT_PROVEN"
    )
    status = verify_issuance_artifact_manifest(
        [event], evidence_root=tmp_path
    )
    assert status["pre_maturity_registration_count"] == 0
    assert status["historical_after_maturity_registration_count"] == 1


def test_historical_append_cannot_backdate_pre_maturity_registration(
    tmp_path,
):
    args, prediction, projection = build_projection()
    _, prediction_path, projection_path = retain_anchor_artifacts(
        tmp_path, args, prediction, projection
    )
    manifest = tmp_path / (
        "research/forward/equity/test/"
        "backdated_historical_manifest.ndjson"
    )
    with pytest.raises(
        MaturityObservationError,
        match="PRE_MATURITY_REGISTRATION_REQUIRES_PROSPECTIVE_TRANSACTION",
    ):
        append_issuance_artifact_manifest(
            manifest,
            prediction_uri=str(prediction_path.relative_to(tmp_path)),
            projection_uri=str(projection_path.relative_to(tmp_path)),
            registered_at=datetime(
                2026, 10, 1, 13, 2, tzinfo=timezone.utc
            ),
            evidence_root=tmp_path,
        )
    assert not manifest.exists()


def test_prospective_issuance_rejects_after_horizon_before_writing(
    tmp_path,
    monkeypatch,
):
    args, prediction, projection = build_projection()
    retain_projection_sources(tmp_path, args, projection)
    prediction_uri = "research/forward/equity/test/late_prediction.json"
    projection_uri = "research/forward/equity/test/late_projection.json"
    manifest = tmp_path / (
        "research/forward/equity/test/late_transaction.ndjson"
    )
    monkeypatch.setattr(
        maturity_module,
        "_system_utc_now",
        lambda: datetime(2026, 10, 8, 10, 0, tzinfo=timezone.utc),
    )
    with pytest.raises(
        MaturityObservationError,
        match="PROSPECTIVE_ISSUANCE_AFTER_HORIZON",
    ):
        publish_prospective_issuance(
            manifest,
            prediction_bytes=json.dumps(
                prediction, sort_keys=True, indent=2
            ).encode("utf-8"),
            projection_bytes=json.dumps(
                projection, sort_keys=True, indent=2
            ).encode("utf-8"),
            prediction_uri=prediction_uri,
            projection_uri=projection_uri,
            evidence_root=tmp_path,
        )
    assert not (tmp_path / prediction_uri).exists()
    assert not (tmp_path / projection_uri).exists()
    assert not manifest.exists()


def test_prospective_issuance_rejects_preexisting_unregistered_artifact(
    tmp_path,
    monkeypatch,
):
    args, prediction, projection = build_projection()
    retain_projection_sources(tmp_path, args, projection)
    prediction_uri = "research/forward/equity/test/orphan_prediction.json"
    projection_uri = "research/forward/equity/test/orphan_projection.json"
    prediction_path = tmp_path / prediction_uri
    prediction_path.write_bytes(b"unregistered")
    manifest = tmp_path / (
        "research/forward/equity/test/orphan_transaction.ndjson"
    )
    monkeypatch.setattr(
        maturity_module,
        "_system_utc_now",
        lambda: datetime(2026, 10, 1, 13, 1, tzinfo=timezone.utc),
    )
    with pytest.raises(
        MaturityObservationError,
        match="PREDICTION_ARTIFACT_ALREADY_EXISTS_UNREGISTERED",
    ):
        publish_prospective_issuance(
            manifest,
            prediction_bytes=json.dumps(
                prediction, sort_keys=True, indent=2
            ).encode("utf-8"),
            projection_bytes=json.dumps(
                projection, sort_keys=True, indent=2
            ).encode("utf-8"),
            prediction_uri=prediction_uri,
            projection_uri=projection_uri,
            evidence_root=tmp_path,
        )
    assert prediction_path.read_bytes() == b"unregistered"
    assert not (tmp_path / projection_uri).exists()
    assert not manifest.exists()


def test_prospective_issuance_rolls_back_on_source_replay_failure(
    tmp_path,
    monkeypatch,
):
    args, prediction, projection = build_projection()
    retain_projection_sources(tmp_path, args, projection)
    cash_uri = projection["source_bindings"]["cash"]["snapshot_uri"]
    (tmp_path / cash_uri).write_bytes(b"mutated-after-projection")
    prediction_uri = "research/forward/equity/test/rollback_prediction.json"
    projection_uri = "research/forward/equity/test/rollback_projection.json"
    manifest = tmp_path / (
        "research/forward/equity/test/rollback_transaction.ndjson"
    )
    monkeypatch.setattr(
        maturity_module,
        "_system_utc_now",
        lambda: datetime(2026, 10, 1, 13, 1, tzinfo=timezone.utc),
    )
    with pytest.raises(MaturityObservationError):
        publish_prospective_issuance(
            manifest,
            prediction_bytes=json.dumps(
                prediction, sort_keys=True, indent=2
            ).encode("utf-8"),
            projection_bytes=json.dumps(
                projection, sort_keys=True, indent=2
            ).encode("utf-8"),
            prediction_uri=prediction_uri,
            projection_uri=projection_uri,
            evidence_root=tmp_path,
        )
    assert not (tmp_path / prediction_uri).exists()
    assert not (tmp_path / projection_uri).exists()
    assert not manifest.exists()


def test_prospective_issuance_rolls_back_on_manifest_commit_failure(
    tmp_path,
    monkeypatch,
):
    args, prediction, projection = build_projection()
    retain_projection_sources(tmp_path, args, projection)
    prediction_uri = "research/forward/equity/test/commit_prediction.json"
    projection_uri = "research/forward/equity/test/commit_projection.json"
    manifest = tmp_path / (
        "research/forward/equity/test/commit_transaction.ndjson"
    )
    monkeypatch.setattr(
        maturity_module,
        "_system_utc_now",
        lambda: datetime(2026, 10, 1, 13, 1, tzinfo=timezone.utc),
    )

    def fail_replace(source, destination):
        raise OSError("simulated atomic replacement failure")

    monkeypatch.setattr(maturity_module.os, "replace", fail_replace)
    with pytest.raises(
        MaturityObservationError,
        match="ISSUANCE_MANIFEST_COMMIT_FAILED",
    ):
        publish_prospective_issuance(
            manifest,
            prediction_bytes=json.dumps(
                prediction, sort_keys=True, indent=2
            ).encode("utf-8"),
            projection_bytes=json.dumps(
                projection, sort_keys=True, indent=2
            ).encode("utf-8"),
            prediction_uri=prediction_uri,
            projection_uri=projection_uri,
            evidence_root=tmp_path,
        )
    assert not (tmp_path / prediction_uri).exists()
    assert not (tmp_path / projection_uri).exists()
    assert not manifest.exists()
    assert not list(manifest.parent.glob(f".{manifest.name}.*.tmp"))


def test_external_publication_receipt_qualifies_pre_horizon_manifest(
    tmp_path,
):
    args, prediction, projection = build_projection()
    manifest_uri, _, _ = retain_anchor_artifacts(
        tmp_path, args, prediction, projection
    )
    receipt_uri, _, event = retain_publication_receipt(
        tmp_path, manifest_uri
    )
    assert event["previous_hash"] == PUBLICATION_RECEIPT_GENESIS_HASH
    assert event["forward_oos_eligible"] is True
    assert event["publication_status"] == (
        "INDEPENDENT_GITHUB_PUBLICATION_BEFORE_HORIZON"
    )
    events = read_external_publication_receipts(
        receipt_uri,
        issuance_manifest_uri=manifest_uri,
        evidence_root=tmp_path,
    )
    assert events == [event]
    status = verify_external_publication_receipts(
        events,
        issuance_manifest_uri=manifest_uri,
        publication_receipt_uri=receipt_uri,
        evidence_root=tmp_path,
    )
    assert status["forward_oos_eligible_count"] == 1
    assert status["historical_publication_count"] == 0
    assert status["order_placement_allowed"] is False


def test_external_publication_import_accepts_manifest_bound_v2(tmp_path):
    args, prediction, projection = build_projection()
    manifest_uri, prediction_path, projection_path = (
        retain_anchor_artifacts(tmp_path, args, prediction, projection)
    )
    manifest_event = read_issuance_artifact_manifest(
        manifest_uri, evidence_root=tmp_path
    )[0]
    body = durable_publication.publication_v2_comment_body(
        manifest_event,
        artifact_commit_sha="2" * 40,
        prediction_raw=prediction_path.read_bytes(),
        projection_raw=projection_path.read_bytes(),
    )
    receipt_uri, source_path, event = retain_publication_receipt(
        tmp_path,
        manifest_uri,
        body=body,
    )
    assert json.loads(source_path.read_text(encoding="utf-8"))["body"] == body
    assert read_external_publication_receipts(
        receipt_uri,
        issuance_manifest_uri=manifest_uri,
        evidence_root=tmp_path,
    ) == [event]
    status = verify_external_publication_receipts(
        [event],
        issuance_manifest_uri=manifest_uri,
        publication_receipt_uri=receipt_uri,
        evidence_root=tmp_path,
    )
    assert status["forward_oos_eligible_count"] == 1
    assert event["live_trading_enabled"] is False
    assert event["order_placement_allowed"] is False


def test_publication_collision_evidence_disqualifies_forward_oos(
    tmp_path,
):
    args, prediction, projection = build_projection()
    manifest_uri, _, _ = retain_anchor_artifacts(
        tmp_path, args, prediction, projection
    )
    receipt_uri, source_path, receipt_event = retain_publication_receipt(
        tmp_path, manifest_uri
    )
    retain_publication_collision(
        tmp_path, receipt_uri, receipt_event, source_path
    )
    events = read_external_publication_receipts(
        receipt_uri,
        issuance_manifest_uri=manifest_uri,
        evidence_root=tmp_path,
    )
    status = verify_external_publication_receipts(
        events,
        issuance_manifest_uri=manifest_uri,
        publication_receipt_uri=receipt_uri,
        evidence_root=tmp_path,
    )
    assert status["receipt_forward_oos_eligible_count"] == 1
    assert status["forward_oos_eligible_count"] == 0
    assert status["publication_identity_collision_count"] == 1
    assert status["collision_disqualified_count"] == 1
    assert status["collision_disqualified_prediction_ids"] == [
        receipt_event["prediction_id"]
    ]
    maturity_status = verify_maturity_observation_chain(
        [],
        issuance_manifest_uri=manifest_uri,
        publication_receipt_uri=receipt_uri,
        evidence_root=tmp_path,
    )
    assert maturity_status["forward_oos_publication_eligible_count"] == 0
    assert maturity_status[
        "receipt_forward_oos_publication_eligible_count"
    ] == 1
    assert maturity_status["publication_identity_collision_count"] == 1
    assert maturity_status[
        "pre_maturity_without_eligible_publication_count"
    ] == 1


def test_publication_collision_cannot_be_hidden_by_receipt_copy(tmp_path):
    args, prediction, projection = build_projection()
    manifest_uri, _, _ = retain_anchor_artifacts(
        tmp_path, args, prediction, projection
    )
    receipt_uri, source_path, receipt_event = retain_publication_receipt(
        tmp_path, manifest_uri
    )
    retain_publication_collision(
        tmp_path, receipt_uri, receipt_event, source_path
    )
    copied_uri = receipt_uri.replace(
        "publication_receipts", "caller_selected_copy"
    )
    (tmp_path / copied_uri).write_bytes((tmp_path / receipt_uri).read_bytes())

    events = read_external_publication_receipts(
        copied_uri,
        issuance_manifest_uri=manifest_uri,
        evidence_root=tmp_path,
    )
    status = verify_external_publication_receipts(
        events,
        issuance_manifest_uri=manifest_uri,
        publication_receipt_uri=copied_uri,
        evidence_root=tmp_path,
    )

    assert status["receipt_forward_oos_eligible_count"] == 1
    assert status["forward_oos_eligible_count"] == 0
    assert status["collision_disqualified_prediction_ids"] == [
        receipt_event["prediction_id"]
    ]


def test_publication_receipt_copy_cannot_leave_source_directory(tmp_path):
    args, prediction, projection = build_projection()
    manifest_uri, _, _ = retain_anchor_artifacts(
        tmp_path, args, prediction, projection
    )
    receipt_uri, _, _ = retain_publication_receipt(
        tmp_path, manifest_uri
    )
    copied_uri = (
        "research/forward/equity/detached/"
        "caller_selected_copy.ndjson"
    )
    copied_path = tmp_path / copied_uri
    copied_path.parent.mkdir(parents=True)
    copied_path.write_bytes((tmp_path / receipt_uri).read_bytes())

    with pytest.raises(
        MaturityObservationError,
        match="PUBLICATION_RECEIPT_SOURCE_DIRECTORY_MISMATCH",
    ):
        read_external_publication_receipts(
            copied_uri,
            issuance_manifest_uri=manifest_uri,
            evidence_root=tmp_path,
        )


def test_publication_collision_evidence_tamper_fails_replay(tmp_path):
    args, prediction, projection = build_projection()
    manifest_uri, _, _ = retain_anchor_artifacts(
        tmp_path, args, prediction, projection
    )
    receipt_uri, source_path, receipt_event = retain_publication_receipt(
        tmp_path, manifest_uri
    )
    collision_uri, _, conflict_path, _ = retain_publication_collision(
        tmp_path, receipt_uri, receipt_event, source_path
    )
    publication_events = read_external_publication_receipts(
        receipt_uri,
        issuance_manifest_uri=manifest_uri,
        evidence_root=tmp_path,
    )
    conflict_path.write_bytes(conflict_path.read_bytes() + b"\n")
    with pytest.raises(
        MaturityObservationError,
        match="SOURCE_HASH_OR_SIZE_MISMATCH",
    ):
        verify_publication_collision_evidence(
            collision_uri,
            publication_events=publication_events,
            evidence_root=tmp_path,
        )


def test_publication_collision_blocks_maturity_append(tmp_path):
    (
        _,
        _,
        observation_uri,
        _,
        manifest_uri,
        _,
        _,
    ) = retained_maturity_case(tmp_path)
    receipt_uri = publication_receipt_uri_for(manifest_uri)
    publication_events = read_external_publication_receipts(
        receipt_uri,
        issuance_manifest_uri=manifest_uri,
        evidence_root=tmp_path,
    )
    source_path = tmp_path / publication_source_uri_for(manifest_uri)
    retain_publication_collision(
        tmp_path,
        receipt_uri,
        publication_events[0],
        source_path,
    )
    with pytest.raises(
        MaturityObservationError,
        match="EXTERNAL_PUBLICATION_BEFORE_HORIZON_REQUIRED",
    ):
        append_maturity_observation(
            tmp_path / "maturity_observations.ndjson",
            observation_uri,
            issuance_manifest_uri=manifest_uri,
            publication_receipt_uri=receipt_uri,
            evidence_root=tmp_path,
        )


def test_prospective_github_publication_posts_refetches_and_retains(
    tmp_path, monkeypatch
):
    args, prediction, projection = build_projection()
    manifest_uri, _, _ = retain_anchor_artifacts(
        tmp_path, args, prediction, projection
    )
    manifest_event = read_issuance_artifact_manifest(
        manifest_uri, evidence_root=tmp_path
    )[0]
    source = github_comment_response(manifest_event)
    source_raw = json.dumps(
        source, sort_keys=True, indent=2
    ).encode("utf-8")
    requests = []

    class Response:
        def __init__(self, request):
            self.request = request
            self.headers = {"Content-Type": "application/json; charset=utf-8"}

        def __enter__(self):
            return self

        def __exit__(self, *_):
            return False

        def getcode(self):
            return 201 if self.request.get_method() == "POST" else 200

        def geturl(self):
            return self.request.full_url

        def read(self, limit):
            if "?per_page=" in self.request.full_url:
                raw = json.dumps(
                    [source]
                    if any(
                        request.get_method() == "POST"
                        for request in requests
                    )
                    else []
                ).encode("utf-8")
            else:
                raw = source_raw
            assert limit > len(raw)
            return raw

    def fake_urlopen(request, timeout):
        assert timeout == 30
        assert request.get_header("Authorization") == "Bearer test-token"
        requests.append(request)
        return Response(request)

    observed_times = iter(
        [
            datetime(2026, 10, 1, 13, 1, 30, tzinfo=timezone.utc),
            datetime(2026, 10, 1, 13, 3, tzinfo=timezone.utc),
        ]
    )
    monkeypatch.setattr(maturity_module, "urlopen", fake_urlopen)
    monkeypatch.setattr(
        maturity_module, "_system_utc_now", lambda: next(observed_times)
    )
    source_uri = publication_source_uri_for(manifest_uri)
    receipt_uri = publication_receipt_uri_for(manifest_uri)
    event = publish_github_attestation_and_retain(
        tmp_path / receipt_uri,
        source_uri,
        issuance_manifest_uri=manifest_uri,
        prediction_id=manifest_event["prediction_id"],
        github_token="test-token",
        evidence_root=tmp_path,
    )
    assert [request.get_method() for request in requests] == [
        "GET", "POST", "GET", "GET"
    ]
    assert json.loads(requests[1].data) == {
        "body": github_publication_comment_body(manifest_event)
    }
    assert requests[2].full_url == source["url"]
    assert (tmp_path / source_uri).read_bytes() == source_raw
    assert event["forward_oos_eligible"] is True
    assert event["first_observed_at"] == "2026-10-01T13:03:00+00:00"
    assert read_external_publication_receipts(
        receipt_uri,
        issuance_manifest_uri=manifest_uri,
        evidence_root=tmp_path,
    ) == [event]
    assert event["live_trading_enabled"] is False
    assert event["order_placement_allowed"] is False


def test_commit_pinned_v2_publication_enters_canonical_receipt_chain(
    tmp_path, monkeypatch
):
    args, prediction, projection = build_projection()
    manifest_uri, prediction_path, projection_path = (
        retain_anchor_artifacts(tmp_path, args, prediction, projection)
    )
    manifest_event = read_issuance_artifact_manifest(
        manifest_uri, evidence_root=tmp_path
    )[0]
    manifest_raw = (tmp_path / manifest_uri).read_bytes()
    prediction_raw = prediction_path.read_bytes()
    projection_raw = projection_path.read_bytes()
    artifact_commit_sha = "3" * 40
    remote = {
        manifest_uri: manifest_raw,
        manifest_event["prediction_uri"]: prediction_raw,
        manifest_event["projection_uri"]: projection_raw,
    }

    def fetch_remote(repository, commit_sha, relative_path):
        assert repository == "psw2025-cmd/Genesis_System3"
        assert commit_sha == artifact_commit_sha
        return remote[relative_path]

    body = durable_publication.publication_v2_comment_body(
        manifest_event,
        artifact_commit_sha=artifact_commit_sha,
        prediction_raw=prediction_raw,
        projection_raw=projection_raw,
    )
    source = github_comment_response(manifest_event, body=body)
    source_raw = json.dumps(
        source, sort_keys=True, indent=2
    ).encode("utf-8")
    requests = []
    published = False

    def request_json(method, url, *, token, payload=None):
        nonlocal published
        requests.append((method, url, payload))
        assert token == "test-token"
        if "?per_page=" in url:
            return json.dumps(
                [source] if published else [], sort_keys=True
            ).encode("utf-8")
        if method == "POST":
            assert json.loads(payload) == {"body": body}
            published = True
        return source_raw

    observed_times = iter(
        [
            datetime(2026, 10, 1, 13, 1, 30, tzinfo=timezone.utc),
            datetime(2026, 10, 1, 13, 3, tzinfo=timezone.utc),
        ]
    )
    monkeypatch.setattr(
        maturity_module, "_github_publication_request_json", request_json
    )
    monkeypatch.setattr(
        maturity_module, "_system_utc_now", lambda: next(observed_times)
    )
    source_uri = publication_source_uri_for(manifest_uri)
    receipt_uri = publication_receipt_uri_for(manifest_uri)
    event = durable_publication.publish_durable_equity_attestation(
        tmp_path / receipt_uri,
        source_uri,
        issuance_manifest_uri=manifest_uri,
        prediction_id=manifest_event["prediction_id"],
        artifact_commit_sha=artifact_commit_sha,
        session_date="2026-10-01",
        github_token="test-token",
        evidence_root=tmp_path,
        fetch_fn=fetch_remote,
    )

    assert [request[0] for request in requests] == [
        "GET", "POST", "GET", "GET"
    ]
    assert (tmp_path / source_uri).read_bytes() == source_raw
    assert read_external_publication_receipts(
        receipt_uri,
        issuance_manifest_uri=manifest_uri,
        evidence_root=tmp_path,
    ) == [event]
    retained_source = json.loads((tmp_path / source_uri).read_bytes())
    attestation = durable_publication.parse_publication_v2_attestation(
        retained_source["body"]
    )
    assert attestation["artifact_commit_sha"] == artifact_commit_sha
    assert attestation["prediction_file_sha256"] == sha256(
        prediction_raw
    ).hexdigest()
    assert attestation["projection_file_sha256"] == sha256(
        projection_raw
    ).hexdigest()
    assert event["forward_oos_eligible"] is True
    assert event["market_validation_claimed"] is False
    assert event["real_money_ready"] is False
    assert event["live_trading_enabled"] is False
    assert event["order_placement_allowed"] is False


def test_commit_pinned_v2_rejects_remote_manifest_byte_drift_before_post(
    tmp_path, monkeypatch
):
    args, prediction, projection = build_projection()
    manifest_uri, prediction_path, projection_path = (
        retain_anchor_artifacts(tmp_path, args, prediction, projection)
    )
    manifest_event = read_issuance_artifact_manifest(
        manifest_uri, evidence_root=tmp_path
    )[0]
    prediction_raw = prediction_path.read_bytes()
    projection_raw = projection_path.read_bytes()
    remote_manifest = json.dumps(
        dict(reversed(list(manifest_event.items()))),
        sort_keys=False,
        separators=(",", ":"),
    ).encode("utf-8") + b"\n"
    local_manifest = (tmp_path / manifest_uri).read_bytes()
    assert len(remote_manifest) == len(local_manifest)
    assert remote_manifest != local_manifest

    def fetch_remote(_repository, _commit_sha, relative_path):
        if relative_path == manifest_uri:
            return remote_manifest
        if relative_path == manifest_event["prediction_uri"]:
            return prediction_raw
        if relative_path == manifest_event["projection_uri"]:
            return projection_raw
        raise AssertionError(relative_path)

    monkeypatch.setattr(
        maturity_module,
        "_github_publication_request_json",
        lambda *_, **__: pytest.fail("GitHub called before byte verification"),
    )
    source_uri = publication_source_uri_for(manifest_uri)
    receipt_uri = publication_receipt_uri_for(manifest_uri)
    with pytest.raises(
        durable_publication.MaturityObservationError,
        match="REMOTE_BYTE_MISMATCH",
    ):
        durable_publication.publish_durable_equity_attestation(
            tmp_path / receipt_uri,
            source_uri,
            issuance_manifest_uri=manifest_uri,
            prediction_id=manifest_event["prediction_id"],
            artifact_commit_sha="4" * 40,
            session_date="2026-10-01",
            github_token="test-token",
            evidence_root=tmp_path,
            fetch_fn=fetch_remote,
        )
    assert not (tmp_path / source_uri).exists()
    assert not (tmp_path / receipt_uri).exists()


def test_prospective_github_publication_recovers_one_exact_comment(
    tmp_path, monkeypatch
):
    args, prediction, projection = build_projection()
    manifest_uri, _, _ = retain_anchor_artifacts(
        tmp_path, args, prediction, projection
    )
    manifest_event = read_issuance_artifact_manifest(
        manifest_uri, evidence_root=tmp_path
    )[0]
    source = github_comment_response(manifest_event)
    source_raw = json.dumps(source, sort_keys=True).encode("utf-8")
    calls = []

    def request_json(method, url, *, token, payload=None):
        calls.append((method, url, payload))
        assert method == "GET"
        if "?per_page=" in url:
            return json.dumps([source], sort_keys=True).encode("utf-8")
        return source_raw

    observed_times = iter(
        [
            datetime(2026, 10, 1, 13, 1, 30, tzinfo=timezone.utc),
            datetime(2026, 10, 1, 13, 3, tzinfo=timezone.utc),
        ]
    )
    monkeypatch.setattr(
        maturity_module, "_github_publication_request_json", request_json
    )
    monkeypatch.setattr(
        maturity_module, "_system_utc_now", lambda: next(observed_times)
    )
    source_uri = publication_source_uri_for(manifest_uri)
    receipt_uri = publication_receipt_uri_for(manifest_uri)
    event = publish_github_attestation_and_retain(
        tmp_path / receipt_uri,
        source_uri,
        issuance_manifest_uri=manifest_uri,
        prediction_id=manifest_event["prediction_id"],
        github_token="test-token",
        evidence_root=tmp_path,
    )
    assert [call[0] for call in calls] == ["GET", "GET", "GET", "GET"]
    assert event["comment_id"] == source["id"]
    assert (tmp_path / source_uri).read_bytes() == source_raw
    assert (tmp_path / receipt_uri).exists()


def test_prospective_github_publication_conflict_fails_before_post(
    tmp_path, monkeypatch
):
    args, prediction, projection = build_projection()
    manifest_uri, _, _ = retain_anchor_artifacts(
        tmp_path, args, prediction, projection
    )
    manifest_event = read_issuance_artifact_manifest(
        manifest_uri, evidence_root=tmp_path
    )[0]
    conflict = github_comment_response(manifest_event)
    prefix, encoded = conflict["body"].split("\n", 1)
    attestation = json.loads(encoded)
    attestation["projection_hash"] = "f" * 64
    conflict["body"] = prefix + "\n" + json.dumps(
        attestation, sort_keys=True, separators=(",", ":")
    )
    calls = []

    def request_json(method, url, *, token, payload=None):
        calls.append((method, url, payload))
        assert method == "GET"
        return json.dumps([conflict], sort_keys=True).encode("utf-8")

    monkeypatch.setattr(
        maturity_module, "_github_publication_request_json", request_json
    )
    monkeypatch.setattr(
        maturity_module,
        "_system_utc_now",
        lambda: datetime(2026, 10, 1, 13, 1, 30, tzinfo=timezone.utc),
    )
    source_uri = publication_source_uri_for(manifest_uri)
    receipt_uri = publication_receipt_uri_for(manifest_uri)
    with pytest.raises(
        MaturityObservationError,
        match="GITHUB_PUBLICATION_REMOTE_IDENTITY_COLLISION",
    ):
        publish_github_attestation_and_retain(
            tmp_path / receipt_uri,
            source_uri,
            issuance_manifest_uri=manifest_uri,
            prediction_id=manifest_event["prediction_id"],
            github_token="test-token",
            evidence_root=tmp_path,
        )
    assert [call[0] for call in calls] == ["GET"]
    assert not (tmp_path / source_uri).exists()
    assert not (tmp_path / receipt_uri).exists()


def test_prospective_github_publication_malformed_marker_fails_closed(
    tmp_path, monkeypatch
):
    args, prediction, projection = build_projection()
    manifest_uri, _, _ = retain_anchor_artifacts(
        tmp_path, args, prediction, projection
    )
    manifest_event = read_issuance_artifact_manifest(
        manifest_uri, evidence_root=tmp_path
    )[0]
    malformed = github_comment_response(manifest_event)
    malformed["body"] = "GENESIS_SYSTEM3_EQUITY_PUBLICATION_V1\n{"
    calls = []

    def request_json(method, url, *, token, payload=None):
        calls.append((method, url, payload))
        return json.dumps([malformed], sort_keys=True).encode("utf-8")

    monkeypatch.setattr(
        maturity_module, "_github_publication_request_json", request_json
    )
    monkeypatch.setattr(
        maturity_module,
        "_system_utc_now",
        lambda: datetime(2026, 10, 1, 13, 1, 30, tzinfo=timezone.utc),
    )
    with pytest.raises(
        MaturityObservationError,
        match="PUBLICATION_ATTESTATION_INVALID_JSON",
    ):
        publish_github_attestation_and_retain(
            tmp_path / publication_receipt_uri_for(manifest_uri),
            publication_source_uri_for(manifest_uri),
            issuance_manifest_uri=manifest_uri,
            prediction_id=manifest_event["prediction_id"],
            github_token="test-token",
            evidence_root=tmp_path,
        )
    assert [call[0] for call in calls] == ["GET"]


def test_github_publication_scan_paginates_and_caps(monkeypatch):
    unrelated = {
        "user": {"login": "someone-else"},
        "author_association": "NONE",
    }
    urls = []

    def paginated(method, url, *, token, payload=None):
        urls.append(url)
        rows = [unrelated] * 100 if url.endswith("page=1") else []
        return json.dumps(rows).encode("utf-8")

    monkeypatch.setattr(
        maturity_module, "_github_publication_request_json", paginated
    )
    assert maturity_module._scan_github_publication_comments(
        "EQ7D-2026-10-01-ABC-V1", token="test-token"
    ) == []
    assert [url.rsplit("=", 1)[-1] for url in urls] == ["1", "2"]

    monkeypatch.setattr(maturity_module, "_GITHUB_PUBLICATION_MAX_PAGES", 2)
    urls.clear()

    def full_pages(method, url, *, token, payload=None):
        urls.append(url)
        return json.dumps([unrelated] * 100).encode("utf-8")

    monkeypatch.setattr(
        maturity_module, "_github_publication_request_json", full_pages
    )
    with pytest.raises(
        MaturityObservationError,
        match="GITHUB_PUBLICATION_COMMENT_SCAN_INCOMPLETE",
    ):
        maturity_module._scan_github_publication_comments(
            "EQ7D-2026-10-01-ABC-V1", token="test-token"
        )
    assert [url.rsplit("=", 1)[-1] for url in urls] == ["1", "2"]


def test_prospective_github_publication_detects_post_race_collision(
    tmp_path, monkeypatch
):
    args, prediction, projection = build_projection()
    manifest_uri, _, _ = retain_anchor_artifacts(
        tmp_path, args, prediction, projection
    )
    manifest_event = read_issuance_artifact_manifest(
        manifest_uri, evidence_root=tmp_path
    )[0]
    source = github_comment_response(manifest_event)
    source_raw = json.dumps(source, sort_keys=True).encode("utf-8")
    conflict = deepcopy(source)
    conflict["id"] = 6123456790
    conflict["url"] = conflict["url"].replace("6123456789", "6123456790")
    conflict["html_url"] = conflict["html_url"].replace(
        "6123456789", "6123456790"
    )
    prefix, encoded = conflict["body"].split("\n", 1)
    attestation = json.loads(encoded)
    attestation["prediction_event_hash"] = "e" * 64
    conflict["body"] = prefix + "\n" + json.dumps(
        attestation, sort_keys=True, separators=(",", ":")
    )
    published = False

    def request_json(method, url, *, token, payload=None):
        nonlocal published
        if "?per_page=" in url:
            rows = [source, conflict] if published else []
            return json.dumps(rows, sort_keys=True).encode("utf-8")
        if method == "POST":
            published = True
        return source_raw

    observed_times = iter(
        [
            datetime(2026, 10, 1, 13, 1, 30, tzinfo=timezone.utc),
            datetime(2026, 10, 1, 13, 3, tzinfo=timezone.utc),
        ]
    )
    monkeypatch.setattr(
        maturity_module, "_github_publication_request_json", request_json
    )
    monkeypatch.setattr(
        maturity_module, "_system_utc_now", lambda: next(observed_times)
    )
    source_uri = publication_source_uri_for(manifest_uri)
    receipt_uri = publication_receipt_uri_for(manifest_uri)
    with pytest.raises(
        MaturityObservationError,
        match="GITHUB_PUBLICATION_REMOTE_IDENTITY_COLLISION",
    ):
        publish_github_attestation_and_retain(
            tmp_path / receipt_uri,
            source_uri,
            issuance_manifest_uri=manifest_uri,
            prediction_id=manifest_event["prediction_id"],
            github_token="test-token",
            evidence_root=tmp_path,
        )
    assert (tmp_path / source_uri).read_bytes() == source_raw
    assert not (tmp_path / receipt_uri).exists()


def test_prospective_github_publication_mismatch_retains_raw_without_receipt(
    tmp_path, monkeypatch
):
    args, prediction, projection = build_projection()
    manifest_uri, _, _ = retain_anchor_artifacts(
        tmp_path, args, prediction, projection
    )
    manifest_event = read_issuance_artifact_manifest(
        manifest_uri, evidence_root=tmp_path
    )[0]
    source = github_comment_response(manifest_event)
    source_raw = json.dumps(source, sort_keys=True).encode("utf-8")
    changed = deepcopy(source)
    changed["body"] += "\n"
    fetched_raw = json.dumps(changed, sort_keys=True).encode("utf-8")
    calls = []

    def request_json(method, url, *, token, payload=None):
        calls.append((method, url, token, payload))
        if "?per_page=" in url:
            return b"[]"
        return source_raw if method == "POST" else fetched_raw

    observed_times = iter(
        [
            datetime(2026, 10, 1, 13, 1, 30, tzinfo=timezone.utc),
            datetime(2026, 10, 1, 13, 3, tzinfo=timezone.utc),
        ]
    )
    monkeypatch.setattr(
        maturity_module,
        "_github_publication_request_json",
        request_json,
    )
    monkeypatch.setattr(
        maturity_module, "_system_utc_now", lambda: next(observed_times)
    )
    source_uri = publication_source_uri_for(manifest_uri)
    receipt_uri = publication_receipt_uri_for(manifest_uri)
    with pytest.raises(
        MaturityObservationError,
        match="GITHUB_PUBLICATION_REFETCH_MISMATCH",
    ):
        publish_github_attestation_and_retain(
            tmp_path / receipt_uri,
            source_uri,
            issuance_manifest_uri=manifest_uri,
            prediction_id=manifest_event["prediction_id"],
            github_token="test-token",
            evidence_root=tmp_path,
        )
    assert [call[0] for call in calls] == ["GET", "POST", "GET"]
    assert (tmp_path / source_uri).read_bytes() == source_raw
    assert not (tmp_path / receipt_uri).exists()

    def unexpected_request(*_, **__):
        raise AssertionError("retry must fail before another GitHub request")

    monkeypatch.setattr(
        maturity_module,
        "_github_publication_request_json",
        unexpected_request,
    )
    with pytest.raises(
        MaturityObservationError,
        match="PUBLICATION_SOURCE_ALREADY_EXISTS_UNREGISTERED",
    ):
        publish_github_attestation_and_retain(
            tmp_path / receipt_uri,
            source_uri,
            issuance_manifest_uri=manifest_uri,
            prediction_id=manifest_event["prediction_id"],
            github_token="test-token",
            evidence_root=tmp_path,
        )


def test_prospective_github_publication_duplicate_fails_before_repost(
    tmp_path, monkeypatch
):
    args, prediction, projection = build_projection()
    manifest_uri, _, _ = retain_anchor_artifacts(
        tmp_path, args, prediction, projection
    )
    manifest_event = read_issuance_artifact_manifest(
        manifest_uri, evidence_root=tmp_path
    )[0]
    source_raw = json.dumps(
        github_comment_response(manifest_event), sort_keys=True
    ).encode("utf-8")
    observed_times = iter(
        [
            datetime(2026, 10, 1, 13, 1, 30, tzinfo=timezone.utc),
            datetime(2026, 10, 1, 13, 3, tzinfo=timezone.utc),
        ]
    )
    published = False

    def request_json(method, url, *, token, payload=None):
        nonlocal published
        if "?per_page=" in url:
            return json.dumps(
                [json.loads(source_raw)] if published else []
            ).encode("utf-8")
        if method == "POST":
            published = True
        return source_raw

    monkeypatch.setattr(
        maturity_module,
        "_github_publication_request_json",
        request_json,
    )
    monkeypatch.setattr(
        maturity_module, "_system_utc_now", lambda: next(observed_times)
    )
    source_uri = publication_source_uri_for(manifest_uri)
    receipt_uri = publication_receipt_uri_for(manifest_uri)
    publish_github_attestation_and_retain(
        tmp_path / receipt_uri,
        source_uri,
        issuance_manifest_uri=manifest_uri,
        prediction_id=manifest_event["prediction_id"],
        github_token="test-token",
        evidence_root=tmp_path,
    )
    monkeypatch.setattr(
        maturity_module,
        "_github_publication_request_json",
        lambda *_, **__: pytest.fail("duplicate GitHub POST attempted"),
    )
    with pytest.raises(
        MaturityObservationError,
        match="PUBLICATION_RECEIPT_ALREADY_RECORDED",
    ):
        publish_github_attestation_and_retain(
            tmp_path / receipt_uri,
            source_uri,
            issuance_manifest_uri=manifest_uri,
            prediction_id=manifest_event["prediction_id"],
            github_token="test-token",
            evidence_root=tmp_path,
        )


def test_prospective_github_publication_rejects_matured_horizon_before_post(
    tmp_path, monkeypatch
):
    args, prediction, projection = build_projection()
    manifest_uri, _, _ = retain_anchor_artifacts(
        tmp_path, args, prediction, projection
    )
    manifest_event = read_issuance_artifact_manifest(
        manifest_uri, evidence_root=tmp_path
    )[0]
    monkeypatch.setattr(
        maturity_module,
        "_system_utc_now",
        lambda: datetime.fromisoformat(
            manifest_event["due_at"].replace("Z", "+00:00")
        ),
    )
    monkeypatch.setattr(
        maturity_module,
        "_github_publication_request_json",
        lambda *_, **__: pytest.fail("matured forecast was published"),
    )
    source_uri = publication_source_uri_for(manifest_uri)
    receipt_uri = publication_receipt_uri_for(manifest_uri)
    with pytest.raises(
        MaturityObservationError,
        match="PUBLICATION_HORIZON_ALREADY_REACHED",
    ):
        publish_github_attestation_and_retain(
            tmp_path / receipt_uri,
            source_uri,
            issuance_manifest_uri=manifest_uri,
            prediction_id=manifest_event["prediction_id"],
            github_token="test-token",
            evidence_root=tmp_path,
        )
    assert not (tmp_path / source_uri).exists()
    assert not (tmp_path / receipt_uri).exists()


def test_maturity_rejects_pre_horizon_manifest_without_receipt(tmp_path):
    (
        _,
        _,
        observation_uri,
        _,
        manifest_uri,
        _,
        _,
    ) = retained_maturity_case(tmp_path)
    with pytest.raises(
        MaturityObservationError,
        match="EXTERNAL_PUBLICATION_BEFORE_HORIZON_REQUIRED",
    ):
        append_maturity_observation(
            tmp_path / "missing_publication_receipt.ndjson",
            observation_uri,
            issuance_manifest_uri=manifest_uri,
            evidence_root=tmp_path,
        )


def test_external_publication_rejects_edited_github_comment(tmp_path):
    args, prediction, projection = build_projection()
    manifest_uri, _, _ = retain_anchor_artifacts(
        tmp_path, args, prediction, projection
    )
    with pytest.raises(
        MaturityObservationError,
        match="PUBLICATION_EDITED_COMMENT_FORBIDDEN",
    ):
        retain_publication_receipt(
            tmp_path,
            manifest_uri,
            updated_at="2026-10-01T13:02:01Z",
        )
    assert not (tmp_path / publication_receipt_uri_for(manifest_uri)).exists()


def test_late_external_publication_remains_historical_only(tmp_path):
    (
        observation,
        observation_bytes,
        observation_uri,
        _,
        manifest_uri,
        _,
        _,
    ) = retained_maturity_case(tmp_path)
    (tmp_path / publication_receipt_uri_for(manifest_uri)).unlink()
    receipt_uri, _, event = retain_publication_receipt(
        tmp_path,
        manifest_uri,
        created_at="2026-10-08T10:00:00Z",
        observed_at=datetime(
            2026, 10, 8, 10, 1, tzinfo=timezone.utc
        ),
    )
    assert event["forward_oos_eligible"] is False
    assert event["publication_status"] == (
        "HISTORICAL_PUBLICATION_NOT_FORWARD_OOS"
    )
    maturity_event = build_maturity_observation_event(
        observation,
        observation_bytes=observation_bytes,
        observation_uri=observation_uri,
        trusted_prediction_event_hash=observation[
            "prediction_event_hash"
        ],
        trusted_projection_hash=observation["projection_hash"],
        previous_hash=MATURITY_LEDGER_GENESIS_HASH,
    )
    with pytest.raises(
        MaturityObservationError,
        match="EXTERNAL_PUBLICATION_BEFORE_HORIZON_REQUIRED",
    ):
        verify_maturity_observation_chain(
            [maturity_event],
            issuance_manifest_uri=manifest_uri,
            publication_receipt_uri=receipt_uri,
            evidence_root=tmp_path,
        )


def test_publication_receipt_replay_rejects_replaced_source_bytes(tmp_path):
    args, prediction, projection = build_projection()
    manifest_uri, _, _ = retain_anchor_artifacts(
        tmp_path, args, prediction, projection
    )
    receipt_uri, source_path, event = retain_publication_receipt(
        tmp_path, manifest_uri
    )
    source = json.loads(source_path.read_text(encoding="utf-8"))
    source["user"]["login"] = "attacker"
    source_path.write_text(
        json.dumps(source, sort_keys=True, indent=2),
        encoding="utf-8",
    )
    with pytest.raises(
        MaturityObservationError,
        match="PUBLICATION_SOURCE_HASH_OR_SIZE_MISMATCH",
    ):
        verify_external_publication_receipts(
            [event],
            issuance_manifest_uri=manifest_uri,
            publication_receipt_uri=receipt_uri,
            evidence_root=tmp_path,
        )


def test_maturity_ledger_requires_retained_issuance_manifest(tmp_path):
    (
        _,
        _,
        observation_uri,
        _,
        _,
        _,
        _,
    ) = retained_maturity_case(tmp_path)
    with pytest.raises(
        MaturityObservationError,
        match="ISSUANCE_MANIFEST_RETAINED_UNAVAILABLE",
    ):
        append_maturity_observation(
            tmp_path / "unregistered_maturity.ndjson",
            observation_uri,
            issuance_manifest_uri=(
                "research/forward/equity/test/missing_manifest.ndjson"
            ),
            evidence_root=tmp_path,
        )


def test_maturity_observation_ledger_is_append_only_and_source_bound(
    tmp_path,
):
    (
        observation,
        _,
        observation_uri,
        observation_path,
        anchor_artifacts,
        _,
        _,
    ) = retained_maturity_case(tmp_path)
    ledger = tmp_path / "maturity_observations.ndjson"
    event = append_maturity_observation(
        ledger,
        observation_uri,
        issuance_manifest_uri=anchor_artifacts,
        publication_receipt_uri=publication_receipt_uri_for(
            anchor_artifacts
        ),
        evidence_root=tmp_path,
    )
    assert event["observation_record_hash"] == observation["record_hash"]
    assert event["adjusted_actual_return_pct"] is None
    assert event["direction_correct"] is None
    assert event["calibration_error"] is None
    assert event["matured_adjusted_outcomes"] == 0
    assert event["order_placement_allowed"] is False
    assert read_maturity_observation_ledger(
        ledger,
        issuance_manifest_uri=anchor_artifacts,
        publication_receipt_uri=publication_receipt_uri_for(
            anchor_artifacts
        ),
        evidence_root=tmp_path,
    ) == [event]

    original = ledger.read_bytes()
    with pytest.raises(
        MaturityObservationError,
        match="OBSERVATION_RECORD_HASH_DUPLICATE",
    ):
        append_maturity_observation(
            ledger,
            observation_uri,
            issuance_manifest_uri=anchor_artifacts,
            publication_receipt_uri=publication_receipt_uri_for(
                anchor_artifacts
            ),
            evidence_root=tmp_path,
        )
    assert ledger.read_bytes() == original

    observation_path.write_bytes(b"{}")
    with pytest.raises(
        MaturityObservationError,
        match="OBSERVATION_RETAINED_HASH_OR_SIZE_MISMATCH",
    ):
        read_maturity_observation_ledger(
            ledger,
            issuance_manifest_uri=anchor_artifacts,
            publication_receipt_uri=publication_receipt_uri_for(
                anchor_artifacts
            ),
            evidence_root=tmp_path,
        )


def test_maturity_ledger_rejects_self_rehashed_anchor_replacement(tmp_path):
    (
        observation,
        _,
        _,
        _,
        anchor_artifacts,
        _,
        _,
    ) = retained_maturity_case(tmp_path)
    replaced = deepcopy(observation)
    replaced["prediction_event_hash"] = "0" * 64
    replaced["raw_reference"]["prediction_event_hash"] = "0" * 64
    replaced["projection_hash"] = "1" * 64
    replaced["raw_reference"]["projection_hash"] = "1" * 64
    payload = {
        key: value
        for key, value in replaced.items()
        if key != "record_hash"
    }
    replaced["record_hash"] = sha256(
        json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode()
    ).hexdigest()
    assert validate_maturity_observation(replaced)["orders_allowed"] is False

    replaced_uri = (
        "research/forward/equity/test/"
        "replaced_maturity_observation.json"
    )
    replaced_path = tmp_path / replaced_uri
    replaced_path.write_text(
        json.dumps(replaced, sort_keys=True, indent=2),
        encoding="utf-8",
    )
    with pytest.raises(
        MaturityObservationError,
        match="PREDICTION_EVENT_HASH_TRUST_MISMATCH",
    ):
        append_maturity_observation(
            tmp_path / "replaced.ndjson",
            replaced_uri,
            issuance_manifest_uri=anchor_artifacts,
            publication_receipt_uri=publication_receipt_uri_for(
                anchor_artifacts
            ),
            evidence_root=tmp_path,
        )


def test_maturity_verifier_rejects_caller_rehashed_anchor_event(tmp_path):
    (
        observation,
        _,
        observation_uri,
        _,
        anchor_artifacts,
        _,
        _,
    ) = retained_maturity_case(tmp_path)
    replaced = deepcopy(observation)
    replaced["prediction_event_hash"] = "2" * 64
    replaced["raw_reference"]["prediction_event_hash"] = "2" * 64
    replaced["projection_hash"] = "3" * 64
    replaced["raw_reference"]["projection_hash"] = "3" * 64
    replaced["record_hash"] = sha256(json.dumps(
        {
            key: value
            for key, value in replaced.items()
            if key != "record_hash"
        },
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode()).hexdigest()
    replaced_bytes = json.dumps(
        replaced,
        sort_keys=True,
        indent=2,
    ).encode("utf-8")
    event = build_maturity_observation_event(
        replaced,
        observation_bytes=replaced_bytes,
        observation_uri=observation_uri,
        trusted_prediction_event_hash="2" * 64,
        trusted_projection_hash="3" * 64,
        previous_hash=MATURITY_LEDGER_GENESIS_HASH,
    )
    with pytest.raises(
        MaturityObservationError,
        match="PREDICTION_EVENT_HASH_TRUST_MISMATCH",
    ):
        verify_maturity_observation_chain(
            [event],
            issuance_manifest_uri=anchor_artifacts,
            publication_receipt_uri=publication_receipt_uri_for(
                anchor_artifacts
            ),
            evidence_root=tmp_path,
        )


def test_maturity_verifier_rejects_detached_rehashed_projection(tmp_path):
    (
        observation,
        observation_bytes,
        observation_uri,
        _,
        anchor_artifacts,
        _,
        projection_path,
    ) = retained_maturity_case(tmp_path)
    event = build_maturity_observation_event(
        observation,
        observation_bytes=observation_bytes,
        observation_uri=observation_uri,
        trusted_prediction_event_hash=observation[
            "prediction_event_hash"
        ],
        trusted_projection_hash=observation["projection_hash"],
        previous_hash=MATURITY_LEDGER_GENESIS_HASH,
    )
    projection = json.loads(projection_path.read_text(encoding="utf-8"))
    projection["prediction_event_hash"] = "4" * 64
    rehash_projection(projection)
    projection_path.write_text(
        json.dumps(projection, sort_keys=True, indent=2),
        encoding="utf-8",
    )
    with pytest.raises(
        MaturityObservationError,
        match="PROJECTION_ARTIFACT_MANIFEST_MISMATCH",
    ):
        verify_maturity_observation_chain(
            [event],
            issuance_manifest_uri=anchor_artifacts,
            publication_receipt_uri=publication_receipt_uri_for(
                anchor_artifacts
            ),
            evidence_root=tmp_path,
        )


def test_maturity_verifier_rejects_non_genesis_prediction_chain(tmp_path):
    (
        observation,
        observation_bytes,
        observation_uri,
        _,
        anchor_artifacts,
        prediction_path,
        projection_path,
    ) = retained_maturity_case(tmp_path)
    event = build_maturity_observation_event(
        observation,
        observation_bytes=observation_bytes,
        observation_uri=observation_uri,
        trusted_prediction_event_hash=observation[
            "prediction_event_hash"
        ],
        trusted_projection_hash=observation["projection_hash"],
        previous_hash=MATURITY_LEDGER_GENESIS_HASH,
    )
    prediction = json.loads(prediction_path.read_text(encoding="utf-8"))
    prediction["previous_event_hash"] = "5" * 64
    rehash(prediction)
    prediction_path.write_text(
        json.dumps(prediction, sort_keys=True, indent=2),
        encoding="utf-8",
    )
    projection = json.loads(projection_path.read_text(encoding="utf-8"))
    projection["prediction_event_hash"] = prediction["event_hash"]
    rehash_projection(projection)
    projection_path.write_text(
        json.dumps(projection, sort_keys=True, indent=2),
        encoding="utf-8",
    )
    with pytest.raises(
        MaturityObservationError,
        match="PREDICTION_ARTIFACT_MANIFEST_MISMATCH",
    ):
        verify_maturity_observation_chain(
            [event],
            issuance_manifest_uri=anchor_artifacts,
            publication_receipt_uri=publication_receipt_uri_for(
                anchor_artifacts
            ),
            evidence_root=tmp_path,
        )


def test_maturity_ledger_rejects_rehashed_premature_score(tmp_path):
    (
        observation,
        observation_bytes,
        observation_uri,
        _,
        anchor_artifacts,
        _,
        _,
    ) = retained_maturity_case(tmp_path)
    event = build_maturity_observation_event(
        observation,
        observation_bytes=observation_bytes,
        observation_uri=observation_uri,
        trusted_prediction_event_hash=observation[
            "prediction_event_hash"
        ],
        trusted_projection_hash=observation["projection_hash"],
        previous_hash=MATURITY_LEDGER_GENESIS_HASH,
    )
    event["direction_correct"] = True
    event["event_hash"] = sha256(
        _canonical_maturity_ledger_event(event)
    ).hexdigest()
    with pytest.raises(
        MaturityObservationError,
        match="DIRECTION_CORRECT_PREMATURE",
    ):
        verify_maturity_observation_chain(
            [event],
            issuance_manifest_uri=anchor_artifacts,
            publication_receipt_uri=publication_receipt_uri_for(
                anchor_artifacts
            ),
            evidence_root=tmp_path,
        )


def test_retained_molbio_maturity_observation_ledger_verifies():
    root = Path(__file__).resolve().parents[1]
    manifest_uri = (
        "research/forward/equity/2026-10-01/"
        "equity_issuance_artifact_manifest.ndjson"
    )
    manifest_events = read_issuance_artifact_manifest(
        manifest_uri, evidence_root=root
    )
    by_prediction = {
        event["prediction_id"]: event for event in manifest_events
    }
    assert set(by_prediction) == {
        "EQ7D-2026-10-01-MOLBIO-V1",
        "EQ7D-2026-10-13-CMLL-V1",
    }
    historical = by_prediction["EQ7D-2026-10-01-MOLBIO-V1"]
    assert historical["pre_maturity_registered"] is False
    assert historical["registration_status"] == (
        "HISTORICAL_AFTER_MATURITY_REGISTRATION_NOT_PROVEN"
    )
    prospective = by_prediction["EQ7D-2026-10-13-CMLL-V1"]
    assert prospective["pre_maturity_registered"] is True
    assert prospective["registration_status"] == "PRE_MATURITY_REGISTERED"
    events = read_maturity_observation_ledger(
        root
        / "research/forward/equity/2026-10-01/"
        "equity_maturity_observation_ledger.ndjson",
        issuance_manifest_uri=manifest_uri,
        evidence_root=root,
    )
    assert len(events) == 1
    assert events[0]["observation_record_hash"] == (
        "d222604fb3df647e1f95373aa642f6d0"
        "0e21ac6ce2a81d3ecc6a46b28b7f4f9b"
    )
    assert events[0]["matured_adjusted_outcomes"] == 0
    assert events[0]["direction_correct"] is None
    assert events[0]["order_placement_allowed"] is False


def test_retained_cmll_publication_receipt_verifies():
    root = Path(__file__).resolve().parents[1]
    manifest_uri = (
        "research/forward/equity/2026-10-01/"
        "equity_issuance_artifact_manifest.ndjson"
    )
    events = read_external_publication_receipts(
        "research/forward/equity/2026-10-13/"
        "equity_publication_receipts.ndjson",
        issuance_manifest_uri=manifest_uri,
        evidence_root=root,
    )
    assert len(events) == 1
    assert events[0]["prediction_id"] == "EQ7D-2026-10-13-CMLL-V1"
    assert events[0]["comment_id"] == 6149542270
    assert events[0]["forward_oos_eligible"] is True
    summary = verify_external_publication_receipts(
        events,
        issuance_manifest_uri=manifest_uri,
        publication_receipt_uri=(
            "research/forward/equity/2026-10-13/"
            "equity_publication_receipts.ndjson"
        ),
        evidence_root=root,
    )
    assert summary["record_count"] == 1
    assert summary["receipt_forward_oos_eligible_count"] == 1
    assert summary["forward_oos_eligible_count"] == 0
    assert summary["publication_identity_collision_count"] == 1
    assert summary["collision_disqualified_prediction_ids"] == [
        "EQ7D-2026-10-13-CMLL-V1"
    ]
    maturity_status = verify_maturity_observation_chain(
        [],
        issuance_manifest_uri=manifest_uri,
        publication_receipt_uri=(
            "research/forward/equity/2026-10-13/"
            "equity_publication_receipts.ndjson"
        ),
        evidence_root=root,
    )
    assert maturity_status["forward_oos_publication_eligible_count"] == 0
    assert maturity_status["publication_identity_collision_count"] == 1
    assert summary["market_validation_claimed"] is False
    assert summary["order_placement_allowed"] is False
