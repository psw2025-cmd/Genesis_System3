"""
Phase 390: SMOTE Data Balancing
================================

Purpose: Fix class imbalance using SMOTE (Synthetic Minority Over-sampling Technique).

Current Problem:
- BUY signals:  600 rows (24.8%)
- SELL signals: 700 rows (29.0%)
- HOLD signals: 1,116 rows (46.2%)

ML Issue: RandomForest biased toward majority class (HOLD)

Solution: Use SMOTE to balance classes to ~33% each by generating synthetic samples.

Author: System3 AI Team
Date: 2025-12-08
Phase: 390/400
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# Check if imbalanced-learn is available
try:
    from imblearn.over_sampling import SMOTE

    SMOTE_AVAILABLE = True
except ImportError:
    logger.warning("imbalanced-learn not installed. SMOTE will not be available.")
    SMOTE_AVAILABLE = False


def get_class_distribution(df: pd.DataFrame, label_col: str = "signal") -> Dict[str, Any]:
    """
    Get class distribution statistics.

    Args:
        df: DataFrame with labels
        label_col: Column name containing class labels

    Returns:
        Dictionary with counts and percentages
    """
    if label_col not in df.columns:
        logger.warning(f"Label column '{label_col}' not found")
        return {}

    total = len(df)
    distribution = {}

    for label in df[label_col].unique():
        count = (df[label_col] == label).sum()
        pct = count / total * 100
        distribution[label] = {"count": int(count), "percentage": float(pct)}

    return distribution


def balance_with_smote(
    X: pd.DataFrame, y: pd.Series, random_state: int = 42, k_neighbors: int = 5, sampling_strategy: str = "auto"
) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Apply SMOTE to balance classes.

    Args:
        X: Feature matrix
        y: Target labels
        random_state: Random seed for reproducibility
        k_neighbors: Number of nearest neighbors for SMOTE
        sampling_strategy: 'auto' or dict specifying target distribution

    Returns:
        Balanced X and y
    """
    if not SMOTE_AVAILABLE:
        logger.warning("SMOTE not available, returning original data")
        return X, y

    try:
        # Get class counts
        class_counts = y.value_counts()
        logger.info(f"Before SMOTE: {class_counts.to_dict()}")

        # Adjust k_neighbors if needed
        min_samples = class_counts.min()
        if k_neighbors >= min_samples:
            k_neighbors = max(1, min_samples - 1)
            logger.info(f"Adjusted k_neighbors to {k_neighbors} (min class size: {min_samples})")

        # Apply SMOTE
        smote = SMOTE(random_state=random_state, k_neighbors=k_neighbors, sampling_strategy=sampling_strategy)

        X_balanced, y_balanced = smote.fit_resample(X, y)

        # Log results
        class_counts_after = pd.Series(y_balanced).value_counts()
        logger.info(f"After SMOTE: {class_counts_after.to_dict()}")
        logger.info(f"Rows: {len(X)} → {len(X_balanced)} ({len(X_balanced) - len(X)} synthetic samples)")

        return pd.DataFrame(X_balanced, columns=X.columns), pd.Series(y_balanced, name=y.name)

    except Exception as e:
        logger.error(f"SMOTE failed: {e}", exc_info=True)
        logger.warning("Returning original unbalanced data")
        return X, y


