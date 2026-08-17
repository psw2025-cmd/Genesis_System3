"""Eval: append-only proof ledger + fail-closed infinite intent spec."""

from __future__ import annotations

import json

from dashboard.backend.proof_ledger_service import (
    FORBIDDEN_LEDGER_KEYS,
    append_ledger_entry,
    build_intent_tick,
    ledger_tip,
    proof_ledger_status,
    verify_ledger_chain,
)


def test_append_only_hash_chain(tmp_path):
    root = tmp_path
    first = append_ledger_entry(
        root,
        git_sha="aaa111",
        cloud_run_revision="rev-1",
        broker_connected=False,
        gate_ids=["ML_SPEARMAN_RHO_GTE_0_70_OVER_5_DAYS"],
        next_id="A2",
        evidence_class="HISTORICAL_STORED",
    )
    second = append_ledger_entry(
        root,
        git_sha="bbb222",
        cloud_run_revision="rev-2",
        broker_connected=True,
        gate_ids=["ML_SPEARMAN_RHO_GTE_0_70_OVER_5_DAYS"],
        next_id="A2",
        evidence_class="REQUEST_SCOPED_LIVE",
    )
    assert first["prev_hash"] == "GENESIS"
    assert second["prev_hash"] == first["entry_hash"]
    assert first["entry_hash"] != second["entry_hash"]
    assert verify_ledger_chain(root)["ok"] is True
    assert verify_ledger_chain(root)["entries"] == 2
    tip = ledger_tip(root)
    assert tip["git_sha"] == "bbb222"
    assert tip["live_trading_enabled"] is False
    assert tip["order_placement_allowed"] is False
    assert tip["secret_payloads_present"] is False
    assert "access_token" not in json.dumps(tip)


def test_ledger_rejects_secret_payload_fields(tmp_path):
    try:
        append_ledger_entry(
            tmp_path,
            git_sha="ccc",
            extra={"dhan_access_token": "should-never-store"},
        )
        assert False, "must reject secret-like keys"
    except ValueError as exc:
        assert "forbidden" in str(exc).lower()
    for key in FORBIDDEN_LEDGER_KEYS:
        assert any(
            fragment in key
            for fragment in (
                "token",
                "secret",
                "pin",
                "totp",
                "password",
                "authorization",
                "bearer",
                "key",
            )
        )


def test_intent_tick_never_waits_for_user_on_routine_work():
    tick = build_intent_tick(
        next_id="A2",
        defect="ML spearman collecting",
        success_criteria="Do not force PASS; keep collecting real days",
    )
    assert tick["schema"] == "system3_autonomous_intent_v1"
    assert tick["wait_for_user"] is False
    assert tick["live_trading_enabled"] is False
    assert tick["auto_continue"] is True
    assert "LIVE=false" in tick["constraints"]
    assert "no_secret_mint_except_rotator" in tick["constraints"]
    assert "never_weaken_proof_gates" in tick["constraints"]


def test_intent_tick_blocks_live_enable_even_in_infinite_loop():
    tick = build_intent_tick(
        next_id="LIVE",
        defect="enable live trading",
        success_criteria="turn LIVE on",
        requested_live=True,
    )
    assert tick["wait_for_user"] is True
    assert tick["auto_continue"] is False
    assert tick["live_trading_enabled"] is False
    assert tick["human_gate_required"] == "LIVE_ENABLEMENT"
    assert tick["rejected_action"] == "enable_live_trading"


def test_infinite_loop_does_not_mutate_gate_thresholds():
    tick = build_intent_tick(next_id="A2", defect="rho low", success_criteria="improve model")
    assert tick["strategy_mutation_allowed"] == "code_via_pr_and_evals_only"
    assert tick["proof_gate_thresholds_locked"] is True
    assert tick["synthetic_metrics_allowed"] is False
    assert tick["hot_graph_rewrite_allowed"] is False


def test_tampered_ledger_fails_chain_verify(tmp_path):
    append_ledger_entry(tmp_path, git_sha="aaa", next_id="A2")
    path = tmp_path / "reports" / "latest" / "proof_ledger" / "ledger.jsonl"
    rows = path.read_text(encoding="utf-8").splitlines()
    row = json.loads(rows[0])
    row["git_sha"] = "tampered"
    path.write_text(json.dumps(row, sort_keys=True) + "\n", encoding="utf-8")
    proof = verify_ledger_chain(tmp_path)
    assert proof["ok"] is False
    assert proof["reason"] == "hash_mismatch"


def test_proof_ledger_status_is_read_only(tmp_path):
    append_ledger_entry(tmp_path, git_sha="ddd", next_id="A2")
    before = verify_ledger_chain(tmp_path)["entries"]
    status = proof_ledger_status(tmp_path)
    assert status["schema"] == "system3_proof_ledger_status_v1"
    assert status["live_trading_enabled"] is False
    assert status["wait_for_user_routine"] is False
    assert status["tip"]["next_id"] == "A2"
    assert status["intent_tick"]["auto_continue"] is True
    assert verify_ledger_chain(tmp_path)["entries"] == before


def test_orchestrator_and_api_are_wired():
    from pathlib import Path

    root = Path(__file__).resolve().parents[2]
    orchestrator = (root / "scripts" / "system3_continuous_closure_orchestrator.py").read_text(encoding="utf-8")
    app = (root / "dashboard" / "backend" / "app.py").read_text(encoding="utf-8")
    policy = (root / "agent_policy.yaml").read_text(encoding="utf-8")
    assert "append_ledger_entry" in orchestrator
    assert '@app.get("/api/proof_ledger")' in app
    assert "append_ledger_entry" not in app.split('@app.get("/api/proof_ledger")', 1)[1][:1200]
    assert "infinite_gitops_loop:" in policy
    assert "wait_for_user_on_routine_gitops" in policy
