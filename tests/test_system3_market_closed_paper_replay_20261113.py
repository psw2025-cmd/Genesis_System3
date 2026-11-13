"""Mock replay is isolated and must never certify live trading or ML."""
import pytest

from scripts.system3_market_closed_paper_replay import run_mock_replay


@pytest.mark.parametrize("count", [3, 10, 219])
def test_exchange_closed_paper_ledger_replay(count):
    proof = run_mock_replay(symbol_count=count)
    assert proof["status"] == "MOCK_REPLAY_PASS"
    assert proof["mock_instrument_count"] == count
    assert proof["mock_positions_opened_and_closed"] == 3
    assert proof["ledger_hash_chain_verified"] is True
    assert proof["restart_reconciliation"] == "PASS"
    assert proof["idempotency_guards_pass"] is True
    assert proof["real_broker_order_calls"] == 0
    assert proof["firestore_writes"] == 0
    assert proof["secret_reads"] == 0
    assert proof["production_state_mutated"] is False
    assert proof["production_readiness"] == "NOT_PROVEN"
    assert proof["is_synthetic"] is True
    assert all(x == "NOT_VERIFIED" for x in proof["synthetic_outcomes"])
    assert proof["model_promoted"] is False


@pytest.mark.parametrize("bad_count", [-1, 2, 1001])
def test_mock_universe_size_guard(bad_count):
    with pytest.raises(ValueError):
        run_mock_replay(symbol_count=bad_count)
