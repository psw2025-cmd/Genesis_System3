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
    _ledger_lock,
    append_issued_forecast,
    build_issued_forecast,
    read_ledger,
    verify_chain,
)


NOW = datetime(2026, 9, 1, 13, tzinfo=timezone.utc)
SOURCE_BYTES = b"NSE,2026-09-01,RAYMOND,100.00"
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
}


def test_builds_deterministic_fail_closed_equity_event():
    first = build_issued_forecast(FORECAST, now=NOW)
    second = build_issued_forecast(FORECAST, now=NOW)
    assert first == second
    assert first["previous_hash"] == GENESIS_HASH
    assert len(first["event_hash"]) == 64
    assert first["entry_source_size_bytes"] == len(SOURCE_BYTES)
    assert "entry_source_snapshot" not in first
    assert first["live_trading_enabled"] is False
    assert first["order_placement_allowed"] is False
    assert verify_chain([first])["record_count"] == 1


def test_append_preserves_chain_and_rejects_duplicate(tmp_path):
    ledger = tmp_path / "equity_forecasts.ndjson"
    first = append_issued_forecast(ledger, FORECAST, now=NOW)
    later = {
        **FORECAST,
        "prediction_id": "equity-20260901-raymond-30d-v1",
        "horizon_days": 30,
        "due_at": "2026-10-01T12:00:00+00:00",
    }
    second = append_issued_forecast(ledger, later, now=NOW)
    records = read_ledger(ledger)
    assert len(records) == 2
    assert second["previous_hash"] == first["event_hash"]
    assert verify_chain(records)["head_hash"] == second["event_hash"]
    with pytest.raises(LedgerError, match="PREDICTION_ID_DUPLICATE"):
        append_issued_forecast(ledger, FORECAST, now=NOW)


def test_exclusive_lock_serializes_a_competing_writer(tmp_path):
    ledger = tmp_path / "equity_forecasts.ndjson"
    with ThreadPoolExecutor(max_workers=1) as pool:
        with _ledger_lock(ledger, exclusive=True):
            pending = pool.submit(
                append_issued_forecast,
                ledger,
                FORECAST,
                now=NOW,
            )
            with pytest.raises(FutureTimeout):
                pending.result(timeout=0.05)
        sealed = pending.result(timeout=2)

    records = read_ledger(ledger)
    assert records == [sealed]
    assert verify_chain(records)["status"] == "VERIFIED"


def test_concurrent_unique_forecasts_preserve_every_record_and_hash_link(tmp_path):
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
                    now=NOW,
                ),
                forecasts,
            )
        )

    records = read_ledger(ledger)
    assert len(sealed) == len(records) == 16
    assert {row["prediction_id"] for row in records} == {
        row["prediction_id"] for row in forecasts
    }
    assert verify_chain(records)["head_hash"] == records[-1]["event_hash"]


def test_tampering_and_truncation_are_detected(tmp_path):
    ledger = tmp_path / "equity_forecasts.ndjson"
    sealed = append_issued_forecast(ledger, FORECAST, now=NOW)

    tampered = deepcopy(sealed)
    tampered["predicted_return_pct"] = 99.0
    with pytest.raises(LedgerError, match="HASH_MISMATCH"):
        verify_chain([tampered])

    ledger.write_text(json.dumps(sealed), encoding="utf-8")
    with pytest.raises(LedgerError, match="LEDGER_TRUNCATED"):
        read_ledger(ledger)


def test_lookahead_backfill_and_bad_provenance_fail_closed():
    with pytest.raises(LedgerError, match="INVALID_FORECAST_TIME_ORDER"):
        build_issued_forecast(
            FORECAST,
            now=datetime(2026, 9, 9, tzinfo=timezone.utc),
        )
    with pytest.raises(LedgerError, match="ENTRY_SOURCE_UNVERIFIED"):
        build_issued_forecast(
            {**FORECAST, "entry_source": "BLOG"},
            now=NOW,
        )
    with pytest.raises(LedgerError, match="HORIZON_DUE_MISMATCH"):
        build_issued_forecast(
            {**FORECAST, "horizon_days": 30},
            now=NOW,
        )


def test_declared_source_hash_must_match_retained_exact_bytes():
    without_bytes = dict(FORECAST)
    without_bytes.pop("entry_source_snapshot")
    with pytest.raises(LedgerError, match="ENTRY_SOURCE_SNAPSHOT_REQUIRED"):
        build_issued_forecast(without_bytes, now=NOW)

    with pytest.raises(LedgerError, match="ENTRY_SOURCE_SNAPSHOT_HASH_MISMATCH"):
        build_issued_forecast(
            {**FORECAST, "entry_source_snapshot": b"different NSE bytes"},
            now=NOW,
        )
