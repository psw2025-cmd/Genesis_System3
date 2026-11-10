#!/usr/bin/env python3
"""Quick smoke of Phase 392 imports."""

import sys
from pathlib import Path


project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def main() -> int:
    """Run the legacy smoke only when invoked directly."""
    print(f"Project root: {project_root}")
    print("Attempting import...")
    try:
        from core.engine.system3_phase392_ensemble_integration import run_phase_392

        print("Import successful")
        result = run_phase_392()
        print(f"Status: {result.get('status')}")
        print(f"Scores computed: {result.get('scores_computed')}")
        return 0
    except Exception as exc:
        print(f"Error: {exc}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
