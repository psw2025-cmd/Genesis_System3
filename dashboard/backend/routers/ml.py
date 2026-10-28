"""
ML router — predictions, accuracy, signals.
Heavy imports (pandas, joblib) loaded ONLY when endpoint is called.
Saves ~75MB RAM at startup.
"""
from __future__ import annotations
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter

from fo_eligibility_filter import get_fo_eligibility_filter
from option_strike_visibility_audit import OptionVisibilityAuditor, generate_sample_audit_report

router = APIRouter(tags=["ml"])

# dashboard/backend/routers/ml.py -> repo/runtime root
ROOT = Path(__file__).resolve().parents[3]
GAIN_RANK_FILE = ROOT / "state" / "gain_rank_history.json"
VAL_DIR = ROOT / "state" / "market_validations"
PAPER_VAL_DIR = ROOT / "state" / "paper_validations"
BENCHMARK_SUMMARY = ROOT / "reports" / "latest" / "performance_benchmark" / "benchmark_summary.md"
OPTIONS_ML_SUMMARY = ROOT / "reports" / "latest" / "options_ml_training" / "summary.json"

_COMPLETED_PASS_STATUSES = {
    "PASS",
    "COMPLETE",
    "COMPLETED",
    "PROVEN",
    "RECONCILED",
    "WALK_FORWARD_PASS",
    "COSTED_WALK_FORWARD_PASS",
}
_RECON_COMPLETE_STATUSES = {"COMPLETE", "COMPLETED", "PASS", "PASSED", "RECONCILED"}
_WALK_FORWARD_PASS_STATUSES = {"PASS", "PASSED", "WALK_FORWARD_PASS", "COSTED_WALK_FORWARD_PASS"}
_STUB_STATUSES = {"STUB", "PLACEHOLDER", "SYNTHETIC", "FABRICATED", "DRAFT", "SAMPLE", "MOCK"}
_NOT_PROVEN_REASON = "REAL_PAPER_LIFECYCLE_NOT_PROVEN - run scripts/run_paper_validation.py"
_FRESH_WINDOW = timedelta(days=14)
_MIN_RHO = 0.70


def _load_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return default


def _load_history() -> List[Dict]:
    data = _load_json(GAIN_RANK_FILE, [])
    return data if isinstance(data, list) else []


def _load_validations() -> List[Dict]:
    rows: List[Dict] = []
    by_date: Dict[str, Dict] = {}
    if VAL_DIR.exists():
        for f in sorted(VAL_DIR.glob("market_validation_*.json")):
            data = _load_json(f, None)
            if isinstance(data, dict):
                data.setdefault("_file", f.name)
                day = str(data.get("date") or f.stem.replace("market_validation_", ""))
                if day:
                    by_date[day] = data
    # Cloud durable path (Firestore) wins — never depend on laptop local state/.
    try:
        import os

        if os.environ.get("SYSTEM3_STATE_BACKEND", "").lower() == "firestore" or os.environ.get("SYSTEM3_FIRESTORE_PROJECT"):
            from dashboard.backend.firestore_state_backend import FirestoreSchedulerEvidenceBackend

            for row in FirestoreSchedulerEvidenceBackend().list_validation_days():
                if isinstance(row, dict) and row.get("date"):
                    by_date[str(row["date"])] = row
    except Exception:
        pass
    rows = [by_date[k] for k in sorted(by_date)]
    return rows


def _as_float(value: Any) -> Optional[float]:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        try:
            return float(text)
        except ValueError:
            return None
    return None


def _first_float(data: Dict[str, Any], keys: tuple[str, ...]) -> Optional[float]:
    for key in keys:
        if key not in data:
            continue
        number = _as_float(data.get(key))
        if number is not None:
            return number
    return None


def _status_text(value: Any) -> str:
    if isinstance(value, dict):
        return str(value.get("status") or "").strip().upper()
    return str(value or "").strip().upper()


def _flag_complete(value: Any, ok_statuses: set[str]) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        text = value.strip().upper()
        return text in ok_statuses or text == "TRUE"
    if isinstance(value, dict):
        if _status_text(value) in ok_statuses:
            return True
        if value.get("complete") is True or value.get("pass") is True:
            return True
    return False


