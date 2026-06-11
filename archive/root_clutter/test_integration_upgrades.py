"""
Comprehensive Integration Test for Upgraded Signal Engine
Tests ensemble, regime, and multi-timeframe integrations
"""
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime
import logging

# Setup paths
ROOT_DIR = Path(__file__).parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_test_snapshot() -> pd.DataFrame:
    """Create a test snapshot DataFrame."""
    np.random.seed(42)
    n_rows = 50
    
    data = {
        "ts": [datetime.now().isoformat()] * n_rows,
        "underlying": ["NIFTY"] * n_rows,
        "expiry": ["30DEC2025"] * n_rows,
        "strike": np.linspace(22000, 24000, n_rows),
        "side": ["CE"] * (n_rows // 2) + ["PE"] * (n_rows // 2),
        "ltp": np.random.uniform(50, 500, n_rows),
        "spot": [23000.0] * n_rows,
        "iv": np.random.uniform(0.15, 0.35, n_rows),
        "volume": np.random.randint(100, 10000, n_rows),
        "oi": np.random.randint(1000, 50000, n_rows),
    }
    
    df = pd.DataFrame(data)
    
    # Add some Greeks
    df["delta"] = np.random.uniform(-1, 1, n_rows)
    df["gamma"] = np.random.uniform(0, 0.1, n_rows)
    df["theta"] = np.random.uniform(-50, 0, n_rows)
    df["vega"] = np.random.uniform(0, 100, n_rows)
    
    return df

def test_ensemble_integration():
    """Test that ensemble predictor is integrated."""
    logger.info("=" * 60)
    logger.info("TEST 1: Ensemble Integration")
    logger.info("=" * 60)
    
    try:
        from core.engine.ensemble_predictor import predict_with_ensemble
        
        df = create_test_snapshot()
        logger.info(f"Created test snapshot: {len(df)} rows")
        
        # Test ensemble prediction
        df_result = predict_with_ensemble(df.copy(), "NIFTY", use_dynamic_weights=True)
        
        # Check results
        assert "ai_score" in df_result.columns, "ai_score column missing"
        assert "ensemble_method" in df_result.columns, "ensemble_method column missing"
        
        logger.info(f"✅ Ensemble integration: PASSED")
        logger.info(f"   - ai_score range: [{df_result['ai_score'].min():.4f}, {df_result['ai_score'].max():.4f}]")
        logger.info(f"   - ensemble_method: {df_result['ensemble_method'].iloc[0] if len(df_result) > 0 else 'N/A'}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Ensemble integration: FAILED - {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def test_regime_classification():
    """Test that regime classification is integrated."""
    logger.info("=" * 60)
    logger.info("TEST 2: Regime Classification Integration")
    logger.info("=" * 60)
    
    try:
        from core.engine.angel_market_regime_classifier import classify_market_regime, adjust_strategy_for_regime
        
        df = create_test_snapshot()
        
        # Test regime classification
        regime = classify_market_regime(df)
        logger.info(f"Detected regime: {regime}")
        
        # Test strategy adjustment
        strategy_result = adjust_strategy_for_regime(regime, previous_regime=None)
        logger.info(f"Strategy result: {strategy_result}")
        
        assert regime in ["TRENDING_UP", "TRENDING_DOWN", "RANGING", "VOLATILE", "CALM", "UNKNOWN"], \
            f"Invalid regime: {regime}"
        assert "strategy" in strategy_result, "Strategy missing from result"
        
        logger.info(f"✅ Regime classification: PASSED")
        logger.info(f"   - Regime: {regime}")
        logger.info(f"   - Strategy: {strategy_result.get('strategy', 'N/A')}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Regime classification: FAILED - {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def test_multi_timeframe_confirmation():
    """Test that multi-timeframe confirmation is integrated."""
    logger.info("=" * 60)
    logger.info("TEST 3: Multi-Timeframe Confirmation Integration")
    logger.info("=" * 60)
    
    try:
        from core.engine.angel_multi_timeframe_confirmation import check_multi_timeframe_confirmation
        
        df = create_test_snapshot()
        df["pred_label"] = ["BUY"] * (len(df) // 3) + ["SELL"] * (len(df) // 3) + ["HOLD"] * (len(df) - 2 * (len(df) // 3))
        df["pred_confidence"] = np.random.uniform(0.5, 0.9, len(df))
        
        # Test multi-timeframe confirmation
        df_result = check_multi_timeframe_confirmation(df.copy(), timeframes=None, timeframe_data=None)
        
        # Check results
        assert "confirmation_score" in df_result.columns, "confirmation_score column missing"
        assert "confirmed_signal" in df_result.columns, "confirmed_signal column missing"
        assert "timeframe_agreement" in df_result.columns, "timeframe_agreement column missing"
        
        confirmed_count = (df_result["confirmed_signal"] == True).sum()
        logger.info(f"✅ Multi-timeframe confirmation: PASSED")
        logger.info(f"   - Confirmed signals: {confirmed_count}/{len(df_result)}")
        logger.info(f"   - Avg confirmation score: {df_result['confirmation_score'].mean():.4f}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Multi-timeframe confirmation: FAILED - {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def test_end_to_end_signal_generation():
    """Test end-to-end signal generation with all integrations."""
    logger.info("=" * 60)
    logger.info("TEST 4: End-to-End Signal Generation")
    logger.info("=" * 60)
    
    try:
        from core.engine.system3_signal_engine import run_signal_engine
        
        df = create_test_snapshot()
        logger.info(f"Created test snapshot: {len(df)} rows")
        
        # Run signal engine
        df_signals = run_signal_engine(df, enable_safety_checks=False)
        
        # Check results
        assert not df_signals.empty, "Signal generation returned empty DataFrame"
        assert "signal" in df_signals.columns, "signal column missing"
        assert "final_score" in df_signals.columns, "final_score column missing"
        
        # Check for new columns from integrations
        ensemble_columns = ["ensemble_method", "ensemble_models_used", "ensemble_model_count"]
        regime_columns = ["market_regime", "strategy_name", "strategy_switched"]
        mtf_columns = ["confirmation_score", "confirmed_signal", "timeframe_agreement"]
        
        ensemble_found = any(col in df_signals.columns for col in ensemble_columns)
        regime_found = any(col in df_signals.columns for col in regime_columns)
        mtf_found = any(col in df_signals.columns for col in mtf_columns)
        
        signal_counts = df_signals["signal"].value_counts()
        
        logger.info(f"✅ End-to-end signal generation: PASSED")
        logger.info(f"   - Signals generated: {len(df_signals)}")
        logger.info(f"   - Signal distribution: {dict(signal_counts)}")
        logger.info(f"   - Ensemble columns present: {ensemble_found}")
        logger.info(f"   - Regime columns present: {regime_found}")
        logger.info(f"   - Multi-TF columns present: {mtf_found}")
        
        return True
    except Exception as e:
        logger.error(f"❌ End-to-end signal generation: FAILED - {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def test_dashboard_compatibility():
    """Test that new columns don't break dashboard."""
    logger.info("=" * 60)
    logger.info("TEST 5: Dashboard Compatibility")
    logger.info("=" * 60)
    
    try:
        from core.engine.system3_signal_engine import run_signal_engine
        
        df = create_test_snapshot()
        df_signals = run_signal_engine(df, enable_safety_checks=False)
        
        # Required columns for dashboard
        required_columns = [
            "ts", "underlying", "strike", "side", "ltp", "spot",
            "signal", "final_score", "ai_score", "confidence"
        ]
        
        missing_columns = [col for col in required_columns if col not in df_signals.columns]
        
        if missing_columns:
            logger.warning(f"⚠️  Missing required columns: {missing_columns}")
            return False
        
        # Check data types
        numeric_columns = ["final_score", "ai_score", "confidence"]
        for col in numeric_columns:
            if col in df_signals.columns:
                if not pd.api.types.is_numeric_dtype(df_signals[col]):
                    logger.warning(f"⚠️  Column {col} is not numeric")
                    return False
        
        logger.info(f"✅ Dashboard compatibility: PASSED")
        logger.info(f"   - All required columns present")
        logger.info(f"   - Data types correct")
        
        return True
    except Exception as e:
        logger.error(f"❌ Dashboard compatibility: FAILED - {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def main():
    """Run all tests."""
    logger.info("=" * 60)
    logger.info("COMPREHENSIVE INTEGRATION TEST SUITE")
    logger.info("=" * 60)
    logger.info(f"Started at: {datetime.now().isoformat()}")
    logger.info("")
    
    results = {}
    
    # Run all tests
    results["ensemble"] = test_ensemble_integration()
    logger.info("")
    
    results["regime"] = test_regime_classification()
    logger.info("")
    
    results["multi_timeframe"] = test_multi_timeframe_confirmation()
    logger.info("")
    
    results["end_to_end"] = test_end_to_end_signal_generation()
    logger.info("")
    
    results["dashboard"] = test_dashboard_compatibility()
    logger.info("")
    
    # Summary
    logger.info("=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"  {test_name}: {status}")
    
    logger.info("")
    logger.info(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 ALL TESTS PASSED!")
        return 0
    else:
        logger.error(f"⚠️  {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    exit(main())
