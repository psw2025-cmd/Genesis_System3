#!/usr/bin/env python3
"""Quick test of Phase 392 imports"""

import os
import sys
from pathlib import Path

# Setup path
project_root = Path(__file__).resolve().parents[2]
print(f"Project root: {project_root}")
print(f"Current dir: {os.getcwd()}")

os.chdir(str(project_root))
print(f"Changed to: {os.getcwd()}")

sys.path.insert(0, str(project_root))
print(f"sys.path[0]: {sys.path[0]}")

# Try import
print("\nAttempting import...")
try:
    from core.engine.system3_phase392_ensemble_integration import run_phase_392

    print("✓ Import successful")

    # Run Phase 392
    print("\nRunning Phase 392...")
    result = run_phase_392()

    print("\nPhase 392 Result:")
    print(f"Status: {result.get('status')}")
    print(f"Scores computed: {result.get('scores_computed')}")

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback

    traceback.print_exc()
