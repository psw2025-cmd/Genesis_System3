"""Live Genesis Brain / ML health — no hardcoded confidence, no fake VERIFIED.

Ensemble is VERIFIED only when the Spearman proof gate actually passes.
Truth score is live data-integrity, not July historical proof-matrix files.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[2]
GATES_JSON = ROOT / "reports" / "latest" / "system3_auto_gates" / "summary.json"
HEALTH_JSON = ROOT / "outputs" / "health.json"
PAPER_STATE = ROOT / "outputs" / "paper_engine_state.json"
PAPER_PNL = ROOT / "outputs" / "paper_pnl_summary.json"
PRED_CACHE = ROOT / "outputs" / "ml_predictions_live.json"
NIFTY_CHAIN = ROOT / "state" / "chain_cache" / "NIFTY.json"
RETRAIN_SIGNAL = ROOT / "state" / "retrain_signal.json"

SPEARMAN_GATE = "ML_SPEARMAN_RHO_GTE_0_70_OVER_5_DAYS"
RETRAIN_RHO = 0.40


def _read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _spearman_gate(auto_gates: Dict[str, Any]) -> Dict[str, Any]:
    gates = auto_gates.get("gates") if isinstance(auto_gates.get("gates"), dict) else {}
    raw = gates.get(SPEARMAN_GATE) if isinstance(gates, dict) else {}
    if not isinstance(raw, dict):
        raw = {}
    return raw


def predictions_from_scanner_rows(scan: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Map daily_gain_scanner output into confidence rows. No invented scores."""
    rows = []
    if not isinstance(scan, dict):
        return rows
    for row in list(scan.get("full_ranking") or scan.get("top_predictions") or [])[:10]:
        if not isinstance(row, dict):
            continue
        try:
            score = float(row.get("gain_score") or row.get("expected_move_pct") or row.get("score") or 0)
        except (TypeError, ValueError):
            continue
        try:
            conf = float(row.get("confidence_pct")) if row.get("confidence_pct") is not None else None
        except (TypeError, ValueError):
            conf = None
        if conf is None:
            conf = min(99.0, abs(score) * 10.0 if abs(score) <= 10 else abs(score))
        rows.append(
            {
                "symbol": row.get("underlying") or row.get("symbol"),
                "confidence_pct": round(float(conf), 2),
                "recommendation": row.get("recommendation"),
                "source": str(row.get("source") or "daily_gain_scanner"),
            }
        )
    return rows


def _paper_sim_performance(paper: Dict[str, Any]) -> Dict[str, Any]:
    closed: List[Dict[str, Any]] = []
    for candidate in (
        paper.get("closed_positions"),
        (paper.get("summary") or {}).get("closed_positions") if isinstance(paper.get("summary"), dict) else None,
    ):
        if isinstance(candidate, list):
            closed = [row for row in candidate if isinstance(row, dict)]
            break
    gross_win = 0.0
    gross_loss = 0.0
    for row in closed:
        try:
            pnl = float(row.get("realized_pnl") or 0)
        except (TypeError, ValueError):
            continue
        if pnl > 0:
            gross_win += pnl
        elif pnl < 0:
            gross_loss += abs(pnl)
    profit_factor = round(gross_win / gross_loss, 4) if gross_loss > 0 else None
    return {
        "profit_factor": profit_factor,
        "max_drawdown": None,
        "profit_factor_source": "paper_simulator_closed_trades" if closed else "none",
        "profit_factor_note": (
            "Paper simulator gross win/loss; not ensemble expectancy"
            if profit_factor is not None
            else "No paper closed-trade gross win/loss yet"
        ),
        "paper_closed_count": len(closed),
    }


def _live_confidence(predictions: List[Dict[str, Any]]) -> Dict[str, Any]:
    rows = [p for p in predictions if isinstance(p, dict)]
    tradeable = [
        p
        for p in rows
        if str(p.get("recommendation") or "").upper() == "TRADE"
        and p.get("confidence_pct") is not None
    ]
    pool = tradeable or rows
    values: List[float] = []
    for row in pool:
        try:
            values.append(float(row.get("confidence_pct")))
        except (TypeError, ValueError):
            continue
    if not values:
        return {
            "confidence": None,
            "prediction_confidence": None,
            "confidence_source": "none",
            "confidence_note": "No live scanner/model confidence available",
        }
    mean = sum(values) / len(values)
    return {
        "confidence": round(mean, 2),
        "prediction_confidence": round(mean, 2),
        "confidence_source": str((pool[0] or {}).get("source") or "daily_gain_scanner"),
        "confidence_note": "Mean live scanner confidence; not a calibrated ensemble probability",
    }


