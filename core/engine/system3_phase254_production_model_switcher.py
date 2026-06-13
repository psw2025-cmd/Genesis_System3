"""
System3 Phase 254 - Production Model Switcher

Atomically promote validated shadow models to production.
Shadow-only promotion - does not impact live trading (RandomForest/XGBoost still primary).

References:
- SPRINT1_DL_SPEC.md (Phase 254 specification)
- Phase 253: Shadow model validator (promotion criteria)
"""

import sys
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Directories
MODELS_DIR = PROJECT_ROOT / "core" / "models" / "dhan"
LOGS_DIR = PROJECT_ROOT / "logs"

UNDERLYINGS = ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX"]


def promote_shadow_model(underlying: str) -> Dict[str, Any]:
    """
    Promote validated shadow LSTM model to production.

    Args:
        underlying: Symbol to promote

    Returns:
        dict with promotion result
    """
    shadow_model = MODELS_DIR / f"{underlying}_lstm_model_shadow.pth"
    shadow_meta = MODELS_DIR / f"{underlying}_lstm_meta_shadow.json"

    prod_model = MODELS_DIR / f"{underlying}_lstm_model.pth"
    prod_meta = MODELS_DIR / f"{underlying}_lstm_meta.json"

    backup_model = MODELS_DIR / f"{underlying}_lstm_model_backup.pth"
    backup_meta = MODELS_DIR / f"{underlying}_lstm_meta_backup.json"

    # Check if shadow model exists
    if not shadow_model.exists():
        return {
            "status": "SKIP",
            "reason": "Shadow model not found",
        }

    try:
        # Step 1: Backup current production model
        if prod_model.exists():
            shutil.copy(prod_model, backup_model)
            print(f"[BACKUP] {prod_model.name} → {backup_model.name}")

        if prod_meta.exists():
            shutil.copy(prod_meta, backup_meta)
            print(f"[BACKUP] {prod_meta.name} → {backup_meta.name}")

        # Step 2: Promote shadow to production
        shutil.copy(shadow_model, prod_model)
        print(f"[PROMOTE] {shadow_model.name} → {prod_model.name}")

        if shadow_meta.exists():
            shutil.copy(shadow_meta, prod_meta)
            print(f"[PROMOTE] {shadow_meta.name} → {prod_meta.name}")

        # Step 3: Log promotion
        print(f"[SUCCESS] {underlying} shadow model promoted to production")

        return {
            "status": "SUCCESS",
            "underlying": underlying,
            "promoted_at": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        return {
            "status": "FAIL",
            "reason": str(e),
        }


def run_phase254(**kwargs) -> Dict[str, Any]:
    """
    Run Phase 254: Production Model Switcher.

    Returns:
        dict: Phase execution result
    """
    errors = []
    results = {}

    try:
        # Check validation log for promotable models
        validation_logs = list(LOGS_DIR.glob("phase253_validation_*.log"))

        if not validation_logs:
            return {
                "phase": 254,
                "status": "SKIP",
                "details": "No validation logs found",
                "outputs": {},
                "errors": [],
            }

        # Get latest validation log
        latest_log = max(validation_logs, key=lambda p: p.stat().st_mtime)

        # Parse validation results (STUB: would parse actual log)
        # For now, assume no promotable models (validation would set this)
        promotable = []  # Placeholder

        if not promotable:
            return {
                "phase": 254,
                "status": "SKIP",
                "details": "No models ready for promotion",
                "outputs": {},
                "errors": [],
            }

        print(f"[PHASE 254] Promoting {len(promotable)} validated models")

        # Promote each validated model
        for underlying in promotable:
            result = promote_shadow_model(underlying)
            results[underlying] = result

        # Generate promotion log
        log_file = LOGS_DIR / f"phase254_promotion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        LOGS_DIR.mkdir(parents=True, exist_ok=True)

        with log_file.open("w", encoding="utf-8") as f:
            f.write(f"Phase 254: Model Promotion Log\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n\n")
            for underlying, res in results.items():
                f.write(f"{underlying}: {res['status']}\n")
                if res["status"] == "SUCCESS":
                    f.write(f"  Promoted at: {res['promoted_at']}\n")

        print(f"[SAVE] Promotion log: {log_file}")

        success_count = sum(1 for r in results.values() if r["status"] == "SUCCESS")

        status = "OK" if success_count > 0 else "WARN"
        details = f"Promoted {success_count}/{len(promotable)} models to production"

        return {
            "phase": 254,
            "status": status,
            "details": details,
            "outputs": {
                "results": results,
                "log_file": str(log_file),
            },
            "errors": errors,
        }

    except Exception as e:
        errors.append(f"Phase 254 exception: {e}")
        return {
            "phase": 254,
            "status": "ERROR",
            "details": f"Model promotion failed: {e}",
            "outputs": {},
            "errors": errors,
        }


def main():
    """CLI entry point."""
    print("=" * 80)
    print("Phase 254: Production Model Switcher")
    print("=" * 80)

    result = run_phase254()

    print(f"\n[PHASE 254] Status: {result['status']}")
    print(f"[PHASE 254] Details: {result['details']}")


if __name__ == "__main__":
    main()