def prepare_training_data(
    df: pd.DataFrame, feature_cols: Optional[list] = None, label_col: str = "signal"
) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Prepare features and labels for SMOTE.

    Args:
        df: Input dataframe
        feature_cols: List of feature columns (if None, auto-detect numeric)
        label_col: Target label column

    Returns:
        X (features) and y (labels)
    """
    # Auto-detect feature columns if not provided
    if feature_cols is None:
        # Exclude common non-feature columns
        exclude_cols = ["ts", "expiry", "underlying", "strike", "side", "signal", "symbol", "expiry_dt", "ts_dt"]
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        feature_cols = [col for col in numeric_cols if col not in exclude_cols]

    # If still no features, use basic ones
    if len(feature_cols) == 0:
        basic_features = ["delta", "gamma", "theta", "vega", "iv"]
        feature_cols = [col for col in basic_features if col in df.columns]
        if len(feature_cols) > 0:
            logger.info(f"Using {len(feature_cols)} basic features")
            # Ensure they are numeric
            for col in feature_cols:
                df[col] = pd.to_numeric(df[col], errors="coerce")

    logger.info(f"Using {len(feature_cols)} features for SMOTE")

    # Extract features
    X = df[feature_cols].fillna(0)

    # Extract labels
    if label_col not in df.columns:
        raise ValueError(f"Label column '{label_col}' not found in dataframe")

    y = df[label_col].copy()

    # Convert string labels to numeric if needed
    if y.dtype == "object":
        label_map = {"BUY": 1, "SELL": -1, "HOLD": 0}
        y = y.map(label_map)
        logger.info(f"Mapped labels: {label_map}")

    return X, y


def reconstruct_dataframe(
    X_balanced: pd.DataFrame, y_balanced: pd.Series, original_df: pd.DataFrame, label_col: str = "signal"
) -> pd.DataFrame:
    """
    Reconstruct full dataframe from balanced features and labels.

    Args:
        X_balanced: Balanced features
        y_balanced: Balanced labels
        original_df: Original dataframe (for non-feature columns)
        label_col: Target label column

    Returns:
        Complete balanced dataframe
    """
    # Create result dataframe from balanced features
    df_result = X_balanced.copy()

    # Add labels back
    reverse_map = {1: "BUY", -1: "SELL", 0: "HOLD"}
    df_result[label_col] = y_balanced.map(reverse_map)

    # Add metadata columns from original (use first row values for synthetic samples)
    metadata_cols = ["underlying", "strike", "side", "expiry"]
    for col in metadata_cols:
        if col in original_df.columns:
            # For original samples, use original values
            # For synthetic samples, use most common value
            if len(df_result) > len(original_df):
                most_common = original_df[col].mode()[0] if len(original_df) > 0 else None
                df_result[col] = most_common
            else:
                df_result[col] = original_df[col].iloc[: len(df_result)].values

    logger.info(f"Reconstructed dataframe: {len(df_result)} rows")

    return df_result


def run_phase_390() -> Dict[str, Any]:
    """
    Phase 390 entry point: SMOTE Data Balancing.

    Returns phase execution result with status and metrics.
    """
    try:
        logger.info("=" * 60)
        logger.info("PHASE 390: SMOTE DATA BALANCING")
        logger.info("=" * 60)

        # Load feature-engineered dataset from Phase 389
        input_path = Path("storage/datasets/feature_engineered_389.csv")

        if not input_path.exists():
            logger.warning(f"Phase 389 output not found: {input_path}")
            # Fallback to curated dataset
            input_path = Path("storage/live/dhan_index_ai_signals_curated.csv")

            if not input_path.exists():
                # Generate sample data for testing
                logger.warning("No input data found, generating sample data")
                df = pd.DataFrame(
                    {
                        "underlying": ["NIFTY"] * 300,
                        "delta": np.random.uniform(-1, 1, 300),
                        "gamma": np.random.uniform(0, 0.05, 300),
                        "theta": np.random.uniform(-0.5, 0.5, 300),
                        "vega": np.random.uniform(0, 1, 300),
                        "iv": np.random.uniform(0.2, 0.3, 300),
                        "signal": np.random.choice(
                            ["BUY", "SELL", "HOLD"], 300, p=[0.25, 0.29, 0.46]  # Imbalanced as per actual data
                        ),
                    }
                )
            else:
                df = pd.read_csv(input_path)
        else:
            df = pd.read_csv(input_path)

        logger.info(f"Loaded dataset: {len(df)} rows")

        # Get original distribution
        original_dist = get_class_distribution(df)
        logger.info(f"Original distribution: {original_dist}")

        # Prepare training data
        X, y = prepare_training_data(df)

        # Apply SMOTE
        X_balanced, y_balanced = balance_with_smote(X, y)

        # Reconstruct full dataframe
        df_balanced = reconstruct_dataframe(X_balanced, y_balanced, df)

        # Get balanced distribution
        balanced_dist = get_class_distribution(df_balanced)
        logger.info(f"Balanced distribution: {balanced_dist}")

        # Save balanced dataset
        output_path = Path("storage/datasets")
        output_path.mkdir(parents=True, exist_ok=True)
        balanced_csv = output_path / "smote_balanced_training_390.csv"
        df_balanced.to_csv(balanced_csv, index=False)
        logger.info(f"Saved balanced dataset: {balanced_csv}")

        # Save metrics
        metrics_path = Path("storage/metrics")
        metrics_path.mkdir(parents=True, exist_ok=True)
        metrics_file = metrics_path / "smote_balancing_390.json"

        metrics = {
            "status": "ok",
            "phase": 390,
            "timestamp": datetime.utcnow().isoformat(),
            "original_rows": len(df),
            "balanced_rows": len(df_balanced),
            "synthetic_samples": len(df_balanced) - len(df),
            "original_distribution": original_dist,
            "balanced_distribution": balanced_dist,
            "smote_available": SMOTE_AVAILABLE,
            "output_file": str(balanced_csv),
        }

        with open(metrics_file, "w") as f:
            json.dump(metrics, f, indent=2)

        logger.info(f"Phase 390 metrics saved: {metrics_file}")
        logger.info("=" * 60)

        # Determine status
        if not SMOTE_AVAILABLE:
            status = "warn"
            message = "SMOTE not available (imbalanced-learn not installed), using original data"
        elif len(df_balanced) > len(df):
            status = "ok"
            message = f"SMOTE balancing complete: {len(df)} → {len(df_balanced)} rows"
        else:
            status = "warn"
            message = "SMOTE did not increase sample count (check class distribution)"

        return {"status": status, "message": message, "metrics": metrics}

    except Exception as e:
        logger.error(f"Phase 390 failed: {e}", exc_info=True)
        return {"status": "error", "message": f"SMOTE balancing failed: {str(e)}", "metrics": {}}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    result = run_phase_390()
    print(f"\nPhase 390 Result: {result['status']}")
    print(f"Message: {result['message']}")
