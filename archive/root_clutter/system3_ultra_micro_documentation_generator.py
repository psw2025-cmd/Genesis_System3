#!/usr/bin/env python3
"""
System3 Ultra Micro Documentation Generator
Creates comprehensive, ultra-detailed documentation for the entire project and all phases.
"""

import sys
import ast
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import inspect

PROJECT_ROOT = Path(__file__).parent.absolute()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Output directory
DOCS_DIR = PROJECT_ROOT / "docs" / "ultra_micro"
DOCS_DIR.mkdir(parents=True, exist_ok=True)

print("="*80)
print("SYSTEM3 ULTRA MICRO DOCUMENTATION GENERATOR")
print("="*80)
print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*80)
print()

# ============================================================================
# PHASE 1: PROJECT OVERVIEW
# ============================================================================

def analyze_project_structure() -> Dict[str, Any]:
    """Analyze overall project structure."""
    print("Analyzing project structure...")
    
    structure = {
        "project_name": "System3",
        "description": "Autonomous Trading System for AngelOne Index Options",
        "language": "Python 3.8+",
        "architecture": "Modular Phase-Based System",
        "directories": {},
        "key_files": {},
        "dependencies": [],
    }
    
    # Analyze directories
    key_dirs = [
        "core",
        "core/engine",
        "core/phases",
        "core/brokers",
        "config",
        "storage",
        "storage/live",
        "storage/meta",
        "logs",
        "docs",
    ]
    
    for dir_path in key_dirs:
        full_path = PROJECT_ROOT / dir_path
        if full_path.exists():
            files = list(full_path.glob("*"))
            structure["directories"][dir_path] = {
                "exists": True,
                "file_count": len([f for f in files if f.is_file()]),
                "subdir_count": len([f for f in files if f.is_dir()]),
            }
    
    # Key files
    key_files = [
        "system3_autorun_master.py",
        "system3_watchdog.py",
        "system3_live_day_autopilot.py",
        "START_AUTORUN_AND_WATCHDOG.bat",
    ]
    
    for file_name in key_files:
        file_path = PROJECT_ROOT / file_name
        if file_path.exists():
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            structure["key_files"][file_name] = {
                "exists": True,
                "size_bytes": len(content),
                "lines": len(content.splitlines()),
                "has_main": "def main()" in content or "if __name__" in content,
            }
    
    return structure


# ============================================================================
# PHASE 2: PHASE ANALYSIS
# ============================================================================

def analyze_phase_file(phase_file: Path) -> Dict[str, Any]:
    """Analyze a single phase file in ultra-micro detail."""
    try:
        content = phase_file.read_text(encoding="utf-8", errors="ignore")
        
        # Extract phase number
        phase_match = re.search(r"phase(\d+)", phase_file.stem, re.IGNORECASE)
        phase_num = int(phase_match.group(1)) if phase_match else None
        
        # Parse AST
        try:
            tree = ast.parse(content)
        except:
            tree = None
        
        # Extract information
        info = {
            "phase_number": phase_num,
            "file_name": phase_file.name,
            "file_path": str(phase_file.relative_to(PROJECT_ROOT)),
            "size_bytes": len(content),
            "lines_total": len(content.splitlines()),
            "functions": [],
            "classes": [],
            "imports": [],
            "docstring": None,
            "has_run_function": False,
            "dependencies": [],
            "outputs": [],
            "inputs": [],
        }
        
        # Extract docstring
        if tree and tree.body and isinstance(tree.body[0], ast.Expr):
            if isinstance(tree.body[0].value, ast.Str):
                info["docstring"] = tree.body[0].value.s
        
        # Extract functions
        if tree:
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_info = {
                        "name": node.name,
                        "line_start": node.lineno,
                        "args": [arg.arg for arg in node.args.args],
                        "has_docstring": ast.get_docstring(node) is not None,
                    }
                    info["functions"].append(func_info)
                    
                    if node.name.startswith("run_phase") or node.name == f"run_phase{phase_num}":
                        info["has_run_function"] = True
                
                elif isinstance(node, ast.ClassDef):
                    class_info = {
                        "name": node.name,
                        "line_start": node.lineno,
                        "has_docstring": ast.get_docstring(node) is not None,
                    }
                    info["classes"].append(class_info)
                
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        info["imports"].append(alias.name)
                
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        info["imports"].append(f"{module}.{alias.name}")
        
        # Extract file paths (potential inputs/outputs)
        path_patterns = [
            r'["\']([^"\']*\.csv)["\']',
            r'["\']([^"\']*\.json)["\']',
            r'["\']([^"\']*\.md)["\']',
            r'Path\(["\']([^"\']+)["\']',
        ]
        
        for pattern in path_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if "storage" in match or "logs" in match or "output" in match:
                    if match not in info["outputs"]:
                        info["outputs"].append(match)
                elif "input" in match or "read" in match.lower():
                    if match not in info["inputs"]:
                        info["inputs"].append(match)
        
        return info
    except Exception as e:
        return {
            "phase_number": None,
            "file_name": phase_file.name,
            "error": str(e),
        }