def _has_run_timestamp(data: Dict[str, Any]) -> bool:
    for key in ("timestamp", "generated_at", "generated_at_utc", "completed_at", "run_at", "finished_at"):
        raw = data.get(key)
        if isinstance(raw, str) and len(raw.strip()) >= 10:
            return True
    return False


def _parse_run_datetime(value: str) -> Optional[datetime]:
    text = value.strip()
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _freshness_problem(data: Dict[str, Any]) -> Optional[str]:
    """Reject missing or stale run timestamps. Fourteen days is the forward-validation window."""
    stamps: List[datetime] = []
    for key in ("timestamp", "generated_at", "generated_at_utc", "completed_at", "run_at", "finished_at", "date"):
        raw = data.get(key)
        if isinstance(raw, str):
            parsed = _parse_run_datetime(raw)
            if parsed is not None:
                stamps.append(parsed)
    if not stamps:
        return "missing run timestamp"
    newest = max(stamps)
    now = datetime.now(timezone.utc)
    if newest - now > timedelta(days=1):
        return "run timestamp is in the future"
    if now - newest > _FRESH_WINDOW:
        return "run is not fresh (older than 14 days)"
    return None


def _list_or_count(value: Any) -> int:
    if isinstance(value, list):
        return len([item for item in value if item not in (None, "")])
    if isinstance(value, dict):
        count = _as_float(value.get("count") or value.get("n") or value.get("closed_count") or value.get("trade_count"))
        if count is not None:
            return int(count)
        for key in ("trade_ids", "closed_trade_ids", "trades"):
            nested = value.get(key)
            if isinstance(nested, list):
                return len(nested)
    return 0


def _closed_trade_count(data: Dict[str, Any]) -> int:
    best = 0
    for key in ("trade_ids", "closed_trade_ids", "trades", "closed_trades", "closed_trade_reconciliation", "reconciliation"):
        best = max(best, _list_or_count(data.get(key)))
    for key in ("closed_trade_count", "n_closed_trades", "trade_count"):
        count = _as_float(data.get(key))
        if count is not None:
            best = max(best, int(count))
    return best


def _walk_forward_trade_count(data: Dict[str, Any]) -> int:
    best = 0
    for key in ("costed_walk_forward", "walk_forward", "costed_walkforward"):
        value = data.get(key)
        if isinstance(value, dict):
            count = _as_float(
                value.get("n_trades")
                or value.get("trade_count")
                or value.get("windows")
                or value.get("folds")
            )
            if count is not None:
                best = max(best, int(count))
            best = max(best, _list_or_count(value.get("trades")))
        else:
            best = max(best, _list_or_count(value))
    for key in ("walk_forward_trades", "n_walk_forward_trades"):
        count = _as_float(data.get(key))
        if count is not None:
            best = max(best, int(count))
    return best


def _reconciliation_complete(data: Dict[str, Any]) -> bool:
    if _flag_complete(data.get("closed_trade_reconciliation"), _RECON_COMPLETE_STATUSES):
        return True
    if _flag_complete(data.get("reconciliation_status"), _RECON_COMPLETE_STATUSES):
        return True
    if _flag_complete(data.get("reconciliation"), _RECON_COMPLETE_STATUSES):
        return True
    return data.get("reconciliation_complete") is True or data.get("closed_trades_reconciled") is True


def _walk_forward_pass(data: Dict[str, Any]) -> bool:
    if _status_text(data.get("status")) in {"WALK_FORWARD_PASS", "COSTED_WALK_FORWARD_PASS"}:
        return True
    for key in (
        "costed_walk_forward",
        "walk_forward",
        "costed_walkforward",
        "walk_forward_status",
        "costed_walk_forward_status",
    ):
        if _flag_complete(data.get(key), _WALK_FORWARD_PASS_STATUSES):
            return True
    return data.get("costed_walk_forward_pass") is True


