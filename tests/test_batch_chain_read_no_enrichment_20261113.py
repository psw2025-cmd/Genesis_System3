"""The batch-chain GET must never perform market baseline enrichment or writes."""
from __future__ import annotations

import ast
import copy
import json
import sys
import time
import types
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def get_resolver(tmp_path, normalizer):
    source = (ROOT / "dashboard/backend/app.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                and n.name == "_resolve_batch_chain_entry")
    node = copy.deepcopy(node)
    scope = {
        "ROOT_DIR": tmp_path,
        "json": json,
        "Dict": dict,
        "Any": object,
        "_chain_from_push_cache": lambda sym: None,
        "_usable_chain_snapshot": lambda data: (
            isinstance(data, dict)
            and bool(data.get("contracts"))
            and float(data.get("spot") or 0) > 0
        ),
        "_cache_get": lambda *args: None,
        "_TTL_CHAIN": 8,
        "_store_index_chain_snapshot": lambda *args: (_ for _ in ()).throw(
            AssertionError("READ endpoint must not enrich/persist")
        ),
        "_warming_chain_placeholder": lambda sym: {
            "underlying": sym, "contracts": [], "spot": 0,
            "status": "CHAIN_CACHE_WARMING", "live": False,
        },
    }
    fake = types.ModuleType("dashboard.backend.chain_adapter")
    fake.normalize_index_chain_exchange = normalizer
    exec(compile(ast.fix_missing_locations(
        ast.Module(body=[node], type_ignores=[])
    ), "<batch-resolver>", "exec"), scope)
    return scope["_resolve_batch_chain_entry"], fake


def seed(tmp_path, sym, source):
    dir = tmp_path / "state" / "chain_cache"
    dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "data_source": source,
        "spot": 25000.0,
        "contracts": [{"strike": 25000, "option_type": "CE"}],
        "fetched_at_utc": "2026-11-12T09:35:00Z",
        "status": "MARKET_CLOSED_DHAN_SNAPSHOT",
    }
    (dir / (sym + ".json")).write_text(json.dumps(payload), encoding="utf-8")


def normalize(snap, sym):
    return dict(snap, underlying=sym, verification_status=(
        "DHAN_EOD_SNAPSHOT" if snap.get("data_source") == "dhan"
        else "NOT_VERIFIED"
    ))


def test_saved_dhan_snapshot_returns_immediately_with_original_timestamp(tmp_path):
    seed(tmp_path, "NIFTY", "dhan")
    fn, fake = get_resolver(tmp_path, normalize)
    with patch.dict(sys.modules, {"dashboard.backend.chain_adapter": fake}):
        started = time.monotonic()
        data = fn("NIFTY")
        elapsed = time.monotonic() - started
    assert elapsed < 0.25, elapsed
    assert data["status"] == "MARKET_CLOSED_DHAN_SNAPSHOT"
    assert data["verification_status"] == "DHAN_EOD_SNAPSHOT"
    assert data["fetched_at_utc"] == "2026-11-12T09:35:00Z"
    assert data["live"] is False
    assert data["stale"] is True


def test_unknown_source_never_upgraded_to_dhan(tmp_path):
    seed(tmp_path, "BANKNIFTY", "csv_mock")
    fn, fake = get_resolver(tmp_path, normalize)
    with patch.dict(sys.modules, {"dashboard.backend.chain_adapter": fake}):
        out = fn("BANKNIFTY")
    assert out["status"] == "CHAIN_CACHE_WARMING"
    assert not out["contracts"]


def test_missing_file_returns_warming_without_network_or_write(tmp_path):
    fn, fake = get_resolver(tmp_path, normalize)
    with patch.dict(sys.modules, {"dashboard.backend.chain_adapter": fake}):
        out = fn("BANKEX")
    assert out["status"] == "CHAIN_CACHE_WARMING"


def test_source_code_does_not_call_enrichment_from_batch_resolver():
    tree = ast.parse((ROOT / "dashboard/backend/app.py").read_text(encoding="utf-8"))
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
              and n.name == "_resolve_batch_chain_entry")
    called = [ast.unparse(x.func) for x in ast.walk(fn) if isinstance(x, ast.Call)]
    assert "_store_index_chain_snapshot" not in called
    assert "_get_chain_uncached" not in called
