"""
ML Model Performance Tracking System
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
import pytz

IST = pytz.timezone("Asia/Kolkata")


class MLPerformanceTracker:
    """
    Track ML model performance over time
    """

    def __init__(self, data_file: Optional[Path] = None):
        if data_file is None:
            data_file = Path(__file__).parent.parent.parent / "outputs" / "ml_performance.json"
        self.data_file = data_file
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        self._load_data()

    def _load_data(self):
        """Load performance data"""
        if self.data_file.exists():
            try:
                with open(self.data_file, "r", encoding="utf-8-sig") as f:
                    self.data = json.load(f)
                self.data.setdefault("models", {})
                self.data.setdefault("predictions", [])
                # Ensure underlyings is list (JSON may have loaded set as list)
                for name, stats in self.data["models"].items():
                    if isinstance(stats.get("underlyings"), set):
                        stats["underlyings"] = list(stats["underlyings"])
                    stats.setdefault("underlyings", [])
            except Exception:
                self.data = {"models": {}, "predictions": []}
        else:
            self.data = {"models": {}, "predictions": []}

    def _save_data(self):
        """Save performance data"""
        with open(self.data_file, "w") as f:
            json.dump(self.data, f, indent=2, default=str)

    def record_prediction(
        self,
        model_name: str,
        underlying: str,
        prediction: float,
        confidence: float,
        actual_result: Optional[float] = None,
    ):
        """Record a prediction"""
        prediction_record = {
            "model_name": model_name,
            "underlying": underlying,
            "prediction": prediction,
            "confidence": confidence,
            "actual_result": actual_result,
            "timestamp": datetime.now(IST).isoformat(),
            "accuracy": None,
        }

        if actual_result is not None:
            # Calculate accuracy
            error = abs(prediction - actual_result)
            accuracy = 1.0 - (error / abs(actual_result)) if actual_result != 0 else 1.0
            prediction_record["accuracy"] = accuracy

        self.data["predictions"].append(prediction_record)

        # Update model stats
        if model_name not in self.data["models"]:
            self.data["models"][model_name] = {
                "total_predictions": 0,
                "total_accuracy": 0.0,
                "avg_confidence": 0.0,
                "underlyings": [],
            }

        model_stats = self.data["models"][model_name]
        model_stats["total_predictions"] += 1
        underlyings_list = list(model_stats.get("underlyings", []))
        if underlying not in underlyings_list:
            underlyings_list.append(underlying)
        model_stats["underlyings"] = underlyings_list

        if prediction_record["accuracy"] is not None:
            model_stats["total_accuracy"] += prediction_record["accuracy"]

        # Update average confidence
        all_confidences = [p["confidence"] for p in self.data["predictions"] if p["model_name"] == model_name]
        model_stats["avg_confidence"] = sum(all_confidences) / len(all_confidences) if all_confidences else 0.0

        self._save_data()

    def get_model_performance(self, model_name: Optional[str] = None) -> Dict[str, Any]:
        """Get model performance metrics"""
        if model_name:
            if model_name not in self.data["models"]:
                return {"status": "ERROR", "message": f"Model {model_name} not found"}

            model_stats = self.data["models"][model_name].copy()
            predictions = [p for p in self.data["predictions"] if p["model_name"] == model_name]

            # Calculate metrics
            total = model_stats["total_predictions"]
            avg_accuracy = model_stats["total_accuracy"] / total if total > 0 else 0.0

            # Recent performance (last 100 predictions)
            recent = predictions[-100:]
            recent_with_accuracy = [p for p in recent if p["accuracy"] is not None]
            recent_accuracy = (
                sum(p["accuracy"] for p in recent_with_accuracy) / len(recent_with_accuracy)
                if recent_with_accuracy
                else 0.0
            )

            return {
                "status": "ok",
                "model_name": model_name,
                "total_predictions": total,
                "avg_accuracy": avg_accuracy,
                "recent_accuracy": recent_accuracy,
                "avg_confidence": model_stats["avg_confidence"],
                "underlyings": model_stats["underlyings"],
                "trend": (
                    "improving"
                    if recent_accuracy > avg_accuracy
                    else "declining" if recent_accuracy < avg_accuracy else "stable"
                ),
            }
        else:
            # All models
            models_summary = {}
            for name, stats in self.data["models"].items():
                total = stats["total_predictions"]
                avg_accuracy = stats["total_accuracy"] / total if total > 0 else 0.0

                models_summary[name] = {
                    "total_predictions": total,
                    "avg_accuracy": avg_accuracy,
                    "avg_confidence": stats["avg_confidence"],
                    "underlyings_count": len(stats["underlyings"]),
                }

            return {"status": "ok", "models": models_summary}

    def get_prediction_history(self, model_name: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get prediction history"""
        predictions = self.data["predictions"]

        if model_name:
            predictions = [p for p in predictions if p["model_name"] == model_name]

        return predictions[-limit:]

    def compare_models(self) -> Dict[str, Any]:
        """Compare all models. Returns consistent structure even when empty."""
        models = list(self.data.get("models", {}).keys())

        if not models:
            return {
                "status": "ok",
                "models": {},
                "best_model": None,
                "message": "No models trained yet. Run the trading system to record predictions.",
            }

        comparison = {}
        for model_name in models:
            perf = self.get_model_performance(model_name)
            if perf.get("status") == "ok":
                comparison[model_name] = {
                    "avg_accuracy": perf["avg_accuracy"],
                    "recent_accuracy": perf["recent_accuracy"],
                    "avg_confidence": perf["avg_confidence"],
                    "total_predictions": perf["total_predictions"],
                }

        # Find best model (only if at least one has predictions)
        models_with_data = {k: v for k, v in comparison.items() if (v.get("total_predictions") or 0) > 0}
        best_model = (
            max(models_with_data.items(), key=lambda x: x[1]["avg_accuracy"])
            if models_with_data
            else None
        )

        return {
            "status": "ok",
            "models": comparison,
            "best_model": {"name": best_model[0], "metrics": best_model[1]} if best_model else None,
        }


# Global instance
_ml_tracker = MLPerformanceTracker()


def get_ml_tracker() -> MLPerformanceTracker:
    """Get global ML tracker instance"""
    return _ml_tracker
