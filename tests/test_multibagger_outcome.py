"""Numerical checks for the equity outcome contract; no claims about model skill."""
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
import json
from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

import pytest

from dashboard.backend.multibagger_outcome import (
    OUTCOME_GENESIS_HASH,
    OutcomeLedgerError,
    _canonical_outcome_event,
    append_outcome_event,
    build_outcome_event,
    read_outcome_ledger,
    reconcile,
    verify_outcome_chain,
)


HEADERS = (
    "TradDt,BizDt,Sgmt,Src,FinInstrmTp,ISIN,TckrSymb,SctySrs,SsnId,"
    "OpnPric,HghPric,LwPric,ClsPric,TtlTradgVol\n"
)


def _nse_archive(
    trade_date: str,
    symbol: str,
    close: str,
    *,
    isin: str = "INE301R01014",
) -> tuple[bytes, str]:
    stamp = trade_date.replace("-", "")
    member = f"BhavCopy_NSE_CM_0_0_0_{stamp}_F_0000.csv"
    numeric_close = float(close)
    row = (
        f"{trade_date},{trade_date},CM,NSE,STK,{isin},{symbol},EQ,F1,"
        f"{numeric_close - 1:.2f},{numeric_close + 1:.2f},"
        f"{numeric_close - 2:.2f},{close},1000\n"
    )
    buffer = BytesIO()
    info = ZipInfo(member, date_time=(2026, 1, 1, 0, 0, 0))
    info.compress_type = ZIP_DEFLATED
    with ZipFile(buffer, "w") as archive:
        archive.writestr(info, (HEADERS + row).encode("utf-8"))
    url = (
        "https://nsearchives.nseindia.com/content/cm/"
        f"{member}.zip"
    )
    return buffer.getvalue(), url


ENTRY_BYTES, ENTRY_URL = _nse_archive("2026-09-01", "RAYMOND", "100.00")
OUTCOME_BYTES, OUTCOME_URL = _nse_archive("2026-09-08", "RAYMOND", "110.00")
ENTRY_SHA = sha256(ENTRY_BYTES).hexdigest()
OUTCOME_SHA = sha256(OUTCOME_BYTES).hexdigest()
PREDICTION = {
    "prediction_id": "p-1",
    "event_hash": "a" * 64,
    "symbol": "RAYMOND",
    "isin": "INE301R01014",
    "issued_at": "2026-09-01T12:00:00+00:00",
    "due_at": "2026-09-08T10:00:00+00:00",
    "entry_observed_at": "2026-09-01T10:00:00+00:00",
    "entry_reference_close": 100.0,
    "predicted_return_pct": 20.0,
    "entry_source": "NSE",
    "entry_source_url": ENTRY_URL,
    "entry_source_hash": ENTRY_SHA,
    "entry_source_snapshot": ENTRY_BYTES,
    "entry_snapshot_uri": "snapshots/nse/entry-raymond.zip",
    "price_basis": "UNADJUSTED_EXCHANGE_REFERENCE",
    "adjustment_basis": "fixture-no-action-series-v1",
}
OUTCOME = {
    "symbol": "RAYMOND",
    "isin": "INE301R01014",
    "price_as_of_at": "2026-09-08T10:00:00+00:00",
    "source_published_at": "2026-09-08T10:05:00+00:00",
    "source_first_observed_at": "2026-09-08T10:06:00+00:00",
    "reference_close": 110.0,
    "source": "NSE",
    "source_url": OUTCOME_URL,
    "source_hash": OUTCOME_SHA,
    "source_snapshot": OUTCOME_BYTES,
    "source_snapshot_uri": "snapshots/nse/outcome-raymond.zip",
    "price_basis": "UNADJUSTED_EXCHANGE_REFERENCE",
    "adjustment_basis": "fixture-no-action-series-v1",
}
NOW = datetime(2026, 9, 24, tzinfo=timezone.utc)


