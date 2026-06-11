"""
System3 Phase Registry Builder

Scans docs and code to build a comprehensive phase registry.
Follows System3 MASTER AGENT INSTRUCTION pattern.
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Set
from collections import defaultdict

PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DOCS_DIR = PROJECT_ROOT / "docs"
ENGINE_DIR = PROJECT_ROOT / "core" / "engine"
ROOT_DIR = PROJECT_ROOT

# Registry structure
registry: Dict[int, Dict[str, Any]] = {}


def scan_spec_files() -> Dict[int, Dict[str, Any]]:
    """Scan docs for phase specifications."""
    spec_registry = {}
    
    # Pattern 1: System3_Phases_*_FullPass.md
    for spec_file in DOCS_DIR.glob("System3_Phases_*_FullPass*.md"):
        try:
            content = spec_file.read_text(encoding="utf-8")
            # Extract phase numbers
            phase_matches = re.findall(r"## PHASE (\d+)", content)
            for phase_str in phase_matches:
                phase_num = int(phase_str)
                if phase_num not in spec_registry:
                    spec_registry[phase_num] = {
                        "spec_present": True,
                        "spec_file": str(spec_file),
                        "spec_type": "FullPass",
                    }
        except Exception as e:
            print(f"Warning: Error reading {spec_file}: {e}")
    
    # Pattern 2: system3_phases_*_*.md (status/implementation docs)
    for status_file in DOCS_DIR.glob("system3_phases_*_*.md"):
        try:
            # Extract phase range from filename
            match = re.search(r"phases_(\d+)_(\d+)", status_file.stem)
            if match:
                start, end = int(match.group(1)), int(match.group(2))
                for phase_num in range(start, end + 1):
                    if phase_num not in spec_registry:
                        spec_registry[phase_num] = {
                            "spec_present": False,
                            "spec_file": None,
                            "spec_type": None,
                        }
                    if "status" not in spec_registry[phase_num]:
                        spec_registry[phase_num]["status_files"] = []
                    if "status_files" not in spec_registry[phase_num]:
                        spec_registry[phase_num]["status_files"] = []
                    spec_registry[phase_num]["status_files"].append(str(status_file))
        except Exception:
            pass
    
    return spec_registry


def scan_implementation_files() -> Dict[int, Dict[str, Any]]:
    """Scan core/engine for phase implementation files."""
    impl_registry = {}
    
    # Scan core/engine
    for phase_file in ENGINE_DIR.glob("system3_phase*.py"):
        match = re.search(r"phase(\d+)", phase_file.stem)
        if match:
            phase_num = int(match.group(1))
            impl_registry[phase_num] = {
                "implemented": True,
                "impl_file": str(phase_file),
                "impl_location": "core/engine",
            }
    
    # Scan root for phase scripts
    for phase_file in ROOT_DIR.glob("system3_phase*.py"):
        match = re.search(r"phase(\d+)", phase_file.stem)
        if match:
            phase_num = int(match.group(1))
            if phase_num not in impl_registry:
                impl_registry[phase_num] = {
                    "implemented": True,
                    "impl_file": str(phase_file),
                    "impl_location": "root",
                }
    
    # Scan root for phase diagnostic scripts
    for diag_file in ROOT_DIR.glob("system3_phase_*_diagnostics.py"):
        match = re.search(r"phase_(\d+)_(\d+)_diagnostics", diag_file.stem)
        if match:
            start, end = int(match.group(1)), int(match.group(2))
            for phase_num in range(start, end + 1):
                if phase_num not in impl_registry:
                    impl_registry[phase_num] = {
                        "implemented": False,
                        "impl_file": None,
                        "impl_location": None,
                    }
                if "diagnostics_scripts" not in impl_registry[phase_num]:
                    impl_registry[phase_num]["diagnostics_scripts"] = []
                impl_registry[phase_num]["diagnostics_scripts"].append(str(diag_file))
    
    return impl_registry


def merge_registry(spec_registry: Dict, impl_registry: Dict) -> Dict[int, Dict[str, Any]]:
    """Merge spec and implementation registries."""
    all_phases = set(spec_registry.keys()) | set(impl_registry.keys())
    merged = {}
    
    for phase_num in sorted(all_phases):
        merged[phase_num] = {
            "phase": phase_num,
            "spec_present": spec_registry.get(phase_num, {}).get("spec_present", False),
            "spec_file": spec_registry.get(phase_num, {}).get("spec_file"),
            "spec_type": spec_registry.get(phase_num, {}).get("spec_type"),
            "status_files": spec_registry.get(phase_num, {}).get("status_files", []),
            "implemented": impl_registry.get(phase_num, {}).get("implemented", False),
            "impl_file": impl_registry.get(phase_num, {}).get("impl_file"),
            "impl_location": impl_registry.get(phase_num, {}).get("impl_location"),
            "diagnostics_scripts": impl_registry.get(phase_num, {}).get("diagnostics_scripts", []),
            "warn_or_error": False,  # Will be updated from diagnostics
            "notes": "",
        }
    
    return merged


def load_status_from_docs(registry: Dict[int, Dict[str, Any]]) -> Dict[int, Dict[str, Any]]:
    """Load implementation status from existing status documents."""
    # Known status documents
    status_docs = {
        (1, 100): "system3_complete_phase_status.md",
        (101, 130): "system3_phases_101_130_final_status.md",
        (131, 200): "system3_phases_131_200_implementation_status.md",
        (201, 230): "system3_phases_201_230_implementation_status.md",
        (231, 260): "system3_phases_231_260_implementation_status.md",
        (261, 300): "system3_phases_261_300_implementation_summary.md",
    }
    
    for (start, end), doc_name in status_docs.items():
        doc_path = DOCS_DIR / doc_name
        if doc_path.exists():
            for phase_num in range(start, end + 1):
                if phase_num in registry:
                    registry[phase_num]["status_doc"] = str(doc_path)
                    # Mark as implemented if status doc exists
                    if not registry[phase_num]["implemented"]:
                        # Check if status doc says implemented
                        try:
                            content = doc_path.read_text(encoding="utf-8")
                            if "IMPLEMENTATION COMPLETE" in content or "✅" in content:
                                registry[phase_num]["implemented"] = True
                        except Exception:
                            pass
    
    return registry


def build_registry() -> Dict[int, Dict[str, Any]]:
    """Build complete phase registry."""
    print("Scanning specification files...")
    spec_registry = scan_spec_files()
    
    print("Scanning implementation files...")
    impl_registry = scan_implementation_files()
    
    print("Merging registries...")
    merged = merge_registry(spec_registry, impl_registry)
    
    print("Loading status from docs...")
    merged = load_status_from_docs(merged)
    
    return merged


def generate_registry_report(registry: Dict[int, Dict[str, Any]]) -> str:
    """Generate markdown report from registry."""
    lines = [
        "# System3 Phase Registry",
        "",
        f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Total Phases Found**: {len(registry)}",
        "",
        "---",
        "",
        "## Summary Statistics",
        "",
    ]
    
    # Calculate statistics
    total = len(registry)
    with_spec = sum(1 for p in registry.values() if p.get("spec_present"))
    implemented = sum(1 for p in registry.values() if p.get("implemented"))
    max_phase = max(registry.keys()) if registry else 0
    
    lines.extend([
        f"- **Total Phases**: {total}",
        f"- **Phases with Spec**: {with_spec} ({with_spec/total*100:.1f}%)",
        f"- **Phases Implemented**: {implemented} ({implemented/total*100:.1f}%)",
        f"- **Highest Phase Number**: {max_phase}",
        "",
        "---",
        "",
        "## Phase Ranges",
        "",
    ])
    
    # Group by ranges
    ranges = defaultdict(list)
    for phase_num in sorted(registry.keys()):
        range_start = (phase_num // 100) * 100 + 1
        range_end = ((phase_num // 100) + 1) * 100
        range_key = f"{range_start}-{range_end}"
        ranges[range_key].append(phase_num)
    
    for range_key in sorted(ranges.keys()):
        phases = ranges[range_key]
        implemented_count = sum(1 for p in phases if registry[p].get("implemented"))
        lines.append(f"### Phases {range_key}")
        lines.append(f"- **Total**: {len(phases)}")
        lines.append(f"- **Implemented**: {implemented_count} ({implemented_count/len(phases)*100:.1f}%)")
        lines.append("")
    
    lines.extend([
        "---",
        "",
        "## Detailed Phase List",
        "",
        "| Phase | Spec | Implemented | Location | Status Files |",
        "|-------|------|-------------|----------|---------------|",
    ])
    
    for phase_num in sorted(registry.keys()):
        phase_data = registry[phase_num]
        spec = "✅" if phase_data.get("spec_present") else "❌"
        impl = "✅" if phase_data.get("implemented") else "❌"
        location = phase_data.get("impl_location", "N/A")
        status_count = len(phase_data.get("status_files", []))
        lines.append(
            f"| {phase_num} | {spec} | {impl} | {location} | {status_count} |"
        )
    
    return "\n".join(lines)


def main():
    """Main function."""
    print("=" * 70)
    print("SYSTEM3 PHASE REGISTRY BUILDER")
    print("=" * 70)
    print()
    
    registry = build_registry()
    
    # Save JSON registry
    registry_json = PROJECT_ROOT / "storage" / "meta" / "system3_phase_registry.json"
    registry_json.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert to JSON-serializable format
    json_registry = {}
    for phase_num, data in registry.items():
        json_registry[str(phase_num)] = {
            k: v for k, v in data.items()
            if isinstance(v, (str, int, bool, list)) or v is None
        }
    
    with registry_json.open("w", encoding="utf-8") as f:
        json.dump(json_registry, f, indent=2)
    
    print(f"Registry saved to: {registry_json}")
    
    # Generate report
    report = generate_registry_report(registry)
    report_path = DOCS_DIR / "system3_phase_registry_report.md"
    with report_path.open("w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"Report saved to: {report_path}")
    
    # Print summary
    print()
    print("=" * 70)
    print("REGISTRY SUMMARY")
    print("=" * 70)
    print(f"Total Phases: {len(registry)}")
    print(f"Highest Phase: {max(registry.keys()) if registry else 0}")
    print(f"With Spec: {sum(1 for p in registry.values() if p.get('spec_present'))}")
    print(f"Implemented: {sum(1 for p in registry.values() if p.get('implemented'))}")
    print("=" * 70)


if __name__ == "__main__":
    main()

