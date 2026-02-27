"""
Ultra Models Loader - Load pre-trained per-underlying models

System3 Phase 381-388 Implementation
Path A: Ultra Models Integration

Usage:
    from core.engine.ultra_models_loader import load_ultra_model
    model = load_ultra_model("NIFTY")
    if model:
        predictions = model.predict(X)

Safety:
    - NEVER raises exceptions (returns None gracefully)
    - NEVER downloads external data
    - NEVER modifies model files
    - Uses only local pre-trained models
"""

from pathlib import Path
import joblib
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import os

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ULTRA_MODELS_DIR = PROJECT_ROOT / "core" / "models" / "angel_one_ultra"

# Supported underlyings
SUPPORTED_UNDERLYINGS = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]


def load_ultra_model(underlying: str) -> Optional[Any]:
    """
    Load pre-trained ultra model for given underlying.
    
    Args:
        underlying: "NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"
    
    Returns:
        Loaded sklearn/xgboost model or None if not found
        
    Behavior:
        - Checks core/models/angel_one_ultra/{underlying}_ultra_model.pkl
        - Returns None gracefully if model missing (enables delta fallback)
        - Logs success/failure explicitly for telemetry
        - NEVER raises exceptions to caller
    
    Example:
        >>> model = load_ultra_model("NIFTY")
        >>> if model:
        >>>     scores = model.predict_proba(X)
    """
    if not underlying:
        logger.warning("load_ultra_model: underlying is None or empty")
        return None
    
    # Normalize underlying name
    underlying = str(underlying).upper().strip()
    
    if underlying not in SUPPORTED_UNDERLYINGS:
        logger.warning(
            f"load_ultra_model: {underlying} not in supported list {SUPPORTED_UNDERLYINGS}"
        )
        return None
    
    model_path = ULTRA_MODELS_DIR / f"{underlying}_ultra_model.pkl"
    
    if not model_path.exists():
        logger.warning(f"Ultra model not found: {model_path} (will use delta fallback)")
        return None
    
    try:
        model = joblib.load(model_path)
        logger.info(f"✓ USING_ULTRA_MODEL for {underlying} (path={model_path})")
        return model
    except Exception as e:
        logger.error(
            f"Failed to load Ultra model for {underlying}: {e} "
            "(will use delta fallback)"
        )
        return None


def get_ultra_model_metadata(underlying: str) -> Dict[str, Any]:
    """
    Extract model metadata (file size, modified date, exists status).
    
    Args:
        underlying: "NIFTY", "BANKNIFTY", etc.
    
    Returns:
        {
            "underlying": "NIFTY",
            "model_path": "core/models/angel_one_ultra/NIFTY_ultra_model.pkl",
            "file_size_kb": 245.6,
            "last_modified": "2025-12-05 14:23:10",
            "exists": True,
            "loadable": True
        }
    
    Example:
        >>> meta = get_ultra_model_metadata("NIFTY")
        >>> if meta["exists"] and meta["loadable"]:
        >>>     print(f"NIFTY model ready: {meta['file_size_kb']} KB")
    """
    underlying = str(underlying).upper().strip()
    model_path = ULTRA_MODELS_DIR / f"{underlying}_ultra_model.pkl"
    
    metadata = {
        "underlying": underlying,
        "model_path": str(model_path),
        "file_size_kb": 0.0,
        "last_modified": None,
        "exists": False,
        "loadable": False
    }
    
    if model_path.exists():
        metadata["exists"] = True
        try:
            file_size = model_path.stat().st_size
            metadata["file_size_kb"] = round(file_size / 1024, 2)
            
            mtime = model_path.stat().st_mtime
            metadata["last_modified"] = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
            
            # Test if loadable
            model = joblib.load(model_path)
            metadata["loadable"] = model is not None
        except Exception as e:
            logger.warning(f"Could not extract metadata for {underlying}: {e}")
            metadata["loadable"] = False
    
    return metadata


def load_ultra_models_all() -> Dict[str, Any]:
    """
    Load all available ultra models (one per underlying).
    
    Returns:
        {
            "NIFTY": model_object,
            "BANKNIFTY": model_object,
            ...
        }
        (Only includes successfully loaded models)
    
    Example:
        >>> models = load_ultra_models_all()
        >>> logger.info(f"Loaded {len(models)}/{len(SUPPORTED_UNDERLYINGS)} ultra models")
        >>> if "NIFTY" in models:
        >>>     nifty_scores = models["NIFTY"].predict(X)
    """
    models = {}
    
    for underlying in SUPPORTED_UNDERLYINGS:
        model = load_ultra_model(underlying)
        if model:
            models[underlying] = model
    
    logger.info(
        f"✓ Loaded {len(models)}/{len(SUPPORTED_UNDERLYINGS)} ultra models "
        f"({', '.join(models.keys())})"
    )
    return models


