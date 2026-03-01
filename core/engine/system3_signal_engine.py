"""
System3 Signal Engine - Complete signal generation pipeline

Integrates all engines:
- Greeks Engine
- Trend Model
- Volatility Model
- Breakout Model
- Momentum Model
- Entry/Exit Engine
- Scoring Engine
- AI Model

Outputs to: storage/live/angel_index_ai_signals.csv
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Ensure project root is in path
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.utils.logger import logger

# Import all engines
from core.engine.greeks_engine import compute_greeks_for_df
from core.engine.trend_model import compute_trend_features, compute_multi_timeframe_trend
from core.engine.volatility_model import compute_volatility_features, detect_volatility_regime
from core.engine.breakout_model import detect_breakouts
from core.engine.momentum_model import compute_momentum_features
from core.engine.entry_exit_engine import compute_entry_signals, compute_exit_signals, compute_dynamic_sl_tp
from core.engine.scoring_engine import compute_final_score, generate_signals
from core.engine.ai_model import (
    train_ml_model,
    predict_direction,
    get_training_dataframe,
)
from core.engine.ultra_models_loader import load_ultra_model

# UPGRADED: Import advanced ensemble, regime, and multi-timeframe functions
try:
    from core.engine.ensemble_predictor import predict_with_ensemble

    ENSEMBLE_AVAILABLE = True
except ImportError:
    ENSEMBLE_AVAILABLE = False
    logger.warning("Ensemble predictor not available, will use Ultra/delta fallback")

try:
    from core.engine.angel_market_regime_classifier import classify_market_regime, adjust_strategy_for_regime

    REGIME_AVAILABLE = True
except ImportError:
    REGIME_AVAILABLE = False
    logger.warning("Market regime classifier not available")

try:
    from core.engine.angel_multi_timeframe_confirmation import check_multi_timeframe_confirmation

    MULTI_TF_AVAILABLE = True
except ImportError:
    MULTI_TF_AVAILABLE = False
    logger.warning("Multi-timeframe confirmation not available")

# Output path
LIVE_DIR = ROOT_DIR / "storage" / "live"
LIVE_DIR.mkdir(parents=True, exist_ok=True)
SIGNALS_CSV = LIVE_DIR / "angel_index_ai_signals.csv"


def load_recent_signal_history(
    history_path: Path,
    max_rows: int = 5000,
) -> Optional[pd.DataFrame]:
    """
    System3 AI upgrade: Load recent signal history from CSV.

    Args:
        history_path: Path to angel_index_ai_signals.csv
        max_rows: Max number of recent rows to keep

    Returns:
        DataFrame with recent history or None if unavailable
    """
    if not history_path.exists():
        logger.info(
            "History CSV not found for short-history features: %s",
            history_path,
        )
        return None

    try:
        hist_df = pd.read_csv(history_path)
    except Exception:
        # Be lenient with malformed historical rows, similar to test-mode
        try:
            hist_df = pd.read_csv(history_path, engine="python", on_bad_lines="skip")
            logger.warning("Some malformed lines were skipped while reading recent signal history.")
        except Exception as exc:
            logger.warning("Failed to load recent signal history: %s", exc)
            return None

    if hist_df.empty:
        return None

    if len(hist_df) > max_rows:
        hist_df = hist_df.tail(max_rows)

    # Parse timestamp column if present
    ts_col = None
    for cand in ["ts", "timestamp", "time"]:
        if cand in hist_df.columns:
            ts_col = cand
            break
    if ts_col:
        hist_df[ts_col] = pd.to_datetime(hist_df[ts_col], errors="coerce")

    return hist_df


def compute_short_history_features(
    history_df: Optional[pd.DataFrame],
    snapshot_df: pd.DataFrame,
    min_history_points: int = 5,
) -> pd.DataFrame:
    """
    System3 AI upgrade: Compute short-term trend/vol/momentum features
    from recent intraday history and merge onto the current snapshot.
    """
    if history_df is None or history_df.empty:
        return snapshot_df
    if snapshot_df.empty:
        return snapshot_df

    df_hist = history_df.copy()
    df_snap = snapshot_df.copy()

    key_cols = ["underlying", "strike", "side"]
    for col in key_cols:
        if col not in df_hist.columns or col not in df_snap.columns:
            return df_snap

    # Choose a price column from history
    price_col_hist = None
    for cand in ["ltp", "spot", "close", "price"]:
        if cand in df_hist.columns:
            price_col_hist = cand
            break
    if price_col_hist is None:
        return df_snap

    df_hist[price_col_hist] = pd.to_numeric(
        df_hist[price_col_hist],
        errors="coerce",
    ).fillna(0.0)

    short_return_map: Dict[Any, float] = {}
    short_vol_map: Dict[Any, float] = {}
    short_mom_map: Dict[Any, float] = {}

    grouped = df_hist.groupby(key_cols)
    for group_key, g in grouped:
        if len(g) < min_history_points:
            continue

        window = g.tail(20)
        prices = window[price_col_hist].astype(float)
        if prices.empty:
            continue

        first_price = prices.iloc[0]
        last_price = prices.iloc[-1]
        if first_price <= 0:
            short_ret = 0.0
        else:
            short_ret = (last_price / first_price) - 1.0

        returns = prices.pct_change().dropna()
        short_vol = float(returns.std()) if not returns.empty else 0.0

        if len(prices) > 1:
            short_mom = float(prices.iloc[-1] - prices.iloc[-2])
        else:
            short_mom = 0.0

        short_return_map[group_key] = float(np.tanh(short_ret * 5.0))
        short_vol_map[group_key] = float(np.clip(short_vol * 20.0, 0.0, 2.0))
        scale_den = max(last_price, 1.0)
        short_mom_map[group_key] = float(
            np.tanh(short_mom / scale_den * 10.0),
        )

    df_snap["short_return"] = 0.0
    df_snap["short_vol"] = 0.0
    df_snap["short_momentum"] = 0.0

    for idx, row in df_snap.iterrows():
        key = (row.get("underlying"), row.get("strike"), row.get("side"))
        if key in short_return_map:
            df_snap.at[idx, "short_return"] = short_return_map[key]
            df_snap.at[idx, "short_vol"] = short_vol_map.get(key, 0.0)
            df_snap.at[idx, "short_momentum"] = short_mom_map.get(key, 0.0)

    return df_snap


def process_snapshot(df_snap: pd.DataFrame) -> pd.DataFrame:
    """
    Process a snapshot DataFrame through the complete signal engine.

    Args:
        df_snap: Snapshot DataFrame with columns: ts, underlying, expiry, strike, side, ltp, spot

    Returns:
        DataFrame with all signals and final score
    """
    if df_snap is None or df_snap.empty:
        logger.warning("Empty snapshot provided to signal engine")
        return pd.DataFrame()

    # INSTRUMENTATION: Track rows through signal generation pipeline
    INITIAL_ROW_COUNT = len(df_snap)
    logger.info(f"🔍 SIGNAL PIPELINE START: {INITIAL_ROW_COUNT} rows in snapshot")

    df = df_snap.copy()

    # Ensure required columns
    required_cols = ["spot", "strike", "ltp", "side"]
    for col in required_cols:
        if col not in df.columns:
            logger.warning("Missing required column: %s", col)
            df[col] = 0.0

    # System3 AI upgrade: enrich with recent history before feature computation
    try:
        hist_df = load_recent_signal_history(SIGNALS_CSV, max_rows=5000)
        df = compute_short_history_features(hist_df, df, min_history_points=5)
    except Exception as exc:
        logger.warning("Short-history feature enrichment failed: %s", exc)

    # Step 1: Compute Greeks
    logger.info("Step 1: Computing Greeks...")
    try:
        df = compute_greeks_for_df(df)
        # Verify Greeks were computed
        if "delta" not in df.columns or df["delta"].isna().all():
            logger.warning("Greeks computation returned NaN, setting defaults")
            df["delta"] = 0.0
            df["gamma"] = 0.0
            df["theta"] = 0.0
            df["vega"] = 0.0
        logger.info("✓ Greeks computed")
    except Exception as e:
        logger.error(f"Error computing Greeks: {e}")
        import traceback

        logger.error(traceback.format_exc())
        df["delta"] = 0.0
        df["gamma"] = 0.0
        df["theta"] = 0.0
        df["vega"] = 0.0

    # Step 2: Compute Trend Features
    logger.info("Step 2: Computing trend features...")
    try:
        # Base proxy using moneyness
        if "spot" in df.columns and "strike" in df.columns:
            moneyness = (df["spot"] - df["strike"]) / df["strike"].replace(0, 1)
            if "side" in df.columns:
                trend_proxy = moneyness.where(df["side"] == "CE", -moneyness)
            else:
                trend_proxy = moneyness
            base_trend = trend_proxy.clip(-1.0, 1.0).fillna(0.0)
        else:
            base_trend = pd.Series(0.0, index=df.index)

        # System3 AI upgrade: blend in short_return from intraday history if available
        if "short_return" in df.columns:
            hist_trend = df["short_return"].clip(-1.0, 1.0).fillna(0.0)
            df["trend_score"] = (0.5 * base_trend + 0.5 * hist_trend).clip(-1.0, 1.0)
        else:
            df["trend_score"] = base_trend

        df["multi_tf_trend_score"] = df["trend_score"]
        df["rsi"] = 50.0 + (df["trend_score"] * 20.0).clip(-20, 20)

        # Try full trend computation if we have enough data
        try:
            df = compute_trend_features(df, price_col="spot")
            df = compute_multi_timeframe_trend(df, price_col="spot")
            # If full computation resulted in zeros, keep our proxy
            if (df["trend_score"].abs() < 0.001).all() and "spot" in df.columns:
                moneyness = (df["spot"] - df["strike"]) / df["strike"].replace(0, 1)
                if "side" in df.columns:
                    trend_proxy = moneyness.where(df["side"] == "CE", -moneyness)
                else:
                    trend_proxy = moneyness
                df["trend_score"] = trend_proxy.clip(-1.0, 1.0).fillna(0.0) * 0.4
                df["multi_tf_trend_score"] = df["trend_score"]
        except:
            pass  # Use fallback values above

        logger.info("✓ Trend features computed")
    except Exception as e:
        logger.error(f"Error computing trend features: {e}")
        df["rsi"] = 50.0
        df["trend_score"] = 0.0
        df["multi_tf_trend_score"] = 0.0

    # Step 3: Compute Volatility Features
    logger.info("Step 3: Computing volatility features...")
    try:
        # Ensure IV exists
        if "iv" not in df.columns:
            if "iv_estimate" in df.columns:
                df["iv"] = df["iv_estimate"]
            else:
                # Create IV proxy from time value
                if "ltp" in df.columns and "spot" in df.columns and "strike" in df.columns:
                    intrinsic_ce = (df["spot"] - df["strike"]).clip(0, None)
                    intrinsic_pe = (df["strike"] - df["spot"]).clip(0, None)
                    intrinsic = (
                        intrinsic_ce.where(df["side"] == "CE", intrinsic_pe) if "side" in df.columns else intrinsic_ce
                    )
                    time_value = (df["ltp"] - intrinsic).clip(0, None)
                    # IV proxy: time value relative to spot
                    df["iv"] = (time_value / df["spot"].replace(0, 1)).clip(0, 0.5).fillna(0.2)
                else:
                    df["iv"] = 0.2  # Default 20% IV

        df = compute_volatility_features(df, iv_col="iv")
        df = detect_volatility_regime(df, iv_col="iv")

        # If volatility_score is still zero, create from IV and short_vol
        if "volatility_score" in df.columns and (df["volatility_score"].abs() < 0.001).all():
            vol_from_iv = 0.0
            if "iv_percentile" in df.columns:
                vol_from_iv = ((df["iv_percentile"] - 50.0) / 50.0).clip(-1.0, 1.0).fillna(0.0) * 0.3
            vol_from_hist = 0.0
            if "short_vol" in df.columns:
                # Map short_vol (0..~2) to 0..1
                vol_from_hist = (df["short_vol"] / 2.0).clip(0.0, 1.0).fillna(0.0) * 0.5
            df["volatility_score"] = (vol_from_iv + vol_from_hist).clip(-1.0, 1.0)

        logger.info("✓ Volatility features computed")
    except Exception as e:
        logger.error(f"Error computing volatility features: {e}")
        df["iv_percentile"] = 50.0
        df["iv_rank"] = 50.0
        df["volatility_score"] = 0.0

    # Step 4: Detect Breakouts
    logger.info("Step 4: Detecting breakouts...")
    try:
        # For single snapshot, create breakout proxy based on price action
        if "spot" in df.columns and "strike" in df.columns:
            # Breakout proxy: how far is spot from strike
            breakout_proxy = (df["spot"] - df["strike"]) / df["strike"].replace(0, 1)
            df["breakout_score"] = breakout_proxy.clip(-1.0, 1.0).fillna(0.0)
        else:
            df["breakout_score"] = 0.0

        # Try full breakout detection if we have enough data
        try:
            df = detect_breakouts(df, price_col="spot")
        except:
            pass  # Use fallback values above

        logger.info("✓ Breakouts detected")
    except Exception as e:
        logger.error(f"Error detecting breakouts: {e}")
        df["breakout_score"] = 0.0

    # Step 5: Compute Momentum
    logger.info("Step 5: Computing momentum...")
    try:
        # Base proxy from option time value
        if "ltp" in df.columns and "spot" in df.columns and "strike" in df.columns:
            intrinsic_ce = (df["spot"] - df["strike"]).clip(0, None)
            intrinsic_pe = (df["strike"] - df["spot"]).clip(0, None)
            intrinsic = intrinsic_ce.where(df["side"] == "CE", intrinsic_pe)
            time_value = df["ltp"] - intrinsic
            momentum_proxy = (time_value / df["ltp"].replace(0, 1)).clip(0, 1) * 2.0 - 1.0
            base_mom = momentum_proxy.fillna(0.0)
        else:
            base_mom = pd.Series(0.0, index=df.index)

        # System3 AI upgrade: blend in short_momentum from history if available
        if "short_momentum" in df.columns:
            hist_mom = df["short_momentum"].clip(-1.0, 1.0).fillna(0.0)
            df["momentum_score"] = (0.5 * base_mom + 0.5 * hist_mom).clip(-1.0, 1.0)
        else:
            df["momentum_score"] = base_mom

        # Try full momentum computation if we have enough data
        try:
            df = compute_momentum_features(df, price_col="spot")
        except:
            pass  # Use fallback values above

        logger.info("✓ Momentum computed")
    except Exception as e:
        logger.error(f"Error computing momentum: {e}")
        df["momentum_score"] = 0.0

    # Step 5.5: PHASE 391 FIX - Add Ultra Model Required Features
    logger.info("Step 5.5: Adding Ultra Model required features...")
    try:
        # Price & Moneyness Features
        if "spot" in df.columns and "strike" in df.columns:
            if "moneyness" not in df.columns:
                df["moneyness"] = (df["spot"] - df["strike"]) / df["strike"].replace(0, 1)
            df["atm_dist_pct"] = ((df["spot"] - df["strike"]) / df["strike"].replace(0, 1)) * 100
            df["atm_dist_abs"] = np.abs(df["atm_dist_pct"])
            df["u_moneyness_sq"] = df["moneyness"] ** 2
            df["u_moneyness_cube"] = df["moneyness"] ** 3
            df["u_moneyness_sqrt"] = np.sign(df["moneyness"]) * np.sqrt(np.abs(df["moneyness"]))
        else:
            if "moneyness" not in df.columns:
                df["moneyness"] = 0.0
            df["atm_dist_pct"] = 0.0
            df["atm_dist_abs"] = 0.0
            df["u_moneyness_sq"] = 0.0
            df["u_moneyness_cube"] = 0.0
            df["u_moneyness_sqrt"] = 0.0

        # CE/PE Spread Features
        if "ltp" in df.columns and "side" in df.columns:
            ce_ltp = df.loc[df["side"] == "CE", "ltp"].mean() if (df["side"] == "CE").any() else df["ltp"].mean()
            pe_ltp = df.loc[df["side"] == "PE", "ltp"].mean() if (df["side"] == "PE").any() else df["ltp"].mean()
            df["ce_pe_ratio"] = ce_ltp / (pe_ltp + 1e-8)
            df["ce_pe_diff"] = ce_ltp - pe_ltp
        else:
            df["ce_pe_ratio"] = 1.0
            df["ce_pe_diff"] = 0.0

        # Price Change Features
        if "ltp" in df.columns:
            df["ltp_chg_1_pct"] = df.groupby(["underlying", "strike", "side"])["ltp"].pct_change() * 100
            df["ltp_chg_1_pct"] = df["ltp_chg_1_pct"].fillna(0.0)
        else:
            df["ltp_chg_1_pct"] = 0.0

        if "spot" in df.columns:
            df["spot_chg_1_pct"] = df.groupby("underlying")["spot"].pct_change() * 100
            df["spot_chg_1_pct"] = df["spot_chg_1_pct"].fillna(0.0)
        else:
            df["spot_chg_1_pct"] = 0.0

        # Rolling Volatility
        if "ltp" in df.columns:
            df["ltp_roll_std_5"] = (
                df.groupby(["underlying", "strike", "side"])["ltp"]
                .transform(lambda x: x.rolling(5, min_periods=1).std())
                .fillna(0.0)
            )
        else:
            df["ltp_roll_std_5"] = 0.0

        if "spot" in df.columns:
            df["spot_roll_std_5"] = (
                df.groupby("underlying")["spot"].transform(lambda x: x.rolling(5, min_periods=1).std()).fillna(0.0)
            )
        else:
            df["spot_roll_std_5"] = 0.0

        # Momentum Features (u_momentum_1, 3, 5, 10)
        for period in [1, 3, 5, 10]:
            col_name = f"u_momentum_{period}"
            if "ltp" in df.columns:
                df[col_name] = (
                    df.groupby(["underlying", "strike", "side"])["ltp"]
                    .transform(lambda x: x.diff(period) / (x.shift(period) + 1e-8))
                    .fillna(0.0)
                )
            else:
                df[col_name] = 0.0

        # Spot Momentum Features (u_spot_momentum_1, 3, 5, 10)
        for period in [1, 3, 5, 10]:
            col_name = f"u_spot_momentum_{period}"
            if "spot" in df.columns:
                df[col_name] = (
                    df.groupby("underlying")["spot"]
                    .transform(lambda x: x.diff(period) / (x.shift(period) + 1e-8))
                    .fillna(0.0)
                )
            else:
                df[col_name] = 0.0

        df["u_momentum_ratio_1_5"] = df.get("u_momentum_1", 0.0) / (np.abs(df.get("u_momentum_5", 0.0)) + 1e-8)

        # Volatility Regime Features
        if "ltp" in df.columns:
            df["u_vol_short"] = (
                df.groupby(["underlying", "strike", "side"])["ltp"]
                .transform(lambda x: x.rolling(5, min_periods=1).std())
                .fillna(0.0)
            )
            df["u_vol_long"] = (
                df.groupby(["underlying", "strike", "side"])["ltp"]
                .transform(lambda x: x.rolling(20, min_periods=1).std())
                .fillna(0.0)
            )
            df["u_vol_ratio"] = df["u_vol_short"] / (df["u_vol_long"] + 1e-8)
        else:
            df["u_vol_short"] = 0.0
            df["u_vol_long"] = 0.0
            df["u_vol_ratio"] = 1.0

        if "spot" in df.columns:
            df["u_spot_vol_short"] = (
                df.groupby("underlying")["spot"].transform(lambda x: x.rolling(5, min_periods=1).std()).fillna(0.0)
            )
            df["u_spot_vol_long"] = (
                df.groupby("underlying")["spot"].transform(lambda x: x.rolling(20, min_periods=1).std()).fillna(0.0)
            )
            df["u_spot_vol_ratio"] = df["u_spot_vol_short"] / (df["u_spot_vol_long"] + 1e-8)
        else:
            df["u_spot_vol_short"] = 0.0
            df["u_spot_vol_long"] = 0.0
            df["u_spot_vol_ratio"] = 1.0

        df["u_regime_high_vol"] = (df["u_vol_ratio"] > 1.5).astype(int)
        df["u_regime_low_vol"] = (df["u_vol_ratio"] < 0.7).astype(int)

        # Time Features
        if "ts" in df.columns:
            ts_series = pd.to_datetime(df["ts"], errors="coerce")
            df["u_hour"] = ts_series.dt.hour.fillna(12).astype(int)
            df["u_minute"] = ts_series.dt.minute.fillna(0).astype(int)
        else:
            df["u_hour"] = 12
            df["u_minute"] = 0

        # Cross Features (require ai_score - compute after AI prediction)
        df["confidence"] = 0.5  # Placeholder, will be updated after AI
        df["u_moneyness_x_score"] = 0.0  # Will be computed after AI
        df["u_moneyness_x_conf"] = 0.0
        df["u_score_x_conf"] = 0.0

        # Win Rate Features (placeholder)
        df["u_is_win"] = 0.5
        df["u_rolling_win_rate_5"] = 0.5
        df["u_rolling_win_rate_10"] = 0.5

        # Percentile Features
        if "ltp" in df.columns:
            df["u_ltp_percentile"] = (
                df.groupby(["underlying", "strike", "side"])["ltp"]
                .transform(lambda x: x.rank(pct=True) * 100)
                .fillna(50.0)
            )
        else:
            df["u_ltp_percentile"] = 50.0

        logger.info("✓ Ultra Model features added successfully")
    except Exception as e:
        logger.error(f"Error adding Ultra Model features: {e}")
        import traceback

        logger.error(traceback.format_exc())

    # Step 6: AI Model Prediction (UPGRADED: Ensemble Predictor with 5-7 models)
    logger.info("Step 6: Running AI model (Ensemble Predictor / Ultra Models / Delta Fallback)...")
    try:
        underlying = df["underlying"].iloc[0] if "underlying" in df.columns and len(df) > 0 else None

        # UPGRADED: Try ensemble predictor first (5-7 models with dynamic weighting)
        ensemble_used = False
        if ENSEMBLE_AVAILABLE and underlying:
            try:
                logger.info(f"Attempting ensemble prediction for {underlying}...")
                df_ensemble = predict_with_ensemble(df.copy(), underlying, use_dynamic_weights=True)

                if "ai_score" in df_ensemble.columns and not df_ensemble["ai_score"].isna().all():
                    # Use ensemble prediction
                    df["ai_score"] = df_ensemble["ai_score"].fillna(0.0)
                    df["ensemble_method"] = df_ensemble.get("ensemble_method", "ensemble")
                    df["ensemble_models_used"] = df_ensemble.get("ensemble_models_used", "unknown")
                    df["ensemble_model_count"] = df_ensemble.get("ensemble_model_count", 0)

                    # Calculate confidence from ensemble
                    if "ensemble_confidence" in df_ensemble.columns:
                        df["confidence"] = df_ensemble["ensemble_confidence"].fillna(0.0)
                    else:
                        df["confidence"] = np.abs(df["ai_score"]).clip(0.0, 1.0)

                    ensemble_used = True
                    logger.info(
                        f"✓ USING_ENSEMBLE_PREDICTOR for {underlying} ({df['ensemble_model_count'].iloc[0]} models, method={df['ensemble_method'].iloc[0]})"
                    )
                else:
                    logger.warning(f"Ensemble prediction returned invalid results, falling back to Ultra/delta")
            except Exception as e:
                logger.warning(f"Ensemble prediction failed for {underlying}: {e}, falling back to Ultra/delta")

        # Fallback: Try Ultra model (original Phase 381-388 logic)
        if not ensemble_used:
            ultra_model = None
            if underlying:
                ultra_model = load_ultra_model(underlying)
                if ultra_model:
                    try:
                        df = predict_direction(ultra_model, df)
                        logger.info(f"✓ USING_ULTRA_MODEL for {underlying}")
                        # Check if AI scores are varied
                        if "ai_score" in df.columns:
                            unique_scores = df["ai_score"].nunique()
                            if unique_scores == 1:
                                logger.warning(
                                    f"Ultra model returning same score for all signals "
                                    f"({df['ai_score'].iloc[0]:.4f}), using delta fallback"
                                )
                                ultra_model = None  # Trigger fallback
                    except Exception as e:
                        logger.warning(f"Ultra model failed for {underlying}: {e}, using delta fallback")
                        ultra_model = None

            # Final fallback: Delta-based scoring
            if not ultra_model:
                logger.info(f"USING_DELTA_FALLBACK for {underlying or 'unknown'} (no ensemble/ultra model available)")

                if "delta" in df.columns:
                    delta_proxy = df["delta"].copy()
                    if "side" in df.columns:
                        delta_proxy = delta_proxy.where(df["side"] == "CE", -delta_proxy)
                    df["ai_score"] = (delta_proxy * 2.0 - 1.0).clip(-1.0, 1.0).fillna(0.0) * 0.3
                else:
                    df["ai_score"] = 0.0

                # Set default confidence for delta fallback
                if "confidence" not in df.columns:
                    df["confidence"] = 0.3  # Lower confidence for delta fallback

        # Ensure confidence is set
        if "confidence" not in df.columns:
            df["confidence"] = np.abs(df.get("ai_score", 0.0))

        logger.info("✓ AI model prediction completed")

        # Update cross-features now that ai_score is available
        df["u_moneyness_x_score"] = df.get("moneyness", 0.0) * df.get("ai_score", 0.0)
        df["u_moneyness_x_conf"] = df.get("moneyness", 0.0) * df["confidence"]
        df["u_score_x_conf"] = df.get("ai_score", 0.0) * df["confidence"]

    except Exception as e:
        logger.error(f"Error in AI model: {e}")
        import traceback

        logger.error(traceback.format_exc())
        # Fallback: use delta-based AI score
        if "delta" in df.columns:
            delta_proxy = df["delta"].copy()
            if "side" in df.columns:
                delta_proxy = delta_proxy.where(df["side"] == "CE", -delta_proxy)
            df["ai_score"] = (delta_proxy * 2.0 - 1.0).clip(-1.0, 1.0).fillna(0.0) * 0.3
        else:
            df["ai_score"] = 0.0

        # Update cross-features even in fallback case
        df["confidence"] = np.abs(df.get("ai_score", 0.0))
        df["u_moneyness_x_score"] = df.get("moneyness", 0.0) * df.get("ai_score", 0.0)
        df["u_moneyness_x_conf"] = df.get("moneyness", 0.0) * df["confidence"]
        df["u_score_x_conf"] = df.get("ai_score", 0.0) * df["confidence"]

    # Step 7: Compute Final Score
    logger.info("Step 7: Computing final score...")
    try:
        # Ensure all component scores exist and have values
        # Greeks score from delta
        if "greeks_score" not in df.columns:
            if "delta" in df.columns:
                delta_score = df["delta"].copy().fillna(0.0)
                if "side" in df.columns:
                    delta_score = delta_score.where(df["side"] == "CE", -delta_score)
                df["greeks_score"] = (delta_score * 2.0 - 1.0).clip(-1.0, 1.0).fillna(0.0)
            else:
                df["greeks_score"] = 0.0

        # Trend score
        if "trend_score" not in df.columns:
            if "multi_tf_trend_score" in df.columns:
                df["trend_score"] = df["multi_tf_trend_score"].fillna(0.0)
            else:
                df["trend_score"] = 0.0

        # Volatility score
        if "volatility_score" not in df.columns:
            df["volatility_score"] = 0.0

        # Breakout score
        if "breakout_score" not in df.columns:
            df["breakout_score"] = 0.0

        # Momentum score
        if "momentum_score" not in df.columns:
            df["momentum_score"] = 0.0

        # AI score
        if "ai_score" not in df.columns:
            if "expected_move_score" in df.columns:
                df["ai_score"] = df["expected_move_score"].fillna(0.0)
            else:
                df["ai_score"] = 0.0

        # Fill all NaN values and ensure we have at least some non-zero values
        component_cols = [
            "greeks_score",
            "trend_score",
            "volatility_score",
            "breakout_score",
            "momentum_score",
            "ai_score",
        ]
        for col in component_cols:
            df[col] = df[col].fillna(0.0)
            # Log sample values for debugging
            if len(df) > 0:
                sample_val = df[col].iloc[0]
                non_zero_count = (df[col].abs() > 0.001).sum()
                logger.info(f"  {col}: sample={sample_val:.4f}, non-zero={non_zero_count}/{len(df)}")

        # If all components are zero, create at least one non-zero component from available data
        all_zero = (
            (df["greeks_score"].abs() < 0.001).all()
            & (df["trend_score"].abs() < 0.001).all()
            & (df["volatility_score"].abs() < 0.001).all()
            & (df["breakout_score"].abs() < 0.001).all()
            & (df["momentum_score"].abs() < 0.001).all()
            & (df["ai_score"].abs() < 0.001).all()
        )

        if all_zero and len(df) > 0:
            logger.warning("All component scores are zero, creating fallback scores from raw data")
            # Create fallback scores from available data
            if "spot" in df.columns and "strike" in df.columns:
                # Moneyness-based trend score
                moneyness = (df["spot"] - df["strike"]) / df["strike"].replace(0, 1)
                df["trend_score"] = moneyness.clip(-1.0, 1.0).fillna(0.0) * 0.5  # Scale down
                logger.info(f"  Created fallback trend_score: {df['trend_score'].iloc[0]:.4f}")

            if "delta" in df.columns:
                # Use delta directly as greeks score
                delta_score = df["delta"].copy().fillna(0.0)
                if "side" in df.columns:
                    delta_score = delta_score.where(df["side"] == "CE", -delta_score)
                df["greeks_score"] = (delta_score * 2.0 - 1.0).clip(-1.0, 1.0).fillna(0.0) * 0.3
                logger.info(f"  Created fallback greeks_score: {df['greeks_score'].iloc[0]:.4f}")

        # Compute final score
        df = compute_final_score(df)

        # Verify final score was computed
        if "final_score" not in df.columns:
            logger.error("Final score column not created!")
            df["final_score"] = 0.0
        else:
            # Ensure no NaN values
            df["final_score"] = df["final_score"].fillna(0.0)
            # Check for zeros
            zero_count = (df["final_score"].abs() < 0.0001).sum()
            non_zero_final = len(df) - zero_count
            logger.info(f"✓ Final score computed: {non_zero_final}/{len(df)} non-zero scores")
            if zero_count > 0:
                logger.warning(f"  {zero_count} signals have zero/near-zero scores")
                # Force at least small non-zero values if all components aren't zero
                all_zero_mask = (
                    (df["greeks_score"].abs() < 0.001)
                    & (df["trend_score"].abs() < 0.001)
                    & (df["volatility_score"].abs() < 0.001)
                    & (df["breakout_score"].abs() < 0.001)
                    & (df["momentum_score"].abs() < 0.001)
                    & (df["ai_score"].abs() < 0.001)
                )
                # For rows where not all components are zero, ensure final_score is non-zero
                not_all_zero = ~all_zero_mask
                if not_all_zero.any():
                    # Use weighted sum directly for these rows
                    base_score = (
                        df.loc[not_all_zero, "greeks_score"] * 0.15
                        + df.loc[not_all_zero, "trend_score"] * 0.20
                        + df.loc[not_all_zero, "volatility_score"] * 0.15
                        + df.loc[not_all_zero, "breakout_score"] * 0.15
                        + df.loc[not_all_zero, "momentum_score"] * 0.15
                        + df.loc[not_all_zero, "ai_score"] * 0.20
                    )
                    df.loc[not_all_zero, "final_score"] = base_score.clip(-1.0, 1.0).values
    except Exception as e:
        logger.error(f"Error computing final score: {e}")
        import traceback

        logger.error(traceback.format_exc())
        df["final_score"] = 0.0

    # Step 8: Generate Signals
    logger.info("Step 8: Generating signals...")
    try:
        # Phase 232: Load thresholds from optimized candidates
        thresholds_by_underlying = None
        try:
            from core.engine.threshold_loader import load_thresholds

            thresholds_by_underlying = load_thresholds(prefer_candidates=True)
            # Log threshold summary (once per session)
            if not hasattr(run_signal_engine, "_thresholds_logged"):
                threshold_summary = []
                for key, val in thresholds_by_underlying.items():
                    threshold_summary.append(f"{key}(buy={val['buy']:.3f}, sell={val['sell']:.3f})")
                logger.info(f"Loaded thresholds: {', '.join(threshold_summary)}")
                run_signal_engine._thresholds_logged = True
        except Exception as e:
            logger.warning(f"Failed to load thresholds, using defaults: {e}")

        # Use thresholds from loader (or defaults)
        # INSTRUMENTATION: Log row counts before signal generation
        logger.info(
            f"  Before signal generation: {len(df)} rows, final_score range=[{df['final_score'].min():.4f}, {df['final_score'].max():.4f}]"
        )
        df = generate_signals(df, thresholds_by_underlying=thresholds_by_underlying)
        # INSTRUMENTATION: Log signal distribution after generation
        signal_counts = df["signal"].value_counts() if "signal" in df.columns else {}
        logger.info(f"  After signal generation: {len(df)} rows | Signal distribution: {dict(signal_counts)}")
        logger.info("✓ Signals generated")
    except Exception as e:
        logger.error(f"Error generating signals: {e}")
        df["signal"] = "HOLD"

    # Step 8.5: UPGRADED - Multi-Timeframe Confirmation (after signal generation)
    if MULTI_TF_AVAILABLE:
        logger.info("Step 8.5: Checking multi-timeframe confirmation...")
        try:
            # For now, use single-timeframe confirmation (can be enhanced with actual multi-TF data)
            df = check_multi_timeframe_confirmation(df, timeframes=None, timeframe_data=None)

            # Log confirmation statistics
            if "confirmation_score" in df.columns:
                confirmed_count = (df["confirmed_signal"] == True).sum() if "confirmed_signal" in df.columns else 0
                avg_confirmation = df["confirmation_score"].mean() if len(df) > 0 else 0.0
                logger.info(
                    f"  Confirmed signals: {confirmed_count}/{len(df)}, avg confirmation score: {avg_confirmation:.3f}"
                )

            logger.info("✓ Multi-timeframe confirmation completed")
        except Exception as e:
            logger.warning(f"Multi-timeframe confirmation failed: {e}")
            # Add default confirmation columns
            df["confirmation_score"] = df.get("confidence", 0.5)
            df["confirmed_signal"] = df["confirmation_score"] >= 0.7
            df["timeframe_agreement"] = "MODERATE"
            df["timeframe_agreement_count"] = 1
    else:
        # Add default confirmation columns if multi-TF not available
        df["confirmation_score"] = df.get("confidence", 0.5)
        df["confirmed_signal"] = df["confirmation_score"] >= 0.7
        df["timeframe_agreement"] = "MODERATE"
        df["timeframe_agreement_count"] = 1

    # Step 9: Compute Entry/Exit Signals
    logger.info("Step 9: Computing entry/exit signals...")
    try:
        df = compute_entry_signals(df, score_col="final_score")

        # Compute dynamic SL/TP
        sl_tp_results = []
        for _, row in df.iterrows():
            if row.get("entry_buy") == 1 or row.get("entry_sell") == 1:
                iv = float(row.get("iv", 0.0)) or float(row.get("iv_estimate", 0.0)) or 0.2
                sl_tp = compute_dynamic_sl_tp(entry_price=float(row.get("ltp", 0.0)), volatility=iv, risk_reward=2.0)
                sl_tp_results.append(sl_tp)
            else:
                sl_tp_results.append({"stop_loss": 0.0, "target_price": 0.0, "risk_amount": 0.0})

        if sl_tp_results:
            df["stop_loss"] = [r["stop_loss"] for r in sl_tp_results]
            df["target_price"] = [r["target_price"] for r in sl_tp_results]
            df["risk_amount"] = [r["risk_amount"] for r in sl_tp_results]

        df = compute_exit_signals(df)
        logger.info("✓ Entry/exit signals computed")
    except Exception as e:
        logger.error(f"Error computing entry/exit: {e}")
        df["entry_buy"] = 0
        df["entry_sell"] = 0
        df["entry_hold"] = 1

    # Ensure timestamp
    if "ts" not in df.columns:
        df["ts"] = datetime.now().isoformat()

    # Map signal to pred_label format (for compatibility)
    def map_signal(sig, side):
        if sig == "BUY":
            return "BUY_CE" if side == "CE" else "BUY_PE"
        elif sig == "SELL":
            return "SELL_CE" if side == "CE" else "SELL_PE"
        else:
            return "HOLD"

    if "side" in df.columns:
        df["pred_label"] = df.apply(lambda row: map_signal(row.get("signal", "HOLD"), row.get("side", "CE")), axis=1)
    else:
        df["pred_label"] = df["signal"]

    # Map final_score to expected_move_score (for compatibility)
    df["expected_move_score"] = df["final_score"]

    # Confidence from signal strength
    if "signal_strength" in df.columns:
        df["pred_confidence"] = df["signal_strength"]
    else:
        df["pred_confidence"] = np.abs(df["final_score"]).clip(0.0, 1.0)

    # INSTRUMENTATION: Final row count and summary
    FINAL_ROW_COUNT = len(df)
    if FINAL_ROW_COUNT > 0:
        buy_count = len(df[df["signal"] == "BUY"])
        sell_count = len(df[df["signal"] == "SELL"])
        hold_count = len(df[df["signal"] == "HOLD"])

        logger.info(f"🔍 SIGNAL PIPELINE END: {FINAL_ROW_COUNT} rows generated")
        logger.info(f"   Signals: BUY={buy_count} | SELL={sell_count} | HOLD={hold_count}")

        if buy_count + sell_count == 0:
            logger.warning(f"⚠️  NO ACTION SIGNALS: All {FINAL_ROW_COUNT} signals are HOLD")
            logger.warning(f"   Check: Thresholds in generate_signals() are too strict")
        else:
            logger.info(f"✓ ACTION SIGNALS: {buy_count + sell_count} out of {FINAL_ROW_COUNT} are BUY/SELL")
    else:
        logger.warning(f"⚠️  NO SIGNALS GENERATED: DataFrame is empty after processing")

    return df


def append_signals_to_csv(df_signals: pd.DataFrame) -> None:
    """
    Append signals to CSV file.

    Args:
        df_signals: DataFrame with signals
    """
    if df_signals is None or df_signals.empty:
        logger.warning("⚠️  No signals to append to CSV")
        return

    try:
        write_header = not SIGNALS_CSV.exists()
        df_signals.to_csv(SIGNALS_CSV, mode="a", header=write_header, index=False, encoding="utf-8")
        # INSTRUMENTATION: Log CSV append with detailed stats
        buy_signals = len(df_signals[df_signals.get("signal") == "BUY"]) if "signal" in df_signals.columns else 0
        sell_signals = len(df_signals[df_signals.get("signal") == "SELL"]) if "signal" in df_signals.columns else 0
        logger.info(f"✓ Appended {len(df_signals)} signals to CSV [BUY={buy_signals}, SELL={sell_signals}]")
    except Exception as e:
        logger.error(f"❌ Error appending signals to CSV: {e}")


def _get_execution_state() -> tuple:
    """Get open_positions and pending_signals from outputs/execution state."""
    import json

    try:
        outputs_dir = ROOT_DIR / "outputs"
        positions_file = outputs_dir / "positions_live.json"
        open_pos = 0
        if positions_file.exists():
            data = json.loads(positions_file.read_text())
            if isinstance(data, dict):
                open_pos = data.get("open_count", len(data.get("positions", [])))
            elif isinstance(data, list):
                open_pos = len(data)
        pending_sig = 0
        vo_file = outputs_dir / "virtual_orders.jsonl"
        if vo_file.exists():
            try:
                pending_sig = sum(1 for _ in open(vo_file, encoding="utf-8"))
            except Exception:
                pass
        return (open_pos, min(pending_sig, 100))
    except Exception:
        return (0, 0)


def run_signal_engine(df_snap: pd.DataFrame, enable_safety_checks: bool = True) -> pd.DataFrame:
    """
    Main entry point: Process snapshot and append to CSV.

    Args:
        df_snap: Snapshot DataFrame
        enable_safety_checks: Enable runtime safety guards (default: True)

    Returns:
        Processed signals DataFrame
    """
    # INSTRUMENTATION: Entry point logging
    snap_size = len(df_snap) if df_snap is not None else 0
    logger.info(f"🚀 SIGNAL ENGINE START: Snapshot size={snap_size}")

    df_signals = process_snapshot(df_snap)

    if not df_signals.empty:
        # INSTRUMENTATION: Log signals ready for downstream
        logger.info(f"🚀 SIGNAL ENGINE: {len(df_signals)} signals ready for CSV append and execution")
        # Runtime safety checks
        if enable_safety_checks:
            try:
                from core.validation.live_safety_guard import check_signal_safety, log_safety_trip

                # Group signals by underlying and check safety
                for underlying in df_signals.get("underlying", pd.Series()).unique():
                    if pd.isna(underlying):
                        continue

                    und_signals = df_signals[df_signals["underlying"] == underlying]
                    buy_signals = len(und_signals[und_signals.get("signal", "") == "BUY"])
                    sell_signals = len(und_signals[und_signals.get("signal", "") == "SELL"])
                    total_signals = buy_signals + sell_signals

                    if total_signals > 0:
                        # Get open_positions and pending_signals from outputs/execution state
                        open_pos, pending_sig = _get_execution_state()
                        is_safe, error = check_signal_safety(
                            underlying=str(underlying),
                            signal_count=total_signals,
                            open_positions=open_pos,
                            pending_signals=pending_sig,
                        )

                        if not is_safe:
                            logger.warning(f"Safety check failed for {underlying}: {error}")
                            # Log but don't block - safety guard logs the trip
            except Exception as e:
                # Don't crash if safety guard fails
                logger.warning(f"Safety guard check failed (non-critical): {e}")

        append_signals_to_csv(df_signals)

        # Phase 237: Wire Virtual Execution into Live Loop
        try:
            from core.engine.threshold_loader import load_thresholds
            from core.config.live_trade_config_loader import load_live_trade_config
            from core.execution.live_execution_engine import (
                plan_orders_from_signals,
                run_risk_checks_on_orders,
                log_virtual_orders,
            )

            thresholds = load_thresholds(prefer_candidates=True)
            live_cfg = load_live_trade_config()

            # Build snapshot DataFrame (use last N rows if multiple snapshots)
            snapshot_df = df_signals.tail(30).copy() if len(df_signals) > 30 else df_signals.copy()

            # Plan orders from signals
            planned_orders = plan_orders_from_signals(snapshot_df, thresholds, live_cfg)

            if planned_orders:
                # Run risk checks (current_pnl and open_positions can be 0 for now)
                risk_decisions = run_risk_checks_on_orders(planned_orders, live_cfg, 0.0, 0)

                # Log virtual orders
                log_virtual_orders(planned_orders, risk_decisions)

        except Exception as e:
            # Don't crash the autopilot loop
            logger.warning(f"Virtual execution failed (non-critical): {e}")
            import traceback

            logger.debug(traceback.format_exc())

    return df_signals


if __name__ == "__main__":
    # Test with sample data
    test_df = pd.DataFrame(
        {
            "ts": [datetime.now().isoformat()],
            "underlying": ["NIFTY"],
            "expiry": ["30DEC2025"],
            "strike": [23000.0],
            "side": ["CE"],
            "ltp": [150.0],
            "spot": [23000.0],
        }
    )

    result = run_signal_engine(test_df)
    print("\n=== TEST RESULT ===")
    print(result[["underlying", "strike", "side", "signal", "final_score", "pred_label"]].to_string())
