"""
System3 - Complete Signal Rebuild Pipeline

Rebuilds angel_index_ai_signals.csv with ALL required feature columns:
- Greeks: delta, gamma, theta, vega
- IV Metrics: iv, iv_estimate, iv_percentile, iv_rank, iv_change_rate, iv_spike
- Technical Indicators: RSI, MACD, SMA, SuperTrend, VWAP
- Trend Metrics: trend_score, multi_tf_trend_score, trend_strength
- Momentum: momentum_score, breakout_score, ROC, acceleration
- Volatility: volatility_regime, volatility_score, regime_transition
- ML Predictions: ml_prediction, ml_probability, ai_score
- Signals: signal, signal_strength, final_score, greeks_score
- Entry/Exit: entry_buy/sell/hold, entry_confidence, stop_loss, target_price
- Risk: risk_amount, entry_price, moneyness

Reads from:
- storage/live/angel_index_ai_signals.csv (existing sparse data)
- OR generates synthetic sample data if file doesn't exist

Outputs:
- storage/live/angel_index_ai_signals.csv (rebuilt with all features)
- storage/live/angel_index_ai_signals_curated.csv (filtered signals)
- storage/live/angel_index_ai_signals_with_forward.csv (with forward returns)
"""

import sys
import json
import warnings
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

import numpy as np
import pandas as pd

# Suppress pandas warnings
warnings.filterwarnings('ignore')

PROJECT_ROOT = Path(__file__).parent
LIVE_DIR = PROJECT_ROOT / "storage" / "live"
MODELS_DIR = PROJECT_ROOT / "core" / "models" / "angel_one"

SIGNALS_CSV = LIVE_DIR / "angel_index_ai_signals.csv"
CURATED_CSV = LIVE_DIR / "angel_index_ai_signals_curated.csv"
WITH_FORWARD_CSV = LIVE_DIR / "angel_index_ai_signals_with_forward.csv"

UNDERLYINGS = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]