def _is_stub_validation(data: Dict[str, Any]) -> bool:
    if _status_text(data.get("status")) in _STUB_STATUSES:
        return True
    if any(data.get(flag) is True for flag in ("stub", "fabricated", "placeholder", "synthetic")):
        return True
    details = data.get("actual_details")
    if not isinstance(details, list) or not details:
        return False
    scores = [
        _as_float(row.get("combined_gain_score"))
        for row in details
        if isinstance(row, dict) and "combined_gain_score" in row
    ]
    if not scores:
        return False
    return all(score == 0.0 for score in scores) and _closed_trade_count(data) == 0


def _validation_json_files() -> List[Path]:
    files: List[Path] = []
    if PAPER_VAL_DIR.is_dir():
        files.extend(sorted(path for path in PAPER_VAL_DIR.glob("*.json") if path.is_file()))
    if VAL_DIR.is_dir():
        files.extend(sorted(path for path in VAL_DIR.glob("*.json") if path.is_file()))
    return files


def _assess_validation_file(path: Path) -> tuple[bool, str]:
    """True only for a completed real run with rho, hit rate, and reconciliation or walk-forward."""
    data = _load_json(path, None)
    if not isinstance(data, dict) or not data:
        return False, f"{path.name}: unreadable or empty JSON"
    problems: List[str] = []
    if _is_stub_validation(data):
        problems.append("stub or placeholder scores, not a real run")
    rho = _first_float(
        data,
        ("spearman_correlation", "rank_correlation_spearman", "rho", "avg_rho", "spearman_rho"),
    )
    hit = _first_float(data, ("hit_rate", "avg_hit_rate", "direction_hit_rate"))
    if rho is None:
        problems.append("missing numeric rho")
    elif rho <= _MIN_RHO:
        problems.append(f"rho {rho} is not > 0.70")
    if hit is None:
        problems.append("missing numeric hit_rate")
    status = _status_text(data.get("status"))
    if status not in _COMPLETED_PASS_STATUSES:
        shown = status or "MISSING"
        problems.append(f"status {shown} is not a completed real-run pass")
    reconciled = _reconciliation_complete(data)
    walk_pass = _walk_forward_pass(data)
    if not (reconciled or walk_pass):
        problems.append("closed-trade reconciliation is not complete and costed walk-forward is not PASS")
    freshness = _freshness_problem(data)
    if freshness:
        problems.append(freshness)
    evidence_count = 0
    if reconciled:
        evidence_count = max(evidence_count, _closed_trade_count(data))
    if walk_pass:
        evidence_count = max(evidence_count, _walk_forward_trade_count(data))
    if (reconciled or walk_pass) and evidence_count <= 0:
        problems.append("no closed-trade ids or walk-forward trade count from the run")
    if problems:
        return False, f"{path.name}: " + "; ".join(problems)
    return True, f"{path.name}: completed forward validation with numeric rho and hit_rate"


def _paper_validation_assessment() -> tuple[bool, str]:
    """Read existing validation JSON only. Never writes files. Default is not proven."""
    files = _validation_json_files()
    if not files:
        missing: List[str] = []
        if not PAPER_VAL_DIR.is_dir():
            missing.append("state/paper_validations is missing")
        else:
            missing.append("state/paper_validations has no JSON")
        if not VAL_DIR.is_dir():
            missing.append("state/market_validations is missing")
        else:
            missing.append("state/market_validations has no JSON")
        return False, "ready_for_live is false: " + "; ".join(missing)
    details = [_assess_validation_file(path) for path in files]
    proven = [detail for ok, detail in details if ok]
    if proven:
        return True, "ready_for_live is true from real files: " + "; ".join(proven)
    reasons = [detail for ok, detail in details if not ok]
    parts: List[str] = []
    if not PAPER_VAL_DIR.is_dir():
        parts.append("state/paper_validations is missing")
    elif not any(PAPER_VAL_DIR.glob("*.json")):
        parts.append("state/paper_validations has no JSON")
    parts.extend(reasons)
    return False, "ready_for_live is false: " + "; ".join(parts)


def _check_real_validations() -> tuple[bool, str]:
    """Read on-disk validation JSON. True only for real forward-validation evidence."""
    proven, detail = _paper_validation_assessment()
    if proven:
        return True, detail
    if _NOT_PROVEN_REASON not in detail:
        detail = f"{_NOT_PROVEN_REASON}: {detail}"
    return False, detail


def _paper_validation_proven() -> bool:
    return _check_real_validations()[0]


