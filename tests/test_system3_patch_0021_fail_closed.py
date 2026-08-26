"""Fail-closed proofs for System3 consolidated patch 0021.

Reconstructs Claude's T9/T11/T12/R2-R3/T14 gift on current main. The original
0021 file never reached GitHub or Gmail as bytes; these tests pin the same
live-observed lies so they cannot return.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


LIVE_AUTO_REFRESH = {
    "success": False,
    "skipped": "AUTO_REFRESH_DISABLED_OR_LIVE_GATE",
    "attempted": False,
    "message": "Token generated via PIN + TOTP (fully automated)",
    "strategy": "generate_token",
    "token_value_printed": False,
    "cooldown_remaining_s": 13,
    "reason": "TOKEN_EXPIRED_OR_INVALID",
    "cooldown_s": 3600,
}

LIVE_CANONICAL_ROTATION = {
    "operation_started": True,
    "success": False,
    "skipped": "CANONICAL_SELF_HEAL_DISABLED",
    "order_placement_allowed": False,
    "error_type": "HTTPError",
    "attempted": False,
    "message": (
        "403 Client Error: Forbidden for url: https://run.googleapis.com/v2/projects/"
        "system3-openalgo-safe/locations/asia-south1/operations/65a2c16c-19d4-42c0-b7b3-45f5b"
    ),
    "authority": "gcp-cloud-run-job",
    "job": "genesis-system3-dhan-token-rotate",
    "live_trading_enabled": False,
    "cooldown_remaining_s": 254,
    "raw_token_exposed": False,
    "reason": "get_status_auth_failure",
}


# ── T9: profit/expectancy gate must refuse the bundled fixture ───────────────


def test_t9_fixture_is_not_a_default_trade_source():
    proof = _load_module(
        "system3_friction_expectancy_proof_0021",
        ROOT / "scripts" / "system3_friction_expectancy_proof.py",
    )
    sources = [str(p) for p in proof.REAL_TRADE_SOURCES]
    joined = " ".join(sources)
    assert "paper_closed_trades_feb2026" not in joined
    assert "tests/fixtures" not in joined.replace("\\", "/")
    assert any("storage/live" in s.replace("\\", "/") for s in sources)


def test_t9_load_trades_never_returns_fixture_by_default(monkeypatch):
    proof = _load_module(
        "system3_friction_expectancy_proof_0021_load",
        ROOT / "scripts" / "system3_friction_expectancy_proof.py",
    )
    monkeypatch.delenv("SYSTEM3_ALLOW_FIXTURE_TRADES", raising=False)
    monkeypatch.setattr(proof, "_fetch_cloud_trades", lambda: [])
    monkeypatch.setattr(proof, "REAL_TRADE_SOURCES", [])
    trades, source, is_fixture = proof._load_trades()
    assert trades == []
    assert is_fixture is False
    assert "feb2026" not in source


def test_t9_build_report_never_passes_on_fixture(monkeypatch):
    proof = _load_module(
        "system3_friction_expectancy_proof_0021_report",
        ROOT / "scripts" / "system3_friction_expectancy_proof.py",
    )
    fake_trades = [
        {
            "underlying": "NIFTY",
            "entry_price": 100,
            "exit_price": 120,
            "qty": 50,
            "realized_pnl": 1000,
        }
        for _ in range(9)
    ]
    monkeypatch.setattr(proof, "_load_trades", lambda: (fake_trades, "tests/fixtures/paper_closed_trades_feb2026.json", True))
    report = proof.build_report()
    assert report["is_fixture"] is True
    assert report["pass"] is False
    assert report["blocker_if_fixture"] == "INSUFFICIENT_REAL_TRADES"


def test_t9_gate_evaluator_refuses_fixture_even_if_pass_true(tmp_path):
    gate = _load_module(
        "system3_gate_evaluator_0021_fix",
        ROOT / "scripts" / "system3_gate_evaluator.py",
    )

    summary = tmp_path / "reports" / "latest" / "friction_expectancy"
    summary.mkdir(parents=True)
    (summary / "summary.json").write_text(
        json.dumps(
            {
                "pass": True,
                "is_fixture": True,
                "source": "tests/fixtures/paper_closed_trades_feb2026.json",
                "evidence": {
                    "net_expectancy_after_costs": 12.5,
                    "win_rate": 0.66,
                    "trade_count": 9,
                },
            }
        ),
        encoding="utf-8",
    )
    out = gate.eval_expectancy_gate(tmp_path)
    assert out["pass"] is False
    assert out["is_fixture"] is True
    assert out["blocker_id"] == "INSUFFICIENT_REAL_TRADES"


def test_t9_gate_evaluator_refuses_fixture_path_even_without_flag(tmp_path):
    gate = _load_module(
        "system3_gate_evaluator_0021_path",
        ROOT / "scripts" / "system3_gate_evaluator.py",
    )

    summary = tmp_path / "reports" / "latest" / "friction_expectancy"
    summary.mkdir(parents=True)
    (summary / "summary.json").write_text(
        json.dumps(
            {
                "pass": True,
                "source": "tests/fixtures/paper_closed_trades_feb2026.json",
                "evidence": {
                    "net_expectancy_after_costs": 12.5,
                    "trade_count": 9,
                },
            }
        ),
        encoding="utf-8",
    )
    out = gate.eval_expectancy_gate(tmp_path)
    assert out["pass"] is False
    assert out["is_fixture"] is True


def test_t9_gate_evaluator_passes_only_real_positive_expectancy(tmp_path):
    gate = _load_module(
        "system3_gate_evaluator_0021_pass",
        ROOT / "scripts" / "system3_gate_evaluator.py",
    )

    summary = tmp_path / "reports" / "latest" / "friction_expectancy"
    summary.mkdir(parents=True)
    (summary / "summary.json").write_text(
        json.dumps(
            {
                "pass": True,
                "is_fixture": False,
                "source": "storage/live/paper_closed_trades.json",
                "evidence": {
                    "net_expectancy_after_costs": 8.1,
                    "trade_count": 12,
                    "win_rate": 0.58,
                },
            }
        ),
        encoding="utf-8",
    )
    out = gate.eval_expectancy_gate(tmp_path)
    assert out["pass"] is True
    assert out["blocker_id"] is None
    assert out["is_fixture"] is False


# ── T11: live /api/state success-sounding copy while skipped ───────────────


def test_t11_sanitizer_strips_live_auto_refresh_lie():
    from core.brokers.dhan.dhan_readonly import sanitize_attempt_block

    out = sanitize_attempt_block(LIVE_AUTO_REFRESH)
    assert out["attempted"] is False
    assert out["success"] is False
    assert out["skipped"] == "AUTO_REFRESH_DISABLED_OR_LIVE_GATE"
    msg = str(out.get("message") or "").lower()
    assert "fully automated" not in msg
    assert "token generated" not in msg
    assert "pin + totp" not in msg
    assert "refresh not run" in msg
    assert out["strategy"] == "not_attempted"


def test_t11_sanitizer_strips_live_stale_403_while_skipped():
    from core.brokers.dhan.dhan_readonly import sanitize_attempt_block

    out = sanitize_attempt_block(LIVE_CANONICAL_ROTATION)
    assert out["attempted"] is False
    assert out["success"] is False
    assert out["skipped"] == "CANONICAL_SELF_HEAL_DISABLED"
    msg = str(out.get("message") or "")
    assert "403" not in msg
    assert "Forbidden" not in msg
    assert "Refresh not run (CANONICAL_SELF_HEAL_DISABLED)" == msg
    assert out.get("operation_started") is False
    assert "error_type" not in out or out.get("error_type") is None


def test_t11_status_payload_sanitizes_both_blocks():
    from core.brokers.dhan.dhan_readonly import sanitize_status_payload

    live = {
        "connected": True,
        "auto_refresh": dict(LIVE_AUTO_REFRESH),
        "canonical_rotation": dict(LIVE_CANONICAL_ROTATION),
        "live_trading_enabled": False,
    }
    out = sanitize_status_payload(live)
    blob = json.dumps(out).lower()
    assert "fully automated" not in blob
    assert "token generated" not in blob
    assert "403 client error" not in blob
    assert out["connected"] is True
    assert out["live_trading_enabled"] is False


def test_t11_sanitizer_keeps_true_success_copy():
    from core.brokers.dhan.dhan_readonly import sanitize_attempt_block

    out = sanitize_attempt_block(
        {
            "attempted": True,
            "success": True,
            "message": "Token generated via PIN + TOTP (fully automated)",
            "strategy": "generate_token",
        }
    )
    assert out["success"] is True
    assert "fully automated" in str(out["message"]).lower()


def test_t11_sanitizer_handles_none_and_non_dict():
    from core.brokers.dhan.dhan_readonly import sanitize_attempt_block

    assert sanitize_attempt_block(None) == {"attempted": False, "success": False}
    assert sanitize_attempt_block("nope") == {"attempted": False, "success": False}


def test_t11_runtime_state_store_source_sanitizes_broker_status():
    src = (ROOT / "dashboard" / "backend" / "runtime_state_store.py").read_text(encoding="utf-8")
    assert "sanitize_status_payload" in src
    assert "return sanitize_status_payload(_dhan_status())" in src


def test_t11_cloud_runtime_patch_sanitizes_wrap_output():
    src = (ROOT / "core" / "brokers" / "dhan" / "cloud_runtime_patch.py").read_text(encoding="utf-8")
    wrap = src.split("def _wrap_read", 1)[1].split("def install()", 1)[0]
    assert "sanitize_attempt_block" in wrap
    assert 'result["canonical_rotation"]' in wrap
    assert "auto_refresh" in wrap


def test_t11_live_proof_snapshot_still_documents_the_lie():
    """Before-proof: the captured live payload really had the contradictory copy."""
    snap = ROOT / "reports" / "latest" / "live_proof_center" / "LATEST" / "api" / "state.json"
    if not snap.exists():
        pytest.skip("live proof snapshot not present in this checkout")
    data = json.loads(snap.read_text(encoding="utf-8"))
    payload = data.get("data") if isinstance(data.get("data"), dict) else data
    broker = payload.get("broker") or {}
    auto = broker.get("auto_refresh") or {}
    assert auto.get("attempted") is False
    assert auto.get("success") is False
    assert "fully automated" in str(auto.get("message") or "").lower()


# ── T12: prediction analytics must not be a hardcoded PASS ───────────────


def test_t12_proof_pack_does_not_hardcode_prediction_pass():
    src = (ROOT / "scripts" / "generate_proof_pack.py").read_text(encoding="utf-8")
    assert '"6_prediction_analytics": "PASS"' not in src
    assert "_prediction_analytics_status()" in src


def test_t12_prediction_status_fails_on_no_prediction_found():
    pack = _load_module("generate_proof_pack_0021", ROOT / "scripts" / "generate_proof_pack.py")
    status = pack._prediction_analytics_status()
    assert status == "FAIL"


def test_t12_prediction_status_fails_on_zero_proof_pass_count(tmp_path, monkeypatch):
    pack = _load_module("generate_proof_pack_0021_zero", ROOT / "scripts" / "generate_proof_pack.py")
    monkeypatch.setattr(pack, "ROOT", tmp_path)
    report_dir = tmp_path / "reports" / "latest"
    report_dir.mkdir(parents=True)
    (report_dir / "model_accuracy_report.json").write_text(
        json.dumps({"proof_pass_count": 0, "rows": [{"symbol": "NIFTY"}], "blocker": "NO_PREDICTION_SOURCE_FOUND"}),
        encoding="utf-8",
    )
    assert pack._prediction_analytics_status() == "FAIL"


def test_t12_prediction_status_passes_only_with_real_rows(tmp_path, monkeypatch):
    pack = _load_module("generate_proof_pack_0021_ok", ROOT / "scripts" / "generate_proof_pack.py")
    monkeypatch.setattr(pack, "ROOT", tmp_path)
    report_dir = tmp_path / "reports" / "latest"
    report_dir.mkdir(parents=True)
    (report_dir / "model_accuracy_report.json").write_text(
        json.dumps(
            {
                "proof_pass_count": 3,
                "rows": [{"symbol": "NIFTY"}, {"symbol": "BANKNIFTY"}],
                "blocker": "",
            }
        ),
        encoding="utf-8",
    )
    assert pack._prediction_analytics_status() == "PASS"


def test_t12_model_accuracy_report_is_still_unproven():
    md = ROOT / "reports" / "latest" / "model_accuracy_report.md"
    if not md.exists():
        pytest.skip("model accuracy report not present")
    text = md.read_text(encoding="utf-8")
    assert "NO_PREDICTION_FOUND" in text
    assert "Proof pass count**: `0`" in text or "Proof pass count**: 0" in text


# ── T14: live-trading guardrails must read the real flags ───────────────


def test_t14_proof_pack_does_not_hardcode_guardrail_pass():
    src = (ROOT / "scripts" / "generate_proof_pack.py").read_text(encoding="utf-8")
    assert '"7_live_trading_guardrails": "PASS"' not in src
    assert "_live_trading_guardrails_status()" in src


def test_t14_guardrails_pass_only_when_both_flags_false():
    pack = _load_module("generate_proof_pack_0021_t14", ROOT / "scripts" / "generate_proof_pack.py")
    assert pack._live_trading_guardrails_status() == "PASS"


def test_t14_guardrails_fail_if_live_trading_enabled(tmp_path, monkeypatch):
    pack = _load_module("generate_proof_pack_0021_t14_fail", ROOT / "scripts" / "generate_proof_pack.py")
    cfg = tmp_path / "config"
    cfg.mkdir()
    (cfg / "live_trade_config.py").write_text(
        "LIVE_TRADING_ENABLED = True\nUSE_LIVE_EXECUTION_ENGINE = False\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(pack, "ROOT", tmp_path)
    assert pack._live_trading_guardrails_status() == "FAIL"


def test_t14_guardrails_fail_if_execution_engine_enabled(tmp_path, monkeypatch):
    pack = _load_module("generate_proof_pack_0021_t14_engine", ROOT / "scripts" / "generate_proof_pack.py")
    cfg = tmp_path / "config"
    cfg.mkdir()
    (cfg / "live_trade_config.py").write_text(
        "LIVE_TRADING_ENABLED = False\nUSE_LIVE_EXECUTION_ENGINE = True\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(pack, "ROOT", tmp_path)
    assert pack._live_trading_guardrails_status() == "FAIL"


def test_t14_live_trade_config_flags_are_false_in_repo():
    cfg = (ROOT / "config" / "live_trade_config.py").read_text(encoding="utf-8")
    assert "LIVE_TRADING_ENABLED = False" in cfg
    assert "USE_LIVE_EXECUTION_ENGINE = False" in cfg
    assert "LIVE_TRADING_ENABLED = True" not in cfg


def test_t14_guardrails_blocked_if_config_missing(tmp_path, monkeypatch):
    pack = _load_module("generate_proof_pack_0021_t14_missing", ROOT / "scripts" / "generate_proof_pack.py")
    monkeypatch.setattr(pack, "ROOT", tmp_path)
    assert pack._live_trading_guardrails_status() == "BLOCKED"


# ── R2/R3: batch chains on-demand fallback, never cache warming ───────────────


def test_r2r3_batch_chains_source_has_on_demand_dhan_fallback():
    src = (ROOT / "dashboard" / "backend" / "app.py").read_text(encoding="utf-8")
    helper = src.split("async def _fill_warming_required_chains", 1)[1].split("async def batch_chains()", 1)[0]
    batch = src.split("async def batch_chains():", 1)[1].split("async def get_chain(", 1)[0]
    assert "asyncio.wait_for" in helper
    assert "_warm_one_index_chain" in helper
    assert "_fill_warming_required_chains" in batch
    assert "if not ready:" in batch
    assert batch.index("if not ready:") < batch.rindex("_cache_set")


def test_r2r3_warming_placeholder_is_not_usable():
    src = (ROOT / "dashboard" / "backend" / "app.py").read_text(encoding="utf-8")
    assert "CHAIN_CACHE_WARMING" in src
    assert "_usable_chain_snapshot" in src


# ── Combined fail-closed contract ────────────────────────────


def test_0021_does_not_enable_live_trading():
    cfg = (ROOT / "config" / "live_trade_config.py").read_text(encoding="utf-8")
    app = (ROOT / "dashboard" / "backend" / "app.py").read_text(encoding="utf-8")
    ro = (ROOT / "core" / "brokers" / "dhan" / "dhan_readonly.py").read_text(encoding="utf-8")
    assert "LIVE_TRADING_ENABLED = False" in cfg
    assert '"live_trading_enabled": False' in app.split("async def batch_chains():", 1)[1][:1200]
    assert "live_trading_enabled" in ro
    assert "True" not in [
        line.split("=")[-1].strip()
        for line in cfg.splitlines()
        if line.strip().startswith("LIVE_TRADING_ENABLED")
    ]


def test_0021_proof_pack_cycle_fails_while_predictions_unproven():
    pack = _load_module("generate_proof_pack_0021_cycle", ROOT / "scripts" / "generate_proof_pack.py")
    statuses = {
        "6_prediction_analytics": pack._prediction_analytics_status(),
        "7_live_trading_guardrails": pack._live_trading_guardrails_status(),
    }
    assert statuses["6_prediction_analytics"] == "FAIL"
    assert statuses["7_live_trading_guardrails"] == "PASS"
    assert not all(v == "PASS" for v in statuses.values())
