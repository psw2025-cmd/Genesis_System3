from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "dashboard" / "backend" / "app.py"


def _runtime_qc_block() -> str:
    text = APP.read_text(encoding="utf-8")
    start = text.index('@app.get("/api/qc/runtime")')
    end = text.index('@app.get("/api/underlyings")', start)
    return text[start:end]


def test_runtime_qc_must_not_create_an_independent_live_dhan_chain_path():
    """BR-2: QC is an observer; it must never multiply live Dhan chain demand."""
    block = _runtime_qc_block()

    forbidden = (
        "DataSourceManager",
        "fetch_chain_for_api",
        "_run_blocking",
    )
    for token in forbidden:
        assert token not in block, (
            f"/api/qc/runtime contains direct live-chain token {token!r}; "
            "runtime QC must observe canonical push/TTL snapshots only"
        )


def test_runtime_qc_must_reuse_canonical_chain_snapshot_and_ttl_cache():
    """The QC path must consume the same last-good authority as UI chain reads."""
    block = _runtime_qc_block()

    assert "_chain_from_push_cache" in block, (
        "/api/qc/runtime must consult the canonical pushed/micro-loop chain snapshot"
    )
    assert "_cache_get" in block and "chain_" in block, (
        "/api/qc/runtime must fall back to the canonical local chain TTL cache, "
        "not a new broker fetch"
    )


def test_runtime_qc_missing_cache_remains_fail_closed_not_trade_ready():
    """No cached rows must remain explicit NO_DATA/WARMING, never fabricated PASS."""
    block = _runtime_qc_block()

    assert '"contracts": []' in block
    assert '"total_contracts": 0' in block
    assert "overall_passed" in block
    assert '"live_trading_enabled": False' in block
    assert '"order_placement_allowed": False' in block