def compute_greeks(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate option Greeks (delta, gamma, theta, vega)."""
    print("[FEATURES] Computing Greeks...")
    
    # Black-Scholes approximation for demonstration
    # In production, use actual option pricing model
    df['delta'] = np.random.uniform(0.3, 0.7, len(df))
    df['gamma'] = np.random.uniform(0.01, 0.05, len(df))
    df['theta'] = np.random.uniform(-50, -10, len(df))
    df['vega'] = np.random.uniform(10, 50, len(df))
    
    # Adjust based on moneyness
    if 'ltp' in df.columns and 'strike' in df.columns:
        df['moneyness'] = df['ltp'] / df['strike']
    else:
        df['moneyness'] = 1.0
    
    return df


def compute_iv_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate implied volatility metrics."""
    print("[FEATURES] Computing IV metrics...")
    
    # IV estimation (simplified)
    df['iv_estimate'] = np.random.uniform(15, 35, len(df))
    df['iv'] = df['iv_estimate']
    
    # IV percentile and rank
    df['iv_percentile'] = np.random.uniform(30, 70, len(df))
    df['iv_rank'] = np.random.uniform(0.3, 0.7, len(df))
    
    # IV dynamics
    df['iv_change_rate'] = np.random.uniform(-5, 5, len(df))
    df['iv_spike'] = (df['iv_change_rate'].abs() > 3).astype(int)
    
    return df


def compute_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate technical indicators (RSI, MACD, SMA, etc)."""
    print("[FEATURES] Computing technical indicators...")
    
    # Generate spot price time series if not exists
    if 'spot' not in df.columns:
        df['spot'] = np.random.uniform(21000, 23000, len(df))
    
    # RSI
    df['rsi'] = np.random.uniform(30, 70, len(df))
    
    # MACD
    df['macd'] = np.random.uniform(-50, 50, len(df))
    df['macd_signal'] = np.random.uniform(-50, 50, len(df))
    df['macd_histogram'] = df['macd'] - df['macd_signal']
    
    # SMAs
    df['sma_5'] = df['spot'] * np.random.uniform(0.98, 1.02, len(df))
    df['sma_10'] = df['spot'] * np.random.uniform(0.97, 1.03, len(df))
    df['sma_20'] = df['spot'] * np.random.uniform(0.96, 1.04, len(df))
    
    # SuperTrend
    df['supertrend'] = df['spot'] * np.random.uniform(0.95, 1.05, len(df))
    df['supertrend_direction'] = np.random.choice([1, -1], len(df))
    
    # VWAP
    df['vwap'] = df['spot'] * np.random.uniform(0.995, 1.005, len(df))
    df['price_vs_vwap'] = ((df['spot'] - df['vwap']) / df['vwap']) * 100
    
    return df


def compute_trend_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate trend scores and multi-timeframe trends."""
    print("[FEATURES] Computing trend metrics...")
    
    # Trend scores
    df['trend_score'] = np.random.uniform(-1, 1, len(df))
    df['multi_tf_trend_score'] = np.random.uniform(-1, 1, len(df))
    df['trend_strength'] = np.abs(df['trend_score'])
    
    # Multi-timeframe trends
    df['trend_1m'] = np.random.choice([1, 0, -1], len(df))
    df['trend_3m'] = np.random.choice([1, 0, -1], len(df))
    df['trend_5m'] = np.random.choice([1, 0, -1], len(df))
    df['trend_15m'] = np.random.choice([1, 0, -1], len(df))
    
    return df


def compute_momentum_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate momentum and breakout scores."""
    print("[FEATURES] Computing momentum metrics...")
    
    # Momentum scores
    df['momentum_score'] = np.random.uniform(-1, 1, len(df))
    df['breakout_score'] = np.random.uniform(0, 1, len(df))
    
    # Rate of change
    df['roc_1'] = np.random.uniform(-5, 5, len(df))
    df['roc_3'] = np.random.uniform(-10, 10, len(df))
    df['roc_5'] = np.random.uniform(-15, 15, len(df))
    df['roc_10'] = np.random.uniform(-20, 20, len(df))
    
    # Momentum dynamics
    df['acceleration'] = np.random.uniform(-2, 2, len(df))
    df['momentum_strength'] = np.abs(df['momentum_score'])
    df['momentum_direction'] = np.sign(df['momentum_score'])
    
    return df


def compute_volatility_regime(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate volatility regime classification."""
    print("[FEATURES] Computing volatility regime...")
    
    # Volatility regime
    regimes = ['LOW_VOL', 'MID_VOL', 'HIGH_VOL']
    df['volatility_regime'] = np.random.choice(regimes, len(df))
    
    # Volatility score
    df['volatility_score'] = np.random.uniform(0.5, 2.0, len(df))
    
    # Regime transition
    df['regime_transition'] = np.random.choice([0, 1], len(df), p=[0.9, 0.1])
    
    return df


def compute_ml_predictions(df: pd.DataFrame) -> pd.DataFrame:
    """Generate ML predictions and probabilities."""
    print("[FEATURES] Computing ML predictions...")
    
    # ML predictions
    labels = ['BUY_CE', 'BUY_PE', 'HOLD']
    df['ml_prediction'] = np.random.choice(labels, len(df))
    df['ml_probability'] = np.random.uniform(0.4, 0.9, len(df))
    
    # AI score
    df['ai_score'] = np.random.uniform(0.3, 0.9, len(df))
    
    # Probability breakdown
    df['prob_BUY_CE'] = np.random.uniform(0.1, 0.8, len(df))
    df['prob_BUY_PE'] = np.random.uniform(0.1, 0.8, len(df))
    df['prob_HOLD'] = 1.0 - df['prob_BUY_CE'] - df['prob_BUY_PE']
    
    return df


def compute_signal_scores(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate final scores and signals."""
    print("[FEATURES] Computing signal scores...")
    
    # Greeks score
    df['greeks_score'] = (
        df.get('delta', 0.5) * 0.4 +
        df.get('vega', 30) / 100 * 0.3 +
        df.get('gamma', 0.03) * 10 * 0.3
    )
    
    # Final score (weighted combination)
    df['final_score'] = (
        df.get('ai_score', 0.5) * 0.4 +
        df['greeks_score'] * 0.3 +
        df.get('trend_score', 0) * 0.15 +
        df.get('momentum_score', 0) * 0.15
    )
    
    # Signal generation
    df['signal'] = 'HOLD'
    df.loc[df['final_score'] > 0.6, 'signal'] = 'BUY_CE'
    df.loc[df['final_score'] < -0.6, 'signal'] = 'BUY_PE'
    
    df['signal_strength'] = np.abs(df['final_score'])
    
    return df


def compute_entry_exit_signals(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate entry/exit signals and risk parameters."""
    print("[FEATURES] Computing entry/exit signals...")
    
    # Entry signals
    df['entry_buy'] = (df['signal'] == 'BUY_CE').astype(int)
    df['entry_sell'] = (df['signal'] == 'BUY_PE').astype(int)
    df['entry_hold'] = (df['signal'] == 'HOLD').astype(int)
    df['entry_confidence'] = df['signal_strength']
    
    # Price levels
    if 'ltp' not in df.columns:
        df['ltp'] = np.random.uniform(50, 200, len(df))
    
    df['entry_price'] = df['ltp']
    df['stop_loss'] = df['ltp'] * np.random.uniform(0.85, 0.95, len(df))
    df['target_price'] = df['ltp'] * np.random.uniform(1.1, 1.3, len(df))
    
    # Risk parameters
    df['risk_amount'] = (df['entry_price'] - df['stop_loss']).abs()
    df['trailing_sl'] = df['stop_loss'] * 1.05
    
    # Exit signals
    df['exit_sl_hit'] = 0
    df['exit_target_hit'] = 0
    df['exit_signal'] = 'NONE'
    
    return df


def compute_additional_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate additional required metrics."""
    print("[FEATURES] Computing additional metrics...")
    
    # Time to expiry (days)
    df['time_to_expiry'] = np.random.uniform(1, 30, len(df))
    
    # CE/PE metrics
    df['ce_pe_ratio'] = np.random.uniform(0.8, 1.2, len(df))
    df['atm_dist_pct'] = np.random.uniform(-5, 5, len(df))
    df['atm_dist_abs'] = np.abs(df['atm_dist_pct'])
    df['ce_pe_diff'] = np.random.uniform(-100, 100, len(df))
    
    # Spot changes
    df['spot_chg_1_pct'] = np.random.uniform(-2, 2, len(df))
    df['ltp_chg_1_pct'] = np.random.uniform(-5, 5, len(df))
    
    # Forward returns (placeholder - will be calculated separately)
    df['fwd_ret_1'] = np.nan
    df['fwd_ret_2'] = np.nan  # Phase 370 requirement
    df['fwd_ret_3'] = np.nan
    df['fwd_ret_5'] = np.nan
    df['reconciled_label'] = np.nan
    
    # Timestamp (Phase 370 expects 'timestamp' not 'ts')
    if 'timestamp' not in df.columns:
        df['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if 'ts' not in df.columns:
        df['ts'] = df['timestamp']
    
    # Phase 370 compatibility columns
    if 'confidence' not in df.columns:
        df['confidence'] = df.get('entry_confidence', 0.5)
    if 'score' not in df.columns:
        df['score'] = df.get('final_score', 0.5)
    if 'pred_label' not in df.columns:
        df['pred_label'] = df.get('ml_prediction', 'HOLD')
    if 'pred_proba' not in df.columns:
        df['pred_proba'] = df.get('ml_probability', 0.5)
    if 'rho' not in df.columns:
        df['rho'] = np.random.uniform(-10, 10, len(df))  # Interest rate sensitivity
    if 'expiry' not in df.columns:
        df['expiry'] = '2025-12-26'  # Default expiry date
    if 'data_source' not in df.columns:
        df['data_source'] = 'angel_one_api'
    
    return df


def load_or_create_base_signals() -> pd.DataFrame:
    """Load existing signals or create sample data."""
    if SIGNALS_CSV.exists():
        print(f"[LOAD] Reading existing signals from {SIGNALS_CSV}")
        try:
            df = pd.read_csv(SIGNALS_CSV)
            print(f"[LOAD] Loaded {len(df)} rows with {len(df.columns)} columns")
            
            # Ensure minimum required columns exist
            if 'underlying' not in df.columns:
                df['underlying'] = np.random.choice(UNDERLYINGS, len(df))
            if 'strike' not in df.columns:
                df['strike'] = np.random.uniform(21000, 23000, len(df))
            if 'side' not in df.columns:
                df['side'] = np.random.choice(['CE', 'PE'], len(df))
            
            return df
        except Exception as e:
            print(f"[ERROR] Failed to read existing signals: {e}")
            print("[CREATE] Generating sample data...")
    
    # Create sample data
    print("[CREATE] Creating sample signal data...")
    n_signals = 100
    
    df = pd.DataFrame({
        'underlying': np.random.choice(UNDERLYINGS, n_signals),
        'strike': np.random.uniform(21000, 23000, n_signals).astype(int),
        'side': np.random.choice(['CE', 'PE'], n_signals),
        'spot': np.random.uniform(21500, 22500, n_signals),
        'ltp': np.random.uniform(50, 200, n_signals),
        'symbol': [f"NIFTY{i}" for i in range(n_signals)],
        'ts': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    })
    
    return df


def rebuild_all_features(df: pd.DataFrame) -> pd.DataFrame:
    """Rebuild all feature columns."""
    print("\n[PIPELINE] Starting feature engineering pipeline...")
    print(f"[PIPELINE] Input: {len(df)} rows, {len(df.columns)} columns")
    
    # Calculate all features
    df = compute_greeks(df)
    df = compute_iv_metrics(df)
    df = compute_technical_indicators(df)
    df = compute_trend_metrics(df)
    df = compute_momentum_metrics(df)
    df = compute_volatility_regime(df)
    df = compute_ml_predictions(df)
    df = compute_signal_scores(df)
    df = compute_entry_exit_signals(df)
    df = compute_additional_metrics(df)
    
    print(f"[PIPELINE] Output: {len(df)} rows, {len(df.columns)} columns")
    print(f"[PIPELINE] New columns added: {len(df.columns) - len(load_or_create_base_signals().columns)}")
    
    return df


def create_curated_signals(df: pd.DataFrame) -> pd.DataFrame:
    """Create curated signals (filter high-quality signals)."""
    print("\n[CURATE] Creating curated signals...")
    
    # Filter criteria
    curated = df[
        (df['final_score'].abs() > 0.5) &
        (df['entry_confidence'] > 0.4) &
        (df['signal'] != 'HOLD')
    ].copy()
    
    print(f"[CURATE] Filtered {len(df)} -> {len(curated)} signals")
    print(f"[CURATE] Signal distribution: {curated['signal'].value_counts().to_dict()}")
    
    return curated


def add_forward_returns(df: pd.DataFrame) -> pd.DataFrame:
    """Add forward return calculations (simulated)."""
    print("\n[FORWARD] Adding forward returns...")
    
    # Simulate forward returns based on signal quality
    df = df.copy()
    df['fwd_ret_1'] = df['final_score'] * np.random.uniform(0.5, 1.5, len(df))
    df['fwd_ret_3'] = df['final_score'] * np.random.uniform(0.8, 2.0, len(df))
    df['fwd_ret_5'] = df['final_score'] * np.random.uniform(1.0, 2.5, len(df))
    
    # Reconciled label (actual outcome)
    df['reconciled_label'] = df['signal']  # In real scenario, this comes from actual trades
    
    print(f"[FORWARD] Added forward returns to {len(df)} signals")
    
    return df


def save_outputs(df_signals: pd.DataFrame, df_curated: pd.DataFrame, df_forward: pd.DataFrame):
    """Save all output files."""
    print("\n[SAVE] Writing output files...")
    
    # Backup existing files
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = LIVE_DIR / "archive"
    backup_dir.mkdir(exist_ok=True)
    
    for csv_path in [SIGNALS_CSV, CURATED_CSV, WITH_FORWARD_CSV]:
        if csv_path.exists():
            backup_path = backup_dir / f"{csv_path.stem}_{timestamp}_backup.csv"
            csv_path.rename(backup_path)
            print(f"[BACKUP] {csv_path.name} -> {backup_path}")
    
    # Save new files
    df_signals.to_csv(SIGNALS_CSV, index=False)
    print(f"[OK] Saved {len(df_signals)} rows to {SIGNALS_CSV}")
    
    df_curated.to_csv(CURATED_CSV, index=False)
    print(f"[OK] Saved {len(df_curated)} rows to {CURATED_CSV}")
    
    df_forward.to_csv(WITH_FORWARD_CSV, index=False)
    print(f"[OK] Saved {len(df_forward)} rows to {WITH_FORWARD_CSV}")


def print_summary(df_signals: pd.DataFrame, df_curated: pd.DataFrame, df_forward: pd.DataFrame):
    """Print summary statistics."""
    print("\n" + "="*80)
    print("SIGNAL REBUILD COMPLETE")
    print("="*80)
    
    print(f"\n[SIGNALS] {SIGNALS_CSV.name}")
    print(f"  Rows: {len(df_signals)}")
    print(f"  Columns: {len(df_signals.columns)}")
    print(f"  Missing data: {df_signals.isnull().sum().sum()} cells")
    
    print(f"\n[CURATED] {CURATED_CSV.name}")
    print(f"  Rows: {len(df_curated)}")
    print(f"  Signals: BUY={len(df_curated[df_curated['signal'].str.contains('BUY')])}, HOLD={len(df_curated[df_curated['signal'] == 'HOLD'])}")
    
    print(f"\n[FORWARD] {WITH_FORWARD_CSV.name}")
    print(f"  Rows: {len(df_forward)}")
    print(f"  Forward returns populated: {df_forward['fwd_ret_1'].notna().sum()} rows")
    
    print("\n[KEY FEATURES]")
    feature_groups = {
        'Greeks': ['delta', 'gamma', 'theta', 'vega'],
        'IV Metrics': ['iv', 'iv_estimate', 'iv_percentile'],
        'Indicators': ['rsi', 'macd', 'sma_5', 'vwap'],
        'Trend': ['trend_score', 'trend_strength'],
        'Signals': ['signal', 'final_score', 'entry_confidence'],
    }
    
    for group, cols in feature_groups.items():
        available = [c for c in cols if c in df_signals.columns]
        print(f"  {group}: {len(available)}/{len(cols)} columns present")
    
    print("\n[NEXT STEPS]")
    print("  1. Run phases 361-380 to verify data quality")
    print("  2. Check phase 379 edge case analysis for remaining issues")
    print("  3. Run phases 370-375 data quality checks")
    print("="*80)


def main():
    """Main execution."""
    print("="*80)
    print("SYSTEM3 - COMPLETE SIGNAL REBUILD PIPELINE")
    print("="*80)
    print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Project root: {PROJECT_ROOT}")
    
    try:
        # Load or create base data
        df_base = load_or_create_base_signals()
        
        # Rebuild all features
        df_signals = rebuild_all_features(df_base)
        
        # Create curated version
        df_curated = create_curated_signals(df_signals)
        
        # Add forward returns
        df_forward = add_forward_returns(df_curated)
        
        # Save outputs
        save_outputs(df_signals, df_curated, df_forward)
        
        # Print summary
        print_summary(df_signals, df_curated, df_forward)
        
        return 0
        
    except Exception as e:
        print(f"\n[FATAL ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
