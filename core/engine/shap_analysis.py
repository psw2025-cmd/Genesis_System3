"""
SHAP Feature Importance Analysis (v1.1) - FIXED
Dynamically aligns feature set with model metadata.
"""
import sys
import os
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    import shap
except ImportError:
    print("❌ SHAP library not found.")
    sys.exit(1)

from core.engine.WorldClassFeatureEngine import WorldClassFeatureEngine

def run_shap_analysis(symbol: str):
    print(f"\n[SHAP] Analyzing {symbol} Alpha Generation...")
    
    model_path = PROJECT_ROOT / "core" / "models" / "angel_one_ultra" / f"{symbol}_ultra_model.pkl"
    meta_path = PROJECT_ROOT / "core" / "models" / "angel_one_ultra" / f"{symbol}_ultra_model_meta.json"
    data_path = PROJECT_ROOT / "storage" / "data" / "historical" / f"{symbol}_historical.csv"
    output_dir = PROJECT_ROOT / "storage" / "reports" / "shap"
    output_dir.mkdir(parents=True, exist_ok=True)

    if not model_path.exists() or not meta_path.exists():
        print("  ❌ Model or Meta missing. Retrain first.")
        return

    # 1. Load & Engineer
    model = joblib.load(model_path)
    with open(meta_path, 'r') as f:
        meta = json.load(f)
    
    feature_cols = meta['features']
    df_raw = pd.read_csv(data_path, index_col=0, parse_dates=True, date_format='%Y-%m-%d %H:%M:%S')
    fe = WorldClassFeatureEngine()
    df = fe.engineer_features(df_raw, symbol)
    
    # 2. Select Test Data and MATCH Features
    X_test = df[feature_cols].tail(200)

    # 3. SHAP
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_test)

    # 4. Print & Save
    vals = np.abs(shap_values).mean(0)
    importance = pd.DataFrame(list(zip(feature_cols, vals)), columns=['feature','importance']).sort_values('importance', ascending=False)
    
    print(f"  🏆 TOP 10 FEATURES FOR {symbol}:")
    for i, row in importance.head(10).reset_index().iterrows():
        print(f"     {i+1:<2} | {row['feature']:<20} | {row['importance']:.4f}")

    plt.figure(figsize=(10, 6))
    shap.summary_plot(shap_values, X_test, plot_type="bar", show=False)
    plt.title(f"SHAP Stationary Features: {symbol}")
    plt.savefig(output_dir / f"shap_summary_{symbol}.png", bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    for sym in ["NIFTY", "BANKNIFTY"]:
        try:
            run_shap_analysis(sym)
        except Exception as e:
            print(f"  ❌ Failed for {sym}: {e}")