def analyze_all_phases() -> Dict[int, Dict[str, Any]]:
    """Analyze all phase files."""
    print("Analyzing all phase files...")
    
    phase_files = list((PROJECT_ROOT / "core" / "engine").glob("system3_phase*.py"))
    phases = {}
    
    for phase_file in phase_files:
        info = analyze_phase_file(phase_file)
        if info.get("phase_number"):
            phases[info["phase_number"]] = info
    
    print(f"  Found {len(phases)} phase files")
    return phases


# ============================================================================
# PHASE 3: CONFIGURATION ANALYSIS
# ============================================================================

def analyze_configurations() -> Dict[str, Any]:
    """Analyze all configuration files."""
    print("Analyzing configurations...")
    
    configs = {
        "safety_flags": {},
        "trading_config": {},
        "automation_config": {},
        "file_paths": {},
    }
    
    # Check safety flags
    try:
        from config.live_trade_config import LIVE_TRADING_ENABLED, USE_LIVE_EXECUTION_ENGINE
        configs["safety_flags"]["LIVE_TRADING_ENABLED"] = LIVE_TRADING_ENABLED
        configs["safety_flags"]["USE_LIVE_EXECUTION_ENGINE"] = USE_LIVE_EXECUTION_ENGINE
    except:
        pass
    
    # Check automation config
    try:
        from core.engine.angel_automation_config import AUTOMATION_CONFIG
        configs["automation_config"]["auto_execute_trades"] = getattr(AUTOMATION_CONFIG, "auto_execute_trades", None)
    except:
        pass
    
    return configs


# ============================================================================
# PHASE 4: DATA FLOW ANALYSIS
# ============================================================================

def analyze_data_flows() -> Dict[str, Any]:
    """Analyze data flows between components."""
    print("Analyzing data flows...")
    
    flows = {
        "signal_generation": [],
        "phase_execution": [],
        "file_dependencies": {},
    }
    
    # Analyze signal flow
    signal_files = [
        "storage/live/angel_index_ai_signals.csv",
        "storage/live/angel_index_ai_signals_curated.csv",
        "storage/live/angel_index_ai_signals_with_forward.csv",
    ]
    
    for sig_file in signal_files:
        file_path = PROJECT_ROOT / sig_file
        if file_path.exists():
            flows["signal_generation"].append({
                "file": sig_file,
                "exists": True,
                "size_bytes": file_path.stat().st_size,
            })
    
    return flows


# ============================================================================
# MAIN GENERATION
# ============================================================================

