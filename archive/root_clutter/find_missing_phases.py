"""
Find Missing Phases - Micro Investigation

Identifies exactly which 26 phases are missing from the registry.
"""

import json
from pathlib import Path
from collections import defaultdict

PROJECT_ROOT = Path(__file__).parent
REGISTRY_JSON = PROJECT_ROOT / "storage" / "meta" / "system3_phase_registry.json"

# Load registry
with REGISTRY_JSON.open("r", encoding="utf-8") as f:
    registry = json.load(f)

# Convert to int keys
found_phases = {int(k): v for k, v in registry.items()}

# Expected phases 1-300
expected_phases = set(range(1, 301))

# Found phases
found_phase_nums = set(found_phases.keys())

# Missing phases
missing_phases = expected_phases - found_phase_nums

print("=" * 70)
print("MISSING PHASES INVESTIGATION")
print("=" * 70)
print()
print(f"Expected phases: {len(expected_phases)} (1-300)")
print(f"Found phases: {len(found_phase_nums)}")
print(f"Missing phases: {len(missing_phases)}")
print()

if missing_phases:
    print("MISSING PHASES:")
    print("-" * 70)
    missing_sorted = sorted(missing_phases)
    
    # Group by ranges
    ranges = defaultdict(list)
    for phase in missing_sorted:
        range_start = (phase // 100) * 100 + 1
        range_key = f"{range_start}-{range_start+99}"
        ranges[range_key].append(phase)
    
    for range_key in sorted(ranges.keys()):
        phases = ranges[range_key]
        print(f"\n{range_key}: {len(phases)} missing")
        print(f"  Phases: {phases}")
        
        # Check if they're in core/ultra
        for phase in phases:
            ultra_file = PROJECT_ROOT / "core" / "ultra" / f"phase{phase}_*.py"
            ultra_files = list(PROJECT_ROOT.glob(f"core/ultra/phase{phase}_*.py"))
            if ultra_files:
                print(f"    Phase {phase}: Found in core/ultra/ - {ultra_files[0].name}")
            
            # Check root scripts
            root_files = list(PROJECT_ROOT.glob(f"system3_*phase{phase}*.py"))
            if root_files:
                print(f"    Phase {phase}: Found in root - {root_files[0].name}")

print()
print("=" * 70)
print("CHECKING SPECIAL LOCATIONS")
print("=" * 70)

# Check core/ultra for phases 46-55
print("\nChecking core/ultra/ for phases 46-55:")
ultra_phases = []
for phase in range(46, 56):
    ultra_files = list(PROJECT_ROOT.glob(f"core/ultra/phase{phase}_*.py"))
    if ultra_files:
        ultra_phases.append(phase)
        print(f"  Phase {phase}: ✅ Found - {ultra_files[0].name}")
    else:
        print(f"  Phase {phase}: ❌ Not found")

# Check root scripts for phases 231-260
print("\nChecking root scripts for phases 231-260:")
root_phase_scripts = {
    238: "system3_virtual_orders_schema_check.py",
    239: "system3_virtual_trades_enrichment.py",
    240: "system3_virtual_trades_summary.py",
    241: "system3_virtual_trades_diagnostics.py",
    243: "system3_threshold_evolution_tracker.py",
    244: "system3_score_to_trade_attribution.py",
    245: "system3_symbol_participation_summary.py",
    246: "system3_trade_density_vs_regime.py",
    247: "system3_edge_by_score_bucket_tracker.py",
}

for phase, script_name in root_phase_scripts.items():
    script_path = PROJECT_ROOT / script_name
    if script_path.exists():
        print(f"  Phase {phase}: ✅ Found - {script_name}")
    else:
        print(f"  Phase {phase}: ❌ Not found - {script_name}")

# Check special modules
print("\nChecking special modules:")
special_modules = {
    231: "core/engine/threshold_loader.py",
    233: "core/execution/order_models.py",
    234: "core/config/live_trade_config_loader.py",
    235: "core/execution/risk_guard.py",
    236: "core/execution/live_execution_engine.py",
    242: "core/monitoring/alert_hooks.py",
}

for phase, module_path in special_modules.items():
    full_path = PROJECT_ROOT / module_path
    if full_path.exists():
        print(f"  Phase {phase}: ✅ Found - {module_path}")
    else:
        print(f"  Phase {phase}: ❌ Not found - {module_path}")

print()
print("=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"Missing from registry: {len(missing_phases)} phases")
print(f"Missing phase numbers: {sorted(missing_phases)}")

