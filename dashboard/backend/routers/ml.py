"""
ML router — predictions, accuracy, signals.
Heavy imports (pandas, joblib) loaded ONLY when endpoint is called.
Saves ~75MB RAM at startup.
"""
from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from fastapi import APIRouter

router = APIRouter(tags=["ml"])

# dashboard/backend/routers/ml.py -> repo/runtime root
ROOT = Path(__file__).resolve().parents[3]
GAIN_RANK_FILE = ROOT / "state" / "gain_rank_history.json"
VAL_DIR = ROOT / "state" / "market_validations"
BENCHMARK_SUMMARY = ROOT / "reports" / "latest" / "performance_benchmark" / "benchmark_summary.md"
OPTIONS_ML_SUMMARY = ROOT / "reports" / "latest" / "options_ml_training" / "summary.json"


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
    if not VAL_DIR.exists():
        return []
    rows: List[Dict] = []
    for f in sorted(VAL_DIR.glob("market_validation_*.json")):
        data = _load_json(f, None)
        if isinstance(data, dict):
            data.setdefault("_file", f.name)
            rows.append(data)
    return rows


def _options_model_record() -> Dict | None:
    data = _load_json(OPTIONS_ML_SUMMARY, None)
    if not isinstance(data, dict):
        return None
    status = str(data.get("status", "")).upper()
    if status != "PASS":
        return {
            "total_predictions": 0,
            "validation_days": 0,
            "avg_accuracy": None,
            "avg_confidence": None,
            "ready_for_live": False,
            "model_proof_ready": False,
            "status": status or "BLOCKED",
            "reason": data.get("reason", "CE/PE training proof is not PASS"),
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
        "ready_for_live": False,
        "model_proof_ready": True,
        "status": "PROVEN_TRAINED_ANALYZER_ONLY",
        "best_model": best,
        "reason": "CE/PE historical options model trained; live readiness still requires forward paper validation.",
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
    return {
        "validation_days": proof_records,
        "prediction_days": len(prediction_days),
        "avg_rho": round(avg_rho, 4) if avg_rho is not None else None,
        "avg_hit_rate": round(avg_hit, 4) if avg_hit is not None else None,
        "target_rho": 0.70,
        "min_validation_days": 10,
        "ready_for_live": False,
        "model_proof_ready": threshold_met,
        "status": "PROVEN" if threshold_met else "BLOCKED",
        "reason": "threshold_met" if threshold_met else "Need at least 10 real post-market validation reports and average Spearman rho >= 0.70",
        "latest_validation_file": validations[-1].get("_file") if validations else None,
        "benchmark_summary_exists": BENCHMARK_SUMMARY.exists(),
    }


@router.get("/api/gain_rank")
async def get_gain_rank(refresh: bool = False):
    history = _load_history()
    if not history:
        return {"status": "no_data", "latest": None, "history": [], "stale": True, "source_file": str(GAIN_RANK_FILE)}
    today = datetime.now().strftime("%Y-%m-%d")
    today_entry = next((e for e in reversed(history) if e.get("date") == today), None)
    latest = today_entry or history[-1]
    stale = latest.get("date") != today
    return {"status": "ok", "latest": latest, "history": history[-14:], "is_today": not stale, "stale": stale, "source_file": str(GAIN_RANK_FILE), "note": "Rankings computed by worker at 09:15 IST — no inline ML in web process"}


@router.get("/api/accuracy_trend")
async def get_accuracy_trend():
    trend = []
    for v in _load_validations():
        rho = v.get("spearman_correlation")
        if rho is not None:
            trend.append({"date": str(v.get("date") or v.get("_file", "")).replace("market_validation_", "").replace(".json", ""), "rho": rho, "n_predictions": len(v.get("predictions", []))})
    avg_rho = sum(float(t["rho"]) for t in trend) / len(trend) if trend else 0
    return {"trend": trend, "days": len(trend), "avg_rho": round(avg_rho, 4), "target_rho": 0.70, "ready_for_live": False, "model_proof_ready": avg_rho >= 0.70 and len(trend) >= 10}


@router.get("/api/ml/performance")
async def get_ml_performance():
    metrics = _validation_metrics()
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
            "ready_for_live": False,
            "model_proof_ready": metrics["model_proof_ready"],
            "status": metrics["status"],
            "reason": metrics["reason"],
            "latest_validation_file": metrics["latest_validation_file"],
        }

    if not models:
        return {"models": {}, "performance": {"models": {}}, "validation_days": 0, "prediction_days": metrics["prediction_days"], "model_proof_ready": False, "ready_for_live": False, "status": "BLOCKED", "message": "No real post-market validation reports or CE/PE training proof found. Model is not proven trained/ready.", "source_files": {"gain_rank_history": str(GAIN_RANK_FILE), "market_validations": str(VAL_DIR), "options_ml_training": str(OPTIONS_ML_SUMMARY)}}

    any_proven = any(bool(m.get("model_proof_ready")) for m in models.values())
    return {"models": models, "performance": {"models": models}, "validation_days": metrics["validation_days"], "prediction_days": metrics["prediction_days"], "avg_rho": metrics["avg_rho"], "avg_hit_rate": metrics["avg_hit_rate"], "model_proof_ready": any_proven, "ready_for_live": False, "status": "PROVEN_ANALYZER_ONLY" if any_proven else "BLOCKED", "message": "Model proof exists for analyzer only; live readiness remains blocked until forward paper validation passes." if any_proven else metrics["reason"], "source_files": {"gain_rank_history": str(GAIN_RANK_FILE), "market_validations": str(VAL_DIR), "benchmark_summary": str(BENCHMARK_SUMMARY), "options_ml_training": str(OPTIONS_ML_SUMMARY)}}


@router.get("/api/ml/compare")
async def get_ml_compare():
    perf = await get_ml_performance()
    models = perf.get("models", {})
    proven = {k: v for k, v in models.items() if v.get("model_proof_ready")}
    if not proven:
        return {"comparisons": [], "comparison": {"models": {}}, "best_model": None, "status": "BLOCKED", "message": perf.get("message"), "ready_for_live": False}
    best_name = next(iter(proven.keys()))
    return {"comparisons": [], "comparison": {"models": proven}, "best_model": {"name": best_name, "metrics": proven[best_name]}, "status": "PROVEN_ANALYZER_ONLY", "ready_for_live": False}


@router.get("/api/signal/top")
async def get_top_signal():
    history = _load_history()
    if not history:
        return {"signal": None, "status": "no_data", "source_file": str(GAIN_RANK_FILE)}
    latest = history[-1]
    preds = latest.get("predictions", [])
    if not preds:
        return {"signal": None, "status": "no_predictions", "source_file": str(GAIN_RANK_FILE)}
    top = max(preds, key=lambda x: x.get("gain_score", 0))
    return {"signal": {"underlying": top.get("underlying", "NIFTY"), "score": top.get("gain_score", 0), "direction": "BUY" if top.get("gain_score", 0) > 0 else "SELL", "confidence": min(abs(top.get("gain_score", 0)) / 100, 1.0), "date": latest.get("date")}, "status": "ok", "source_file": str(GAIN_RANK_FILE)}
