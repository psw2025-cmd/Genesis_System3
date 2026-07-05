"""
Data Balancing Module for Phase 390 - SMOTE Data Balancing
===========================================================

Balances multiclass imbalanced datasets using SMOTE or fallback upsampling.
Designed for ML training dataset preparation.

Key Functions:
    - load_engineered_features(path: str) -> pd.DataFrame
    - balance_multiclass_signals(df: pd.DataFrame, label_col: str) -> Tuple[pd.DataFrame, dict]

Author: System3 AI Team
Date: 2025-12-08
"""

import logging
from typing import Any, Dict, Tuple

import numpy as np
import pandas as pd

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Try to import SMOTE, fallback if unavailable
try:
    from imblearn.over_sampling import SMOTE

    SMOTE_AVAILABLE = True
    logger.info("✓ imbalanced-learn available - SMOTE method enabled")
except ImportError:
    SMOTE_AVAILABLE = False
    logger.warning("⚠ imbalanced-learn not available - fallback upsampling will be used")


def load_engineered_features(path: str) -> pd.DataFrame:
    """
    Load engineered features from Phase 389 output.

    Args:
        path (str): Path to phase_389_engineered_features.csv

    Returns:
        pd.DataFrame: Loaded features dataframe

    Raises:
        FileNotFoundError: If CSV file not found
        ValueError: If CSV is empty or missing required columns
    """
    logger.info(f"Loading engineered features from: {path}")

    try:
        df = pd.read_csv(path)
        logger.info(f"✓ Loaded {len(df)} rows × {len(df.columns)} columns")

        # Basic validation
        if len(df) == 0:
            raise ValueError("Input CSV is empty")

        if "signal" not in df.columns:
            raise ValueError("Required column 'signal' not found in input CSV")

        logger.info(f"✓ Input validation passed (signal column present)")
        return df

    except FileNotFoundError:
        logger.error(f"✗ File not found: {path}")
        raise
    except Exception as e:
        logger.error(f"✗ Error loading CSV: {str(e)}")
        raise


