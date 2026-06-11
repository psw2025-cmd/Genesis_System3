"""Quick script to verify phase count in registry."""
import json
from pathlib import Path

reg_path = Path("storage/meta/system3_phase_registry.json")
if not reg_path.exists():
    print(f"ERROR: Registry not found: {reg_path}")
    exit(1)

with reg_path.open("r") as f:
    reg = json.load(f)

phases = [int(k) for k in reg.keys() if k.isdigit()]
missing = sorted(set(range(1, 311)) - set(phases))

print(f"Total phases in registry: {len(phases)}")
print(f"Range: {min(phases)}-{max(phases)}")
print(f"Missing phases (1-310): {missing[:30] if missing else 'None'}")
print(f"Missing count: {len(missing)}")

