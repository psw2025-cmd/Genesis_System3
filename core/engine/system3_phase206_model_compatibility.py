"""
System3 Phase 206 - Model Compatibility Checker

Scans models directory and checks version compatibility.
"""

import sys
import pickle
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

LOG_DIR = PROJECT_ROOT / "logs" / "models"
LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = LOG_DIR / "system3_model_compatibility_report.md"

MODELS_DIR = PROJECT_ROOT / "core" / "models"
MODEL_JOBS_DIR = PROJECT_ROOT / "storage" / "model_jobs"
MODEL_JOBS_DIR.mkdir(parents=True, exist_ok=True)

ENGINE_VERSION = "1.0"  # Central engine version constant


def check_model_file(model_path: Path) -> tuple[bool, dict, str]:
    """Check a model file for compatibility."""
    try:
        with model_path.open("rb") as f:
            model_data = pickle.load(f)

        # Try to extract version/metadata
        version = None
        metadata = {}

        if isinstance(model_data, dict):
            version = model_data.get("model_version") or model_data.get("version")
            metadata = model_data
        elif hasattr(model_data, "model_version"):
            version = model_data.model_version
        elif hasattr(model_data, "__dict__"):
            version = getattr(model_data, "model_version", None)
            metadata = model_data.__dict__

        is_compatible = version == ENGINE_VERSION if version else None

        return (
            True,
            {
                "version": version,
                "compatible": is_compatible,
                "metadata": metadata,
            },
            "",
        )
    except Exception as e:
        return False, {}, str(e)


def run_phase206(**kwargs) -> Dict[str, Any]:
    """
    Run Phase 206: Model Compatibility Checker.

    Returns:
        dict: {
            "phase": 206,
            "status": "OK" or "WARN" or "ERROR",
            "details": "short summary",
            "outputs": {
                "checked_models": int,
                "compatible_models": list,
                "incompatible_models": list,
                "rebuild_jobs_created": int,
            },
            "errors": [],
        }
    """
    errors = []
    checked_models = []
    compatible_models = []
    incompatible_models = []
    rebuild_jobs_created = 0

    try:
        # Find all PKL files
        model_files = []
        if MODELS_DIR.exists():
            model_files.extend(MODELS_DIR.rglob("*.pkl"))
            model_files.extend(MODELS_DIR.rglob("*.pickle"))

        with REPORT_PATH.open("w", encoding="utf-8") as f:
            f.write("# System3 Model Compatibility Report\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Engine Version**: {ENGINE_VERSION}\n\n")

            f.write("## Models Checked\n\n")

            for model_path in model_files:
                checked_models.append(str(model_path))
                f.write(f"### {model_path.name}\n\n")
                f.write(f"**Path**: `{model_path}`\n\n")

                is_valid, model_info, error_msg = check_model_file(model_path)

                if not is_valid:
                    f.write(f"**Status**: ❌ ERROR\n\n")
                    f.write(f"**Error**: {error_msg}\n\n")
                    errors.append(f"Failed to check {model_path}: {error_msg}")
                else:
                    version = model_info.get("version")
                    compatible = model_info.get("compatible")

                    if version is None:
                        f.write(f"**Status**: ⚠️ NO_VERSION\n\n")
                        f.write("**Note**: Model does not have version metadata\n\n")
                        incompatible_models.append(str(model_path))
                    elif compatible:
                        f.write(f"**Status**: ✅ COMPATIBLE\n\n")
                        f.write(f"**Version**: {version}\n\n")
                        compatible_models.append(str(model_path))
                    else:
                        f.write(f"**Status**: ❌ INCOMPATIBLE\n\n")
                        f.write(f"**Version**: {version} (expected {ENGINE_VERSION})\n\n")
                        incompatible_models.append(str(model_path))

                        # Create rebuild job
                        job_file = (
                            MODEL_JOBS_DIR
                            / f"rebuild_{model_path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                        )
                        with job_file.open("w", encoding="utf-8") as jf:
                            json.dump(
                                {
                                    "model_path": str(model_path),
                                    "current_version": version,
                                    "target_version": ENGINE_VERSION,
                                    "created": datetime.now().isoformat(),
                                    "status": "PENDING",
                                },
                                jf,
                                indent=2,
                            )
                        rebuild_jobs_created += 1
                        f.write(f"**Action**: Rebuild job created: `{job_file.name}`\n\n")

                f.write("\n")

            f.write("## Summary\n\n")
            f.write(f"- **Models Checked**: {len(checked_models)}\n")
            f.write(f"- **Compatible**: {len(compatible_models)}\n")
            f.write(f"- **Incompatible**: {len(incompatible_models)}\n")
            f.write(f"- **Rebuild Jobs Created**: {rebuild_jobs_created}\n")

            if incompatible_models:
                f.write("\n⚠️ **ACTION REQUIRED**: Some models are incompatible and require rebuild.\n")
            else:
                f.write("\n✅ **STATUS**: All models are compatible.\n")

        status = "WARN" if incompatible_models else "OK"
        details = f"Checked {len(checked_models)} models"
        if incompatible_models:
            details += f", {len(incompatible_models)} incompatible"
        if rebuild_jobs_created:
            details += f", {rebuild_jobs_created} rebuild job(s) created"

        return {
            "phase": 206,
            "status": status,
            "details": details,
            "outputs": {
                "checked_models": len(checked_models),
                "compatible_models": compatible_models,
                "incompatible_models": incompatible_models,
                "rebuild_jobs_created": rebuild_jobs_created,
                "report_path": str(REPORT_PATH),
            },
            "errors": errors,
        }

    except Exception as e:
        return {
            "phase": 206,
            "status": "ERROR",
            "details": f"Phase 206 failed: {e}",
            "outputs": {},
            "errors": [str(e)],
        }


def main():
    """CLI entry point."""
    print("=" * 70)
    print("SYSTEM3 PHASE 206 - MODEL COMPATIBILITY CHECKER")
    print("=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    result = run_phase206()

    print(f"Phase 206: {result['details']}")
    if result.get("errors"):
        for error in result["errors"]:
            print(f"  [ERROR] {error}")

    if result["outputs"]:
        print(f"\nReport: {result['outputs']['report_path']}")
        print(f"Checked: {result['outputs']['checked_models']}")
        print(f"Compatible: {len(result['outputs']['compatible_models'])}")
        print(f"Incompatible: {len(result['outputs']['incompatible_models'])}")

    return 0 if result["status"] in ("OK", "WARN") else 1


if __name__ == "__main__":
    sys.exit(main())