def _integrity_checks(
    *,
    broker_connected: bool,
    token_ok: bool,
    live_locked: bool,
    market_known: bool,
    paper_ok: bool,
    chain_ok: bool,
    gates_present: bool,
    qc_ok: bool,
) -> Dict[str, Any]:
    checks = [
        ("broker_connected", broker_connected),
        ("token_unexpired_or_unknown", token_ok),
        ("live_execution_locked", live_locked),
        ("market_session_known", market_known),
        ("paper_engine_healthy", paper_ok),
        ("index_chain_spot", chain_ok),
        ("auto_gates_snapshot", gates_present),
        ("qc_not_failing", qc_ok),
    ]
    passed = sum(1 for _, ok in checks if ok)
    total = len(checks)
    score = round(100.0 * passed / total, 2) if total else 0.0
    return {
        "truth_score": score,
        "proof_pass": passed,
        "proof_total": total,
        "checks": {name: bool(ok) for name, ok in checks},
        "data_sources_required": 2,
        "score_basis": "live_local_data_integrity_not_historical_proof_matrix",
    }


def build_genesis_ml_health(
    *,
    auto_gates: Optional[Dict[str, Any]] = None,
    broker: Optional[Dict[str, Any]] = None,
    paper: Optional[Dict[str, Any]] = None,
    predictions: Optional[List[Dict[str, Any]]] = None,
    market_open: Optional[bool] = None,
    qc_status: Optional[str] = None,
    chain_spot: Optional[float] = None,
    live_trading_enabled: bool = False,
    token_expired: Optional[bool] = None,
) -> Dict[str, Any]:
    """Deterministic health document for Genesis Brain + /api/ml/health."""
    auto_gates = auto_gates if isinstance(auto_gates, dict) else {}
    broker = broker if isinstance(broker, dict) else {}
    paper = paper if isinstance(paper, dict) else {}
    predictions = predictions if isinstance(predictions, list) else []

    spearman = _spearman_gate(auto_gates)
    spearman_pass = spearman.get("pass") is True
    try:
        latest_rho = float(spearman["latest_rho"]) if spearman.get("latest_rho") is not None else None
    except (TypeError, ValueError):
        latest_rho = None

    broker_connected = broker.get("connected") is True
    live_locked = live_trading_enabled is False
    token_ok = True if token_expired is None else (token_expired is False)
    market_known = market_open is not None
    paper_ok = True
    if market_open is True:
        paper_ok = str(paper.get("status") or "").upper() in {"ONLINE", "OK", "ACTIVE"} or bool(
            paper.get("loop_enabled")
        )
    chain_ok = chain_spot is not None and float(chain_spot) > 0
    gates_present = bool(auto_gates.get("gates") or auto_gates.get("snapshot_id"))
    qc_ok = str(qc_status or "PASS").upper() not in {"FAIL", "ERROR", "DOWN"}

    integrity = _integrity_checks(
        broker_connected=broker_connected,
        token_ok=token_ok,
        live_locked=live_locked,
        market_known=market_known,
        paper_ok=paper_ok,
        chain_ok=chain_ok,
        gates_present=gates_present,
        qc_ok=qc_ok,
    )

    if spearman_pass:
        ensemble_status = "VERIFIED"
        validation_status = "SPEARMAN_GATE_PASS"
    elif latest_rho is None:
        ensemble_status = "NOT_VERIFIED"
        validation_status = "SPEARMAN_EVIDENCE_MISSING"
    else:
        ensemble_status = "NOT_VERIFIED"
        validation_status = "SYS3-BLK-005"

    if latest_rho is None:
        retrain_status = "NO_SIGNAL"
    elif latest_rho < RETRAIN_RHO:
        retrain_status = "RETRAIN_NEEDED"
    elif not spearman_pass:
        retrain_status = "VALIDATION_PENDING"
    else:
        retrain_status = "IDLE_GATES_PASS"

    if not broker_connected or not qc_ok:
        anomaly = "DEGRADED"
    elif not spearman_pass:
        anomaly = "MODEL_PROOF_FAILING"
    else:
        anomaly = "NORMAL"

    confidence = _live_confidence(predictions)
    paper_perf = _paper_sim_performance(paper)
    retrain_signal = RETRAIN_SIGNAL.exists()

    return {
        "generated_utc": _utc(),
        "live_trading_enabled": False,
        "status": ensemble_status,
        "ensemble_status": ensemble_status,
        "validation_status": validation_status,
        "blocker_id": None if spearman_pass else "SYS3-BLK-005",
        "latest_rho": latest_rho,
        "spearman_days_passing": spearman.get("days_passing_threshold"),
        "spearman_days_required": spearman.get("days_required") or 5,
        "spearman_gate_pass": spearman_pass,
        "retraining_status": retrain_status,
        "retrain_signal_present": retrain_signal,
        "promotion_allowed": False,
        "anomaly_status": anomaly,
        "drift_psi": None,
        "psi": None,
        "drift_status": "SPEARMAN_PROXY" if latest_rho is not None else "UNAVAILABLE",
        "drift_display": (
            f"rho={latest_rho:.3f}" if latest_rho is not None else "Unavailable"
        ),
        "truth_score": integrity["truth_score"],
        "truth": {
            **integrity,
            "status": "OK" if integrity["truth_score"] >= 75 else "DEGRADED",
            "anomaly_status": anomaly,
            "drift_psi": None,
            "drift_status": "SPEARMAN_PROXY" if latest_rho is not None else "UNAVAILABLE",
            "model_proof_score": None,
            "model_proof_note": (
                f"Spearman rho={latest_rho} over {spearman.get('days_recorded')} days; "
                "need >=0.70 on 5 qualifying days before ensemble VERIFIED"
            ),
        },
        "accuracy": None,
        **confidence,
        **paper_perf,
        "live_trading_blocked": True,
        "safety": "PAPER_LOCKED",
    }


