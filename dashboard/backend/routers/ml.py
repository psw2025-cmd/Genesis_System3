"""
ML router — predictions, accuracy, signals.
Heavy imports (pandas, joblib) loaded ONLY when endpoint is called.
Saves ~75MB RAM at startup.
"""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from fastapi import APIRouter

router = APIRouter(tags=["ml"])

ROOT = Path(__file__).resolve().parents[2]
GAIN_RANK_FILE  = ROOT / "state" / "gain_rank_history.json"
VAL_DIR         = ROOT / "state" / "market_validations"


def _load_history() -> List[Dict]:
    if not GAIN_RANK_FILE.exists():
        return []
    try:
        return json.loads(GAIN_RANK_FILE.read_text())
    except Exception:
        return []


@router.get("/api/gain_rank")
async def get_gain_rank(refresh: bool = False):
    """Latest gain rank predictions — file-based, no ML compute in web process."""
    history = _load_history()
    if not history:
        return {"status": "no_data", "latest": None, "history": [], "stale": True}

    today = datetime.now(tz=__import__("pytz").timezone("Asia/Kolkata")).strftime("%Y-%m-%d")
    today_entry = next((e for e in reversed(history) if e.get("date") == today), None)
    latest = today_entry or history[-1]
    stale = latest.get("date") != today

    return {
        "status": "ok",
        "latest": latest,
        "history": history[-14:],
        "is_today": not stale,
        "stale": stale,
        "note": "Rankings computed by worker at 09:15 IST — no inline ML in web process",
    }


@router.get("/api/accuracy_trend")
async def get_accuracy_trend():
    """Spearman ρ history from validation files."""
    trend = []
    if VAL_DIR.exists():
        for f in sorted(VAL_DIR.glob("market_validation_*.json")):
            try:
                v = json.loads(f.read_text())
                rho = v.get("spearman_correlation")
                if rho is not None:
                    trend.append({
                        "date": f.stem.replace("market_validation_", ""),
                        "rho": rho,
                        "n_predictions": len(v.get("predictions", [])),
                    })
            except Exception:
                continue
    avg_rho = sum(t["rho"] for t in trend) / len(trend) if trend else 0
    return {
        "trend": trend,
        "days": len(trend),
        "avg_rho": round(avg_rho, 4),
        "target_rho": 0.70,
        "ready_for_live": avg_rho >= 0.70 and len(trend) >= 10,
    }


@router.get("/api/ml/performance")
async def get_ml_performance():
    """ML model comparison — no model loading, reads pre-computed results."""
    history = _load_history()
    if not history:
        return {"models": [], "message": "No model comparison data available"}

    return {
        "models": [],
        "validation_days": len(list(VAL_DIR.glob("*.json"))) if VAL_DIR.exists() else 0,
        "message": "Models will appear here once training data is available",
    }


@router.get("/api/ml/compare")
async def get_ml_compare():
    """Compare ML model versions."""
    return {"comparisons": [], "message": "Model comparison requires training data"}


@router.get("/api/signal/top")
async def get_top_signal():
    """Top signal from latest gain_rank."""
    history = _load_history()
    if not history:
        return {"signal": None, "status": "no_data"}

    latest = history[-1]
    preds = latest.get("predictions", [])
    if not preds:
        return {"signal": None, "status": "no_predictions"}

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
    }