def test_reconciles_signed_point_in_time_prices_without_claiming_target_hit():
    result = reconcile(PREDICTION, OUTCOME, now=NOW)
    assert result["status"] == "EVALUATED"
    assert result["actual_return_pct"] == 10.0
    assert result["absolute_error_pp"] == 10.0
    assert result["direction_correct"] is True
    assert result["outcome_price_as_of_at"] == PREDICTION["due_at"]
    assert result["outcome_source_published_at"] == OUTCOME["source_published_at"]
    assert (
        result["outcome_source_first_observed_at"]
        == OUTCOME["source_first_observed_at"]
    )
    assert result["entry_source_hash"] == ENTRY_SHA
    assert result["outcome_source_hash"] == OUTCOME_SHA
    assert len(result["entry_source_row_hash"]) == 64
    assert len(result["outcome_source_row_hash"]) == 64
    assert result["price_basis"] == "UNADJUSTED_EXCHANGE_REFERENCE"
    assert result["isin"] == "INE301R01014"
    assert result["market_validation_claimed"] is False
    assert result["live_trading_enabled"] is False
    assert result["order_placement_allowed"] is False


def test_rejects_future_outcome_or_missing_provenance():
    assert (
        reconcile(
            PREDICTION,
            {**OUTCOME, "source_first_observed_at": "2026-09-25T12:00:00+00:00"},
            now=NOW,
        )["status"]
        == "NOT_PROVEN"
    )
    assert (
        reconcile(PREDICTION, {**OUTCOME, "source_hash": ""}, now=NOW)["reason"]
        == "OUTCOME_SOURCE_HASH_INVALID_SHA256"
    )
    assert (
        reconcile(
            PREDICTION,
            {**OUTCOME, "adjustment_basis": "raw-unadjusted"},
            now=NOW,
        )["reason"]
        == "CORPORATE_ACTION_BASIS_MISMATCH"
    )


def test_rejects_non_cryptographic_hash_and_unapproved_source():
    assert (
        reconcile(
            {**PREDICTION, "entry_source_hash": "entry-sha"},
            OUTCOME,
            now=NOW,
        )["reason"]
        == "ENTRY_SOURCE_HASH_INVALID_SHA256"
    )
    assert (
        reconcile(
            {**PREDICTION, "entry_source": "BLOG"},
            OUTCOME,
            now=NOW,
        )["reason"]
        == "ENTRY_SOURCE_UNVERIFIED"
    )
    assert (
        reconcile(
            PREDICTION,
            {**OUTCOME, "source": "BLOG"},
            now=NOW,
        )["reason"]
        == "OUTCOME_SOURCE_UNVERIFIED"
    )


def test_rejects_outcome_before_horizon_and_invalid_numbers():
    assert (
        reconcile(
            PREDICTION,
            {**OUTCOME, "price_as_of_at": "2026-09-07T10:00:00+00:00"},
            now=NOW,
        )["reason"]
        == "OUTCOME_HORIZON_MISMATCH"
    )
    assert (
        reconcile(
            PREDICTION,
            {**OUTCOME, "reference_close": float("nan")},
            now=NOW,
        )["reason"]
        == "INVALID_PRICE"
    )
    assert (
        reconcile(
            {**PREDICTION, "predicted_return_pct": True},
            OUTCOME,
            now=NOW,
        )["reason"]
        == "INVALID_FORECAST"
    )


@pytest.mark.parametrize(
    "mutation,error",
    [
        (
            lambda record: record.update(
                price_as_of_at="2026-09-09T10:00:00+00:00",
                source_published_at="2026-09-09T10:05:00+00:00",
                source_first_observed_at="2026-09-09T10:06:00+00:00",
                reference_close=200.0,
            ),
            "OUTCOME_HORIZON_MISMATCH",
        ),
        (
            lambda record: record.update(
                source_published_at="2026-09-08T09:59:59+00:00"
            ),
            "INVALID_SOURCE_TIME_ORDER",
        ),
        (
            lambda record: record.update(
                source_first_observed_at="2026-09-08T10:04:59+00:00"
            ),
            "INVALID_SOURCE_TIME_ORDER",
        ),
        (
            lambda record: record.pop("price_as_of_at"),
            "REQUIRED_EVIDENCE_MISSING",
        ),
    ],
)
def test_horizon_and_source_availability_timestamps_fail_closed(
    mutation,
    error,
):
    outcome = dict(OUTCOME)
    mutation(outcome)
    result = reconcile(PREDICTION, outcome, now=NOW)
    assert result["status"] == "NOT_PROVEN"
    assert result["reason"] == error