def _paper_validation_reason() -> str:
    return _check_real_validations()[1]


def _options_model_record() -> Dict | None:
    data = _load_json(OPTIONS_ML_SUMMARY, None)
    if not isinstance(data, dict):
        return None
    live_ready, live_reason = _check_real_validations()
    status = str(data.get("status", "")).upper()
    if status != "PASS":
        return {
            "total_predictions": 0,
            "validation_days": 0,
            "avg_accuracy": None,
            "avg_confidence": None,
            "ready_for_live": live_ready,
            "model_proof_ready": False,
            "status": status or "BLOCKED",
            "reason": data.get("reason", "CE/PE training proof is not PASS"),
            "ready_for_live_reason": live_reason,
            "source_file": str(OPTIONS_ML_SUMMARY),
        }
    results = data.get("results") if isinstance(data.get("results"), dict) else {}
    best = data.get("best_model")
    best_metrics = results.get(best, {}) if best else {}
    return {
        "total_predictions": data.get("dataset_rows", 0),
        "validation_days": 0,
        "avg_accuracy": best_metrics.get("accuracy"),
        "avg_confidence": None,
        "auc": best_metrics.get("auc"),
        "ready_for_live": live_ready,
        "model_proof_ready": True,
        "status": "PROVEN_TRAINED_ANALYZER_ONLY",
        "best_model": best,
        "reason": "CE/PE historical options model trained. " + live_reason,
        "ready_for_live_reason": live_reason,
        "source_file": str(OPTIONS_ML_SUMMARY),
    }


def _validation_metrics() -> Dict:
    validations = _load_validations()
    rhos = [float(v["spearman_correlation"]) for v in validations if v.get("spearman_correlation") is not None]
    hit_rates = [float(v["hit_rate"]) for v in validations if v.get("hit_rate") is not None]
    avg_rho = sum(rhos) / len(rhos) if rhos else None
    avg_hit = sum(hit_rates) / len(hit_rates) if hit_rates else None
    predictions = _load_history()
    prediction_days = [p for p in predictions if p.get("predictions")]
    proof_records = len(validations)
    threshold_met = bool(avg_rho is not None and avg_rho >= 0.70 and proof_records >= 10)
    live_ready, live_reason = _check_real_validations()
    return {
        "validation_days": proof_records,
        "prediction_days": len(prediction_days),
        "avg_rho": round(avg_rho, 4) if avg_rho is not None else None,
        "avg_hit_rate": round(avg_hit, 4) if avg_hit is not None else None,
        "target_rho": 0.70,
        "min_validation_days": 10,
        "ready_for_live": live_ready,
        "ready_for_live_reason": live_reason,
        "model_proof_ready": threshold_met,
        "status": "PROVEN_ANALYZER_ONLY" if threshold_met else "BLOCKED",
        "reason": "threshold_met" if threshold_met else "Need at least 10 real post-market validation reports and average Spearman rho >= 0.70",
        "latest_validation_file": validations[-1].get("_file") if validations else None,
        "benchmark_summary_exists": BENCHMARK_SUMMARY.exists(),
    }



def _filter_predictions_fo(preds: List[Dict]) -> tuple[List[Dict], List[Dict[str, Any]]]:
    """Keep only F&O-eligible underlyings; return (kept, rejected)."""
    fo = get_fo_eligibility_filter()
    kept: List[Dict] = []
    rejected: List[Dict[str, Any]] = []
    for row in preds or []:
        if not isinstance(row, dict):
            continue
        sym = str(row.get("underlying") or row.get("symbol") or "").strip().upper()
        if not sym:
            rejected.append({"underlying": sym, "reason": "MISSING_SYMBOL"})
            continue
        ok, reason = fo.is_eligible(sym)
        if ok:
            out = dict(row)
            out["fo_check"] = {"eligible": True, "reason": reason}
            kept.append(out)
        else:
            rejected.append({"underlying": sym, "reason": reason})
    return kept, rejected



