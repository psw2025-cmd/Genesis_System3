"""
System3 Ultra - Phase 41: Ultra Promotion Execution Framework (Staging Only)

Provide a safe, two-step mechanism that can prepare promotion of Ultra to baseline,
but does not execute it automatically. This remains a staging step only.

All operations are Ultra-Isolated, Baseline-Protected, Read-Only.
Zero Auto-execution, Zero Auto-updates.

Menu Option: 104
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

PROJECT_ROOT = Path(__file__).parent.parent.parent
CONFIG_DIR = PROJECT_ROOT / "storage" / "config"
ULTRA_DIR = PROJECT_ROOT / "storage" / "ultra"
STAGING_MODELS_DIR = PROJECT_ROOT / "core" / "models" / "dhan_ultra_staging"
BLENDED_MODELS_DIR = PROJECT_ROOT / "core" / "models" / "dhan_real_blended"
LOGS_ULTRA_DIR = PROJECT_ROOT / "storage" / "logs_ultra"

STAGING_MODELS_DIR.mkdir(parents=True, exist_ok=True)
LOGS_ULTRA_DIR.mkdir(parents=True, exist_ok=True)

PROMOTION_FLAG_FILE = CONFIG_DIR / "ultra_promotion_flag.txt"
PROMOTION_PLAN_FILE = ULTRA_DIR / "phase33_promotion_plan.json"
LOG_FILE = LOGS_ULTRA_DIR / "system3_phases_39_45.log"

REQUIRED_KEYWORD = "ALLOW_ULTRA_PROMOTION_STAGING"


def _log(message: str) -> None:
    """Log message to file and console."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] [Phase41] {message}\n"
    print(f"[Phase41] {message}")

    try:
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(log_line)
    except Exception as e:
        print(f"[Phase41][WARN] Failed to write log: {e}")


def find_latest_snapshot_dir() -> Optional[Path]:
    """Find the latest snapshot directory."""
    from core.engine.system3_phase42_snapshot_manager import find_latest_snapshot_dir as find_snap

    return find_snap()


def check_promotion_flag() -> bool:
    """Check if promotion flag file exists and contains required keyword."""
    if not PROMOTION_FLAG_FILE.exists():
        _log("Promotion flag file not found")
        return False

    try:
        content = PROMOTION_FLAG_FILE.read_text(encoding="utf-8").strip()
        if REQUIRED_KEYWORD in content:
            _log("Promotion flag detected and valid")
            return True
        else:
            _log(f"Promotion flag file exists but keyword '{REQUIRED_KEYWORD}' not found")
            return False
    except Exception as e:
        _log(f"Error reading promotion flag: {e}")
        return False


def get_eligible_underlyings() -> List[str]:
    """Get list of eligible underlyings from promotion plan."""
    if not PROMOTION_PLAN_FILE.exists():
        _log("Promotion plan file not found")
        return []

    try:
        with PROMOTION_PLAN_FILE.open("r", encoding="utf-8") as f:
            plan = json.load(f)

        eligible = []
        for underlying, data in plan.items():
            if isinstance(data, dict) and data.get("eligible", False):
                eligible.append(underlying)

        return eligible
    except Exception as e:
        _log(f"Error reading promotion plan: {e}")
        return []


def stage_ultra_model(underlying: str, snapshot_dir: Optional[Path]) -> bool:
    """Stage Ultra model for an underlying."""
    model_file = BLENDED_MODELS_DIR / f"{underlying}_model_blended_v3.pkl"
    meta_file = BLENDED_MODELS_DIR / f"{underlying}_model_blended_v3_meta.json"

    # Fallback to regular blended models if v3 not found
    if not model_file.exists():
        model_file = BLENDED_MODELS_DIR / f"{underlying}_model.pkl"
        meta_file = BLENDED_MODELS_DIR / f"{underlying}_model_meta.json"

    if not model_file.exists():
        _log(f"WARN: Ultra model not found for {underlying}")
        return False

    # Copy to staging
    staging_model = STAGING_MODELS_DIR / f"{underlying}_model.pkl"
    staging_meta = STAGING_MODELS_DIR / f"{underlying}_model_meta.json"

    try:
        shutil.copy2(model_file, staging_model)
        if meta_file.exists():
            shutil.copy2(meta_file, staging_meta)

        snapshot_str = snapshot_dir.name if snapshot_dir else "unknown"
        _log(f"Staged Ultra model for {underlying} based on snapshot {snapshot_str}")
        return True
    except Exception as e:
        _log(f"Error staging model for {underlying}: {e}")
        return False


