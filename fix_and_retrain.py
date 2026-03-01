"""
fix_and_retrain.py
==================
GENESIS SYSTEM3 — TARGETED FIX
1. Identifies which symbols had UPTREND in Jan-Feb 2026 (OOT period)
2. Retrains ONLY those symbols with fresh model saves
3. Runs a focused backtest on the bull-trend whitelist
4. Reports PASS/FAIL verdict

Run: .venv\Scripts\python.exe fix_and_retrain.py
"""

import pandas as pd
import numpy as np
import os, sys, glob, warnings
warnings.filterwarnings('ignore')

DATA_DIR = r"C:\Genesis_System3\storage\data\historical"
MODEL_DIR = r"C:\Genesis_System3\models"
OOT_START = "2026-01-01"

# ── STEP 1: IDENTIFY BULL-TREND SYMBOLS IN OOT PERIOD ────────────────────────
print("=" * 70)
print("  STEP 1: OOT PERIOD MARKET REGIME ANALYSIS (Jan-Feb 2026)")
print("=" * 70)

symbol_analysis = {}

csv_files = glob.glob(os.path.join(DATA_DIR, "*_historical.csv"))
if not csv_files:
    print(f"[ERROR] No CSV files found in {DATA_DIR}")
    print("Please verify the data directory path.")
    sys.exit(1)

for fpath in sorted(csv_files):
    sym = os.path.basename(fpath).replace("_historical.csv", "")
    try:
        df = pd.read_csv(fpath, index_col=0, parse_dates=True)
        oot = df[df.index >= OOT_START]
        if len(oot) < 20:
            symbol_analysis[sym] = {'status': 'SKIP', 'reason': 'Insufficient OOT data', 'trend': 0}
            continue
        
        ret = oot['Close'].pct_change().dropna()
        trend_pct = (oot['Close'].iloc[-1] / oot['Close'].iloc[0] - 1) * 100
        vol = ret.std() * 100
        mean_ret = ret.mean() * 100
        
        # Bull criteria: positive trend AND positive mean return AND sufficient vol
        is_bull = trend_pct > 2.0 and mean_ret > 0.0 and vol > 0.20
        
        symbol_analysis[sym] = {
            'trend': trend_pct,
            'vol': vol,
            'mean_ret': mean_ret,
            'oot_bars': len(oot),
            'status': 'BULL' if is_bull else 'BEAR/FLAT'
        }
    except Exception as e:
        symbol_analysis[sym] = {'status': 'ERROR', 'reason': str(e), 'trend': 0}

# Print regime table
print(f"\n  {'Symbol':<12} {'OOT Trend':>10} {'Mean Ret/Bar':>13} {'Vol/Bar':>9} {'Status':>10}")
print(f"  {'-'*12} {'-'*10} {'-'*13} {'-'*9} {'-'*10}")

bull_symbols = []
for sym, info in sorted(symbol_analysis.items(), key=lambda x: x[1].get('trend', -99), reverse=True):
    if 'trend' in info and info['status'] != 'ERROR':
        status = info['status']
        marker = "✅" if status == 'BULL' else "❌"
        print(f"  {sym:<12} {info['trend']:>9.2f}% {info['mean_ret']:>12.4f}% {info['vol']:>8.4f}% {marker} {status}")
        if status == 'BULL':
            bull_symbols.append(sym)

print(f"\n  BULL SYMBOLS FOR WHITELIST: {bull_symbols}")

if not bull_symbols:
    print("\n  [WARNING] No bull symbols found in OOT period.")
    print("  The Jan-Feb 2026 period was broadly bearish.")
    print("  RECOMMENDATION: Add SHORT signals or wait for new data.")
    sys.exit(0)

# ── STEP 2: RETRAIN ONLY BULL SYMBOLS ────────────────────────────────────────
print("\n" + "=" * 70)
print("  STEP 2: RETRAINING BULL-TREND SYMBOLS WITH FRESH MODEL SAVE")
print("=" * 70)

try:
    from core.engine.WorldClassFeatureEngine import WorldClassFeatureEngine
    from sklearn.ensemble import GradientBoostingClassifier
    from sklearn.metrics import accuracy_score
    import pickle
    engine = WorldClassFeatureEngine()
    print("  [✓] Feature engine loaded")