def maybe_write_retrain_signal(
    payload: Dict[str, Any],
    path: Optional[Path] = None,
) -> bool:
    """Write state/retrain_signal.json once when Spearman ρ says retrain.

    Does not promote models and does not enable LIVE. ``scripts/auto_retrain.py``
    is the only trainer consumer; it still cannot pass the Spearman gate.
    """
    target = path or RETRAIN_SIGNAL
    if payload.get("retraining_status") != "RETRAIN_NEEDED":
        return False
    if target.exists():
        return False
    target.parent.mkdir(parents=True, exist_ok=True)
    body = {
        "triggered_at": _utc(),
        "reason": (
            f"latest Spearman rho={payload.get('latest_rho')} "
            f"below {RETRAIN_RHO} ({payload.get('blocker_id') or 'SYS3-BLK-005'})"
        ),
        "action": "run scripts/auto_retrain.py; do not mark ensemble VERIFIED; LIVE remains locked",
        "promotion_allowed": False,
        "live_trading_enabled": False,
        "source": "genesis_ml_health",
    }
    target.write_text(json.dumps(body, indent=2), encoding="utf-8")
    return True


def build_genesis_ml_health_from_disk(
    extra_predictions: Optional[List[Dict[str, Any]]] = None,
    extra_broker: Optional[Dict[str, Any]] = None,
    extra_paper: Optional[Dict[str, Any]] = None,
    extra_market_open: Optional[bool] = None,
    extra_qc: Optional[str] = None,
    emit_retrain_signal: bool = True,
    retrain_signal_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """File-backed builder used by API handlers (no extra Dhan OC calls)."""
    auto_gates = _read_json(GATES_JSON)
    health = _read_json(HEALTH_JSON)
    paper_state = _read_json(PAPER_STATE)
    paper_pnl = _read_json(PAPER_PNL)
    nifty = _read_json(NIFTY_CHAIN)
    broker = extra_broker if extra_broker is not None else (health.get("broker") if isinstance(health.get("broker"), dict) else health)
    if not isinstance(broker, dict):
        broker = {}
    paper = extra_paper if extra_paper is not None else paper_state
    if not isinstance(paper, dict):
        paper = {}
    else:
        paper = dict(paper)
    if not paper.get("closed_positions") and isinstance(paper_pnl.get("closed_positions"), list):
        paper["closed_positions"] = paper_pnl["closed_positions"]
    if extra_predictions:
        preds = extra_predictions
    else:
        runtime = _read_json(ROOT / "outputs" / "runtime_state.json")
        preds = list(runtime.get("ml_predictions") or []) if isinstance(runtime, dict) else []
        if not preds:
            cached = _read_json(PRED_CACHE)
            cached_rows = cached.get("predictions") if isinstance(cached.get("predictions"), list) else []
            preds = [row for row in cached_rows if isinstance(row, dict)]
    market_open = extra_market_open
    if market_open is None:
        market = health.get("market") if isinstance(health.get("market"), dict) else {}
        market_open = market.get("is_open")
        if market_open is None:
            market_open = str(health.get("market_status") or "").lower() == "open"
    qc = extra_qc or health.get("qc_status")
    try:
        spot = float(nifty.get("spot") or 0) or None
    except (TypeError, ValueError):
        spot = None
    token_expired = None
    token_proof = broker.get("token_proof") if isinstance(broker.get("token_proof"), dict) else {}
    if "expired" in token_proof:
        token_expired = bool(token_proof.get("expired"))
    payload = build_genesis_ml_health(
        auto_gates=auto_gates,
        broker=broker,
        paper=paper,
        predictions=preds if isinstance(preds, list) else [],
        market_open=market_open,
        qc_status=str(qc) if qc is not None else None,
        chain_spot=spot,
        live_trading_enabled=False,
        token_expired=token_expired,
    )
    if emit_retrain_signal:
        payload["retrain_signal_written"] = maybe_write_retrain_signal(
            payload, path=retrain_signal_path
        )
        signal_path = retrain_signal_path or RETRAIN_SIGNAL
        payload["retrain_signal_present"] = signal_path.exists()
    else:
        payload["retrain_signal_written"] = False
    return payload
