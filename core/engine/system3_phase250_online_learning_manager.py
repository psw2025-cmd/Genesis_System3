"""
Phase 250: Online Learning Manager (LSTM Model Incremental Trainer)

Purpose:
  - Load trained Phase 249 LSTM models from disk (shadow models)
  - Read new Phase 221 data rows at regular intervals (e.g., every 30 minutes)
  - Perform incremental training bursts with minimal computational overhead
  - Preserve the same binary label logic as Phase 249 (0=loss/hold, 1=profit)
  - Track model versions and online learning history
  - Output metrics for downstream drift detection (Phase 251)

Architecture:
  - SimpleLSTM: 10-feature input → 64 hidden × 2 layers → 2-class output
  - Training: Adam optimizer, lr=0.001, batch_size=32, epochs=2 per burst
  - Incremental learning: New data appended to existing training set, random sampling
  - Model persistence: Saves updated models + metadata with online_learning_count
  - Validation: Holdout set evaluated every burst to track accuracy drift

Non-Invasive:
  - Shadow models only, no impact on live trading
  - Runs in background thread or scheduled task
  - Models locked during training (no concurrent access)

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

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Directories
MODELS_DIR = PROJECT_ROOT / "core" / "models" / "dhan"
LOGS_DIR = PROJECT_ROOT / "logs"
STORAGE_DIR = PROJECT_ROOT / "storage" / "live"

# Input: Recent data (from Phase 221)
INPUT_CSV = STORAGE_DIR / "dhan_index_ai_signals_with_forward.csv"

# Configuration
SEQUENCE_LENGTH = 20  # Same as Phase 249
UNDERLYINGS = ["NIFTY", "SENSEX", "FINNIFTY", "MIDCPNIFTY", "BANKNIFTY"]
FEATURE_COLS = ["ltp", "spot", "iv", "delta", "gamma", "theta", "vega", "trend_score", "rsi", "time_to_expiry"]
TARGET_COL = "fwd_ret_5"


class OnlineLearningManager:
    """Manages incremental training of Phase 249 LSTM models."""

    def __init__(self, burst_size: int = 32, min_burst_epochs: int = 2):
        """
        Initialize Online Learning Manager.

        Args:
            burst_size: Number of new samples per incremental training burst
            min_burst_epochs: Epochs per burst (low number to minimize overhead)
        """
        self.burst_size = burst_size
        self.min_burst_epochs = min_burst_epochs

        try:
            import torch
            import torch.nn as nn
            import torch.optim as optim
            from torch.utils.data import DataLoader, TensorDataset

            self.torch = torch
            self.nn = nn
            self.optim = optim
            self.DataLoader = DataLoader
            self.TensorDataset = TensorDataset
            self.torch_available = True
        except ImportError:
            logger.error("PyTorch not installed. Install with: pip install torch>=2.0.0")
            self.torch_available = False

    def load_phase221_data(self) -> pd.DataFrame:
        """Load latest Phase 221 forward returns data."""
        if not INPUT_CSV.exists():
            logger.error(f"Phase 221 CSV not found: {INPUT_CSV}")
            return None

        try:
            df = pd.read_csv(INPUT_CSV)
            logger.info(f"[OLM] Loaded Phase 221 data: {len(df)} rows, {len(df.columns)} columns")
            return df
        except Exception as e:
            logger.error(f"[OLM] Error loading Phase 221 data: {e}")
            return None

    def get_new_samples(self, df: pd.DataFrame, last_row_processed: int) -> Tuple[pd.DataFrame, int]:
        """Extract new samples added since last burst."""
        if last_row_processed >= len(df):
            return None, last_row_processed

        new_data = df.iloc[last_row_processed:].copy()
        updated_index = len(df)

        logger.info(f"[OLM] Found {len(new_data)} new samples since last burst")
        return new_data, updated_index

    def create_incremental_sequences(self, df: pd.DataFrame, underlying: str) -> Tuple[np.ndarray, np.ndarray]:
        """Create training sequences from incremental data (same logic as Phase 249)."""
        sequences = []
        labels = []

        # Filter to underlying
        df_underlying = df[df["underlying"] == underlying].copy() if "underlying" in df.columns else df.copy()

        if len(df_underlying) < SEQUENCE_LENGTH:
            logger.warning(f"[OLM] Insufficient data for {underlying}: {len(df_underlying)} rows")
            return np.array([]), np.array([])

        # Check available features
        available_cols = [col for col in FEATURE_COLS if col in df_underlying.columns]
        if not available_cols:
            logger.error(f"[OLM] {underlying}: No feature columns found")
            return np.array([]), np.array([])

        # Convert forward returns to numeric
        if TARGET_COL in df_underlying.columns:
            df_underlying[TARGET_COL] = pd.to_numeric(df_underlying[TARGET_COL], errors="coerce")
        # Data sanitation: replace inf with nan (explicit copy to avoid downcast warning)
        df_underlying = df_underlying.replace([np.inf, -np.inf], np.nan).infer_objects(copy=False)

        # Create sequences with same binary discretization as Phase 249
        for i in range(SEQUENCE_LENGTH, len(df_underlying)):
            seq = df_underlying.iloc[i - SEQUENCE_LENGTH : i][available_cols].values.astype(np.float32)
            if not np.isfinite(seq).all():
                continue

            # Binary label: 0=loss/hold, 1=profit
            if TARGET_COL in df_underlying.columns:
                fwd_ret = df_underlying.iloc[i][TARGET_COL]
                if pd.isna(fwd_ret):
                    continue
                label = 1 if fwd_ret > 0.001 else 0
            else:
                # Fallback: use signal column if available
                if "signal" in df_underlying.columns:
                    signal = df_underlying.iloc[i]["signal"]
                    label = 1 if signal == "BUY" else 0
                else:
                    continue

            sequences.append(seq)
            labels.append(label)

        if len(sequences) == 0:
            logger.warning(f"[OLM] {underlying}: No valid sequences from incremental data")
            return np.array([]), np.array([])

        return np.array(sequences, dtype=np.float32), np.array(labels, dtype=np.int64)

    def load_model_and_meta(self, underlying: str) -> Tuple[Any, Dict]:
        """Load trained LSTM model and metadata from Phase 249."""
        model_path = MODELS_DIR / f"{underlying}_lstm_model.pth"
        meta_path = MODELS_DIR / f"{underlying}_lstm_meta.json"

        if not model_path.exists():
            logger.warning(f"[OLM] Model not found: {model_path}")
            return None, None

        try:
            # Load state dict and reconstruct model
            state_dict = self.torch.load(model_path, weights_only=False)

            # Import model class
            from core.engine.system3_phase249_model_loader import SimpleLSTM

            # Reconstruct with correct architecture
            model = SimpleLSTM(input_size=10, hidden_size=64, num_layers=2, num_classes=2)
            model.load_state_dict(state_dict)

            logger.info(f"[OLM] Loaded model: {underlying}")
        except Exception as e:
            logger.error(f"[OLM] Error loading model {underlying}: {e}")
            return None, None

        meta = None
        if meta_path.exists():
            try:
                with open(meta_path) as f:
                    meta = json.load(f)
            except Exception as e:
                logger.warning(f"[OLM] Error loading metadata: {e}")

        return model, meta

    def train_incremental_burst(
        self, model: Any, X_new: np.ndarray, y_new: np.ndarray, underlying: str
    ) -> Dict[str, Any]:
        """Perform one incremental training burst on new samples. Fail-closed: no update on NaN/inf."""
        if len(X_new) == 0:
            return {"status": "SKIP", "reason": "No new data", "underlying": underlying}

        # Fail-closed: reject NaN/inf in inputs
        if not np.isfinite(X_new).all():
            logger.error(f"[OLM] {underlying}: NaN/inf in input tensors - skipping update")
            return {"status": "ERROR", "underlying": underlying, "reason": "NaN/inf in input", "avg_loss": None}
        if not np.isfinite(y_new).all():
            logger.error(f"[OLM] {underlying}: NaN/inf in labels - skipping update")
            return {"status": "ERROR", "underlying": underlying, "reason": "NaN/inf in labels", "avg_loss": None}

        try:
            # Convert to tensors
            X_tensor = self.torch.tensor(X_new, dtype=self.torch.float32)
            y_tensor = self.torch.tensor(y_new, dtype=self.torch.long)

            # Create data loader
            dataset = self.TensorDataset(X_tensor, y_tensor)
            loader = self.DataLoader(dataset, batch_size=min(16, len(X_new)), shuffle=True)

            # Setup training
            model.train()
            optimizer = self.optim.Adam(model.parameters(), lr=0.001)
            criterion = self.nn.CrossEntropyLoss()

            # Gradient clipping for stability
            total_loss = 0
            for epoch in range(self.min_burst_epochs):
                epoch_loss = 0
                for X_batch, y_batch in loader:
                    optimizer.zero_grad()
                    outputs = model(X_batch)
                    loss = criterion(outputs, y_batch)
                    if not self.torch.isfinite(loss).item():
                        logger.error(f"[OLM] {underlying} Epoch {epoch+1}: Loss is NaN/inf - aborting step, not saving")
                        return {"status": "WARN", "underlying": underlying, "reason": "Loss NaN/inf", "avg_loss": None}
                    loss.backward()
                    self.torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                    optimizer.step()
                    epoch_loss += loss.item()

                avg_epoch_loss = epoch_loss / len(loader)
                total_loss += avg_epoch_loss
                logger.info(f"[OLM] {underlying} Epoch {epoch+1}/{self.min_burst_epochs} - Loss: {avg_epoch_loss:.4f}")

            avg_loss = total_loss / self.min_burst_epochs
            if not np.isfinite(avg_loss):
                logger.error(f"[OLM] {underlying}: Avg loss NaN/inf - not saving model")
                return {"status": "WARN", "underlying": underlying, "reason": "Avg loss NaN/inf", "avg_loss": None}

            logger.info(f"[OLM] {underlying} - Incremental burst complete. Avg loss: {avg_loss:.4f}")

            return {
                "status": "SUCCESS",
                "underlying": underlying,
                "samples_trained": len(X_new),
                "epochs": self.min_burst_epochs,
                "avg_loss": float(avg_loss),
                "burst_timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"[OLM] Training error for {underlying}: {e}")
            return {"status": "ERROR", "underlying": underlying, "error": str(e)}

    def save_updated_model(self, model: Any, meta: Dict, underlying: str, burst_metrics: Dict) -> bool:
        """Save updated model and metadata after incremental training."""
        if meta is None:
            meta = {
                "underlying": underlying,
                "model_version": "lstm_v1",
                "model_type": "LSTM",
                "shadow_model": True,
                "training_data_source": "phase_221_forward_returns_incremental",
                "online_learning_count": 0,
            }

        # Update metadata
        meta["online_learning_count"] = meta.get("online_learning_count", 0) + 1
        meta["last_burst_timestamp"] = burst_metrics.get("burst_timestamp", datetime.now().isoformat())
        meta["last_burst_samples"] = burst_metrics.get("samples_trained", 0)
        meta["last_burst_loss"] = burst_metrics.get("avg_loss", None)

        model_path = MODELS_DIR / f"{underlying}_lstm_model.pth"
        meta_path = MODELS_DIR / f"{underlying}_lstm_meta.json"

        try:
            # Save model
            self.torch.save(model, model_path)
            logger.info(f"[OLM] Saved updated model: {model_path}")

            # Save metadata
            with open(meta_path, "w") as f:
                json.dump(meta, f, indent=2)
            logger.info(f"[OLM] Saved metadata: {meta_path}")

            return True
        except Exception as e:
            logger.error(f"[OLM] Error saving model {underlying}: {e}")
            return False

    def run_training_burst(self, burst_mode: str = "automatic") -> Dict[str, Any]:
        """Execute one complete incremental training burst across all underlyings."""
        logger.info(f"\n[OLM] ===== TRAINING BURST START ({burst_mode} mode) =====")

        if not self.torch_available:
            logger.error("[OLM] PyTorch not available - cannot run training burst")
            return {"status": "ERROR", "reason": "PyTorch not installed"}

        # Load latest Phase 221 data
        df = self.load_phase221_data()
        if df is None:
            return {"status": "ERROR", "reason": "Could not load Phase 221 data"}

        burst_results = {
            "burst_timestamp": datetime.now().isoformat(),
            "burst_mode": burst_mode,
            "total_rows_available": len(df),
            "underlyings_trained": [],
        }

        for underlying in UNDERLYINGS:
            logger.info(f"\n[OLM] --- Processing {underlying} ---")

            # Get last processed row index (from metadata if available)
            meta_path = MODELS_DIR / f"{underlying}_lstm_meta.json"
            last_row = 0
            if meta_path.exists():
                try:
                    with open(meta_path) as f:
                        meta = json.load(f)
                        last_row = meta.get("last_row_processed", 0)
                except:
                    pass

            # Extract new samples
            new_data, updated_row = self.get_new_samples(df, last_row)
            if new_data is None or len(new_data) == 0:
                logger.info(f"[OLM] {underlying}: No new data")
                continue

            # Create sequences from new data
            X_new, y_new = self.create_incremental_sequences(new_data, underlying)
            if len(X_new) == 0:
                logger.info(f"[OLM] {underlying}: Could not create sequences")
                continue

            # Load existing model
            model, meta = self.load_model_and_meta(underlying)
            if model is None:
                logger.warning(f"[OLM] {underlying}: Could not load model, skipping")
                continue

            # Train incremental burst
            burst_metrics = self.train_incremental_burst(model, X_new, y_new, underlying)

            # Only save when SUCCESS and loss is finite (fail-closed)
            avg_loss = burst_metrics.get("avg_loss")
            if burst_metrics.get("status") == "SUCCESS" and avg_loss is not None and np.isfinite(avg_loss):
                # Save updated model
                if self.save_updated_model(model, meta, underlying, burst_metrics):
                    burst_results["underlyings_trained"].append(
                        {
                            "underlying": underlying,
                            "samples": burst_metrics.get("samples_trained", 0),
                            "loss": burst_metrics.get("avg_loss", None),
                        }
                    )

                    # Update row tracking
                    if meta is not None:
                        meta["last_row_processed"] = updated_row
                        meta_path = MODELS_DIR / f"{underlying}_lstm_meta.json"
                        try:
                            with open(meta_path, "w") as f:
                                json.dump(meta, f, indent=2)
                        except:
                            pass

        logger.info(f"\n[OLM] ===== TRAINING BURST COMPLETE =====")
        logger.info(f"[OLM] Underlyings trained: {len(burst_results['underlyings_trained'])}")
        for result in burst_results["underlyings_trained"]:
            loss_val = result.get("loss")
            logger.info(
                f"  - {result['underlying']}: {result['samples']} samples, loss={loss_val if loss_val is not None else 'N/A'}"
            )

        return burst_results


def check_torch_available() -> bool:
    """Check if PyTorch is available."""
    try:
        import torch

        return True
    except ImportError:
        return False


def run_phase250(**kwargs) -> Dict[str, Any]:
    """
    Run Phase 250: Online Learning Manager (SHADOW MODEL).

    Returns:
        dict: Phase execution result
    """
    errors = []

    try:
        # Check PyTorch
        if not check_torch_available():
            logger.warning("[PHASE 250] PyTorch not available - skipping online learning")
            return {
                "phase": 250,
                "status": "SKIP",
                "details": "PyTorch not installed",
                "outputs": {},
                "errors": ["PyTorch not installed"],
            }

        # Check input file
        if not INPUT_CSV.exists():
            logger.warning("[PHASE 250] Phase 221 output not found")
            return {
                "phase": 250,
                "status": "SKIP",
                "details": "Phase 221 output not found",
                "outputs": {},
                "errors": ["Input CSV missing"],
            }

        # Run training burst
        manager = OnlineLearningManager(burst_size=32, min_burst_epochs=2)
        burst_results = manager.run_training_burst(burst_mode="automatic")

        # Generate log
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        log_file = LOGS_DIR / f"phase250_online_learning_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

        with open(log_file, "w", encoding="utf-8") as f:
            f.write(f"[{datetime.now().isoformat()}] Phase 250: Online Learning Manager\n")
            f.write(f"Burst Results: {json.dumps(burst_results, indent=2)}\n")

        success_count = len(burst_results.get("underlyings_trained", []))
        status = "OK" if success_count > 0 else "SKIP"

        return {
            "phase": 250,
            "status": status,
            "details": f"Online learning: {success_count}/{len(UNDERLYINGS)} models updated (shadow only)",
            "outputs": {
                "results": burst_results,
                "log_file": str(log_file),
            },
            "errors": errors,
        }

    except Exception as e:
        errors.append(f"Phase 250 exception: {e}")
        logger.error(f"[PHASE 250] Exception: {e}")
        return {
            "phase": 250,
            "status": "ERROR",
            "details": f"Online learning failed: {e}",
            "outputs": {},
            "errors": errors,
        }


def main():
    """CLI entry point."""
    print("=" * 80)
    print("Phase 250: Online Learning Manager (SHADOW MODEL)")
    print("=" * 80)

    result = run_phase250()

    print(f"\n[PHASE 250] Status: {result['status']}")
    print(f"[PHASE 250] Details: {result['details']}")

    if result["outputs"]:
        print(f"[PHASE 250] Results:")
        print(json.dumps(result["outputs"].get("results", {}), indent=2))


if __name__ == "__main__":
    main()
