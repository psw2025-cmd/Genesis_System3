#!/usr/bin/env python3
"""
System3 Debug Signals Pipeline - STEP 5 Health Script

Quick signal pipeline diagnostic tool.
Run this during market hours to check signal generation status.
Respects DRY-RUN mode (no real trading).

Usage:
    python system3_debug_signals_pipeline.py

Output:
    - Loads latest market snapshot
    - Runs signal generation
    - Shows row counts and signal distribution
    - Identifies why signals may not be generated
"""

import sys
import pandas as pd
from pathlib import Path
from datetime import datetime

# Setup paths
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.utils.logger import logger

def load_latest_snapshot():
    """Load the latest market snapshot from watch file."""
    watch_csv = ROOT_DIR / "storage" / "live" / "angel_index_options_watch.csv"
    
    if not watch_csv.exists():
        logger.warning(f"Watch file not found: {watch_csv}")
        return None
    
    try:
        df = pd.read_csv(watch_csv)
        if df.empty:
            logger.warning("Watch file is empty")
            return None
        
        # Use last 100 rows or all if fewer
        df = df.tail(100)
        logger.info(f"✓ Loaded snapshot: {len(df)} rows from {watch_csv}")
        return df
    except Exception as e:
        logger.error(f"Failed to load snapshot: {e}")
        return None