@router.get("/api/gain_rank")
async def get_gain_rank(refresh: bool = False):
    history = _load_history()
    if not history:
        return {"status": "no_data", "latest": None, "history": [], "stale": True, "source_file": str(GAIN_RANK_FILE)}
    today = datetime.now().strftime("%Y-%m-%d")
    today_entry = next((e for e in reversed(history) if e.get("date") == today), None)
    latest = dict(today_entry or history[-1])
    stale = latest.get("date") != today
    preds = latest.get("predictions") if isinstance(latest.get("predictions"), list) else []
    kept, rejected = _filter_predictions_fo(preds)
    latest["predictions"] = kept
    latest["fo_filtered_out"] = rejected
    latest["fo_filter"] = {
        "eligible_count": len(kept),
        "rejected_count": len(rejected),
        "universe_size": len(get_fo_eligibility_filter().get_current_universe()),
    }
    return {"status": "ok", "latest": latest, "history": history[-14:], "is_today": not stale, "stale": stale, "source_file": str(GAIN_RANK_FILE), "note": "Rankings computed by worker at 09:15 IST — FO eligibility filter applied on read (BLK-004)", "fo_rejected": rejected}


@router.get("/api/accuracy_trend")
async def get_accuracy_trend():
    """Delegate to shared builder so trend days match auto_gates (Firestore + local)."""
    try:
        from dashboard.backend.accuracy_trend_service import build_accuracy_trend_payload
    except ImportError:
        from accuracy_trend_service import build_accuracy_trend_payload
    payload = build_accuracy_trend_payload(ROOT, retrain_needed=False)
    live_ready, live_reason = _check_real_validations()
    # Preserve legacy keys used by older ML clients without claiming live readiness.
    return {
        **payload,
        "days": payload.get("days_available", 0),
        "target_rho": 0.70,
        "ready_for_live": live_ready,
        "ready_for_live_reason": live_reason,
        "model_proof_ready": False,
    }


@router.get("/api/ml/performance")
async def get_ml_performance():
    metrics = _validation_metrics()
    live_ready = bool(metrics.get("ready_for_live"))
    live_reason = str(metrics.get("ready_for_live_reason") or _paper_validation_reason())
    models: Dict[str, Dict] = {}
    options_record = _options_model_record()
    if options_record:
        models["options_ce_pe_model"] = options_record

    if metrics["validation_days"] > 0:
        models["gain_rank_validator"] = {
            "total_predictions": metrics["prediction_days"],
            "validation_days": metrics["validation_days"],
            "avg_accuracy": metrics["avg_hit_rate"],
            "avg_confidence": None,
            "avg_spearman_rho": metrics["avg_rho"],
            "target_rho": metrics["target_rho"],
            "ready_for_live": live_ready,
            "model_proof_ready": metrics["model_proof_ready"],
            "status": metrics["status"],
            "reason": metrics["reason"],
            "latest_validation_file": metrics["latest_validation_file"],
        }

    source_files = {
        "gain_rank_history": str(GAIN_RANK_FILE),
        "market_validations": str(VAL_DIR),
        "paper_validations": str(PAPER_VAL_DIR),
        "benchmark_summary": str(BENCHMARK_SUMMARY),
        "options_ml_training": str(OPTIONS_ML_SUMMARY),
    }
    if not models:
        return {
            "models": {},
            "performance": {"models": {}},
            "validation_days": 0,
            "prediction_days": metrics["prediction_days"],
            "model_proof_ready": False,
            "ready_for_live": live_ready,
            "status": "BLOCKED",
            "message": "No real post-market validation reports or CE/PE training proof found. Model is not proven trained/ready. " + live_reason,
            "source_files": source_files,
        }

    any_proven = any(bool(m.get("model_proof_ready")) for m in models.values())
    if live_ready:
        status = "PROVEN_FORWARD_VALIDATION"
        message = live_reason
    elif any_proven:
        status = "PROVEN_ANALYZER_ONLY"
        message = "Model proof exists for analyzer only. " + live_reason
    else:
        status = "BLOCKED"
        message = f"{metrics['reason']} {live_reason}".strip()
    return {
        "models": models,
        "performance": {"models": models},
        "validation_days": metrics["validation_days"],
        "prediction_days": metrics["prediction_days"],
        "avg_rho": metrics["avg_rho"],
        "avg_hit_rate": metrics["avg_hit_rate"],
        "model_proof_ready": any_proven,
        "ready_for_live": live_ready,
        "status": status,
        "message": message,
        "source_files": source_files,
    }


