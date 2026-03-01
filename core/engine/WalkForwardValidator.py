"""
Walk-Forward Validation Engine
Implements purged, time-series cross-validation for institutional grade reliability.
Replaces simplistic train/test splits.
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from typing import Dict, Any, List

class WalkForwardValidator:
    def __init__(self, n_splits=5):
        self.n_splits = n_splits

    def validate(self, model, X, y, buffer: int = 24) -> Dict[str, Any]:
        """
        Perform walk-forward validation with a purge buffer to prevent data leakage.
        
        Args:
            model: The ML model to train/test
            X: Feature matrix
            y: Target vector
            buffer: Number of rows to drop between train and test sets (default 24 for 1h bars = 24 hours)
        """
        tscv = TimeSeriesSplit(n_splits=self.n_splits)
        
        accuracies = []
        precisions = []
        recalls = []
        
        # X and y are assumed to be time-sorted
        for train_index, test_index in tscv.split(X):
            # Apply purge buffer: remove the last 'buffer' samples from training
            if len(train_index) <= buffer:
                continue
                
            purged_train_index = train_index[:-buffer]
            
            X_train, X_test = X[purged_train_index], X[test_index]
            y_train, y_test = y[purged_train_index], y[test_index]
            
            # Check if we have at least 2 classes in training
            if len(np.unique(y_train)) < 2:
                continue
                
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            
            accuracies.append(accuracy_score(y_test, y_pred))
            precisions.append(precision_score(y_test, y_pred, average='weighted', zero_division=0))
            recalls.append(recall_score(y_test, y_pred, average='weighted', zero_division=0))

        if not accuracies:
            return {"status": "FAIL", "message": "Insufficient variance in training folds"}

        return {
            "status": "SUCCESS",
            "avg_accuracy": float(np.mean(accuracies)),
            "std_accuracy": float(np.std(accuracies)),
            "avg_precision": float(np.mean(precisions)),
            "avg_recall": float(np.mean(recalls)),
            "folds_completed": len(accuracies)
        }

    def calculate_sharpe(self, predictions, returns, risk_free_rate=0.0) -> float:
        """
        Calculate annualized Sharpe ratio of the signal strategy.
        """
        # Simple strategy: Long if predict 1, else 0 (cash)
        strategy_returns = predictions * returns
        excess_returns = strategy_returns - (risk_free_rate / 252)
        
        if len(excess_returns) < 2 or np.std(excess_returns) == 0:
            return 0.0
            
        sharpe = np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252 * 6.5) # Annualize (6.5 hours/day)
        return float(sharpe)