def run_phase41_promotion_executor() -> None:
    """Execute promotion to staging."""
    print("=" * 60)
    print("SYSTEM3 ULTRA - PHASE 41: PROMOTION EXECUTOR (STAGING ONLY)")
    print("=" * 60)
    print("\n[SAFETY] Ultra-Isolated, Baseline-Protected, Read-Only")
    print("[SAFETY] Staging only - no baseline models will be modified\n")

    # Check flag
    if not check_promotion_flag():
        print("\n[ERROR] Promotion flag not found or invalid")
        print(f"[INFO] Create {PROMOTION_FLAG_FILE} with keyword: {REQUIRED_KEYWORD}")
        return

    # Get eligible underlyings
    eligible = get_eligible_underlyings()
    if not eligible:
        print("\n[ERROR] No eligible underlyings found in promotion plan")
        print("[INFO] Run Phase 33 to generate promotion plan")
        return

    _log(f"Eligible underlyings: {', '.join(eligible)}")

    # Find latest snapshot
    snapshot_dir = find_latest_snapshot_dir()
    if not snapshot_dir:
        print("\n[ERROR] No snapshot found, cannot stage promotion")
        print("[INFO] Run Phase 42 to create a snapshot first")
        return

    _log(f"Using snapshot: {snapshot_dir}")

    # Stage models
    staged = []
    failed = []

    for underlying in eligible:
        if stage_ultra_model(underlying, snapshot_dir):
            staged.append(underlying)
        else:
            failed.append(underlying)

    # Create report
    report_lines = []
    report_lines.append("# Ultra Promotion Staging Report")
    report_lines.append("")
    report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("")
    report_lines.append("## Staging Summary")
    report_lines.append("")
    report_lines.append(f"- **Underlyings Staged**: {len(staged)}")
    report_lines.append(f"- **Underlyings Failed**: {len(failed)}")
    report_lines.append("")

    if staged:
        report_lines.append("### Successfully Staged")
        report_lines.append("")
        for u in staged:
            report_lines.append(f"- **{u}**: `{STAGING_MODELS_DIR}/{u}_model.pkl`")
        report_lines.append("")

    if failed:
        report_lines.append("### Failed to Stage")
        report_lines.append("")
        for u in failed:
            report_lines.append(f"- **{u}**: Model file not found")
        report_lines.append("")

    report_lines.append("## Source Paths")
    report_lines.append("")
    report_lines.append(f"- **Blended Models**: `{BLENDED_MODELS_DIR}`")
    report_lines.append(f"- **Staging Models**: `{STAGING_MODELS_DIR}`")
    report_lines.append("")

    report_lines.append("## Snapshot Used")
    report_lines.append("")
    report_lines.append(f"- **Snapshot Directory**: `{snapshot_dir}`")
    report_lines.append("")

    report_lines.append("## Flag File Status")
    report_lines.append("")
    report_lines.append(f"- **Flag File**: `{PROMOTION_FLAG_FILE}`")
    report_lines.append(f"- **Keyword**: `{REQUIRED_KEYWORD}`")
    report_lines.append(f"- **Status**: Valid")
    report_lines.append("")

    report_lines.append("## Notes")
    report_lines.append("")
    report_lines.append("- Models are staged only, not promoted to baseline")
    report_lines.append("- Baseline models remain unchanged")
    report_lines.append("- Manual review required before any baseline changes")

    report_file = ULTRA_DIR / "phase41_promotion_staging_report.md"
    with report_file.open("w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print(f"\n[OK] Phase 41 Promotion Executor completed")
    print(f"[SAVE] Staging report: {report_file}")

    if staged:
        print(f"\n[INFO] Staged {len(staged)} model(s) to: {STAGING_MODELS_DIR}")
        print("[INFO] Baseline models remain unchanged")


def main() -> None:
    """CLI entry point."""
    run_phase41_promotion_executor()


if __name__ == "__main__":
    main()