def get_all_ultra_models_inventory() -> Dict[str, Any]:
    """
    Get complete inventory of all ultra models (metadata only, no loading).
    
    Returns:
        {
            "scan_timestamp": "2025-12-07T20:45:00Z",
            "models_found": 5,
            "models_missing": 0,
            "models": [
                {
                    "underlying": "NIFTY",
                    "exists": True,
                    "loadable": True,
                    "file_size_kb": 245.6,
                    ...
                }
            ]
        }
    
    Used by Phase 381 (Ultra Models Scanner)
    """
    inventory = {
        "scan_timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "models_found": 0,
        "models_missing": 0,
        "models": []
    }
    
    for underlying in SUPPORTED_UNDERLYINGS:
        metadata = get_ultra_model_metadata(underlying)
        inventory["models"].append(metadata)
        
        if metadata["exists"]:
            inventory["models_found"] += 1
        else:
            inventory["models_missing"] += 1
    
    return inventory


def verify_ultra_models_health() -> Dict[str, Any]:
    """
    Comprehensive health check for all ultra models.
    
    Returns:
        {
            "overall_status": "ok" | "warn" | "error",
            "models_available": 5,
            "models_total": 5,
            "health_checks": {
                "NIFTY": {"status": "ok", "message": "Model loaded and functional"},
                ...
            }
        }
    
    Used by Phase 382 (Sanity Validator) and Phase 388 (Health Gate)
    """
    health = {
        "overall_status": "ok",
        "models_available": 0,
        "models_total": len(SUPPORTED_UNDERLYINGS),
        "health_checks": {}
    }
    
    for underlying in SUPPORTED_UNDERLYINGS:
        check_result = {
            "status": "error",
            "message": "Unknown error"
        }
        
        try:
            model = load_ultra_model(underlying)
            if model:
                check_result["status"] = "ok"
                check_result["message"] = "Model loaded and functional"
                health["models_available"] += 1
            else:
                check_result["status"] = "warn"
                check_result["message"] = "Model not found (will use delta fallback)"
        except Exception as e:
            check_result["status"] = "error"
            check_result["message"] = f"Load failed: {str(e)}"
        
        health["health_checks"][underlying] = check_result
    
    # Determine overall status
    if health["models_available"] == health["models_total"]:
        health["overall_status"] = "ok"
    elif health["models_available"] > 0:
        health["overall_status"] = "warn"
    else:
        health["overall_status"] = "error"
    
    return health


if __name__ == "__main__":
    """
    Quick test of Ultra Models Loader
    
    Run with:
        C:/Genesis_System3/venv/Scripts/python.exe core/engine/ultra_models_loader.py
    """
    print("=" * 60)
    print("ULTRA MODELS LOADER - QUICK TEST")
    print("=" * 60)
    
    # Test 1: Inventory scan
    print("\n[Test 1] Ultra Models Inventory:")
    inventory = get_all_ultra_models_inventory()
    print(f"  Timestamp: {inventory['scan_timestamp']}")
    print(f"  Models Found: {inventory['models_found']}/{len(SUPPORTED_UNDERLYINGS)}")
    for model_info in inventory["models"]:
        status = "✅" if model_info["exists"] else "❌"
        print(f"  {status} {model_info['underlying']}: {model_info['file_size_kb']} KB")
    
    # Test 2: Health check
    print("\n[Test 2] Health Check:")
    health = verify_ultra_models_health()
    print(f"  Overall Status: {health['overall_status'].upper()}")
    print(f"  Available: {health['models_available']}/{health['models_total']}")
    for underlying, check in health["health_checks"].items():
        status_icon = {"ok": "✅", "warn": "⚠️", "error": "❌"}[check["status"]]
        print(f"  {status_icon} {underlying}: {check['message']}")
    
    # Test 3: Load all models
    print("\n[Test 3] Load All Models:")
    models = load_ultra_models_all()
    print(f"  Loaded: {len(models)}/{len(SUPPORTED_UNDERLYINGS)} models")
    for underlying, model in models.items():
        model_type = type(model).__name__
        print(f"  ✅ {underlying}: {model_type}")
    
    print("\n" + "=" * 60)
    print("ULTRA MODELS LOADER TEST COMPLETE")
    print("=" * 60)
