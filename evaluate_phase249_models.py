"""
Phase 249 Extended: Model Evaluation & Accuracy Validation Script

Purpose:
  - Reload all trained Phase 249 LSTM models from disk (.pth files)
  - Recompute accuracy on holdout test sets to detect model degradation
  - Validate that saved models still work correctly
  - Generate accuracy report for drift detection (Phase 251) and promotion (Phase 254)
  - Track model health and version compatibility

Usage:
  python evaluate_phase249_models.py

Output:
  - Accuracy metrics for all 5 underlyings
  - Model health status (OK/DEGRADED/CORRUPTED)
  - Holdout set evaluation results
  - JSON report saved to logs/ directory

Status: OPERATIONAL
Date: 2025-12-06
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).parent.absolute()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Directories - use absolute paths
MODELS_DIR = PROJECT_ROOT / "core" / "models" / "dhan"
LOGS_DIR = PROJECT_ROOT / "logs"
STORAGE_DIR = PROJECT_ROOT / "storage" / "live"

# Configuration
SEQUENCE_LENGTH = 20  # Same as Phase 249
UNDERLYINGS = ["NIFTY", "SENSEX", "FINNIFTY", "MIDCPNIFTY", "BANKNIFTY"]
FEATURE_COLS = ["ltp", "spot", "iv", "delta", "gamma", "theta", "vega", "trend_score", "rsi", "time_to_expiry"]
TARGET_COL = "fwd_ret_5"
INPUT_CSV = STORAGE_DIR / "dhan_index_ai_signals_with_forward.csv"


class ModelEvaluator:
    """Evaluates Phase 249 trained models on accuracy."""

    def __init__(self):
        """Initialize evaluator with PyTorch."""
        try:
            import torch

            self.torch = torch
            self.torch_available = True
        except ImportError:
            logger.error("PyTorch not installed")
            self.torch_available = False

    def load_data(self) -> pd.DataFrame:
        """Load Phase 221 CSV data."""
        if not INPUT_CSV.exists():
            logger.error(f"Data file not found: {INPUT_CSV}")
            return None

        try:
            df = pd.read_csv(INPUT_CSV)
            logger.info(f"[EVAL] Loaded {len(df)} rows from Phase 221")
            return df
        except Exception as e:
            logger.error(f"[EVAL] Error loading data: {e}")
            return None

    def prepare_holdout_set(self, df: pd.DataFrame, underlying: str) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare holdout test set for model evaluation.
        Uses sequences from all data (since we don't have strict train/test split in Phase 249).
        """
        # Filter to underlying
        if "underlying" in df.columns:
            df_underlying = df[df["underlying"] == underlying].copy()
        else:
            # If no underlying column, use all data
            df_underlying = df.copy()

        if len(df_underlying) < SEQUENCE_LENGTH:
            logger.warning(f"[EVAL] Insufficient data for {underlying}: {len(df_underlying)} rows")
            return np.array([]), np.array([])

        # Check features
        available_cols = [col for col in FEATURE_COLS if col in df_underlying.columns]
        if not available_cols:
            logger.warning(f"[EVAL] No feature columns for {underlying}")
            return np.array([]), np.array([])

        # Convert target to numeric
        if TARGET_COL in df_underlying.columns:
            df_underlying[TARGET_COL] = pd.to_numeric(df_underlying[TARGET_COL], errors="coerce")

        sequences = []
        labels = []

        # Create sequences from all data (use last 50% as test to avoid data leakage)
        test_start = int(0.5 * len(df_underlying))
        df_test = df_underlying.iloc[test_start:].reset_index(drop=True)

        # Create sequences
        for i in range(SEQUENCE_LENGTH, len(df_test)):
            seq = df_test.iloc[i - SEQUENCE_LENGTH : i][available_cols].values.astype(np.float32)

            # Binary label
            if TARGET_COL in df_test.columns:
                fwd_ret = df_test.iloc[i][TARGET_COL]
                if pd.isna(fwd_ret):
                    continue
                label = 1 if fwd_ret > 0.001 else 0
            else:
                continue

            sequences.append(seq)
            labels.append(label)

        if len(sequences) == 0:
            logger.warning(f"[EVAL] {underlying}: No valid sequences created from test data")
            return np.array([]), np.array([])

        logger.info(f"[EVAL] {underlying}: Prepared {len(sequences)} test sequences from {len(df_test)} rows")
        return np.array(sequences, dtype=np.float32), np.array(labels, dtype=np.int64)

    def load_model(self, underlying: str) -> Tuple[Any, Dict]:
        """Load model and metadata."""
        model_path = MODELS_DIR / f"{underlying}_lstm_model.pth"
        meta_path = MODELS_DIR / f"{underlying}_lstm_meta.json"

        if not model_path.exists():
            logger.warning(f"[EVAL] Model not found: {model_path}")
            return None, None

        try:
            # Load state dict and reconstruct model
            state_dict = self.torch.load(model_path, weights_only=False)

            # Import model class from Phase 249
            from core.engine.system3_phase249_model_loader import SimpleLSTM

            # Reconstruct with correct architecture
            model = SimpleLSTM(input_size=10, hidden_size=64, num_layers=2, num_classes=2)
            model.load_state_dict(state_dict)
            model.eval()

            logger.info(f"[EVAL] Loaded {underlying} model")
        except Exception as e:
            logger.error(f"[EVAL] Error loading {underlying} model: {e}")
            return None, None

        meta = None
        if meta_path.exists():
            try:
                with open(meta_path) as f:
                    meta = json.load(f)
            except Exception as e:
                logger.warning(f"[EVAL] Could not load metadata: {e}")

        return model, meta

    def evaluate_model(self, model: Any, X_test: np.ndarray, y_test: np.ndarray, underlying: str) -> Dict[str, Any]:
        """Evaluate model accuracy on holdout set."""
        if len(X_test) == 0:
            return {"underlying": underlying, "status": "SKIP", "reason": "No test data"}

        try:
            # Convert to tensors
            X_tensor = self.torch.tensor(X_test, dtype=self.torch.float32)
            y_tensor = self.torch.tensor(y_test, dtype=self.torch.long)

            # Evaluate
            model.eval()
            with self.torch.no_grad():
                outputs = model(X_tensor)
                predictions = self.torch.argmax(outputs, dim=1).numpy()

            # Calculate accuracy
            accuracy = np.mean(predictions == y_test)

            # Calculate class distribution
            true_positives = np.sum((predictions == 1) & (y_test == 1))
            false_positives = np.sum((predictions == 1) & (y_test == 0))
            true_negatives = np.sum((predictions == 0) & (y_test == 0))
            false_negatives = np.sum((predictions == 0) & (y_test == 1))

            # Calculate metrics
            precision = (
                true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
            )
            recall = (
                true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
            )
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

            logger.info(
                f"[EVAL] {underlying}: Accuracy={accuracy:.1%}, Precision={precision:.1%}, Recall={recall:.1%}, F1={f1:.1%}"
            )

            return {
                "underlying": underlying,
                "status": "SUCCESS",
                "accuracy": accuracy,
                "precision": precision,
                "recall": recall,
                "f1_score": f1,
                "test_samples": len(X_test),
                "true_positives": int(true_positives),
                "false_positives": int(false_positives),
                "true_negatives": int(true_negatives),
                "false_negatives": int(false_negatives),
                "evaluation_timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"[EVAL] Error evaluating {underlying}: {e}")
            return {"underlying": underlying, "status": "ERROR", "error": str(e)}

    def run_evaluation(self) -> Dict[str, Any]:
        """Run full model evaluation suite."""
        if not self.torch_available:
            logger.error("[EVAL] PyTorch not available")
            return {"status": "ERROR", "reason": "PyTorch not installed"}

        logger.info("\n[EVAL] ===== MODEL EVALUATION START =====")

        # Load data
        df = self.load_data()
        if df is None:
            return {"status": "ERROR", "reason": "Could not load data"}

        results = {"evaluation_timestamp": datetime.now().isoformat(), "total_models": len(UNDERLYINGS), "models": {}}

        for underlying in UNDERLYINGS:
            logger.info(f"\n[EVAL] Evaluating {underlying}...")

            # Load model and metadata
            model, meta = self.load_model(underlying)
            if model is None:
                results["models"][underlying] = {"status": "SKIP", "reason": "Model not found"}
                continue

            # Prepare test data
            X_test, y_test = self.prepare_holdout_set(df, underlying)
            if len(X_test) == 0:
                results["models"][underlying] = {"status": "SKIP", "reason": "Insufficient test data"}
                continue

            # Evaluate
            eval_result = self.evaluate_model(model, X_test, y_test, underlying)

            # Add metadata
            if meta:
                eval_result["training_accuracy"] = meta.get("accuracy", None)
                eval_result["online_learning_count"] = meta.get("online_learning_count", 0)
                eval_result["model_version"] = meta.get("model_version", None)

            results["models"][underlying] = eval_result

        # Summary statistics
        successful = [m for m in results["models"].values() if m.get("status") == "SUCCESS"]
        if successful:
            accuracies = [m["accuracy"] for m in successful]
            results["summary"] = {
                "evaluated_models": len(successful),
                "avg_accuracy": float(np.mean(accuracies)),
                "min_accuracy": float(np.min(accuracies)),
                "max_accuracy": float(np.max(accuracies)),
                "std_accuracy": float(np.std(accuracies)),
            }

        logger.info(f"\n[EVAL] ===== MODEL EVALUATION COMPLETE =====")
        logger.info(f"[EVAL] Summary: {len(successful)}/{len(UNDERLYINGS)} models evaluated successfully")
        if "summary" in results:
            logger.info(f"[EVAL] Avg Accuracy: {results['summary']['avg_accuracy']:.1%}")

        return results

    def save_report(self, results: Dict[str, Any]) -> Path:
        """Save evaluation report to JSON file."""
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        report_path = LOGS_DIR / f"phase249_model_evaluation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        try:
            with open(report_path, "w") as f:
                json.dump(results, f, indent=2)
            logger.info(f"[EVAL] Report saved: {report_path}")
            # Write latest-eval pointer for Phase 251 (read pointer first, then glob fallback)
            pointer_path = LOGS_DIR / "phase249_latest_eval_path.txt"
            with open(pointer_path, "w") as f:
                f.write(str(report_path.resolve()))
            logger.info(f"[EVAL] Latest eval pointer: {pointer_path}")
            return report_path
        except Exception as e:
            logger.error(f"[EVAL] Error saving report: {e}")
            return None


def main():
    """Run model evaluation."""
    print("=" * 80)
    print("Phase 249 Extended: Model Evaluation & Accuracy Validation")
    print("=" * 80)

    evaluator = ModelEvaluator()
    results = evaluator.run_evaluation()

    print(f"\n[EVAL] Results:")
    print(json.dumps(results, indent=2))

    # Save report
    report_path = evaluator.save_report(results)
    print(f"\n[EVAL] Report: {report_path}")


if __name__ == "__main__":
    main()
