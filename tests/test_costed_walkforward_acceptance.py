"""The daily-bhavcopy diagnostic must not promote itself to costed proof."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "costed_walkforward_proof", ROOT / "scripts/costed_walkforward_proof.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def _trade_with_execution_proof():
    return {
        "execution_evidence": {
            "spread_bps": 12.0,
            "latency_ms": 75.0,
            "fill_timestamp": "2026-11-14T09:16:00+05:30",
            "fill_source": "timestamped_quote_replay",
            "fee_schedule_version": "schedule-2026-11",
        },
        "cost_model": {
            "evidence_status": "VERIFIED",
            "brokerage": 40.0,
            "exchange_charge": 1.0,
            "stt": 0.2,
            "gst": 7.38,
            "sebi": 0.01,
            "slippage": 4.0,
            "spread_cost": 2.0,
            "latency_cost": 1.0,
        },
    }


def test_two_day_daily_bhavcopy_is_not_walk_forward_acceptance():
    result = MODULE.assess_costed_walkforward(2, [_trade_with_execution_proof()])
    assert result["pass"] is False
    assert result["status"] == "BLOCKED"
    assert "NEED_AT_LEAST_30_TRADING_SESSIONS" in result["blockers"]


def test_thirty_days_without_spread_latency_and_cost_provenance_stays_blocked():
    result = MODULE.assess_costed_walkforward(30, [{"cost_model": {"brokerage": 40}}])
    assert result["pass"] is False
    assert "TRADE_1_MISSING_EXECUTION_EVIDENCE" in result["blockers"]


def test_acceptance_requires_thirty_days_and_verified_execution_cost_inputs():
    result = MODULE.assess_costed_walkforward(30, [_trade_with_execution_proof()])
    assert result["pass"] is True
    assert result["status"] == "PASS"


def test_daily_bhavcopy_generator_never_claims_unobserved_costs_as_proven():
    source = (ROOT / "scripts/costed_walkforward_proof.py").read_text(encoding="utf-8")
    assert '"pass": acceptance["pass"]' in source
    assert '"recent_costed_walkforward_proven": acceptance["pass"]' in source
    assert '"spread_included": False' in source
    assert '"latency_included": False' in source


def test_short_daily_bhavcopy_run_is_written_as_blocked_not_pass(tmp_path, monkeypatch):
    bhavcopy = tmp_path / "bhavcopy"
    report_dir = tmp_path / "report"
    bhavcopy.mkdir()
    report_dir.mkdir()
    for day, close in (("20260105", 100.0), ("20260106", 105.0)):
        (bhavcopy / f"{day}_fo_bhavcopy.csv").write_text(
            "Symbol,Close,OI,ChngInOpnIntrst,OptTp,Strike,Expiry\n"
            f"NIFTY,{close},1000,100,CE,25000,2026-01-29\n",
            encoding="utf-8",
        )
    monkeypatch.setattr(MODULE, "BHAVCOPY_DIR", bhavcopy)
    monkeypatch.setattr(MODULE, "OUT", report_dir)
    result = MODULE.run_proof()
    saved = json.loads((report_dir / "costed_walkforward_proof.json").read_text(encoding="utf-8"))
    assert result["pass"] is False
    assert result["status"] == "BLOCKED"
    assert result["recent_costed_walkforward_proven"] is False
    assert saved["costs_slippage_included_proven"] is False
    assert "NEED_AT_LEAST_30_TRADING_SESSIONS" in saved["reason"]
