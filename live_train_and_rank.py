"""
live_train_and_rank.py
======================
GENESIS SYSTEM3 — LIVE TRAINING + TOP 5 RANKER
1. Loads fresh live data from angel_data_fetcher output
2. Engineers features (adaptive v7.0)
3. Trains/updates model per symbol
4. Scores each symbol on LIVE conditions
5. Ranks and outputs TOP 5 with full proof

Run: .venv\Scripts\python.exe live_train_and_rank.py
"""

import os, sys, json, glob, warnings, datetime
import pandas as pd
import numpy as np
import pickle
warnings.filterwarnings('ignore')

LIVE_DIR   = r"C:\Genesis_System3\storage\data\live"
HIST_DIR   = r"C:\Genesis_System3\storage\data\historical"
CHAIN_DIR  = r"C:\Genesis_System3\storage\data\option_chains"
MODEL_DIR  = r"C:\Genesis_System3\models\live_v7"
OUTPUT_DIR = r"C:\Genesis_System3\storage\signals"

os.makedirs(MODEL_DIR,  exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

COST      = 0.002   # 0.20% per trade
THRESHOLD = 0.55    # Live threshold — model proba + chain boost must exceed this
TRAIN_CUTOFF_DAYS = 60  # Retrain on last 60 days rolling

# ── FEATURE ENGINE ────────────────────────────────────────────────────────────
sys.path.insert(0, r"C:\Genesis_System3")
from core.engine.WorldClassFeatureEngine import WorldClassFeatureEngine
engine = WorldClassFeatureEngine()

FEATURE_COLS = [f'z_score_{p}' for p in [10,20,50]] + \
               [f'log_ret_{p}' for p in [10,20,50]] + \
               [f'rsi_{w}' for w in [5,14]] + ['hour']


def load_best_data(symbol):
    """
    Load data: prefer live feed, fall back to historical.
    Merges both if available to maximize training data.
    """
    live_path = os.path.join(LIVE_DIR, f"{symbol}_live.csv")
    hist_path = os.path.join(HIST_DIR, f"{symbol}_historical.csv")
    
    dfs = []
    
    if os.path.exists(live_path):
        df = pd.read_csv(live_path, index_col=0, parse_dates=True)
        dfs.append(df)
    
    if os.path.exists(hist_path) and not dfs:
        df = pd.read_csv(hist_path, index_col=0, parse_dates=True)
        dfs.append(df)
    
    if not dfs:
        return None
    
    combined = pd.concat(dfs)
    combined = combined[~combined.index.duplicated(keep='last')]
    combined = combined.sort_index()
    return combined


def load_chain_signals(symbol):
    """Load latest option chain signals for a symbol."""
    chain_files = sorted(glob.glob(os.path.join(CHAIN_DIR, "chain_signals_*.json")))
    if not chain_files:
        return {}
    
    latest = chain_files[-1]
    with open(latest) as f:
        all_signals = json.load(f)
    
    return all_signals.get(symbol, {})


def train_symbol_model(symbol, df_eng):
    """
    Train XGBoost model on full data, evaluate on last 30 days.
    Returns model + metrics.
    """
    try:
        import xgboost as xgb
        from sklearn.metrics import accuracy_score
        
        feats = [c for c in FEATURE_COLS if c in df_eng.columns]
        
        # Split: last 30 days = OOT test
        cutoff = df_eng.index.max() - pd.Timedelta(days=30)
        train = df_eng[df_eng.index <= cutoff]
        test  = df_eng[df_eng.index >  cutoff]
        
        if len(train) < 100 or 'label_buy' not in df_eng.columns:
            return None, {}
        
        X_train, y_train = train[feats], train['label_buy']
        X_test,  y_test  = test[feats],  test['label_buy']
        
        pos_weight = max(1, (y_train==0).sum() / (y_train==1).sum() + 1e-9)
        
        model = xgb.XGBClassifier(
            n_estimators=300,
            max_depth=4,
            learning_rate=0.03,
            scale_pos_weight=pos_weight,
            subsample=0.8,
            colsample_bytree=0.8,
            eval_metric='logloss',
            verbosity=0,
            random_state=42
        )
        model.fit(X_train, y_train,
                  eval_set=[(X_test, y_test)],
                  verbose=False)
        
        train_acc = accuracy_score(y_train, model.predict(X_train)) * 100
        oot_acc   = accuracy_score(y_test,  model.predict(X_test))  * 100 if len(test) > 5 else 0
        
        # OOT Sharpe simulation
        if len(test) > 5:
            proba = model.predict_proba(X_test)[:, 1]
            signals = (proba >= THRESHOLD).astype(int)
            trades = []
            for i, (sig, ret) in enumerate(zip(signals, test['target_1h'])):
                if sig == 1:
                    trades.append(ret - COST)
            
            if trades:
                s = pd.Series(trades)
                oot_sharpe = (s.mean() / (s.std() + 1e-9)) * np.sqrt(252 * 6)
                oot_ret    = s.sum() * 100
                win_rate   = (s > 0).mean() * 100
                n_trades   = len(trades)
            else:
                oot_sharpe = oot_ret = win_rate = n_trades = 0
        else:
            oot_sharpe = oot_ret = win_rate = n_trades = 0
        
        metrics = {
            'train_acc':  train_acc,
            'oot_acc':    oot_acc,
            'oot_sharpe': oot_sharpe,
            'oot_ret':    oot_ret,
            'win_rate':   win_rate,
            'n_trades':   n_trades,
            'train_rows': len(train),
            'oot_rows':   len(test),
            'features':   feats
        }
        
        return model, metrics
    
    except Exception as e:
        print(f"    [ERROR] Training {symbol}: {e}")
        return None, {}


def score_live_signal(model, df_eng, chain_signals, metrics):
    """
    Generate a composite LIVE SCORE for right now.
    Combines: model probability + option chain confirmation + trend regime.
    Returns score 0–100 and direction.
    """
    if model is None or len(df_eng) == 0:
        return 0, 'NO_SIGNAL', 0
    
    feats = metrics.get('features', [])
    feats = [f for f in feats if f in df_eng.columns]
    if not feats:
        return 0, 'NO_SIGNAL', 0
    
    # Latest bar prediction
    latest = df_eng[feats].iloc[[-1]]
    proba  = model.predict_proba(latest)[0][1]
    
    # Option chain confirmation weight
    chain_boost = 0.0
    pcr_signal  = chain_signals.get('pcr_signal', 'NEUTRAL')
    iv_signal   = chain_signals.get('iv_signal',  'NEUTRAL')
    oi_momentum = chain_signals.get('oi_momentum', 'NEUTRAL')
    
    if pcr_signal  == 'BULLISH': chain_boost += 0.05
    if iv_signal   == 'BULLISH': chain_boost += 0.03
    if oi_momentum == 'BULLISH': chain_boost += 0.04
    if pcr_signal  == 'BEARISH': chain_boost -= 0.05
    if iv_signal   == 'BEARISH': chain_boost -= 0.03
    
    # Trend regime from last 20 bars
    last_20 = df_eng['Close'].iloc[-20:]
    trend   = (last_20.iloc[-1] / last_20.iloc[0] - 1) * 100
    trend_boost = np.clip(trend / 5, -0.05, 0.05)
    
    # Composite probability
    composite_proba = np.clip(proba + chain_boost + trend_boost, 0, 1)
    
    # Score = composite_proba * model quality weight
    quality_weight = np.clip(metrics.get('oot_sharpe', 0) / 20, 0, 1)
    score = composite_proba * 60 + quality_weight * 40
    
    # Direction — requires positive OOT evidence AND live proba signal
    oot_ret    = metrics.get('oot_ret', 0)
    oot_sharpe = metrics.get('oot_sharpe', 0)

    if composite_proba >= THRESHOLD and oot_ret > 0 and oot_sharpe > 0:
        direction = 'BUY'
    elif oot_ret < -1.5 or oot_sharpe < -5:
        direction = 'SELL_AVOID'
    else:
        direction = 'WAIT'
    
    return round(score, 2), direction, round(composite_proba, 4)


def run_live_ranking():
    """Main: train all, rank all, output Top 5."""
    print("=" * 72)
    print("  GENESIS SYSTEM3 — LIVE TRAINING + TOP 5 RANKER")
    print(f"  {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 72)
    
    # Find all available symbols
    live_files = glob.glob(os.path.join(LIVE_DIR, "*_live.csv"))
    hist_files = glob.glob(os.path.join(HIST_DIR, "*_historical.csv"))
    
    live_syms = {os.path.basename(f).replace('_live.csv','') for f in live_files}
    hist_syms = {os.path.basename(f).replace('_historical.csv','') for f in hist_files}
    all_syms  = sorted(live_syms | hist_syms)
    
    print(f"\n[INFO] Found {len(all_syms)} symbols to process")
    print(f"[INFO] Live feed: {len(live_syms)} | Historical: {len(hist_syms)}")
    
    # ── TRAIN + SCORE ALL SYMBOLS ─────────────────────────────────────────────
    print(f"\n{'─'*72}")
    print(f"  {'Symbol':<12} {'TrainAcc':>9} {'OOTAcc':>7} {'OOTRet':>8} "
          f"{'Sharpe':>7} {'Score':>7} {'Signal':>10}")
    print(f"{'─'*72}")
    
    all_results = []
    
    for symbol in all_syms:
        df_raw = load_best_data(symbol)
        if df_raw is None or len(df_raw) < 150:
            continue
        
        try:
            df_eng = engine.engineer_features(df_raw, symbol)
        except Exception as e:
            continue
        
        if len(df_eng) < 100:
            continue
        
        # Train
        model, metrics = train_symbol_model(symbol, df_eng)
        if model is None:
            continue
        
        # Save model
        mpath = os.path.join(MODEL_DIR, f"{symbol}_live_v7.pkl")
        with open(mpath, 'wb') as f:
            pickle.dump({'model': model, 'metrics': metrics, 'symbol': symbol,
                         'trained_at': str(datetime.datetime.now())}, f)
        
        # Load option chain signals
        chain_signals = load_chain_signals(symbol)
        
        # Score live
        score, direction, composite_proba = score_live_signal(
            model, df_eng, chain_signals, metrics)
        
        result = {
            'symbol':     symbol,
            'score':      score,
            'direction':  direction,
            'proba':      composite_proba,
            'oot_ret':    metrics.get('oot_ret', 0),
            'oot_sharpe': metrics.get('oot_sharpe', 0),
            'win_rate':   metrics.get('win_rate', 0),
            'n_trades':   metrics.get('n_trades', 0),
            'train_acc':  metrics.get('train_acc', 0),
            'oot_acc':    metrics.get('oot_acc', 0),
            'chain_pcr':  chain_signals.get('pcr_signal', 'N/A'),
            'iv_signal':  chain_signals.get('iv_signal', 'N/A'),
            'max_pain':   chain_signals.get('max_pain', 'N/A'),
            'model_path': mpath,
        }
        all_results.append(result)
        
        signal_marker = "🟢" if direction == 'BUY' else "🔴" if direction == 'SELL_AVOID' else "⚪"
        print(f"  {symbol:<12} {metrics.get('train_acc',0):>8.1f}% "
              f"{metrics.get('oot_acc',0):>6.1f}% "
              f"{metrics.get('oot_ret',0):>+7.2f}% "
              f"{metrics.get('oot_sharpe',0):>7.2f} "
              f"{score:>7.1f} "
              f"{signal_marker} {direction}")
    
    if not all_results:
        print("\n[ERROR] No symbols processed. Check data paths.")
        return
    
    # ── RANK AND SELECT TOP 5 ─────────────────────────────────────────────────
    df_results = pd.DataFrame(all_results)
    
    # Composite rank: score * oot_sharpe weight * win_rate weight
    df_results['rank_score'] = (
        df_results['score'] * 0.4 +
        df_results['oot_sharpe'].clip(0, 20) / 20 * 35 +
        df_results['win_rate'] / 100 * 25
    )
    
    # Only BUY signals
    buy_signals = df_results[df_results['direction'] == 'BUY'].copy()
    buy_signals = buy_signals.sort_values('rank_score', ascending=False)
    top5 = buy_signals.head(5)
    
    # ── TOP 5 OUTPUT ──────────────────────────────────────────────────────────
    print("\n" + "=" * 72)
    print("  🏆 TOP 5 SYMBOLS — LIVE TRADING SIGNALS")
    print(f"  Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 72)
    
    if len(top5) == 0:
        print("\n  ⚠️  NO BUY SIGNALS AT CURRENT THRESHOLD (0.72)")
        print("  Market conditions do not meet entry criteria right now.")
        print("  Check again at next hourly bar.")
    else:
        print(f"\n  ┌────┬─────────────┬────────┬──────────┬──────────┬──────────┬────────────┐")
        print(f"  │ #  │ Symbol      │ Score  │ OOT Ret% │  Sharpe  │ Win Rate │ Chain PCR  │")
        print(f"  ├────┼─────────────┼────────┼──────────┼──────────┼──────────┼────────────┤")
        
        for rank, (_, row) in enumerate(top5.iterrows(), 1):
            print(f"  │ {rank:<2} │ {row['symbol']:<11} │ {row['score']:>6.1f} │ "
                  f"{row['oot_ret']:>+7.2f}% │ {row['oot_sharpe']:>8.2f} │ "
                  f"{row['win_rate']:>7.1f}% │ {str(row['chain_pcr']):<10} │")
        
        print(f"  └────┴─────────────┴────────┴──────────┴──────────┴──────────┴────────────┘")
        
        print(f"\n  DETAILED BREAKDOWN:")
        print(f"  {'─'*70}")
        for rank, (_, row) in enumerate(top5.iterrows(), 1):
            print(f"\n  #{rank} {row['symbol']}")
            print(f"     Live Score     : {row['score']:.1f}/100")
            print(f"     Model Proba    : {row['proba']:.4f} (threshold: {THRESHOLD})")
            print(f"     OOT Return     : {row['oot_ret']:+.2f}%")
            print(f"     OOT Sharpe     : {row['oot_sharpe']:.2f}")
            print(f"     Win Rate       : {row['win_rate']:.1f}%")
            print(f"     OOT Trades     : {int(row['n_trades'])}")
            print(f"     Train Accuracy : {row['train_acc']:.1f}%")
            print(f"     OOT Accuracy   : {row['oot_acc']:.1f}%")
            print(f"     PCR Signal     : {row['chain_pcr']}")
            print(f"     IV Signal      : {row['iv_signal']}")
            print(f"     Max Pain       : {row['max_pain']}")
    
    # ── SAVE SIGNALS ──────────────────────────────────────────────────────────
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M')
    
    # Save full rankings
    df_results.to_csv(os.path.join(OUTPUT_DIR, f"all_rankings_{timestamp}.csv"), index=False)
    
    # Save top 5 as JSON (for dashboard / telegram / webhook)
    top5_dict = top5.to_dict('records')
    signals_out = {
        'generated_at': str(datetime.datetime.now()),
        'threshold':    THRESHOLD,
        'top5':         top5_dict,
        'total_symbols_scored': len(df_results),
        'buy_signals_found':    len(buy_signals)
    }
    json_path = os.path.join(OUTPUT_DIR, f"top5_signals_{timestamp}.json")
    with open(json_path, 'w') as f:
        json.dump(signals_out, f, indent=2, default=str)
    
    # Also save as LATEST (always overwritten — for live dashboard)
    latest_path = os.path.join(OUTPUT_DIR, "top5_LATEST.json")
    with open(latest_path, 'w') as f:
        json.dump(signals_out, f, indent=2, default=str)
    
    print(f"\n  [✓] Signals saved: {json_path}")
    print(f"  [✓] Latest always at: {latest_path}")
    print(f"\n  Next step: .venv\\Scripts\\python.exe live_dashboard.py")
    print("=" * 72)


if __name__ == "__main__":
    run_live_ranking()