def test_rejects_naive_evaluation_clock():
    result = reconcile(
        PREDICTION,
        OUTCOME,
        now=datetime(2026, 9, 24),
    )
    assert result["status"] == "NOT_PROVEN"
    assert result["reason"] == "NOW_TIMEZONE_REQUIRED"


def test_requires_actual_retained_source_bytes_and_matching_digest():
    assert reconcile(
        {**PREDICTION, "entry_source_snapshot": b"tampered"},
        OUTCOME,
        now=NOW,
    )["reason"] == "ENTRY_SNAPSHOT_HASH_MISMATCH"
    assert reconcile(
        PREDICTION,
        {**OUTCOME, "source_snapshot": b"tampered"},
        now=NOW,
    )["reason"] == "OUTCOME_SNAPSHOT_HASH_MISMATCH"
    assert reconcile(
        {key: value for key, value in PREDICTION.items() if key != "entry_source_snapshot"},
        OUTCOME,
        now=NOW,
    )["reason"] == "ENTRY_SNAPSHOT_REQUIRED"


@pytest.mark.parametrize(
    "prediction,outcome,error",
    [
        (
            {**PREDICTION, "entry_reference_close": 999.0},
            OUTCOME,
            "ENTRY_PRICE_EVIDENCE_MISMATCH",
        ),
        (
            PREDICTION,
            {**OUTCOME, "reference_close": 999.0},
            "OUTCOME_PRICE_EVIDENCE_MISMATCH",
        ),
    ],
)
def test_declared_prices_are_bound_to_exact_retained_nse_rows(
    prediction,
    outcome,
    error,
):
    result = reconcile(prediction, outcome, now=NOW)
    assert result["status"] == "NOT_PROVEN"
    assert result["reason"] == error


def test_rejects_rehashed_archive_with_wrong_symbol():
    wrong_bytes, _ = _nse_archive("2026-09-08", "NOTRAYMOND", "110.00")
    result = reconcile(
        PREDICTION,
        {
            **OUTCOME,
            "source_snapshot": wrong_bytes,
            "source_hash": sha256(wrong_bytes).hexdigest(),
        },
        now=NOW,
    )
    assert result["status"] == "NOT_PROVEN"
    assert result["reason"] == "OUTCOME_NSE_PRICE_ROW_NOT_FOUND"


def test_rejects_rehashed_archive_with_wrong_isin():
    wrong_bytes, _ = _nse_archive(
        "2026-09-08",
        "RAYMOND",
        "110.00",
        isin="INE000X01000",
    )
    result = reconcile(
        PREDICTION,
        {
            **OUTCOME,
            "source_snapshot": wrong_bytes,
            "source_hash": sha256(wrong_bytes).hexdigest(),
        },
        now=NOW,
    )
    assert result["status"] == "NOT_PROVEN"
    assert result["reason"] == "OUTCOME_NSE_ISIN_MISMATCH"


def test_binds_official_url_date_member_and_close_timestamp():
    assert reconcile(
        PREDICTION,
        {
            **OUTCOME,
            "source_url": OUTCOME_URL.replace("20260908", "20260909"),
        },
        now=NOW,
    )["reason"] == "OUTCOME_NSE_PRICE_TIMESTAMP_MISMATCH"

    shifted = {
        **OUTCOME,
        "price_as_of_at": "2026-09-08T10:01:00+00:00",
    }
    shifted_prediction = {
        **PREDICTION,
        "due_at": shifted["price_as_of_at"],
    }
    assert (
        reconcile(shifted_prediction, shifted, now=NOW)["reason"]
        == "OUTCOME_NSE_PRICE_TIMESTAMP_MISMATCH"
    )



