"""Contract tests for the append-only equity forecast ledger."""
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
import json

import pytest

from dashboard.backend.multibagger_ledger import (
    GENESIS_HASH,
    LedgerError,
    _canonical,
    _ledger_lock,
    append_issued_forecast,
    build_issued_forecast,
    read_ledger,
    verify_chain,
)


NOW = datetime(2026, 9, 1, 13, tzinfo=timezone.utc)
SOURCE_BYTES = b"NSE,2026-09-01,RAYMOND,100.00"
ADJUSTMENT_BYTES = (
    b"NSE_CORPORATE_ACTIONS,observed=2026-09-01,RAYMOND,NONE"
)
FORECAST = {
    "prediction_id": "equity-20260901-raymond-7d-v1",
    "symbol": "RAYMOND",
    "horizon_days": 7,
    "issued_at": "2026-09-01T12:00:00+00:00",
    "due_at": "2026-09-08T12:00:00+00:00",
    "entry_observed_at": "2026-09-01T10:00:00+00:00",
    "entry_adjusted_close": 100.0,
    "predicted_return_pct": 8.5,
    "model_name": "multibagger-research",
    "model_version": "candidate-v1",
    "feature_hash": "2" * 64,
    "entry_source": "NSE",
    "entry_source_hash": sha256(SOURCE_BYTES).hexdigest(),
    "entry_source_snapshot": SOURCE_BYTES,
    "entry_snapshot_uri": (
        "snapshots/nse/2026-09-01/RAYMOND-equity.csv"
    ),
    "adjustment_basis": "corporate-action-series-v1",
    "adjustment_observed_at": "2026-09-01T10:30:00+00:00",
    "adjustment_source": "NSE",
    "adjustment_source_hash": sha256(ADJUSTMENT_BYTES).hexdigest(),
    "adjustment_source_snapshot": ADJUSTMENT_BYTES,
    "adjustment_snapshot_uri": (
        "snapshots/nse/2026-09-01/RAYMOND-corporate-actions.csv"
    ),
}


