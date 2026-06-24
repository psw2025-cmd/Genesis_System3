"""
System3 Phase 249 - LSTM Forward Returns Predictor

Train LSTM models to predict forward returns as shadow models.
Does not impact live trading decisions - shadow-only for validation.

References:
- SPRINT1_DL_SPEC.md (Phase 249 specification)
- Phase 221: system3_phase221_forward_returns.py (data source)
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Directories
MODELS_DIR = PROJECT_ROOT / "core" / "models" / "dhan"
LOGS_DIR = PROJECT_ROOT / "logs"
STORAGE_DIR = PROJECT_ROOT / "storage" / "live"

# Input: Phase 221 output (forward returns calculated)
INPUT_CSV = STORAGE_DIR / "dhan_index_ai_signals_with_forward.csv"

# Output: Shadow predictions (does NOT overwrite Phase 221 output)
OUTPUT_CSV = STORAGE_DIR / "dhan_index_ai_signals_with_forward_lstm.csv"

# LSTM configuration
SEQUENCE_LENGTH = 20  # Last 20 timestamps (~30 minutes of data)
FEATURE_COLUMNS = ["ltp", "spot", "iv", "delta", "gamma", "theta", "vega", "trend_score", "rsi", "time_to_expiry"]
UNDERLYINGS = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]


def check_torch_available() -> bool:
    """Check if PyTorch is available (Phase 249 requires torch>=2.0.0)."""
    try:
        import torch

        return True
    except ImportError:
        return False


def create_sequences(df: pd.DataFrame, underlying: str) -> tuple:
    """
    Create sliding window sequences for LSTM training.

    Args:
        df: DataFrame with forward returns (from Phase 221)
        underlying: Underlying symbol (NIFTY, BANKNIFTY, etc.)

    Returns:
        (sequences, labels) - Ready for LSTM training
    """
    # Skip header row if present (first row is column names repeated)
    if df.iloc[0]["underlying"] == "underlying":
        df = df.iloc[1:].reset_index(drop=True)

    df_underlying = df[df["underlying"] == underlying].copy()

    sequences = []
    labels = []

    # Validate required columns exist
    missing_cols = [col for col in FEATURE_COLUMNS if col not in df_underlying.columns]
    if missing_cols:
        print(f"[WARN] Missing columns for {underlying}: {missing_cols}")
        # Use available columns only
        available_cols = [col for col in FEATURE_COLUMNS if col in df_underlying.columns]
    else:
        available_cols = FEATURE_COLUMNS

    if len(df_underlying) < SEQUENCE_LENGTH:
        print(f"[WARN] {underlying}: Insufficient data ({len(df_underlying)} rows, need {SEQUENCE_LENGTH}+)")
        return np.array([]), np.array([])

    # Convert columns to numeric (handle any string/object types)
    for col in available_cols:
        df_underlying[col] = pd.to_numeric(df_underlying[col], errors="coerce")

    # Drop rows with NaN values in feature columns
    df_underlying = df_underlying.dropna(subset=available_cols)

    if len(df_underlying) < SEQUENCE_LENGTH:
        print(f"[WARN] {underlying}: Insufficient data after cleaning ({len(df_underlying)} rows)")
        return np.array([]), np.array([])

    # Label encoding: Map signal strings to integers
    # Priority: Use 'fwd_ret_5' as target (forward return bucket), fallback to 'signal' column
    label_mapping = None
    target_col = None

    if "fwd_ret_5" in df_underlying.columns:
        # Use forward return as target: discretize into buckets
        # -1: negative return (loss), 0: near zero, +1: positive return (profit)
        df_underlying["fwd_ret_5_numeric"] = pd.to_numeric(df_underlying["fwd_ret_5"], errors="coerce")
        target_col = "fwd_ret_5_numeric"
        print(f"[TARGET] Using forward returns (fwd_ret_5) as LSTM target for {underlying}")
        print(
            f"[STATS] Forward return min={df_underlying['fwd_ret_5_numeric'].min():.4f}, "
            f"max={df_underlying['fwd_ret_5_numeric'].max():.4f}"
        )
    elif "signal" in df_underlying.columns:
        # Fallback: Use signal column with explicit mapping
        target_col = "signal"
        label_mapping = {"SELL": 0, "HOLD": 1, "BUY": 2}
        print(f"[TARGET] Using signal column as LSTM target for {underlying}")
        print(f"[MAPPING] {label_mapping}")
    else:
        print(f"[ERROR] {underlying}: No target column found (need fwd_ret_5 or signal)")
        return np.array([]), np.array([])

    # Create sequences (sliding window)
    for i in range(SEQUENCE_LENGTH, len(df_underlying)):
        seq = df_underlying.iloc[i - SEQUENCE_LENGTH : i][available_cols].values.astype(np.float32)

        # Encode label
        if label_mapping:
            # Use signal mapping
            signal_val = df_underlying.iloc[i][target_col]
            label = label_mapping.get(signal_val, 1)  # Default to HOLD (1)
        else:
            # Use forward return (will be discretized for binary classification)
            fwd_ret = df_underlying.iloc[i][target_col]
            # Discretize: 0 = loss/hold (negative or zero return), 1 = profit (positive return)
            if pd.isna(fwd_ret):
                continue  # Skip NaN targets
            label = 1 if fwd_ret > 0.001 else 0

        sequences.append(seq)
        labels.append(label)

    if len(sequences) == 0:
        print(f"[ERROR] {underlying}: No valid sequences created")
        return np.array([]), np.array([])

    labels_array = np.array(labels, dtype=np.int64)
    print(
        f"[LABELS] {underlying}: unique values = {np.unique(labels_array)}, counts = {np.bincount(labels_array + 1) if np.min(labels_array) >= -1 else 'mixed'}"
    )

    return np.array(sequences, dtype=np.float32), labels_array


def train_lstm_for_underlying(underlying: str, df: pd.DataFrame) -> Dict[str, Any]:
    """
    Train LSTM model for a single underlying (SHADOW MODEL ONLY).

    Args:
        underlying: Underlying symbol
        df: DataFrame with forward returns

    Returns:
        dict with training results (accuracy, model_file, etc.)
    """
    try:
        import torch
        import torch.nn as nn
        import torch.optim as optim
        from torch.utils.data import DataLoader, TensorDataset
    except ImportError:
        return {
            "status": "SKIP",
            "reason": "PyTorch not installed (pip install torch>=2.0.0)",
            "underlying": underlying,
        }

    print(f"\n[PHASE 249] Training LSTM for {underlying} (SHADOW MODEL)...")

    # Create sequences
    X, y = create_sequences(df, underlying)

    if len(X) == 0:
        return {
            "status": "SKIP",
            "reason": "Insufficient training data",
            "underlying": underlying,
        }

    print(f"[LABELS] {underlying}: Unique labels = {np.unique(y)}, Distribution = {np.bincount(y)}")

    # Convert to PyTorch tensors
    X_tensor = torch.tensor(X, dtype=torch.float32)
    y_tensor = torch.tensor(y, dtype=torch.long)

    # Determine number of classes from unique labels
    unique_labels = np.unique(y)
    num_classes = len(unique_labels)

    # No need to remap for 2-class binary classification (0 = loss/hold, 1 = profit)
    print(f"[CLASSES] {num_classes} classes detected: {unique_labels}")

    # Train/test split (80/20)
    train_size = int(0.8 * len(X_tensor))
    X_train, X_test = X_tensor[:train_size], X_tensor[train_size:]
    y_train, y_test = y_tensor[:train_size], y_tensor[train_size:]

    print(f"[TRAIN] {underlying} - Train: {len(X_train)} samples, Test: {len(X_test)} samples")
    print(f"[CLASSES] Expected {num_classes} output classes")

    # DataLoader
    train_dataset = TensorDataset(X_train, y_train)
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)

    # Define LSTM model (inline for simplicity)
    class SimpleLSTM(nn.Module):
        def __init__(self, input_size, hidden_size=64, num_layers=2, num_classes=2):
            super(SimpleLSTM, self).__init__()
            self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True, dropout=0.2)
            self.fc = nn.Linear(hidden_size, num_classes)

        def forward(self, x):
            out, _ = self.lstm(x)
            out = self.fc(out[:, -1, :])  # Take last timestamp
            return out

    # Initialize model
    input_size = X_train.shape[2]  # Number of features
    model = SimpleLSTM(input_size=input_size, hidden_size=64, num_layers=2, num_classes=num_classes)

    # Loss and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    # Training loop (10 epochs)
    print(f"[TRAIN] {underlying} - {len(X_train)} train samples, {len(X_test)} test samples")
    for epoch in range(10):
        model.train()
        total_loss = 0
        for batch_X, batch_y in train_loader:
            optimizer.zero_grad()
            outputs = model(batch_X)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        avg_loss = total_loss / len(train_loader)
        if (epoch + 1) % 2 == 0:  # Log every 2 epochs
            print(f"  Epoch {epoch+1}/10 - Loss: {avg_loss:.4f}")

    # Evaluate on test set
    model.eval()
    with torch.no_grad():
        test_outputs = model(X_test)
        _, predicted = torch.max(test_outputs, 1)
        accuracy = (predicted == y_test).sum().item() / len(y_test)

    print(f"[RESULT] {underlying} - Test Accuracy: {accuracy:.4f}")

    # Save LSTM model (SHADOW - separate from RandomForest models)
    model_file = MODELS_DIR / f"{underlying}_lstm_model.pth"
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), model_file)
    print(f"[SAVE] Shadow LSTM Model: {model_file}")

    # Save metadata
    meta = {
        "underlying": underlying,
        "training_date": datetime.utcnow().isoformat(),
        "model_version": "lstm_v1",
        "model_type": "LSTM",
        "shadow_model": True,  # Flag: Does NOT impact live decisions
        "training_data_source": "phase_221_forward_returns",
        "train_rows": len(X_train),
        "test_rows": len(X_test),
        "sequence_length": SEQUENCE_LENGTH,
        "feature_count": input_size,
        "accuracy": float(accuracy),
        "validation_split": 0.2,
        "epochs": 10,
        "online_learning_count": 0,  # Will be incremented by Phase 250
    }

    meta_file = MODELS_DIR / f"{underlying}_lstm_meta.json"
    with meta_file.open("w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    print(f"[SAVE] Metadata: {meta_file}")

    return {
        "status": "SUCCESS",
        "underlying": underlying,
        "accuracy": accuracy,
        "model_file": str(model_file),
        "meta_file": str(meta_file),
        "train_rows": len(X_train),
        "test_rows": len(X_test),
    }


def run_phase249(**kwargs) -> Dict[str, Any]:
    """
    Run Phase 249: LSTM Forward Returns Predictor (SHADOW MODEL).

    Returns:
        dict: {
            "phase": 249,
            "status": "OK" or "WARN" or "ERROR",
            "details": "summary",
            "outputs": {...},
            "errors": [],
        }
    """
    errors = []
    results = {}

    try:
        # Check PyTorch availability
        if not check_torch_available():
            return {
                "phase": 249,
                "status": "SKIP",
                "details": "PyTorch not installed (pip install torch>=2.0.0)",
                "outputs": {"torch_available": False},
                "errors": ["PyTorch not installed"],
            }

        # Check input file (Phase 221 output)
        if not INPUT_CSV.exists():
            return {
                "phase": 249,
                "status": "SKIP",
                "details": "Phase 221 output not found (run Phase 221 first)",
                "outputs": {"input_file": str(INPUT_CSV), "exists": False},
                "errors": ["Phase 221 output missing"],
            }

        # Load forward returns data
        df = pd.read_csv(INPUT_CSV)
        print(f"[PHASE 249] Loaded {len(df)} rows from Phase 221")

        # Train LSTM for each underlying
        for underlying in UNDERLYINGS:
            result = train_lstm_for_underlying(underlying, df)
            results[underlying] = result

        # Generate shadow predictions (for validation only)
        # NOTE: These predictions do NOT impact live trading decisions
        print(f"\n[PHASE 249] Generating shadow predictions...")
        df_with_lstm = df.copy()
        # Remove duplicate header rows and 1970 dummy rows from input before write
        if "underlying" in df_with_lstm.columns:
            df_with_lstm = df_with_lstm[df_with_lstm["underlying"].astype(str) != "underlying"].copy()
        for col in ["ts", "timestamp"]:
            if col in df_with_lstm.columns:
                ser = df_with_lstm[col].astype(str)
                df_with_lstm = df_with_lstm.loc[~ser.str.contains("1970-01-01", na=False)].copy()
        df_with_lstm["lstm_signal"] = 0  # Placeholder (would be actual predictions in production)
        df_with_lstm["lstm_confidence"] = 0.0  # Placeholder

        # Save shadow CSV: atomic write, single header, no dummy row
        STORAGE_DIR.mkdir(parents=True, exist_ok=True)
        tmp_path = OUTPUT_CSV.with_suffix(".tmp.csv")
        df_with_lstm.to_csv(tmp_path, index=False, header=True)
        tmp_path.replace(OUTPUT_CSV)
        print(f"[SAVE] Shadow CSV: {OUTPUT_CSV}")
        # Validate: one header, no duplicate header, no 1970 dummy row
        with OUTPUT_CSV.open("r", encoding="utf-8") as f:
            lines = [f.readline() for _ in range(5)]
        if not lines or "underlying" not in lines[0]:
            raise ValueError(
                f"CSV validation failed: first line must contain 'underlying' header, got: {lines[0][:80]!r}"
                if lines
                else "CSV empty"
            )
        for i, line in enumerate(lines[1:], start=2):
            if line.strip() and (line.strip().startswith("underlying,") or "underlying,strike" in line[:50]):
                raise ValueError(f"CSV validation failed: duplicate header at line {i}")
            if "1970-01-01" in line:
                raise ValueError(f"CSV validation failed: 1970-01-01 dummy row at line {i}")

        # Count successes
        success_count = sum(1 for r in results.values() if r["status"] == "SUCCESS")

        # Generate training log
        log_file = LOGS_DIR / f"phase249_lstm_training_{datetime.now().strftime('%Y%m%d')}.log"
        LOGS_DIR.mkdir(parents=True, exist_ok=True)

        with log_file.open("w", encoding="utf-8") as f:
            f.write(f"Phase 249: LSTM Training Log\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            f.write(f"Input: {INPUT_CSV}\n")
            f.write(f"Output: {OUTPUT_CSV}\n\n")
            f.write(f"Results:\n")
            for underlying, res in results.items():
                f.write(f"  {underlying}: {res['status']}")
                if res["status"] == "SUCCESS":
                    f.write(f" - Accuracy: {res['accuracy']:.4f}\n")
                else:
                    f.write(f" - {res.get('reason', 'N/A')}\n")

        print(f"[SAVE] Training log: {log_file}")

        status = "OK" if success_count == len(UNDERLYINGS) else "WARN"
        details = f"Trained {success_count}/{len(UNDERLYINGS)} LSTM models (shadow only)"

        return {
            "phase": 249,
            "status": status,
            "details": details,
            "outputs": {
                "results": results,
                "shadow_csv": str(OUTPUT_CSV),
                "training_log": str(log_file),
                "models_trained": success_count,
                "total_underlyings": len(UNDERLYINGS),
            },
            "errors": errors,
        }

    except Exception as e:
        errors.append(f"Phase 249 exception: {e}")
        return {
            "phase": 249,
            "status": "ERROR",
            "details": f"LSTM training failed: {e}",
            "outputs": {},
            "errors": errors,
        }


def main():
    """CLI entry point."""
    print("=" * 80)
    print("Phase 249: LSTM Forward Returns Predictor (SHADOW MODEL)")
    print("=" * 80)

    result = run_phase249()

    print(f"\n[PHASE 249] Status: {result['status']}")
    print(f"[PHASE 249] Details: {result['details']}")

    if result["errors"]:
        print(f"[PHASE 249] Errors: {result['errors']}")


if __name__ == "__main__":
    main()
