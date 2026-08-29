"""Comprehensive pre-merge dry-run smoke test for Genesis System3."""

import asyncio
import importlib
import json
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


async def run_smoke_tests():
    print("=== GENESIS SYSTEM3 PRE-MERGE DRY-RUN SMOKE TEST ===")
    results = {"total": 0, "passed": 0, "failed": 0, "failures": []}

    async def test(name, fn_or_coro):
        results["total"] += 1
        try:
            if asyncio.iscoroutinefunction(fn_or_coro):
                await fn_or_coro()
            elif callable(fn_or_coro):
                fn_or_coro()
            results["passed"] += 1
            print(f"  [PASS] {name}")
        except Exception as e:
            results["failed"] += 1
            err_msg = f"{type(e).__name__}: {str(e)}"
            results["failures"].append({"name": name, "error": err_msg, "traceback": traceback.format_exc()})
            print(f"  [FAIL] {name} -> {err_msg}")

    # --- 1. Import & Syntax Tests ---
    print("\n--- 1. Module Import Integrity ---")
    modules_to_test = [
        "dashboard.backend.app",
        "dashboard.backend.chain_adapter",
        "dashboard.backend.portfolio_truth_service",
        "dashboard.backend.multibagger_service",
        "dashboard.backend.ml_intelligence_service",
        "dashboard.backend.backtest_service",
        "dashboard.backend.catalyst_service",
        "core.cloud_storage",
    ]
    for mod_name in modules_to_test:
        await test(f"Import {mod_name}", lambda m=mod_name: importlib.import_module(m))

    # --- 2. FastAPI Route Handlers Direct Tests ---
    print("\n--- 2. FastAPI Route Handlers Execution ---")
    from dashboard.backend.app import (
        get_backtest_results_endpoint,
        get_backtest_strategies_endpoint,
        get_catalysts_endpoint,
        get_deploy_info,
        get_health,
        get_ml_features_endpoint,
        get_multibagger_workspace_endpoint,
        get_news_endpoint,
        get_option_chain_alias,
        get_options_intelligence_endpoint,
        get_paper_account,
        get_paper_positions,
        get_paper_status,
        get_paper_trades,
        get_positions,
        runbook_audit_endpoint,
    )

    async def test_routes():
        h = await get_health()
        assert isinstance(h, dict) and "status" in h, "get_health failed"

        d = await get_deploy_info()
        assert isinstance(d, dict) and "service_name" in d, "get_deploy_info failed"

        p = await get_positions()
        assert isinstance(p, dict) and "positions" in p, "get_positions failed"

        c = await get_option_chain_alias("NIFTY")
        assert isinstance(c, dict) and "underlying" in c, "get_option_chain_alias failed"

        oi = await get_options_intelligence_endpoint("BANKNIFTY")
        assert isinstance(oi, dict) and "underlying" in oi, "get_options_intelligence_endpoint failed"

        pp = await get_paper_positions()
        assert isinstance(pp, dict) and "positions" in pp, "get_paper_positions failed"

        pt = await get_paper_trades()
        assert isinstance(pt, dict) and "trades" in pt, "get_paper_trades failed"

        pa = await get_paper_account()
        assert isinstance(pa, dict) and "initial_capital" in pa, "get_paper_account failed"

        ps = await get_paper_status()
        assert isinstance(ps, dict) and "status" in ps, "get_paper_status failed"

        mb = await get_multibagger_workspace_endpoint()
        assert isinstance(mb, dict) and "candidates" in mb, "get_multibagger_workspace_endpoint failed"

        bt = await get_backtest_results_endpoint()
        assert isinstance(bt, dict) and "summary" in bt, "get_backtest_results_endpoint failed"

        bts = await get_backtest_strategies_endpoint()
        assert isinstance(bts, dict) and "strategies" in bts, "get_backtest_strategies_endpoint failed"

        cat = await get_catalysts_endpoint()
        assert isinstance(cat, dict) and "catalysts" in cat, "get_catalysts_endpoint failed"

        news = await get_news_endpoint()
        assert isinstance(news, dict) and "catalysts" in news, "get_news_endpoint failed"

        ml = await get_ml_features_endpoint()
        assert isinstance(ml, dict) and "pipeline" in ml, "get_ml_features_endpoint failed"

        rb = await runbook_audit_endpoint()
        assert isinstance(rb, dict) and "overall_verdict" in rb, "runbook_audit_endpoint failed"

    await test("All 16 Async Route Handlers", test_routes)

    # --- 3. Domain Logic & Calculations ---
    print("\n--- 3. Core Business Logic & Contract Mathematics ---")
    from dashboard.backend.chain_adapter import (
        _calculate_max_pain,
        _classify_buildup,
    )

    def test_calc():
        assert _classify_buildup(15.0, 1000) == "Long Buildup"
        assert _classify_buildup(-15.0, 1000) == "Short Buildup"
        assert _classify_buildup(15.0, -1000) == "Short Covering"
        assert _classify_buildup(-15.0, -1000) == "Long Unwinding"

        mp = _calculate_max_pain([24000, 24100, 24200], {24000: 100, 24100: 50, 24200: 10}, {24000: 10, 24100: 50, 24200: 100})
        assert mp == 24100, f"Max pain calculation mismatch: {mp}"

    await test("Buildup & Max Pain Algorithms", test_calc)

    # --- Summary ---
    print("\n=== SMOKE TEST SUMMARY ===")
    print(f"Total Tests : {results['total']}")
    print(f"Passed      : {results['passed']}")
    print(f"Failed      : {results['failed']}")

    if results["failed"] > 0:
        print("\n--- FAILURES DETAIL ---")
        for f in results["failures"]:
            print(f"\n[FAILED]: {f['name']}")
            print(f['traceback'])
        sys.exit(1)
    else:
        print("\nALL PRE-MERGE DRY-RUN SMOKE TESTS PASSED 100%!")


if __name__ == "__main__":
    asyncio.run(run_smoke_tests())