@pytest.fixture
def evidence_root(tmp_path):
    root = tmp_path / "evidence"
    for key, payload in (("entry", SOURCE_BYTES), ("adjustment", ADJUSTMENT_BYTES)):
        path = root / FORECAST[f"{key}_snapshot_uri"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
    return root


def test_builds_deterministic_fail_closed_equity_event():
    first = build_issued_forecast(
        FORECAST,
        previous_hash=GENESIS_HASH,
        now=NOW,
    )
    second = build_issued_forecast(
        FORECAST,
        previous_hash=GENESIS_HASH,
        now=NOW,
    )
    assert first == second
    assert first["previous_hash"] == GENESIS_HASH
    assert len(first["event_hash"]) == 64
    assert first["entry_source_size_bytes"] == len(SOURCE_BYTES)
    assert first["adjustment_source_size_bytes"] == len(ADJUSTMENT_BYTES)
    assert "entry_source_snapshot" not in first
    assert "adjustment_source_snapshot" not in first
    assert first["live_trading_enabled"] is False
    assert first["order_placement_allowed"] is False
    assert verify_chain([first])["record_count"] == 1


def test_builder_requires_explicit_trusted_predecessor_anchor():
    with pytest.raises(TypeError, match="previous_hash"):
        build_issued_forecast(FORECAST, now=NOW)


def test_append_preserves_chain_and_rejects_duplicate(tmp_path, evidence_root):
    ledger = tmp_path / "equity_forecasts.ndjson"
    first = append_issued_forecast(ledger, FORECAST, evidence_root=evidence_root, now=NOW)
    later = {
        **FORECAST,
        "prediction_id": "equity-20260901-raymond-30d-v1",
        "horizon_days": 30,
        "due_at": "2026-10-01T12:00:00+00:00",
    }
    second = append_issued_forecast(ledger, later, evidence_root=evidence_root, now=NOW)
    records = read_ledger(ledger, evidence_root=evidence_root)
    assert len(records) == 2
    assert second["previous_hash"] == first["event_hash"]
    assert verify_chain(records)["head_hash"] == second["event_hash"]
    with pytest.raises(LedgerError, match="PREDICTION_ID_DUPLICATE"):
        append_issued_forecast(ledger, FORECAST, evidence_root=evidence_root, now=NOW)


def test_append_rejects_chronological_backfill_without_writing(
    tmp_path,
    evidence_root,
):
    ledger = tmp_path / "equity_forecasts.ndjson"
    first = append_issued_forecast(
        ledger,
        FORECAST,
        evidence_root=evidence_root,
        now=NOW,
    )
    original = ledger.read_bytes()
    backfill = {
        **FORECAST,
        "prediction_id": "equity-20260901-raymond-backfill-v1",
        "issued_at": "2026-09-01T11:00:00+00:00",
        "due_at": "2026-09-08T11:00:00+00:00",
    }

    with pytest.raises(LedgerError, match="ROW_1_ISSUED_ORDER_INVALID"):
        append_issued_forecast(
            ledger,
            backfill,
            evidence_root=evidence_root,
            now=NOW,
        )

    assert ledger.read_bytes() == original
    assert read_ledger(ledger, evidence_root=evidence_root) == [first]


def test_exclusive_lock_serializes_a_competing_writer(tmp_path, evidence_root):
    ledger = tmp_path / "equity_forecasts.ndjson"
    with ThreadPoolExecutor(max_workers=1) as pool:
        with _ledger_lock(ledger, exclusive=True):
            pending = pool.submit(
                append_issued_forecast,
                ledger,
                FORECAST,
                evidence_root=evidence_root,
                now=NOW,
            )
            with pytest.raises(FutureTimeout):
                pending.result(timeout=0.05)
        sealed = pending.result(timeout=2)

    records = read_ledger(ledger, evidence_root=evidence_root)
    assert records == [sealed]
    assert verify_chain(records)["status"] == "VERIFIED"


def test_concurrent_unique_forecasts_preserve_every_record_and_hash_link(tmp_path, evidence_root):
    ledger = tmp_path / "equity_forecasts.ndjson"
    forecasts = [
        {**FORECAST, "prediction_id": f"equity-concurrent-{index:02d}"}
        for index in range(16)
    ]
    with ThreadPoolExecutor(max_workers=8) as pool:
        sealed = list(
            pool.map(
                lambda forecast: append_issued_forecast(
                    ledger,
                    forecast,
                    evidence_root=evidence_root,
                    now=NOW,
                ),
                forecasts,
            )
        )

    records = read_ledger(ledger, evidence_root=evidence_root)
    assert len(sealed) == len(records) == 16
    assert {row["prediction_id"] for row in records} == {
        row["prediction_id"] for row in forecasts
    }
    assert verify_chain(records)["head_hash"] == records[-1]["event_hash"]


def test_tampering_and_truncation_are_detected(tmp_path, evidence_root):
    ledger = tmp_path / "equity_forecasts.ndjson"
    sealed = append_issued_forecast(ledger, FORECAST, evidence_root=evidence_root, now=NOW)

    tampered = deepcopy(sealed)
    tampered["predicted_return_pct"] = 99.0
    with pytest.raises(LedgerError, match="HASH_MISMATCH"):
        verify_chain([tampered])

    ledger.write_text(json.dumps(sealed), encoding="utf-8")
    with pytest.raises(LedgerError, match="LEDGER_TRUNCATED"):
        read_ledger(ledger, evidence_root=evidence_root)


@pytest.mark.parametrize(
    "mutation",
    [
        lambda record: record.update(trade_action="BUY"),
        lambda record: record.update(quantity=100),
        lambda record: record.update(entry_reference_is_executable_fill=True),
        lambda record: record.pop("model_version"),
    ],
)
def test_rehashed_undeclared_or_missing_fields_fail_closed(mutation):
    sealed = build_issued_forecast(
        FORECAST,
        previous_hash=GENESIS_HASH,
        now=NOW,
    )
    mutation(sealed)
    sealed["event_hash"] = sha256(_canonical(sealed)).hexdigest()
    with pytest.raises(LedgerError, match="ROW_0_FIELDS_INVALID"):
        verify_chain([sealed])


@pytest.mark.parametrize(
    "mutation,error",
    [
        (
            lambda record: record.update(
                due_at="2026-09-15T12:00:00+00:00"
            ),
            "ROW_0_HORIZON_DUE_MISMATCH",
        ),
        (
            lambda record: record.update(
                due_at="2026-09-01T11:59:59+00:00"
            ),
            "ROW_0_INVALID_FORECAST_TIME_ORDER",
        ),
        (
            lambda record: record.update(
                entry_observed_at="2026-09-01T12:00:01+00:00"
            ),
            "ROW_0_INVALID_FORECAST_TIME_ORDER",
        ),
        (
            lambda record: record.update(
                adjustment_observed_at="2026-09-01T12:00:01+00:00"
            ),
            "ROW_0_ADJUSTMENT_LOOKAHEAD_FORBIDDEN",
        ),
        (
            lambda record: record.update(horizon_days=True),
            "ROW_0_HORIZON_DAYS_INVALID",
        ),
    ],
)
def test_rehashed_temporal_contract_bypass_fails_closed(mutation, error):
    sealed = build_issued_forecast(
        FORECAST,
        previous_hash=GENESIS_HASH,
        now=NOW,
    )
    mutation(sealed)
    sealed["event_hash"] = sha256(_canonical(sealed)).hexdigest()
    with pytest.raises(LedgerError, match=error):
        verify_chain([sealed])


@pytest.mark.parametrize(
    "mutation,error",
    [
        (
            lambda record: record.update(prediction_id=7),
            "ROW_0_PREDICTION_ID_INVALID",
        ),
        (
            lambda record: record.update(symbol=""),
            "ROW_0_SYMBOL_INVALID",
        ),
        (
            lambda record: record.update(model_version=""),
            "ROW_0_MODEL_IDENTITY_INVALID",
        ),
        (
            lambda record: record.update(adjustment_basis=""),
            "ROW_0_ADJUSTMENT_BASIS_INVALID",
        ),
        (
            lambda record: record.update(entry_source="BLOG"),
            "ROW_0_ENTRY_SOURCE_UNVERIFIED",
        ),
        (
            lambda record: record.update(adjustment_source="BLOG"),
            "ROW_0_ADJUSTMENT_SOURCE_UNVERIFIED",
        ),
        (
            lambda record: record.update(entry_adjusted_close=0),
            "ROW_0_ENTRY_ADJUSTED_CLOSE_INVALID",
        ),
        (
            lambda record: record.update(predicted_return_pct=True),
            "ROW_0_PREDICTED_RETURN_PCT_INVALID",
        ),
        (
            lambda record: record.update(feature_hash="f" * 63),
            "ROW_0_FEATURE_HASH_INVALID_SHA256",
        ),
        (
            lambda record: record.update(entry_source_size_bytes=True),
            "ROW_0_ENTRY_SOURCE_SIZE_BYTES_INVALID",
        ),
        (
            lambda record: record.update(
                entry_snapshot_uri="other/archive/file.csv"
            ),
            "ROW_0_ENTRY_SNAPSHOT_URI_UNAPPROVED_PREFIX",
        ),
    ],
)
def test_rehashed_semantic_contract_bypass_fails_closed(mutation, error):
    sealed = build_issued_forecast(
        FORECAST,
        previous_hash=GENESIS_HASH,
        now=NOW,
    )
    mutation(sealed)
    sealed["event_hash"] = sha256(_canonical(sealed)).hexdigest()
    with pytest.raises(LedgerError, match=error):
        verify_chain([sealed])


def test_read_rejects_rehashed_unapproved_source_with_matching_retained_bytes(
    tmp_path,
    evidence_root,
):
    sealed = build_issued_forecast(
        FORECAST,
        previous_hash=GENESIS_HASH,
        now=NOW,
    )
    sealed["entry_source"] = "BLOG"
    sealed["event_hash"] = sha256(_canonical(sealed)).hexdigest()
    ledger = tmp_path / "equity_forecasts.ndjson"
    ledger.write_text(
        json.dumps(sealed, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(LedgerError, match="ROW_0_ENTRY_SOURCE_UNVERIFIED"):
        read_ledger(ledger, evidence_root=evidence_root)


def test_read_rejects_rehashed_horizon_mismatch(
    tmp_path,
    evidence_root,
):
    sealed = build_issued_forecast(
        FORECAST,
        previous_hash=GENESIS_HASH,
        now=NOW,
    )
    sealed["due_at"] = "2026-09-15T12:00:00+00:00"
    sealed["event_hash"] = sha256(_canonical(sealed)).hexdigest()
    ledger = tmp_path / "equity_forecasts.ndjson"
    ledger.write_text(
        json.dumps(sealed, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(LedgerError, match="ROW_0_HORIZON_DUE_MISMATCH"):
        read_ledger(ledger, evidence_root=evidence_root)


def test_lookahead_backfill_and_bad_provenance_fail_closed():
    with pytest.raises(LedgerError, match="INVALID_FORECAST_TIME_ORDER"):
        build_issued_forecast(
            FORECAST,
            previous_hash=GENESIS_HASH,
            now=datetime(2026, 9, 9, tzinfo=timezone.utc),
        )
    with pytest.raises(LedgerError, match="ENTRY_SOURCE_UNVERIFIED"):
        build_issued_forecast(
            {**FORECAST, "entry_source": "BLOG"},
            previous_hash=GENESIS_HASH,
            now=NOW,
        )
    with pytest.raises(LedgerError, match="HORIZON_DUE_MISMATCH"):
        build_issued_forecast(
            {**FORECAST, "horizon_days": 30},
            previous_hash=GENESIS_HASH,
            now=NOW,
        )


def test_declared_source_hash_must_match_retained_exact_bytes():
    without_bytes = dict(FORECAST)
    without_bytes.pop("entry_source_snapshot")
    with pytest.raises(LedgerError, match="ENTRY_SOURCE_SNAPSHOT_REQUIRED"):
        build_issued_forecast(
            without_bytes,
            previous_hash=GENESIS_HASH,
            now=NOW,
        )

    with pytest.raises(LedgerError, match="ENTRY_SOURCE_SNAPSHOT_HASH_MISMATCH"):
        build_issued_forecast(
            {**FORECAST, "entry_source_snapshot": b"different NSE bytes"},
            previous_hash=GENESIS_HASH,
            now=NOW,
        )


def test_adjustment_basis_requires_point_in_time_exact_source_bytes():
    without_bytes = dict(FORECAST)
    without_bytes.pop("adjustment_source_snapshot")
    with pytest.raises(
        LedgerError,
        match="ADJUSTMENT_SOURCE_SNAPSHOT_REQUIRED",
    ):
        build_issued_forecast(
            without_bytes,
            previous_hash=GENESIS_HASH,
            now=NOW,
        )

    with pytest.raises(
        LedgerError,
        match="ADJUSTMENT_SOURCE_SNAPSHOT_HASH_MISMATCH",
    ):
        build_issued_forecast(
            {
                **FORECAST,
                "adjustment_source_snapshot": b"different adjustment bytes",
            },
            previous_hash=GENESIS_HASH,
            now=NOW,
        )

    with pytest.raises(LedgerError, match="ADJUSTMENT_SOURCE_UNVERIFIED"):
        build_issued_forecast(
            {**FORECAST, "adjustment_source": "BLOG"},
            previous_hash=GENESIS_HASH,
            now=NOW,
        )

    with pytest.raises(LedgerError, match="ADJUSTMENT_LOOKAHEAD_FORBIDDEN"):
        build_issued_forecast(
            {
                **FORECAST,
                "adjustment_observed_at": "2026-09-01T12:01:00+00:00",
            },
            previous_hash=GENESIS_HASH,
            now=NOW,
        )


@pytest.mark.parametrize(
    "field,value,error",
    [
        ("entry_snapshot_uri", "../../tmp/source.csv", "INVALID"),
        ("entry_snapshot_uri", "/tmp/source.csv", "INVALID"),
        ("entry_snapshot_uri", "https://nse.example/file.csv", "INVALID"),
        ("entry_snapshot_uri", r"snapshots\nse\file.csv", "INVALID"),
        ("entry_snapshot_uri", "snapshots/nse/../file.csv", "INVALID"),
        (
            "adjustment_snapshot_uri",
            "research/evidence/%2e%2e/file.csv",
            "INVALID",
        ),
        (
            "adjustment_snapshot_uri",
            "other/archive/file.csv",
            "UNAPPROVED_PREFIX",
        ),
        (
            "adjustment_snapshot_uri",
            " snapshots/nse/file.csv",
            "INVALID",
        ),
    ],
)
def test_snapshot_references_reject_spoofing_and_path_traversal(
    field,
    value,
    error,
):
    with pytest.raises(LedgerError, match=f"{field.upper()}_{error}"):
        build_issued_forecast(
            {**FORECAST, field: value},
            previous_hash=GENESIS_HASH,
            now=NOW,
        )


@pytest.mark.parametrize("source", ["entry", "adjustment"])
@pytest.mark.parametrize("change", ["missing", "replaced", "directory"])
def test_append_rejects_unretained_source_without_writing(tmp_path, evidence_root, source, change):
    path = evidence_root / FORECAST[f"{source}_snapshot_uri"]
    path.unlink()
    if change == "replaced":
        path.write_bytes(b"replacement")
    elif change == "directory":
        path.mkdir()
    ledger = tmp_path / "equity.ndjson"
    with pytest.raises(LedgerError, match=f"{source.upper()}_RETAINED_"):
        append_issued_forecast(ledger, FORECAST, evidence_root=evidence_root, now=NOW)
    assert not ledger.exists()


@pytest.mark.parametrize("source", ["entry", "adjustment"])
@pytest.mark.parametrize("change", ["missing", "replaced"])
def test_read_and_later_append_recheck_every_retained_source(tmp_path, evidence_root, source, change):
    ledger = tmp_path / "equity.ndjson"
    sealed = append_issued_forecast(ledger, FORECAST, evidence_root=evidence_root, now=NOW)
    original = ledger.read_bytes()
    path = evidence_root / FORECAST[f"{source}_snapshot_uri"]
    path.unlink()
    if change == "replaced":
        path.write_bytes(b"replacement")
    assert verify_chain([sealed])["verification_scope"] == "HASH_CHAIN_AND_SEMANTICS"
    with pytest.raises(LedgerError, match=f"{source.upper()}_RETAINED_"):
        read_ledger(ledger, evidence_root=evidence_root)
    with pytest.raises(LedgerError, match=f"{source.upper()}_RETAINED_"):
        append_issued_forecast(
            ledger, {**FORECAST, "prediction_id": "later"}, evidence_root=evidence_root, now=NOW
        )
    assert ledger.read_bytes() == original


@pytest.mark.parametrize("link_parent", [False, True])
def test_retained_links_rejected_even_with_matching_bytes(tmp_path, evidence_root, link_parent):
    outside = tmp_path / "outside"
    outside.mkdir()
    target = outside / "source.csv"
    target.write_bytes(SOURCE_BYTES)
    path = evidence_root / FORECAST["entry_snapshot_uri"]
    path.unlink()
    if link_parent:
        link = evidence_root / "snapshots" / "linked"
        link.symlink_to(outside, target_is_directory=True)
        forecast = {**FORECAST, "entry_snapshot_uri": "snapshots/linked/source.csv"}
    else:
        path.symlink_to(target)
        forecast = FORECAST
    with pytest.raises(LedgerError, match="ENTRY_RETAINED_LINK_FORBIDDEN"):
        append_issued_forecast(tmp_path / "equity.ndjson", forecast, evidence_root=evidence_root, now=NOW)


def test_evidence_root_is_mandatory_and_cannot_be_replaced_by_another_archive(tmp_path, evidence_root):
    ledger = tmp_path / "equity.ndjson"
    with pytest.raises(TypeError, match="evidence_root"):
        append_issued_forecast(ledger, FORECAST, now=NOW)
    append_issued_forecast(ledger, FORECAST, evidence_root=evidence_root, now=NOW)
    with pytest.raises(TypeError, match="evidence_root"):
        read_ledger(ledger)
    with pytest.raises(LedgerError, match="EVIDENCE_ROOT_UNAVAILABLE"):
        read_ledger(ledger, evidence_root=tmp_path / "absent")
