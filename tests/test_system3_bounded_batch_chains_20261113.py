"""Regression: no synchronous snapshot I/O can stall read-only chain endpoints."""
from __future__ import annotations

import ast
import asyncio
import copy
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]


def _load_chain_endpoint(resolver, timeout=0.08, cache=None):
    tree = ast.parse((ROOT / "dashboard/backend/app.py").read_text(encoding="utf-8"))
    fn = next(x for x in tree.body
              if isinstance(x, ast.AsyncFunctionDef) and x.name == "batch_chains")
    node = copy.deepcopy(fn)
    node.decorator_list = []
    pool = ThreadPoolExecutor(max_workers=3)
    cache = {} if cache is None else cache
    scope = {
        "Dict": Dict, "Any": Any,
        "asyncio": asyncio, "datetime": datetime, "IST": timezone.utc,
        "_INDEX_STREAM_SYMBOLS": ("NIFTY", "BANKNIFTY", "FINNIFTY"),
        "_REQUIRED_CHAIN_SYMBOLS": ("NIFTY", "BANKNIFTY", "FINNIFTY"),
        "_BATCH_CHAIN_SNAPSHOT_EXECUTOR": pool,
        "_BATCH_CHAIN_RESOLVE_TIMEOUT_S": timeout,
        "_TTL_BATCH": 8,
        "_resolve_batch_chain_entry": resolver,
        "_cache_get": lambda key, ttl: cache.get(key),
        "_cache_set": lambda key, val: cache.setdefault(key, val),
        "_warming_chain_placeholder": lambda sym: {
            "underlying": sym, "contracts": [], "spot": 0,
            "status": "CHAIN_CACHE_WARMING", "live": False,
        },
        "_required_chain_symbols_ready": lambda chains: all(
            chains[x].get("status") == "VERIFIED_SNAPSHOT"
            for x in ("NIFTY", "BANKNIFTY", "FINNIFTY")
        ),
    }
    code = compile(
        ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])),
        "<chain-route>", "exec"
    )
    exec(code, scope)
    return scope["batch_chains"], pool, cache


def test_hanging_snapshot_reader_returns_bounded_pending_payload():
    def slow(sym):
        time.sleep(0.30)
        return {"status": "VERIFIED_SNAPSHOT", "spot": 100, "contracts": [1]}
    fn, pool, cache = _load_chain_endpoint(slow, timeout=0.04)
    try:
        start = time.monotonic()
        out = asyncio.run(fn())
        elapsed = time.monotonic() - start
        assert elapsed < 0.20, elapsed
        assert out["required_symbols_ready"] is False
        assert len(out["chains"]) == 3
        assert all(x["status"] == "CHAIN_SNAPSHOT_READ_TIMEOUT"
                   for x in out["chains"].values())
        assert all(x["live"] is False for x in out["chains"].values())
        assert not cache
    finally:
        pool.shutdown(wait=True, cancel_futures=True)


def test_fast_verified_snapshots_are_returned_and_cached():
    def fast(sym):
        return {
            "status": "VERIFIED_SNAPSHOT", "underlying": sym,
            "spot": 100, "contracts": [{"type": "CE"}], "live": False,
        }
    fn, pool, cache = _load_chain_endpoint(fast)
    try:
        out = asyncio.run(fn())
        assert out["required_symbols_ready"] is True
        assert all(x["status"] == "VERIFIED_SNAPSHOT" for x in out["chains"].values())
        assert cache["batch_chains_v1"]["required_symbols_ready"] is True
    finally:
        pool.shutdown(wait=True, cancel_futures=True)


def test_single_snapshot_error_does_not_block_other_symbols():
    def mixed(sym):
        if sym == "BANKNIFTY":
            raise OSError("confidential local path should not be logged")
        return {"status": "VERIFIED_SNAPSHOT", "spot": 100, "contracts": [1]}
    fn, pool, cache = _load_chain_endpoint(mixed)
    try:
        out = asyncio.run(fn())
        assert out["required_symbols_ready"] is False
        assert out["chains"]["BANKNIFTY"]["status"] == "CHAIN_SNAPSHOT_READ_ERROR"
        assert out["chains"]["BANKNIFTY"]["pending_reason"] == "OSError"
        assert out["chains"]["NIFTY"]["status"] == "VERIFIED_SNAPSHOT"
        assert not cache
    finally:
        pool.shutdown(wait=True, cancel_futures=True)
