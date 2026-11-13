"""Fail-closed position source provenance and no fabricated mark/freshness."""
from __future__ import annotations

import ast
import asyncio
import copy
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_endpoint(tmp_path: Path, *, state=None, remote=False):
    source = (ROOT / "dashboard/backend/app.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    node = next(
        item for item in tree.body
        if isinstance(item, ast.AsyncFunctionDef) and item.name == "get_positions"
    )
    node = copy.deepcopy(node)
    node.decorator_list = []
    class Store:
        _remote_backend = object() if remote else None
        def get_state(self):
            return state or {}

    scope = {
        "datetime": datetime,
        "timezone": timezone,
        "json": json,
        "OUTPUTS_DIR": tmp_path,
        "SSOT_AVAILABLE": state is not None,
        "state_store": Store(),
        "filter_paper_trade_rows": lambda rows: rows,
    }
    code = compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])), "<position-route>", "exec")
    exec(code, scope)
    return lambda: asyncio.run(scope["get_positions"]())


def test_no_local_file_is_not_verified_flat_or_firestore(tmp_path):
    out = load_endpoint(tmp_path)()
    assert out["positions"] == []
    assert out["source"] == "runtime_ephemeral:outputs/positions_live.json"
    assert out["verification_status"] == "NO_POSITION_SOURCE"
    assert out["freshness_seconds"] is None
    assert out["durable"] is False
    assert "NOT VERIFIED" in out["reason_if_unverified"]


def test_local_file_never_claims_verified_freshness_or_invents_mark(tmp_path):
    (tmp_path / "positions_live.json").write_text(json.dumps({
        "timestamp": "2026-11-12T05:00:00Z",
        "positions": [{"position_id": "POS_FOO", "entry_price": 8.65, "qty": 20}],
    }), encoding="utf-8")
    out = load_endpoint(tmp_path)()
    assert out["source"].startswith("runtime_ephemeral:")
    assert out["verification_status"] == "SIMULATED_UNVERIFIED"
    assert out["freshness_seconds"] is None
    assert out["source_timestamp"] == "2026-11-12T05:00:00Z"
    assert out["positions"][0]["current_price"] is None
    assert out["positions"][0]["unrealized_pnl"] is None


def test_revision_memory_state_cannot_masquerade_as_firestore(tmp_path):
    out = load_endpoint(
        tmp_path,
        state={"positions": [{"position_id": "SIM_123"}],
               "timestamp_utc": "2026-11-13T08:30:00Z"},
        remote=False,
    )()
    assert out["source"] == "runtime_memory:revision_local"
    assert out["durable"] is False
    assert out["verification_status"] == "SIMULATED_SOURCE_REPORTED"


def test_firestore_state_reports_real_backend_but_not_trading_proof(tmp_path):
    out = load_endpoint(
        tmp_path, state={"positions": [{"position_id": "SIM_123"}]}, remote=True
    )()
    assert out["source"] == "firestore:system3_runtime/state"
    assert out["durable"] is True
    assert out["verification_status"] == "SIMULATED_SOURCE_REPORTED"
    assert out["freshness_seconds"] is None


def test_empty_firestore_state_does_not_claim_verified_zero_positions(tmp_path):
    out = load_endpoint(tmp_path, state={"positions": []}, remote=True)()
    assert out["verification_status"] == "NO_POSITION_SOURCE"
    assert out["durable"] is False