def balance_multiclass_signals(df: pd.DataFrame, label_col: str = "signal") -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Balance multiclass signals using SMOTE or upsampling.

    Args:
        df (pd.DataFrame): Input dataframe with signal column
        label_col (str): Name of target column (default: "signal")

    Returns:
        Tuple[pd.DataFrame, dict]:
            - Balanced dataframe
            - Metrics dict with before/after statistics

    Raises:
        ValueError: If label column not found or no valid classes
    """

    if label_col not in df.columns:
        raise ValueError(f"Label column '{label_col}' not found in dataframe")

    logger.info(f"\n{'='*70}")
    logger.info(f"BALANCING MULTICLASS SIGNALS (column: '{label_col}')")
    logger.info(f"{'='*70}")

    # === STEP 1: Analyze input distribution ===
    input_class_counts = df[label_col].value_counts()
    input_total = len(df)

    logger.info(f"\nInput class distribution ({input_total} rows):")
    for cls, count in input_class_counts.items():
        pct = 100.0 * count / input_total
        logger.info(f"  {cls:15s}: {count:6d} ({pct:6.2f}%)")

    # === STEP 2: Filter to primary classes (BUY, SELL, HOLD) ===
    primary_classes = ["BUY", "SELL", "HOLD"]
    valid_classes = [c for c in primary_classes if c in df[label_col].unique()]

    if len(valid_classes) < 2:
        raise ValueError(f"Not enough valid classes for balancing. Found: {valid_classes}")

    logger.info(f"\nFiltering to primary classes: {valid_classes}")
    df_filtered = df[df[label_col].isin(valid_classes)].copy()
    filtered_count = len(df_filtered)
    removed_count = input_total - filtered_count

    logger.info(f"  Kept: {filtered_count} rows | Removed (non-primary): {removed_count} rows")

    # === STEP 3: Separate features from label ===
    X = df_filtered.drop(columns=[label_col])
    y = df_filtered[label_col]

    logger.info(f"\nFeature matrix: {X.shape[0]} rows × {X.shape[1]} features")

    # === STEP 4: Apply SMOTE or fallback upsampling ===
    if SMOTE_AVAILABLE:
        logger.info("\n[SMOTE METHOD]")
        df_balanced, smote_samples = _balance_with_smote(X, y, label_col)
        method = "SMOTE"
        synthetic_count = smote_samples
    else:
        logger.info("\n[FALLBACK UPSAMPLING METHOD]")
        df_balanced, synthetic_count = _balance_with_upsampling(X, y, label_col)
        method = "CLASS_UPSAMPLING"

    # === STEP 5: Log output distribution ===
    output_class_counts = df_balanced[label_col].value_counts()
    output_total = len(df_balanced)

    logger.info(f"\nOutput class distribution ({output_total} rows):")
    for cls in sorted(output_class_counts.index):
        count = output_class_counts[cls]
        pct = 100.0 * count / output_total
        logger.info(f"  {cls:15s}: {count:6d} ({pct:6.2f}%)")

    # === STEP 6: Build metrics ===
    metrics = {
        "input_rows": input_total,
        "output_rows": output_total,
        "rows_added": output_total - filtered_count,
        "rows_removed": removed_count,
        "balancing_method": method,
        "synthetic_samples_generated": synthetic_count,
        "input_class_counts": input_class_counts.to_dict(),
        "output_class_counts": output_class_counts.to_dict(),
        "balance_method_fallback": not SMOTE_AVAILABLE,
    }

    logger.info(f"\n{'='*70}")
    logger.info(f"BALANCING COMPLETE")
    logger.info(f"  Method: {method}")
    logger.info(f"  Rows added: {output_total - filtered_count}")
    logger.info(f"  Synthetic samples: {synthetic_count}")
    logger.info(f"{'='*70}\n")

    return df_balanced, metrics


def _balance_with_smote(X: pd.DataFrame, y: pd.Series, label_col: str) -> Tuple[pd.DataFrame, int]:
    """
    Apply SMOTE oversampling to balance classes.

    Args:
        X (pd.DataFrame): Feature matrix
        y (pd.Series): Target labels
        label_col (str): Name of label column (for result df)

    Returns:
        Tuple[pd.DataFrame, int]: Balanced dataframe, number of synthetic samples
    """

    # Create SMOTE instance with sampling strategy for balanced classes
    # sampling_strategy='not majority' balances minority classes toward majority
    try:
        smote = SMOTE(sampling_strategy="not majority", random_state=42, k_neighbors=5)

        logger.info("  Applying SMOTE with sampling_strategy='not majority'")

        # Apply SMOTE to features and target
        X_smote, y_smote = smote.fit_resample(X, y)

        # Calculate synthetic samples generated
        input_count = len(X)
        output_count = len(X_smote)
        synthetic_count = output_count - input_count

        logger.info(f"  SMOTE output: {output_count} rows (+{synthetic_count} synthetic)")

        # Recreate dataframe with label column
        X_smote_df = pd.DataFrame(X_smote, columns=X.columns)
        X_smote_df[label_col] = y_smote.values

        return X_smote_df, synthetic_count

    except Exception as e:
        logger.error(f"✗ SMOTE failed: {str(e)}")
        logger.info("  Falling back to upsampling...")
        return _balance_with_upsampling(X, y, label_col)


def _balance_with_upsampling(X: pd.DataFrame, y: pd.Series, label_col: str) -> Tuple[pd.DataFrame, int]:
    """
    Fallback: Simple class-based upsampling to balance classes.

    Upsamples minority classes to match majority class count.

    Args:
        X (pd.DataFrame): Feature matrix
        y (pd.Series): Target labels
        label_col (str): Name of label column

    Returns:
        Tuple[pd.DataFrame, int]: Balanced dataframe, number of synthetic samples
    """

    logger.info("  Applying simple upsampling method")

    # Combine features and target
    df_combined = X.copy()
    df_combined[label_col] = y.values

    # Find majority class size
    class_counts = df_combined[label_col].value_counts()
    max_count = class_counts.max()

    logger.info(f"  Target class size (majority): {max_count}")

    # Upsample each class to match majority
    dfs_balanced = []
    total_added = 0

    for cls in df_combined[label_col].unique():
        cls_df = df_combined[df_combined[label_col] == cls]
        cls_count = len(cls_df)

        if cls_count < max_count:
            # Need to upsample this class
            samples_needed = max_count - cls_count
            upsampled = cls_df.sample(n=max_count, replace=True, random_state=42)
            dfs_balanced.append(upsampled)
            total_added += samples_needed
            logger.info(f"    Upsampled {cls:10s}: {cls_count} → {max_count} (+{samples_needed})")
        else:
            dfs_balanced.append(cls_df)
            logger.info(f"    Kept {cls:10s}: {cls_count} (majority)")

    # Combine and shuffle
    df_balanced = pd.concat(dfs_balanced, ignore_index=True)
    df_balanced = df_balanced.sample(frac=1.0, random_state=42).reset_index(drop=True)

    logger.info(f"  Upsampling result: {len(df_balanced)} rows (+{total_added} synthetic)")

    return df_balanced, total_added
