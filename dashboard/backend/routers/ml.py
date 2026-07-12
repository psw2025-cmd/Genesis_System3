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
    """Latest gain rank predictions — file-based, no ML compute in web process."""
    history = _load_history()
    if not history:
        return {"status": "no_data", "latest": None, "history": [], "stale": True, "source_file": str(GAIN_RANK_FILE)}

    today = datetime.now().strftime("%Y-%m-%d")
    today_entry = next((e for e in reversed(history) if e.get("date") == today), None)
    latest = today_entry or history[-1]
    stale = latest.get("date") != today

    return {
        "status": "ok",
        "latest": latest,
        "history": history[-14:],
        "is_today": not stale,
        "stale": stale,
        "source_file": str(GAIN_RANK_FILE),
        "note": "Rankings computed by worker at 09:15 IST — no inline ML in web process",
    }


@router.get("/api/accuracy_trend")
async def get_accuracy_trend():
    """Spearman rho history from validation files."""
    trend = []
    for v in _load_validations():
        rho = v.get("spearman_correlation")
        if rho is not None:
            trend.append({
                "date": str(v.get("date") or v.get("_file", "")).replace("market_validation_", "").replace(".json", ""),
                "rho": rho,
                "n_predictions": len(v.get("predictions", [])),
            })
    avg_rho = sum(float(t["rho"]) for t in trend) / len(trend) if trend else 0
    return {
        "trend": trend,
        "days": len(trend),
        "avg_rho": round(avg_rho, 4),
        "target_rho": 0.70,
        "ready_for_live": False,
        "model_proof_ready": avg_rho >= 0.70 and len(trend) >= 10,
    }


@router.get("/api/ml/performance")
async def get_ml_performance():
    """ML proof from real prediction history + real post-market validation files only."""
    metrics = _validation_metrics()
    if metrics["validation_days"] == 0:
        return {
            "models": {},
            "performance": {"models": {}},
            "validation_days": 0,
            "prediction_days": metrics["prediction_days"],
            "model_proof_ready": False,
            "ready_for_live": False,
            "status": "BLOCKED",
            "message": "No real post-market validation reports found. Model is not proven trained/ready.",
            "source_files": {"gain_rank_history": str(GAIN_RANK_FILE), "market_validations": str(VAL_DIR)},
        }

    model_record = {
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
    return {
        "models": {"gain_rank_validator": model_record},
        "performance": {"models": {"gain_rank_validator": model_record}},
        "validation_days": metrics["validation_days"],
        "prediction_days": metrics["prediction_days"],
        "avg_rho": metrics["avg_rho"],
        "avg_hit_rate": metrics["avg_hit_rate"],
        "model_proof_ready": metrics["model_proof_ready"],
        "ready_for_live": False,
        "status": metrics["status"],
        "message": metrics["reason"],
        "source_files": {"gain_rank_history": str(GAIN_RANK_FILE), "market_validations": str(VAL_DIR), "benchmark_summary": str(BENCHMARK_SUMMARY)},
    }


@router.get("/api/ml/compare")
async def get_ml_compare():
    """Compare ML model proof records. No invented model metrics."""
    metrics = _validation_metrics()
    if not metrics["model_proof_ready"]:
        return {
            "comparisons": [],
            "comparison": {"models": {}},
            "best_model": None,
            "status": "BLOCKED",
            "message": metrics["reason"],
            "ready_for_live": False,
        }
    return {
        "comparisons": [],
        "comparison": {
            "models": {
                "gain_rank_validator": {
                    "avg_spearman_rho": metrics["avg_rho"],
                    "validation_days": metrics["validation_days"],
                    "ready_for_live": False,
                }
            }
        },
        "best_model": {"name": "gain_rank_validator", "metrics": {"avg_accuracy": metrics["avg_hit_rate"], "avg_spearman_rho": metrics["avg_rho"]}},
        "status": "PROVEN",
        "ready_for_live": False,
    }


@router.get("/api/signal/top")
async def get_top_signal():
    """Top signal from latest gain_rank."""
    history = _load_history()
    if not history:
        return {"signal": None, "status": "no_data", "source_file": str(GAIN_RANK_FILE)}

    latest = history[-1]
    preds = latest.get("predictions", [])
    if not preds:
        return {"signal": None, "status": "no_predictions", "source_file": str(GAIN_RANK_FILE)}

    top = max(preds, key=lambda x: x.get("gain_score", 0))
    return {
        "signal": {
            "underlying": top.get("underlying", "NIFTY"),
            "score": top.get("gain_score", 0),
            "direction": "BUY" if top.get("gain_score", 0) > 0 else "SELL",
            "confidence": min(abs(top.get("gain_score", 0)) / 100, 1.0),
            "date": latest.get("date"),
        },
        "status": "ok",
        "source_file": str(GAIN_RANK_FILE),
    }
