"""
Feature Verification Script
Verifies that signal engine now provides all 40 features required by Ultra models
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))

from core.utils.logger import logger

# Expected features from Ultra models
EXPECTED_FEATURES = [
    "ltp", "spot", "moneyness", "atm_dist_abs", "atm_dist_pct",
    "ltp_chg_1_pct", "spot_chg_1_pct", "ltp_roll_std_5", "spot_roll_std_5",
    "ce_pe_diff", "ce_pe_ratio",
    "u_momentum_1", "u_momentum_3", "u_momentum_5", "u_momentum_10",
    "u_spot_momentum_1", "u_spot_momentum_3", "u_spot_momentum_5", "u_spot_momentum_10",
    "u_vol_short", "u_vol_long", "u_vol_ratio",
    "u_spot_vol_short", "u_spot_vol_long", "u_spot_vol_ratio",
    "u_moneyness_sq", "u_moneyness_cube", "u_moneyness_sqrt",
    "u_moneyness_x_score", "u_moneyness_x_conf", "u_score_x_conf",
    "u_regime_high_vol", "u_regime_low_vol",
    "u_hour", "u_minute",
    "u_is_win", "u_rolling_win_rate_5", "u_rolling_win_rate_10",
    "u_momentum_ratio_1_5", "u_ltp_percentile"
]

def verify_signal_csv_features():
    """Check if current signals CSV has all required features"""
    logger.info("=" * 80)
    logger.info("FEATURE VERIFICATION - Ultra Model Compatibility Check")
    logger.info("=" * 80)
    
    signals_csv = ROOT_DIR / "storage" / "live" / "angel_index_ai_signals.csv"
    
    if not signals_csv.exists():
        logger.error(f"Signals CSV not found: {signals_csv}")
        return False
    
    logger.info(f"Reading signals CSV: {signals_csv}")
    df = pd.read_csv(signals_csv)
    logger.info(f"Loaded {len(df)} rows × {len(df.columns)} columns")
    
    # Check for expected features
    missing_features = []
    present_features = []
    
    for feat in EXPECTED_FEATURES:
        if feat in df.columns:
            present_features.append(feat)
        else:
            missing_features.append(feat)
    
    logger.info("")
    logger.info(f"✅ PRESENT: {len(present_features)}/{len(EXPECTED_FEATURES)} features")
    logger.info(f"❌ MISSING: {len(missing_features)}/{len(EXPECTED_FEATURES)} features")
    logger.info("")
    
    if missing_features:
        logger.warning("Missing features:")
        for feat in missing_features:
            logger.warning(f"  - {feat}")
        logger.info("")
        logger.info("🔧 SOLUTION: Wait for next signal generation cycle (30-minute interval)")
        logger.info("   The patched signal engine will add these features automatically.")
        return False
    else:
        logger.info("🎉 ALL FEATURES PRESENT!")
        logger.info("")
        logger.info("Next steps:")
        logger.info("  1. Verify Ultra models load successfully (check logs for 'USING_ULTRA_MODEL')")
        logger.info("  2. Monitor signal distribution (should improve from 79% HOLD)")
        logger.info("  3. Verify ai_score is varied (not all 0.0000)")
        return True

if __name__ == "__main__":
    success = verify_signal_csv_features()
    
    if success:
        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ FEATURE VERIFICATION PASSED")
        logger.info("=" * 80)
        sys.exit(0)
    else:
        logger.info("")
        logger.info("=" * 80)
        logger.info("⏳ WAITING FOR NEXT SIGNAL GENERATION")
        logger.info("=" * 80)
        logger.info("")
        logger.info("The signal engine has been patched. Features will be added")
        logger.info("in the next 30-minute signal generation cycle.")
        sys.exit(1)