TRUSTED_PREDICTION_HASHES = {"p-1": "a" * 64}


@pytest.fixture
def outcome_evidence_root(tmp_path):
    root = tmp_path / "evidence"
    for reference, payload in (
        (PREDICTION["entry_snapshot_uri"], ENTRY_BYTES),
        (OUTCOME["source_snapshot_uri"], OUTCOME_BYTES),
    ):
        path = root / reference
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
    return root


def _rehash_outcome_event(record):
    record["event_hash"] = sha256(_canonical_outcome_event(record)).hexdigest()


def test_builds_deterministic_outcome_event_bound_to_trusted_prediction():
    first = build_outcome_event(
        PREDICTION,
        OUTCOME,
        trusted_prediction_event_hash="a" * 64,
        previous_hash=OUTCOME_GENESIS_HASH,
        now=NOW,
    )
    second = build_outcome_event(
        PREDICTION,
        OUTCOME,
        trusted_prediction_event_hash="a" * 64,
        previous_hash=OUTCOME_GENESIS_HASH,
        now=NOW,
    )
    assert first == second
    assert first["prediction_event_hash"] == "a" * 64
    assert first["actual_return_pct"] == 10.0
    assert first["entry_source_row_hash"]
    assert first["outcome_source_row_hash"]
    assert first["market_validation_claimed"] is False
    assert first["reference_prices_are_executable_fills"] is False
    assert first["performance_gate_passed"] is False
    assert first["real_money_ready"] is False
    assert first["live_trading_enabled"] is False
    assert first["order_placement_allowed"] is False
    verified = verify_outcome_chain(
        [first],
        trusted_prediction_hashes=TRUSTED_PREDICTION_HASHES,
    )
    assert verified["record_count"] == 1
    assert verified["performance_gate_passed"] is False
    assert verified["real_money_ready"] is False


def test_outcome_builder_requires_both_explicit_chain_anchors():
    with pytest.raises(TypeError, match="trusted_prediction_event_hash"):
        build_outcome_event(
            PREDICTION,
            OUTCOME,
            previous_hash=OUTCOME_GENESIS_HASH,
            now=NOW,
        )
    with pytest.raises(TypeError, match="previous_hash"):
        build_outcome_event(
            PREDICTION,
            OUTCOME,
            trusted_prediction_event_hash="a" * 64,
            now=NOW,
        )


def test_append_is_durable_and_duplicate_prediction_fails_closed(
    tmp_path,
    outcome_evidence_root,
):
    ledger = tmp_path / "equity_outcomes.ndjson"
    sealed = append_outcome_event(
        ledger,
        PREDICTION,
        OUTCOME,
        trusted_prediction_hashes=TRUSTED_PREDICTION_HASHES,
        evidence_root=outcome_evidence_root,
        now=NOW,
    )
    assert read_outcome_ledger(
        ledger,
        trusted_prediction_hashes=TRUSTED_PREDICTION_HASHES,
        evidence_root=outcome_evidence_root,
    ) == [sealed]
    original = ledger.read_bytes()
    with pytest.raises(OutcomeLedgerError, match="PREDICTION_ID_DUPLICATE"):
        append_outcome_event(
            ledger,
            PREDICTION,
            OUTCOME,
            trusted_prediction_hashes=TRUSTED_PREDICTION_HASHES,
            evidence_root=outcome_evidence_root,
            now=NOW,
        )
    assert ledger.read_bytes() == original


def test_rehashed_prediction_anchor_substitution_is_rejected():
    event = build_outcome_event(
        PREDICTION,
        OUTCOME,
        trusted_prediction_event_hash="a" * 64,
        previous_hash=OUTCOME_GENESIS_HASH,
        now=NOW,
    )
    event["prediction_event_hash"] = "b" * 64
    _rehash_outcome_event(event)
    with pytest.raises(
        OutcomeLedgerError,
        match="PREDICTION_EVENT_HASH_TRUST_MISMATCH",
    ):
        verify_outcome_chain(
            [event],
            trusted_prediction_hashes=TRUSTED_PREDICTION_HASHES,
        )


