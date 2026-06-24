"""
Dhan Index Options - Model Selector

Selects models based on active profile (BASELINE or LIVE_BETA).
Reads system3_live_beta_profile.json to determine which models to load.

Inputs:
- storage/config/system3_live_beta_profile.json

Outputs:
- Model objects loaded from appropriate paths

Environment/Config: Profile selection via config file.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional

import joblib

PROJECT_ROOT = Path(__file__).parent.parent.parent
CONFIG_DIR = PROJECT_ROOT / "storage" / "config"
CORE_CONFIG_DIR = PROJECT_ROOT / "core" / "config"
MODELS_DIR = PROJECT_ROOT / "core" / "models" / "dhan"
BLENDED_MODELS_DIR = PROJECT_ROOT / "core" / "models" / "dhan_real_blended"
ULTRA_MODELS_DIR = PROJECT_ROOT / "core" / "models" / "dhan_ultra"

BETA_PROFILE_JSON = CONFIG_DIR / "system3_live_beta_profile.json"
ACTIVE_PROFILE_JSON = CORE_CONFIG_DIR / "system3_active_profile.json"

UNDERLYINGS = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]


def load_profile_config() -> Dict[str, Any]:
    """Load live beta profile config."""
    defaults = {
        "enabled": False,
        "use_blended_models": True,
        "max_trades_per_day": 10,
        "max_trades_per_underlying": 3,
        "execution_mode": "DRY_RUN_ONLY",
        "min_confidence": 0.75,
        "min_score": 0.25,
    }

    if BETA_PROFILE_JSON.exists():
        try:
            with BETA_PROFILE_JSON.open("r", encoding="utf-8") as f:
                user_config = json.load(f)
                defaults.update(user_config)
        except Exception as e:
            print(f"[WARN] Failed to load beta profile, using defaults: {e}")

    return defaults


def get_active_profile() -> str:
    """
    Get active profile name.

    Returns:
        "BASELINE", "LIVE_BETA", or "ULTRA_DEV"
    """
    # Check Ultra profile first (highest priority)
    if ACTIVE_PROFILE_JSON.exists():
        try:
            with ACTIVE_PROFILE_JSON.open("r", encoding="utf-8") as f:
                ultra_config = json.load(f)
                profile = ultra_config.get("ACTIVE_PROFILE", "BASELINE")
                if profile == "ULTRA_DEV":
                    return "ULTRA_DEV"
        except Exception:
            pass

    # Check LIVE_BETA profile
    config = load_profile_config()
    if config.get("enabled", False) and config.get("use_blended_models", False):
        return "LIVE_BETA"

    # Default to BASELINE
    return "BASELINE"


def get_model_dir(profile: str = None) -> Path:
    """
    Get model directory for specified profile.

    Args:
        profile: "BASELINE", "LIVE_BETA", or "ULTRA_DEV". If None, auto-detect.

    Returns:
        Path to model directory
    """
    if profile is None:
        profile = get_active_profile()

    if profile == "ULTRA_DEV":
        return ULTRA_MODELS_DIR
    elif profile == "LIVE_BETA":
        return BLENDED_MODELS_DIR
    else:
        return MODELS_DIR


def get_storage_dirs(profile: str = None) -> Dict[str, Path]:
    """
    Get storage directories for specified profile.

    Args:
        profile: "BASELINE", "LIVE_BETA", or "ULTRA_DEV". If None, auto-detect.

    Returns:
        Dict with storage directory paths
    """
    if profile is None:
        profile = get_active_profile()

    if profile == "ULTRA_DEV":
        return {
            "signals_dir": PROJECT_ROOT / "storage" / "ultra",
            "trades_dir": PROJECT_ROOT / "storage" / "ultra",
            "pnl_dir": PROJECT_ROOT / "storage" / "ultra",
            "learning_dir": PROJECT_ROOT / "storage" / "learning_ultra",
            "reports_dir": PROJECT_ROOT / "storage" / "reports_ultra",
        }
    else:
        # BASELINE or LIVE_BETA use standard storage
        return {
            "signals_dir": PROJECT_ROOT / "storage" / "live",
            "trades_dir": PROJECT_ROOT / "storage" / "live",
            "pnl_dir": PROJECT_ROOT / "storage" / "live",
            "learning_dir": PROJECT_ROOT / "storage" / "learning",
            "reports_dir": PROJECT_ROOT / "storage" / "reports",
        }


def load_models_for_profile(profile_name: str = None) -> Dict[str, Any]:
    """
    Load models for specified profile.

    Args:
        profile_name: "BASELINE", "LIVE_BETA", or "ULTRA_DEV". If None, auto-detect from config.

    Returns:
        Dict mapping underlying -> model object
    """
    if profile_name is None:
        profile_name = get_active_profile()

    models = {}
    model_paths = {}
    meta_paths = {}

    if profile_name == "ULTRA_DEV":
        # Use Ultra models
        for underlying in UNDERLYINGS:
            model_file = ULTRA_MODELS_DIR / f"{underlying}_ultra_model.pkl"
            meta_file = ULTRA_MODELS_DIR / f"{underlying}_ultra_model_meta.json"

            if model_file.exists():
                try:
                    model = joblib.load(model_file)
                    models[underlying] = model
                    model_paths[underlying] = str(model_file)
                    if meta_file.exists():
                        meta_paths[underlying] = str(meta_file)
                except Exception as e:
                    print(f"[WARN] Failed to load {underlying} Ultra model: {e}")
            else:
                # Fallback to baseline
                baseline_file = MODELS_DIR / f"{underlying}_model.pkl"
                if baseline_file.exists():
                    try:
                        model = joblib.load(baseline_file)
                        models[underlying] = model
                        model_paths[underlying] = str(baseline_file)
                        print(f"[FALLBACK] {underlying}: Using baseline model")
                    except Exception as e:
                        print(f"[WARN] Failed to load {underlying} baseline model: {e}")
    elif profile_name == "LIVE_BETA":
        # Use blended models
        for underlying in UNDERLYINGS:
            model_file = BLENDED_MODELS_DIR / f"{underlying}_model_blended_v3.pkl"
            meta_file = BLENDED_MODELS_DIR / f"{underlying}_model_blended_v3_meta.json"

            if model_file.exists():
                try:
                    model = joblib.load(model_file)
                    models[underlying] = model
                    model_paths[underlying] = str(model_file)
                    if meta_file.exists():
                        meta_paths[underlying] = str(meta_file)
                except Exception as e:
                    print(f"[WARN] Failed to load {underlying} blended model: {e}")
            else:
                # Fallback to baseline
                baseline_file = MODELS_DIR / f"{underlying}_model.pkl"
                if baseline_file.exists():
                    try:
                        model = joblib.load(baseline_file)
                        models[underlying] = model
                        model_paths[underlying] = str(baseline_file)
                        print(f"[FALLBACK] {underlying}: Using baseline model")
                    except Exception as e:
                        print(f"[WARN] Failed to load {underlying} baseline model: {e}")
    else:
        # Use baseline models
        for underlying in UNDERLYINGS:
            model_file = MODELS_DIR / f"{underlying}_model.pkl"
            meta_file = MODELS_DIR / f"{underlying}_model_meta.json"

            if model_file.exists():
                try:
                    model = joblib.load(model_file)
                    models[underlying] = model
                    model_paths[underlying] = str(model_file)
                    if meta_file.exists():
                        meta_paths[underlying] = str(meta_file)
                except Exception as e:
                    print(f"[WARN] Failed to load {underlying} baseline model: {e}")

    return {
        "profile": profile_name,
        "models": models,
        "model_paths": model_paths,
        "meta_paths": meta_paths,
    }


def get_profile_thresholds(profile_name: str = None) -> Dict[str, float]:
    """
    Get thresholds for specified profile.

    Args:
        profile_name: "BASELINE" or "LIVE_BETA". If None, auto-detect.

    Returns:
        Dict with min_confidence and min_score
    """
    if profile_name is None:
        profile_name = get_active_profile()

    if profile_name == "LIVE_BETA":
        config = load_profile_config()
        return {
            "min_confidence": config.get("min_confidence", 0.75),
            "min_score": config.get("min_score", 0.25),
        }
    else:
        # Baseline thresholds
        try:
            from core.engine.dhan_trade_config import DEFAULT_THRESHOLDS

            return {
                "min_confidence": DEFAULT_THRESHOLDS.min_confidence,
                "min_abs_score": DEFAULT_THRESHOLDS.min_abs_score,
            }
        except Exception:
            return {
                "min_confidence": 0.80,
                "min_abs_score": 0.30,
            }


def show_profile_info() -> None:
    """Show active profile and model sources."""
    print("=== SYSTEM3 LIVE PROFILES & MODEL SOURCES ===\n")

    profile = get_active_profile()
    print(f"Active Profile: {profile}")

    if profile == "ULTRA_DEV":
        print("Ultra Profile: ENABLED")
        print("Mode: SHADOW/EXPERIMENTAL")
    else:
        config = load_profile_config()
        print(f"Beta Profile Enabled: {config.get('enabled', False)}")
        print(f"Use Blended Models: {config.get('use_blended_models', False)}")
        print(f"Execution Mode: {config.get('execution_mode', 'DRY_RUN_ONLY')}")

    # Show model and storage directories
    model_dir = get_model_dir(profile)
    storage_dirs = get_storage_dirs(profile)
    print(f"\n=== PROFILE PATHS ===")
    print(f"Model Directory: {model_dir}")
    print(f"Signals Directory: {storage_dirs['signals_dir']}")
    print(f"Learning Directory: {storage_dirs['learning_dir']}")
    print(f"Reports Directory: {storage_dirs['reports_dir']}")

    # Load models
    model_data = load_models_for_profile(profile)

    print(f"\n=== MODEL SOURCES ===")
    for underlying in UNDERLYINGS:
        if underlying in model_data["model_paths"]:
            path = model_data["model_paths"][underlying]
            if "ultra_model" in path:
                print(f"{underlying}: {path} (ULTRA)")
            elif "blended_v3" in path:
                print(f"{underlying}: {path} (BLENDED)")
            else:
                print(f"{underlying}: {path} (BASELINE)")
        else:
            print(f"{underlying}: NOT FOUND")

    # Show thresholds
    thresholds = get_profile_thresholds(profile)
    print(f"\n=== THRESHOLDS ===")
    for key, value in thresholds.items():
        print(f"{key}: {value}")


def main() -> None:
    """Main entry point."""
    show_profile_info()


if __name__ == "__main__":
    main()
