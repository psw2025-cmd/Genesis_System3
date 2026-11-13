"""Cloud scheduler receipts and paper ledger provenance must be independent."""
from __future__ import annotations
import ast
from pathlib import Path

import pytest

from dashboard.backend.scheduler_evidence_policy import scheduler_evidence_backend

ROOT = Path(__file__).resolve().parents[1]


def test_scheduler_evidence_default_is_local():
    assert scheduler_evidence_backend({}) == "file"


def test_firestore_scheduler_evidence_does_not_enable_firestore_state_writes():
    env = {
        "SYSTEM3_STATE_BACKEND": "file",
        "SYSTEM3_SCHEDULER_EVIDENCE_BACKEND": "firestore",
    }
    assert scheduler_evidence_backend(env) == "firestore"
    assert env["SYSTEM3_STATE_BACKEND"] == "file"


def test_legacy_firestore_runtime_inherits_evidence_mode():
    assert scheduler_evidence_backend({"SYSTEM3_STATE_BACKEND": "firestore"}) == "firestore"


def test_explicit_scheduler_file_mode_overrides_remote_runtime():
    assert scheduler_evidence_backend({
        "SYSTEM3_STATE_BACKEND": "firestore",
        "SYSTEM3_SCHEDULER_EVIDENCE_BACKEND": "file",
    }) == "file"


def test_invalid_scheduler_backend_fails_closed():
    with pytest.raises(ValueError, match="UNSUPPORTED_SCHEDULER_EVIDENCE_BACKEND"):
        scheduler_evidence_backend({
            "SYSTEM3_SCHEDULER_EVIDENCE_BACKEND": "synthetic",
        })


def test_position_endpoint_does_not_lie_about_fire_store_or_market_close():
    source = (ROOT / "dashboard/backend/app.py").read_text(encoding="utf-8")
    start = source.index('@app.get("/api/positions")')
    stop = source.index('@app.get("/api/pnl")', start)
    route = source[start:stop]
    assert '"source": state_source' in route
    assert 'local_instance_runtime_state' in route
    assert 'CLOUD_BACKED_PAPER_SIMULATION_NOT_BROKER_FILL_PROOF' in route
    assert 'LOCAL_INSTANCE_SIMULATION_NOT_DURABLE' in route
    assert '"source": "firestore:system3_paper_positions"' not in route
    assert 'Market closed — zero active paper positions' not in route


def test_firestore_scheduler_route_is_separate_from_remote_state_writes():
    source = (ROOT / "dashboard/backend/app.py").read_text(encoding="utf-8")
    ast.parse(source)
    assert "scheduler_evidence_backend()" in source
    assert '"runtime_state_backend_unchanged"' in source
    assert '"firestore:system3_scheduler_evidence/current"' in source