def run_signal_generation(df_snapshot):
    """Run signal generation and return results."""
    try:
        from core.engine.angel_live_ai_signals import run_once_with_snapshot
        
        logger.info(f"🚀 Starting signal generation on {len(df_snapshot)} rows...")
        df_signals = run_once_with_snapshot(df_snapshot)
        
        return df_signals
    except Exception as e:
        logger.error(f"Signal generation failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None


def analyze_signals(df_signals):
    """Analyze and display signal results."""
    if df_signals is None or df_signals.empty:
        logger.warning("⚠️  No signals generated")
        return
    
    logger.info("\n" + "="*70)
    logger.info("SIGNAL GENERATION ANALYSIS")
    logger.info("="*70)
    
    # Basic counts
    total_rows = len(df_signals)
    buy_count = len(df_signals[df_signals.get('signal') == 'BUY']) if 'signal' in df_signals.columns else 0
    sell_count = len(df_signals[df_signals.get('signal') == 'SELL']) if 'signal' in df_signals.columns else 0
    hold_count = len(df_signals[df_signals.get('signal') == 'HOLD']) if 'signal' in df_signals.columns else 0
    
    logger.info(f"\n📊 SIGNAL DISTRIBUTION:")
    logger.info(f"   Total rows: {total_rows}")
    logger.info(f"   BUY signals: {buy_count} ({100*buy_count/total_rows:.1f}%)")
    logger.info(f"   SELL signals: {sell_count} ({100*sell_count/total_rows:.1f}%)")
    logger.info(f"   HOLD signals: {hold_count} ({100*hold_count/total_rows:.1f}%)")
    
    action_signals = buy_count + sell_count
    if action_signals == 0:
        logger.warning(f"\n⚠️  NO ACTION SIGNALS GENERATED")
        logger.warning(f"    All {total_rows} signals are HOLD")
        logger.warning(f"    This means thresholds filtered out all BUY/SELL signals")
        logger.warning(f"    Check: final_score distribution vs thresholds")
    else:
        logger.info(f"\n✓ ACTION SIGNALS: {action_signals} out of {total_rows} ({100*action_signals/total_rows:.1f}%)")
    
    # Score analysis
    if 'final_score' in df_signals.columns:
        scores = pd.to_numeric(df_signals['final_score'], errors='coerce')
        logger.info(f"\n📈 FINAL SCORE STATISTICS:")
        logger.info(f"   Min: {scores.min():.4f}")
        logger.info(f"   Max: {scores.max():.4f}")
        logger.info(f"   Mean: {scores.mean():.4f}")
        logger.info(f"   Median: {scores.median():.4f}")
        logger.info(f"   Std Dev: {scores.std():.4f}")
    
    # Threshold analysis
    logger.info(f"\n🎯 THRESHOLD ANALYSIS:")
    try:
        from core.engine.threshold_loader import load_thresholds
        thresholds = load_thresholds(prefer_candidates=True)
        default_thr = thresholds.get('default', {})
        buy_thr = default_thr.get('buy', 0.12)
        sell_thr = default_thr.get('sell', -0.10)
        
        logger.info(f"   Buy threshold: {buy_thr:.4f}")
        logger.info(f"   Sell threshold: {sell_thr:.4f}")
        
        if 'final_score' in df_signals.columns:
            scores = pd.to_numeric(df_signals['final_score'], errors='coerce')
            exceeds_buy = len(scores[scores > buy_thr])
            below_sell = len(scores[scores < sell_thr])
            
            logger.info(f"   Scores exceeding BUY threshold: {exceeds_buy}")
            logger.info(f"   Scores below SELL threshold: {below_sell}")
            
            if exceeds_buy == 0 and below_sell == 0:
                logger.warning(f"\n⚠️  THRESHOLD ISSUE DETECTED:")
                logger.warning(f"    No scores exceed thresholds")
                logger.warning(f"    Score range [{scores.min():.4f}, {scores.max():.4f}] doesn't cross thresholds [{sell_thr:.4f}, {buy_thr:.4f}]")
                logger.warning(f"    SOLUTION: Lower thresholds or check component score calculation")
    except Exception as e:
        logger.warning(f"Could not load thresholds: {e}")
    
    # Sample signals
    logger.info(f"\n📋 SAMPLE SIGNALS (first 5):")
    cols_to_show = ['underlying', 'strike', 'side', 'signal', 'final_score', 'pred_label']
    cols_to_show = [c for c in cols_to_show if c in df_signals.columns]
    
    if cols_to_show:
        sample = df_signals[cols_to_show].head(5)
        for idx, row in sample.iterrows():
            sig_str = f"[{row.get('signal', 'N/A')}]"
            score_str = f"score={row.get('final_score', 0):.4f}" if 'final_score' in row else ""
            logger.info(f"   {idx}: {row.get('underlying', 'N/A')} {row.get('strike', 'N/A')} {row.get('side', 'N/A')} {sig_str} {score_str}")
    
    # Check CSV write
    signals_csv = ROOT_DIR / "storage" / "live" / "angel_index_ai_signals.csv"
    if signals_csv.exists():
        csv_size = signals_csv.stat().st_size
        csv_rows = len(pd.read_csv(signals_csv)) if csv_size > 0 else 0
        logger.info(f"\n💾 CSV STATUS:")
        logger.info(f"   File: {signals_csv}")
        logger.info(f"   Rows: {csv_rows}")
        logger.info(f"   Size: {csv_size} bytes")
    
    logger.info("="*70 + "\n")


def check_dry_run_mode():
    """Verify DRY-RUN mode is enabled."""
    try:
        config_file = ROOT_DIR / "config" / "live_mode.json"
        if config_file.exists():
            import json
            with open(config_file) as f:
                config = json.load(f)
            
            dry_run = config.get('DRY_RUN_MODE', True)
            if dry_run:
                logger.info("✓ DRY-RUN MODE: ENABLED (safe for testing)")
            else:
                logger.warning("⚠️  DRY-RUN MODE: DISABLED (real trading may occur)")
            return dry_run
        else:
            logger.warning("Could not find live_mode.json")
            return None
    except Exception as e:
        logger.warning(f"Could not verify DRY-RUN mode: {e}")
        return None


def main():
    """Main execution."""
    logger.info("\n" + "="*70)
    logger.info("SYSTEM3 DEBUG SIGNALS PIPELINE - HEALTH CHECK")
    logger.info(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("="*70 + "\n")
    
    # Check DRY-RUN mode
    check_dry_run_mode()
    
    # Load snapshot
    df_snapshot = load_latest_snapshot()
    if df_snapshot is None:
        logger.error("Cannot proceed without snapshot")
        return 1
    
    # Run signal generation
    df_signals = run_signal_generation(df_snapshot)
    
    # Analyze results
    if df_signals is not None:
        analyze_signals(df_signals)
    
    logger.info(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