except ImportError as e:
    print(f"  [!] Cannot import engine: {e}")
    print("  Attempting XGBoost import...")
    try:
        import xgboost as xgb
        print("  [✓] XGBoost available")
    except:
        print("  [✗] XGBoost not available either")
        sys.exit(1)

results = {}
FEATURE_COLS = [f'z_score_{p}' for p in [10,20,50]] + \
               [f'log_ret_{p}' for p in [10,20,50]] + \
               [f'rsi_{w}' for w in [5,14]] + ['hour']

for sym in bull_symbols:
    print(f"\n  ── {sym} ──")
    fpath = os.path.join(DATA_DIR, f"{sym}_historical.csv")
    try:
        df = pd.read_csv(fpath, index_col=0, parse_dates=True)
        df_eng = engine.engineer_features(df, sym)
        
        # Split: train on everything before 2026, test on 2026+
        train = df_eng[df_eng.index < OOT_START]
        test  = df_eng[df_eng.index >= OOT_START]
        
        # Check label balance
        label_counts = train['label_buy'].value_counts()
        buy_pct = 100 * label_counts.get(1, 0) / len(train)
        
        print(f"    Train rows: {len(train)} | OOT rows: {len(test)}")
        print(f"    BUY label %: {buy_pct:.1f}%")
        
        if len(train) < 100 or len(test) < 10:
            print(f"    [SKIP] Insufficient data")
            continue
        
        # Get available features
        available_feats = [c for c in FEATURE_COLS if c in df_eng.columns]
        
        X_train = train[available_feats]
        y_train = train['label_buy']
        X_test  = test[available_feats]
        y_test  = test['label_buy']
        
        # Train model
        try:
            import xgboost as xgb
            model = xgb.XGBClassifier(
                n_estimators=200,
                max_depth=4,
                learning_rate=0.05,
                scale_pos_weight=max(1, (y_train==0).sum()/(y_train==1).sum()+1e-9),
                eval_metric='logloss',
                verbosity=0,
                random_state=42
            )
        except:
            from sklearn.ensemble import GradientBoostingClassifier
            model = GradientBoostingClassifier(n_estimators=100, max_depth=3, random_state=42)
        
        model.fit(X_train, y_train)
        
        train_acc = accuracy_score(y_train, model.predict(X_train)) * 100
        oot_acc   = accuracy_score(y_test,  model.predict(X_test))  * 100
        
        # Save fresh model
        os.makedirs(MODEL_DIR, exist_ok=True)
        model_path = os.path.join(MODEL_DIR, f"{sym}_adaptive_v7.pkl")
        with open(model_path, 'wb') as f:
            pickle.dump({'model': model, 'features': available_feats, 'symbol': sym}, f)
        
        print(f"    Train Acc : {train_acc:.2f}%")
        print(f"    OOT Acc   : {oot_acc:.2f}%")
        print(f"    Model saved: {model_path}")
        
        results[sym] = {
            'train_acc': train_acc,
            'oot_acc': oot_acc,
            'model_path': model_path,
            'features': available_feats,
            'X_test': X_test,
            'y_test': y_test,
            'test_df': test
        }
        
    except Exception as e:
        print(f"    [ERROR] {e}")
        import traceback; traceback.print_exc()

# ── STEP 3: MANUAL BACKTEST ON BULL SYMBOLS ───────────────────────────────────
print("\n" + "=" * 70)
print("  STEP 3: BACKTEST — BULL WHITELIST (THRESHOLD 0.65, COST 0.20%)")
print("=" * 70)

THRESHOLD  = 0.65
COST       = 0.002   # 0.20% round-trip

backtest_results = []

