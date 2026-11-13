"""Prove expensive background chain enrichment never blocks the ASGI event loop."""
from __future__ import annotations

import ast
import asyncio
import copy
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "dashboard/backend/app.py"


def load_background_function(name, scope):
    tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
    node = next(
        n for n in tree.body
        if isinstance(n, ast.AsyncFunctionDef) and n.name == name
    )
    node = copy.deepcopy(node)
    node.decorator_list = []
    exec(compile(ast.fix_missing_locations(
        ast.Module(body=[node], type_ignores=[])
    ), "<background-loop>", "exec"), scope)
    return scope[name]


async def bounded(fn, *args, timeout=2.0):
    return await asyncio.wait_for(asyncio.to_thread(fn, *args), timeout=timeout)


def test_broker_snapshot_enrichment_cannot_starve_asgi_loop():
    def blocking_market_detection():
        time.sleep(0.10)
        return False

    def blocking_snapshot(symbol, data, open_now):
        time.sleep(0.10)
        return dict(data, saved=True)

    async def fake_chain(symbol, closed_timeout_s=None):
        return {"spot": 100.0, "contracts": [{"ce": 1}], "status": "EOD"}

    scope = {
        "asyncio": asyncio,
        "_run_blocking": bounded,
        "_market_open_from_state": blocking_market_detection,
        "_get_chain_uncached": fake_chain,
        "_csv_or_fallback_chain": lambda x: False,
        "_store_index_chain_snapshot": blocking_snapshot,
    }
    fn = load_background_function("_warm_one_index_chain", scope)

    async def probe():
        task = asyncio.create_task(fn("NIFTY"))
        start = time.monotonic()
        await asyncio.sleep(0.025)
        pulse_elapsed = time.monotonic() - start
        result = await task
        return pulse_elapsed, result

    elapsed, result = asyncio.run(probe())
    assert elapsed < 0.08, elapsed
    assert result["saved"] is True


def test_blocked_market_detection_fails_closed_instead_of_hanging():
    def slow():
        time.sleep(0.08)
        return True

    async def quick_bounded(fn, *args, timeout=2.0):
        return await asyncio.wait_for(asyncio.to_thread(fn, *args), timeout=0.01)

    async def empty(symbol, closed_timeout_s=None):
        return {"spot": 0, "contracts": [], "status": "NO_DHAN_DATA"}

    scope = {
        "asyncio": asyncio,
        "_run_blocking": quick_bounded,
        "_market_open_from_state": slow,
        "_get_chain_uncached": empty,
    }
    fn = load_background_function("_warm_one_index_chain", scope)
    assert asyncio.run(fn("NIFTY")) is None


def test_equity_selector_and_market_detection_run_in_bounded_workers():
    tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
    fn = next(n for n in tree.body
              if isinstance(n, ast.AsyncFunctionDef)
              and n.name == "index_chain_micro_loop")
    calls = [
        ast.unparse(n)
        for n in ast.walk(fn)
        if isinstance(n, ast.Await)
    ]
    joined = " | ".join(calls)
    assert "await _run_blocking(_next_equity_gainer_symbol, timeout=3.0)" in joined
    assert "await _run_blocking(_market_open_from_state, timeout=2.0)" in joined


def test_chain_background_loops_have_no_order_placement_calls():
    tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
    for name in ("_warm_one_index_chain", "index_chain_micro_loop"):
        fn = next(n for n in tree.body
                  if isinstance(n, ast.AsyncFunctionDef) and n.name == name)
        symbols = " ".join(
            ast.unparse(n.func) for n in ast.walk(fn)
            if isinstance(n, (ast.Call, ast.Await)) and isinstance(n, ast.Call)
        ).lower()
        assert "place_order" not in symbols
        assert "placeorder" not in symbols
        assert "execute_trade" not in symbols
