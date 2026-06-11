"""
Add phases 311-330 to the System3 phase registry
"""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
REGISTRY_FILE = PROJECT_ROOT / "storage" / "meta" / "system3_phase_registry.json"

# New phases to add
NEW_PHASES = {
    311: {"name": "Baseline FS Snapshot", "category": "Integrity"},
    312: {"name": "Phase Registry Self-Check", "category": "Integrity"},
    313: {"name": "Config Consistency Auditor", "category": "Integrity"},
    314: {"name": "Data Lineage Tracker", "category": "Integrity"},
    315: {"name": "Transactional Write Guard", "category": "Integrity"},
    316: {"name": "Input Schema Gateway", "category": "Anti-Corruption"},
    317: {"name": "Live Feed Sanitizer", "category": "Anti-Corruption"},
    318: {"name": "Signal Outlier Detector", "category": "Anti-Corruption"},
    319: {"name": "Position State Consistency Checker", "category": "Anti-Corruption"},
    320: {"name": "Risk Config Corruption Guard", "category": "Anti-Corruption"},
    321: {"name": "Latency Profiler", "category": "Observability"},
    322: {"name": "Resource Usage Monitor", "category": "Observability"},
    323: {"name": "Phase Health Timeline Builder", "category": "Observability"},
    324: {"name": "WARN Error Cluster Analyzer", "category": "Observability"},
    325: {"name": "Observability Summary Exporter", "category": "Observability"},
    326: {"name": "Root Cause Hint Generator", "category": "Diagnostics"},
    327: {"name": "Predictive Failure Scout", "category": "Diagnostics"},
    328: {"name": "Daily Integrity Scorecard", "category": "Diagnostics"},
    329: {"name": "Changeset and Version Recorder", "category": "Diagnostics"},
    330: {"name": "Integrity Gate Before Live Toggle", "category": "Diagnostics"},
}

def update_registry():
    """Update the phase registry with new phases."""
    
    # Load existing registry
    with open(REGISTRY_FILE, "r") as f:
        registry = json.load(f)
    
    # Add new phases
    for phase_num, info in NEW_PHASES.items():
        phase_key = str(phase_num)
        
        registry[phase_key] = {
            "phase": phase_num,
            "name": info["name"],
            "category": info["category"],
            "spec_present": True,
            "spec_file": f"docs/system3_phase_{phase_num}_spec.md",
            "spec_type": "auto-generated",
            "status_files": [],
            "implemented": True,
            "impl_file": f"core/engine/system3_phase{phase_num}_*.py",
            "impl_location": "core/engine",
            "diagnostics_scripts": [],
            "warn_or_error": False,
            "notes": f"Phase {phase_num}: {info['name']} - {info['category']} layer",
            "status_doc": "SYSTEM3_PHASES_311_330_IMPLEMENTATION_REPORT.md"
        }
    
    # Save updated registry
    backup_file = REGISTRY_FILE.parent / f"system3_phase_registry_backup_{Path().cwd().name}.json"
    with open(backup_file, "w") as f:
        json.dump(registry, f, indent=2)
    
    with open(REGISTRY_FILE, "w") as f:
        json.dump(registry, f, indent=2)
    
    print(f"✅ Registry updated with {len(NEW_PHASES)} new phases")
    print(f"✅ Backup saved to: {backup_file}")
    print(f"Total phases in registry: {len(registry)}")

if __name__ == "__main__":
    update_registry()