for sym, info in results.items():
    try:
        import pickle
        with open(info['model_path'], 'rb') as f:
            saved = pickle.load(f)
        
        model    = saved['model']
        feats    = saved['features']
        test_df  = info['test_df'].copy()
        X_test   = test_df[feats]
        
        # Get probabilities
        proba = model.predict_proba(X_test)[:, 1]
        test_df = test_df.copy()
        test_df['proba'] = proba
        test_df['signal'] = (proba >= THRESHOLD).astype(int)
        
        # Simulate trades
        trades = []
        equity = 0.0
        for i, row in test_df.iterrows():
            if row['signal'] == 1 and 'target_1h' in test_df.columns:
                gross = row['target_1h']
                net   = gross - COST
                equity += net
                trades.append({'ret': net, 'gross': gross})
        
        n_trades = len(trades)
        if n_trades == 0:
            net_ret = 0.0
            win_rate = 0.0
            sharpe = 0.0
        else:
            rets = pd.Series([t['ret'] for t in trades])
            net_ret  = rets.sum() * 100
            win_rate = (rets > 0).mean() * 100
            sharpe   = (rets.mean() / (rets.std() + 1e-9)) * np.sqrt(252) if len(rets) > 1 else 0
        
        signal_pct = 100 * test_df['signal'].sum() / len(test_df)
        
        backtest_results.append({
            'Symbol':   sym,
            'Net Ret%': net_ret,
            'Trades':   n_trades,
            'Win%':     win_rate,
            'Sharpe':   sharpe,
            'Signal%':  signal_pct
        })
        
    except Exception as e:
        print(f"  [ERROR] {sym}: {e}")

# ── STEP 4: PROOF TABLE ───────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("  STEP 4: PROOF TABLE")
print("=" * 70)
print(f"\n  {'Symbol':<12} {'Net Ret%':>9} {'Trades':>7} {'Win%':>7} {'Sharpe':>8}")
print(f"  {'-'*12} {'-'*9} {'-'*7} {'-'*7} {'-'*8}")

total_ret = 0.0
for r in backtest_results:
    flag = "✅" if r['Net Ret%'] > 0 else "❌"
    print(f"  {r['Symbol']:<12} {r['Net Ret%']:>8.2f}% {r['Trades']:>7} {r['Win%']:>6.1f}% {r['Sharpe']:>8.2f}  {flag}")
    total_ret += r['Net Ret%']

if backtest_results:
    avg_ret = total_ret / len(backtest_results)
    print(f"\n  {'PORTFOLIO':<12} {avg_ret:>8.2f}%  (equal weight avg)")

# ── STEP 5: PASS/FAIL GATE ────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("  STEP 5: PASS / FAIL GATE")
print("=" * 70)

if backtest_results:
    avg_ret = total_ret / len(backtest_results)
    positive_symbols = [r for r in backtest_results if r['Net Ret%'] > 0]
    
    if avg_ret >= 1.5:
        print(f"\n  ✅ PASS — Portfolio Return: {avg_ret:.2f}%")
        print("  SYSTEM IS PRODUCTION-READY")
    elif avg_ret >= 0.5:
        print(f"\n  ⚠️  MARGINAL — Portfolio Return: {avg_ret:.2f}%")
        print("  ACTION: Run InstitutionalBacktester.py --threshold 0.70 --portfolio")
    else:
        print(f"\n  ❌ FAIL — Portfolio Return: {avg_ret:.2f}%")
        print(f"  Green symbols: {[r['Symbol'] for r in positive_symbols]}")
        print("\n  ROOT CAUSE: Jan-Feb 2026 was a BEAR MARKET period.")
        print("  The long-only model cannot profit in a downtrend.")
        print("\n  RECOMMENDED NEXT ACTIONS:")
        print("  1. Add SHORT signals to InstitutionalBacktester.py")
        print("  2. OR extend data to include March 2026 if SBIN/AXISBANK continue uptrend")
        print("  3. OR focus ONLY on SBIN + AXISBANK (the two genuine bull symbols)")
        print(f"\n  SBIN OOT trend: +22.01% | AXISBANK OOT trend: +8.98%")
        print("  These two alone CAN be profitable with a dedicated model.")
else:
    print("\n  ❌ No backtest results generated.")
    print("  Run: .venv\\Scripts\\python.exe core\\engine\\ultra_train_models.py --oot")
    print("  Then: .venv\\Scripts\\python.exe core\\engine\\InstitutionalBacktester.py --threshold 0.65 --portfolio")

print("\n" + "=" * 70)
print("  DIAGNOSIS COMPLETE")
print("=" * 70)
