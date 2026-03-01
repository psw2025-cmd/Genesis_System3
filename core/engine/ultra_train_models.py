"""
WORLD-CLASS ULTRA TRAINER (v4.2) - BUGFIXED
1. Fixed UnboundLocalError for 'y'
2. Automated Class Weighting
3. Strict Stationary Feature Enforcement
"""
import os
import sys
import json
import pandas as pd
import numpy as np
import xgboost as xgb
import joblib
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.engine.HistoricalDataDownloader import SYMBOLS
from core.engine.WorldClassFeatureEngine import WorldClassFeatureEngine
from core.engine.WalkForwardValidator import WalkForwardValidator

MODELS_DIR = PROJECT_ROOT / "core" / "models" / "angel_one_ultra"
DATA_DIR = PROJECT_ROOT / "storage" / "data" / "historical"
REPORTS_DIR = PROJECT_ROOT / "storage" / "reports"
MODELS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

def train_world_class_models(symbols: Optional[List[str]] = None, oot_mode: bool = False):
    mode_str = "OUT-OF-TIME (OOT)" if oot_mode else "WALK-FORWARD (PURGED)"
    print("=" * 80)
    print(f"💎 GENESIS SYSTEM3: WORLD-CLASS MODEL TRAINING (ULTRA V4.2)")
    print(f"MODE: {mode_str}")
    print("=" * 80)
    
    target_symbols = symbols if symbols else list(SYMBOLS.keys())
    engine = WorldClassFeatureEngine()
    validator = WalkForwardValidator(n_splits=5)
    results = {}
    
    for sym in target_symbols:
        file_path = DATA_DIR / f"{sym}_historical.csv"
        if not file_path.exists(): continue
            
        print(f"\n[PROCESS] {sym} | Training...")
        try:
            df_raw = pd.read_csv(file_path, index_col=0, parse_dates=True, date_format='%Y-%m-%d %H:%M:%S')
            df = engine.engineer_features(df_raw, sym)
            
            # 1. Define Features (Stationary only)
            exclude = [c for c in df.columns if 'target' in c or 'label' in c]
            absolute_levels = ['Open', 'High', 'Low', 'Close', 'Volume']
            feature_cols = [c for c in df.columns if c not in exclude and c not in absolute_levels]
            
            # 2. Split Data
            if oot_mode:
                train_df = df[df.index <= "2025-12-31"]
                test_df = df[df.index >= "2026-01-01"]
                if train_df.empty or test_df.empty: continue
                
                X_train, y_train = train_df[feature_cols].values, train_df['label_buy'].values
                X_test, y_test = test_df[feature_cols].values, test_df['label_buy'].values
                X_fit, y_fit = X_train, y_train
            else:
                X_all, y_all = df[feature_cols].values, df['label_buy'].values
                X_fit, y_fit = X_all, y_all

            # 3. Model selection with Institutional Class Weights
            # Because 0.25% moves are rarer, we tell XGBoost to pay more attention
            pos_weight = (len(y_fit) - sum(y_fit)) / (sum(y_fit) + 1e-9)
            
            model = xgb.XGBClassifier(
                n_estimators=300, 
                max_depth=7,
                learning_rate=0.02,
                subsample=0.7,
                colsample_bytree=0.7,
                gamma=2,
                scale_pos_weight=pos_weight, # CRITICAL for Selective Alpha
                random_state=42,
                eval_metric='logloss'
            )
            
            # 4. Validation
            if oot_mode:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
                acc = float(np.mean(y_pred == y_test))
                sharpe = validator.calculate_sharpe(y_pred, test_df['target_1h'].values)
                val_status = "SUCCESS"
            else:
                val_results = validator.validate(model, X_all, y_all, buffer=24)
                val_status = val_results["status"]
                if val_status == "SUCCESS":
                    acc = val_results["avg_accuracy"]
                    model.fit(X_all, y_all)
                    sharpe = validator.calculate_sharpe(model.predict(X_all), df['target_1h'].values)
            
            if val_status == "SUCCESS":
                joblib.dump(model, MODELS_DIR / f"{sym}_ultra_model.pkl")
                with open(MODELS_DIR / f"{sym}_ultra_model_meta.json", "w") as f:
                    json.dump({"symbol": sym, "accuracy": acc, "sharpe": sharpe, "features": feature_cols}, f, indent=2)
                print(f"  ✅ SUCCESS: Acc {acc:.2%} | Sharpe {sharpe:.2f}")
                results[sym] = {"status": "SUCCESS", "accuracy": acc, "sharpe": sharpe}
                
        except Exception as e:
            print(f"  ❌ ERROR for {sym}: {e}")
            
    return {"status": "SUCCESS", "results": results}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--oot", action="store_true")
    args = parser.parse_args()
    train_world_class_models(oot_mode=args.oot)
