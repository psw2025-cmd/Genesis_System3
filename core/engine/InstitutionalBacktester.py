"""
Institutional Grade Backtester (v1.6) - PORTFOLIO READY
Features:
1. Command-line threshold tuning (--threshold)
2. Aggregate Portfolio Summary (--portfolio)
3. Net daily return tracking for Portfolio Sharpe
"""
import sys
import os
import pandas as pd
import numpy as np
import joblib
import json
import argparse
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

MODELS_DIR = PROJECT_ROOT / "core" / "models" / "angel_one_ultra"
DATA_DIR = PROJECT_ROOT / "storage" / "data" / "historical"
REPORTS_DIR = PROJECT_ROOT / "storage" / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# THE HARD GUARD: Columns that MUST be excluded to match training
STATIONARY_EXCLUDE = ['Open', 'High', 'Low', 'Close', 'Volume']

class InstitutionalBacktester:
    def __init__(self, cost_pct=0.0015, slippage_pct=0.0005, threshold=0.65): 
        self.total_impact = cost_pct + slippage_pct
        self.threshold = threshold

    def run_backtest(self, symbol: str):
        model_path = MODELS_DIR / f"{symbol}_ultra_model.pkl"
        data_path = DATA_DIR / f"{symbol}_historical.csv"
        
        if not model_path.exists() or not data_path.exists():
            return None

        # 1. Load & Engineer
        model = joblib.load(model_path)
        df_raw = pd.read_csv(data_path, index_col=0, parse_dates=True, date_format='%Y-%m-%d %H:%M:%S', engine='c')
        from core.engine.WorldClassFeatureEngine import WorldClassFeatureEngine
        fe = WorldClassFeatureEngine()
        df = fe.engineer_features(df_raw, symbol)
        
        # 2. Define Test Set (Out-of-Sample)
        test_df = df[df.index >= "2026-01-01"].copy()
        if len(test_df) < 50:
            test_df = df.tail(int(len(df) * 0.2)).copy()

        # 3. Align Features (Strictly match stationary trainer)
        exclude = [c for c in test_df.columns if 'target' in c or 'label' in c]
        feature_cols = [c for c in test_df.columns if c not in exclude and c not in STATIONARY_EXCLUDE]
        
        X_test = test_df[feature_cols].values
        
        try:
            probs = model.predict_proba(X_test)[:, 1]
        except Exception as e:
            return None
        
        # 4. Simulation Logic
        test_df.loc[:, 'signal'] = (probs >= self.threshold).astype(int)
        test_df.loc[:, 'raw_ret'] = test_df['target_1h']
        test_df.loc[:, 'trade_event'] = test_df['signal'].diff().abs().fillna(0)
        test_df.loc[:, 'net_ret'] = (test_df['signal'] * test_df['raw_ret']) - (test_df['trade_event'] * self.total_impact)
        
        # 5. Calculate Metrics
        cum_ret = (1 + test_df['net_ret']).cumprod()
        total_ret = cum_ret.iloc[-1] - 1 if not cum_ret.empty else 0
        
        trade_count = int(test_df['trade_event'].sum())
        sharpe = np.mean(test_df['net_ret']) / (np.std(test_df['net_ret']) + 1e-9) * np.sqrt(1600)
        
        rolling_max = cum_ret.cummax()
        drawdown = (cum_ret - rolling_max) / (rolling_max + 1e-9)
        max_dd = drawdown.min() if not drawdown.empty else 0
        
        win_rate = len(test_df[(test_df['signal'] == 1) & (test_df['raw_ret'] > 0)]) / len(test_df[test_df['signal'] == 1]) if len(test_df[test_df['signal'] == 1]) > 0 else 0

        return {
            "symbol": symbol,
            "total_return_pct": float(total_ret * 100),
            "sharpe_ratio": float(sharpe),
            "max_drawdown_pct": float(max_dd * 100),
            "win_rate": float(win_rate),
            "trade_count": trade_count,
            "returns_series": test_df['net_ret']
        }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--threshold", type=float, default=0.65, help="Confidence threshold (default 0.65)")
    parser.add_argument("--portfolio", action="store_true", help="Print aggregate portfolio summary")
    args = parser.parse_args()

    from core.engine.HistoricalDataDownloader import SYMBOLS
    bt = InstitutionalBacktester(threshold=args.threshold)
    
    print("=" * 100)
    print(f"💎 GENESIS SYSTEM3: INSTITUTIONAL BACKTEST REPORT (V1.6)")
    print(f"THRESHOLD: {args.threshold} | IMPACT: 0.20%")
    print("=" * 100)
    print(f"{'SYMBOL':<12} | {'RETURN %':<10} | {'SHARPE':<8} | {'MAX DD':<10} | {'WIN %':<8} | {'TRADES'}")
    print("-" * 100)
    
    all_returns = []
    results = []
    for sym in SYMBOLS.keys():
        try:
            res = bt.run_backtest(sym)
            if res:
                results.append(res)
                all_returns.append(res['returns_series'])
                print(f"{res['symbol']:<12} | {res['total_return_pct']:>9.2f}% | {res['sharpe_ratio']:>8.2f} | {res['max_drawdown_pct']:>9.2f}% | {res['win_rate']*100:>7.1f}% | {res['trade_count']:>8}")
        except:
            pass

    if args.portfolio and all_returns:
        print("\n" + "=" * 100)
        print("🌍 AGGREGATE PORTFOLIO SUMMARY (EQUAL WEIGHT)")
        print("=" * 100)
        
        # Fill missing hours with 0 to allow mean calculation
        portfolio_rets = pd.concat(all_returns, axis=1).mean(axis=1).fillna(0)
        port_cum_ret = (1 + portfolio_rets).cumprod()
        port_total_ret = (port_cum_ret.iloc[-1] - 1) * 100
        port_sharpe = np.mean(portfolio_rets) / (np.std(portfolio_rets) + 1e-9) * np.sqrt(1600)
        port_max_dd = ((port_cum_ret - port_cum_ret.cummax()) / (port_cum_ret.cummax() + 1e-9)).min() * 100
        
        print(f"  TOTAL RETURN:  {port_total_ret:>9.2f}%")
        print(f"  PORTFOLIO SHARPE: {port_sharpe:>6.2f}")
        print(f"  MAX DRAWDOWN:  {port_max_dd:>9.2f}%")
        print(f"  ACTIVE SYMBOLS: {len(all_returns)}")
        print("=" * 100)
    
    # Save master report
    save_data = [{k: v for k, v in r.items() if k != 'returns_series'} for r in results]
    with open(REPORTS_DIR / "institutional_backtest_latest.json", "w") as f:
        json.dump(save_data, f, indent=2)