def test_rehashed_outcome_arithmetic_substitution_is_rejected():
    event = build_outcome_event(
        PREDICTION,
        OUTCOME,
        trusted_prediction_event_hash="a" * 64,
        previous_hash=OUTCOME_GENESIS_HASH,
        now=NOW,
    )
    event["actual_return_pct"] = 999.0
    _rehash_outcome_event(event)
    with pytest.raises(OutcomeLedgerError, match="ARITHMETIC_MISMATCH"):
        verify_outcome_chain(
            [event],
            trusted_prediction_hashes=TRUSTED_PREDICTION_HASHES,
        )


def test_execution_claims_are_rejected_even_when_rehashed():
    event = build_outcome_event(
        PREDICTION,
        OUTCOME,
        trusted_prediction_event_hash="a" * 64,
        previous_hash=OUTCOME_GENESIS_HASH,
        now=NOW,
    )
    event["reference_prices_are_executable_fills"] = True
    _rehash_outcome_event(event)
    with pytest.raises(
        OutcomeLedgerError,
        match="REFERENCE_PRICE_EXECUTION_FLAG_INVALID",
    ):
        verify_outcome_chain(
            [event],
            trusted_prediction_hashes=TRUSTED_PREDICTION_HASHES,
        )

    event = build_outcome_event(
        PREDICTION,
        OUTCOME,
        trusted_prediction_event_hash="a" * 64,
        previous_hash=OUTCOME_GENESIS_HASH,
        now=NOW,
    )
    event["quantity"] = 100
    _rehash_outcome_event(event)
    with pytest.raises(OutcomeLedgerError, match="FIELDS_INVALID"):
        verify_outcome_chain(
            [event],
            trusted_prediction_hashes=TRUSTED_PREDICTION_HASHES,
        )


def test_retained_outcome_replacement_is_detected(
    tmp_path,
    outcome_evidence_root,
):
    ledger = tmp_path / "equity_outcomes.ndjson"
    append_outcome_event(
        ledger,
        PREDICTION,
        OUTCOME,
        trusted_prediction_hashes=TRUSTED_PREDICTION_HASHES,
        evidence_root=outcome_evidence_root,
        now=NOW,
    )
    outcome_path = outcome_evidence_root / OUTCOME["source_snapshot_uri"]
    outcome_path.write_bytes(b"replaced")
    with pytest.raises(
        OutcomeLedgerError,
        match="OUTCOME_RETAINED_HASH_OR_SIZE_MISMATCH",
    ):
        read_outcome_ledger(
            ledger,
            trusted_prediction_hashes=TRUSTED_PREDICTION_HASHES,
            evidence_root=outcome_evidence_root,
        )


def test_chronological_backfill_rejection_preserves_ledger_bytes(
    tmp_path,
    outcome_evidence_root,
):
    ledger = tmp_path / "equity_outcomes.ndjson"
    append_outcome_event(
        ledger,
        PREDICTION,
        OUTCOME,
        trusted_prediction_hashes=TRUSTED_PREDICTION_HASHES,
        evidence_root=outcome_evidence_root,
        now=NOW,
    )
    original = ledger.read_bytes()
    second_prediction = {
        **PREDICTION,
        "prediction_id": "p-2",
        "event_hash": "b" * 64,
    }
    trusted = {**TRUSTED_PREDICTION_HASHES, "p-2": "b" * 64}
    earlier = datetime(2026, 9, 23, tzinfo=timezone.utc)
    with pytest.raises(OutcomeLedgerError, match="RECORDED_ORDER_INVALID"):
        append_outcome_event(
            ledger,
            second_prediction,
            OUTCOME,
            trusted_prediction_hashes=trusted,
            evidence_root=outcome_evidence_root,
            now=earlier,
        )
    assert ledger.read_bytes() == original