def generate_ultra_micro_docs():
    """Generate all ultra-micro documentation."""
    
    # 1. Project Overview
    print("\n" + "="*80)
    print("GENERATING PROJECT OVERVIEW")
    print("="*80)
    project_structure = analyze_project_structure()
    
    overview_file = DOCS_DIR / "00_PROJECT_OVERVIEW.md"
    with overview_file.open("w", encoding="utf-8") as f:
        f.write(f"""# System3 - Ultra Micro Project Overview
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Project Information

**Name**: {project_structure['project_name']}  
**Description**: {project_structure['description']}  
**Language**: {project_structure['language']}  
**Architecture**: {project_structure['architecture']}

## Directory Structure

""")
        for dir_path, info in project_structure["directories"].items():
            f.write(f"### `{dir_path}/`\n")
            f.write(f"- **Files**: {info['file_count']}\n")
            f.write(f"- **Subdirectories**: {info['subdir_count']}\n\n")
        
        f.write("## Key Files\n\n")
        for file_name, info in project_structure["key_files"].items():
            f.write(f"### `{file_name}`\n")
            f.write(f"- **Size**: {info['size_bytes']:,} bytes\n")
            f.write(f"- **Lines**: {info['lines']:,}\n")
            f.write(f"- **Has Main**: {info['has_main']}\n\n")
    
    print(f"  ✅ Generated: {overview_file.name}")
    
    # 2. All Phases Analysis
    print("\n" + "="*80)
    print("GENERATING PHASE DOCUMENTATION")
    print("="*80)
    all_phases = analyze_all_phases()
    
    # Generate master phase index
    index_file = DOCS_DIR / "01_PHASE_INDEX.md"
    with index_file.open("w", encoding="utf-8") as f:
        f.write(f"""# System3 Phase Index - Ultra Micro Detail
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Total Phases**: {len(all_phases)}

## Phase Summary

| Phase | File | Lines | Functions | Has Run Function | Status |
|-------|------|-------|-----------|------------------|--------|
""")
        for phase_num in sorted(all_phases.keys()):
            phase = all_phases[phase_num]
            f.write(f"| {phase_num} | `{phase['file_name']}` | {phase['lines_total']} | {len(phase['functions'])} | {phase['has_run_function']} | ✅ |\n")
    
    print(f"  ✅ Generated: {index_file.name}")
    
    # Generate individual phase docs (first 50 for now, can extend)
    print("\nGenerating individual phase documentation...")
    phases_dir = DOCS_DIR / "phases"
    phases_dir.mkdir(exist_ok=True)
    
    for phase_num in sorted(all_phases.keys())[:50]:  # First 50 phases
        phase = all_phases[phase_num]
        phase_file = phases_dir / f"phase_{phase_num:03d}_ultra_micro.md"
        
        with phase_file.open("w", encoding="utf-8") as f:
            f.write(f"""# Phase {phase_num} - Ultra Micro Documentation
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Basic Information

- **Phase Number**: {phase_num}
- **File Name**: `{phase['file_name']}`
- **File Path**: `{phase['file_path']}`
- **Size**: {phase['size_bytes']:,} bytes
- **Total Lines**: {phase['lines_total']:,}

## Documentation

```python
{phase.get('docstring', 'No docstring found')}
```

## Functions ({len(phase['functions'])})

""")
            for func in phase['functions']:
                f.write(f"""### `{func['name']}()`

- **Line**: {func['line_start']}
- **Arguments**: {', '.join(func['args']) if func['args'] else 'None'}
- **Has Docstring**: {func['has_docstring']}

""")
            
            if phase['classes']:
                f.write("## Classes\n\n")
                for cls in phase['classes']:
                    f.write(f"""### `{cls['name']}`

- **Line**: {cls['line_start']}
- **Has Docstring**: {cls['has_docstring']}

""")
            
            if phase['imports']:
                f.write(f"## Imports ({len(phase['imports'])})\n\n")
                for imp in sorted(set(phase['imports']))[:20]:  # First 20 unique
                    f.write(f"- `{imp}`\n")
                if len(set(phase['imports'])) > 20:
                    f.write(f"\n... and {len(set(phase['imports'])) - 20} more\n")
            
            if phase['inputs']:
                f.write(f"\n## Input Files\n\n")
                for inp in phase['inputs']:
                    f.write(f"- `{inp}`\n")
            
            if phase['outputs']:
                f.write(f"\n## Output Files\n\n")
                for out in phase['outputs']:
                    f.write(f"- `{out}`\n")
        
        if phase_num % 10 == 0:
            print(f"  Generated {phase_num} phase docs...")
    
    print(f"  ✅ Generated individual phase docs for {min(50, len(all_phases))} phases")
    
    # 3. Configuration Documentation
    print("\n" + "="*80)
    print("GENERATING CONFIGURATION DOCUMENTATION")
    print("="*80)
    configs = analyze_configurations()
    
    config_file = DOCS_DIR / "02_CONFIGURATION_ULTRA_MICRO.md"
    with config_file.open("w", encoding="utf-8") as f:
        f.write(f"""# System3 Configuration - Ultra Micro Detail
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Safety Flags

""")
        for flag, value in configs["safety_flags"].items():
            f.write(f"- **{flag}**: `{value}`\n")
        
        f.write("\n## Automation Config\n\n")
        for key, value in configs["automation_config"].items():
            f.write(f"- **{key}**: `{value}`\n")
    
    print(f"  ✅ Generated: {config_file.name}")
    
    # 4. Data Flow Documentation
    print("\n" + "="*80)
    print("GENERATING DATA FLOW DOCUMENTATION")
    print("="*80)
    flows = analyze_data_flows()
    
    flow_file = DOCS_DIR / "03_DATA_FLOWS_ULTRA_MICRO.md"
    with flow_file.open("w", encoding="utf-8") as f:
        f.write(f"""# System3 Data Flows - Ultra Micro Detail
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Signal Generation Files

""")
        for sig in flows["signal_generation"]:
            f.write(f"- **{sig['file']}**: {sig['size_bytes']:,} bytes\n")
    
    print(f"  ✅ Generated: {flow_file.name}")
    
    # 5. Master Index
    master_index = DOCS_DIR / "00_MASTER_INDEX.md"
    with master_index.open("w", encoding="utf-8") as f:
        f.write(f"""# System3 Ultra Micro Documentation - Master Index
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Documentation Structure

1. **[Project Overview](00_PROJECT_OVERVIEW.md)** - Overall project structure
2. **[Phase Index](01_PHASE_INDEX.md)** - Complete list of all phases
3. **[Configuration](02_CONFIGURATION_ULTRA_MICRO.md)** - All configuration details
4. **[Data Flows](03_DATA_FLOWS_ULTRA_MICRO.md)** - Data flow analysis

## Individual Phase Documentation

Located in `phases/` directory:
- `phase_001_ultra_micro.md` through `phase_{max(all_phases.keys()):03d}_ultra_micro.md`

## Statistics

- **Total Phases Documented**: {len(all_phases)}
- **Total Functions**: {sum(len(p['functions']) for p in all_phases.values())}
- **Total Classes**: {sum(len(p['classes']) for p in all_phases.values())}
- **Total Lines of Code**: {sum(p['lines_total'] for p in all_phases.values()):,}

## Quick Links

- [Project Overview](00_PROJECT_OVERVIEW.md)
- [Phase Index](01_PHASE_INDEX.md)
- [Configuration Details](02_CONFIGURATION_ULTRA_MICRO.md)
- [Data Flows](03_DATA_FLOWS_ULTRA_MICRO.md)
""")
    
    print(f"  ✅ Generated: {master_index.name}")
    
    # Save JSON summary
    summary = {
        "generated": datetime.now().isoformat(),
        "total_phases": len(all_phases),
        "project_structure": project_structure,
        "phases_summary": {
            phase_num: {
                "file": phase["file_name"],
                "lines": phase["lines_total"],
                "functions": len(phase["functions"]),
            }
            for phase_num, phase in all_phases.items()
        },
    }
    
    summary_file = DOCS_DIR / "summary.json"
    with summary_file.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, default=str)
    
    print(f"  ✅ Generated: {summary_file.name}")
    
    print("\n" + "="*80)
    print("DOCUMENTATION GENERATION COMPLETE")
    print("="*80)
    print(f"\nTotal Phases Documented: {len(all_phases)}")
    print(f"Documentation Location: {DOCS_DIR}")
    print(f"\nStart with: {master_index}")
    print("="*80)


if __name__ == "__main__":
    try:
        generate_ultra_micro_docs()
    except Exception as e:
        import traceback
        print(f"\n❌ Error: {e}")
        print(traceback.format_exc())
        sys.exit(1)