@router.get("/api/ml/compare")
async def get_ml_compare():
    perf = await get_ml_performance()
    live_ready = bool(perf.get("ready_for_live"))
    models = perf.get("models", {})
    proven = {k: v for k, v in models.items() if v.get("model_proof_ready")}
    if not proven:
        return {
            "comparisons": [],
            "comparison": {"models": {}},
            "best_model": None,
            "status": "BLOCKED",
            "message": perf.get("message"),
            "ready_for_live": live_ready,
        }
    best_name = next(iter(proven.keys()))
    return {
        "comparisons": [],
        "comparison": {"models": proven},
        "best_model": {"name": best_name, "metrics": proven[best_name]},
        "status": "PROVEN_FORWARD_VALIDATION" if live_ready else "PROVEN_ANALYZER_ONLY",
        "message": perf.get("message"),
        "ready_for_live": live_ready,
    }


@router.get("/api/signal/top")
async def get_top_signal():
    history = _load_history()
    if not history:
        return {"signal": None, "status": "no_data", "source_file": str(GAIN_RANK_FILE)}
    latest = history[-1]
    preds = latest.get("predictions", [])
    if not preds:
        return {"signal": None, "status": "no_predictions", "source_file": str(GAIN_RANK_FILE)}
    kept, rejected = _filter_predictions_fo(preds)
    if not kept:
        return {"signal": None, "status": "no_fo_eligible_predictions", "fo_rejected": rejected, "source_file": str(GAIN_RANK_FILE)}
    top = max(kept, key=lambda x: x.get("gain_score", 0))
    return {"signal": {"underlying": top.get("underlying", "NIFTY"), "score": top.get("gain_score", 0), "direction": "BUY" if top.get("gain_score", 0) > 0 else "SELL", "confidence": min(abs(top.get("gain_score", 0)) / 100, 1.0), "date": latest.get("date"), "fo_check": top.get("fo_check")}, "status": "ok", "fo_rejected_count": len(rejected), "source_file": str(GAIN_RANK_FILE)}


@router.get("/api/audit/option-visibility")
async def get_option_visibility_audit(sample: bool = False):
    """BLK-003: prove signal underlyings map to visible PE/CE contracts."""
    if sample:
        report = generate_sample_audit_report()
        report["mode"] = "sample"
        return report

    history = _load_history()
    preds: List[Dict] = []
    if history:
        latest = history[-1]
        raw = latest.get("predictions") if isinstance(latest.get("predictions"), list) else []
        preds = [p for p in raw if isinstance(p, dict)]

    chain_candidates = [
        ROOT / "state" / "option_chain_cache.json",
        ROOT / "storage" / "live" / "option_chain_cache.json",
        ROOT / "reports" / "latest" / "option_strike_visibility.json",
    ]
    chain_file: Optional[Path] = next((p for p in chain_candidates if p.exists()), None)
    auditor = OptionVisibilityAuditor(chain_file)
    now = datetime.now()
    if not preds:
        # Fall back to priority FO names so endpoint always returns structure
        for i, sym in enumerate(["NIFTY", "BANKNIFTY", "RELIANCE", "SBIN", "INFY"]):
            auditor.audit_signal(f"SEED-{i+1}", sym, "LONG", 0.5, now)
        report = auditor.generate_report()
        report["mode"] = "seed_no_predictions"
        report["chain_file"] = str(chain_file) if chain_file else None
        return report

    for i, row in enumerate(preds[:25]):
        sym = str(row.get("underlying") or row.get("symbol") or "NIFTY")
        score = float(row.get("gain_score") or 0)
        direction = "LONG" if score >= 0 else "SHORT"
        conf = min(abs(score) / 100.0, 1.0)
        auditor.audit_signal(str(row.get("id") or f"SIG-{i+1}"), sym, direction, conf, now)
    report = auditor.generate_report()
    report["mode"] = "live_history"
    report["chain_file"] = str(chain_file) if chain_file else None
    report["note"] = "Coverage uses local chain cache when present; otherwise symbols are marked missing until Dhan OC is cached."
    return report

